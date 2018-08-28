#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re
import datetime
import subprocess
import tempfile
import logging
import argparse
from . import lib
from .exceptions import (UnknownNotebookError, InvalidNotebookPathError)

log = logging.getLogger(__name__)


class EditSnoteParser(argparse.ArgumentParser):

    def __init__(self):
        super(EditSnoteParser, self).__init__(add_help=False)
        self.add_argument(
            '-t',
            '--timestamp',
            action='store_true',
            help='add a timestamp to the note'
        )
        self.add_argument(
            '-f',
            '--filename',
            type=str,
            default=None,
            help='name a new note, or search for a note to update'
        )


class Snotebook(object):
    """container class to simplify access to configuration settings"""

    @staticmethod
    def get_snotebook(notebook):
        """
        Given the name of a configured Snotebook, returns Snotebook object
        """

        config = lib.get_config()

        if config.has_section(notebook):
            log.debug('Notebook %s exists', notebook)
        else:
            raise UnknownNotebookError(notebook)

        notebook_path = config.get(notebook, 'path')
        if os.path.exists(notebook_path):
            log.debug('Configured notebook path %s exists', notebook_path)
        else:
            raise InvalidNotebookPathError(notebook_path)

        snotebook_cfg = {
            'name': notebook,
            'location': notebook_path,
            'editor': config.get(notebook, 'editor'),
            'ext': config.get(notebook, 'ext'),
            'datefmt': config.get(notebook, 'datefmt'),
            'timefmt': config.get(notebook, 'timefmt'),
            'timestamp': config.get(notebook, 'timestamp'),
            'template': config.get(notebook, 'template'),
            'max_list': config.get(notebook, 'max_list', fallback=-1),
            'default_title': config.get(notebook, 'default_title')
        }

        return Snotebook(**snotebook_cfg)

    def __init__(self, name, location, editor='vim', ext='md',
                 datefmt='%Y-%m-%d', timefmt='%H:%M:%S',
                 timestamp='\n{time}', template=None, max_list=-1, default_title=None):
        self._name = name
        self._location = location
        self._editor = editor
        self._ext = ext
        self._datefmt = datefmt
        self._timefmt = timefmt
        self._timestamp = timestamp
        self._template = template
        self._max_list = max_list
        self._default_title = default_title

    @property
    def name(self):
        return self._name

    @property
    def location(self):
        return self._location

    @property
    def editor(self):
        return self._editor

    @property
    def ext(self):
        return self._ext

    @property
    def template(self):
        '''
        :returns: str representation of content in template file if configured,
        or an empty str
        '''
        if self._template:
            return lib.get_file_content(self._template).decode('utf-8')
        else:
            return ''

    @property
    def max_list(self):
        return int(self._max_list)

    @property
    def default_title(self):
        '''
        :returns: str representation of default title if configured, or an
        empty str
        '''
        if self._default_title:
            return self._default_title
        else:
            return ''

    def date(self):
        '''
        :returns: str representation of invocation date according to _datefmt
        '''
        return datetime.datetime.today().strftime(self._datefmt)

    def time(self):
        '''
        :returns: str representation of invocation time according to _timefmt
        '''
        current_time = datetime.datetime.now().strftime(self._timefmt)
        timestamp = self._timestamp.format(time=current_time)
        return timestamp.encode('utf-8')

    def call_writer(self, load_content, timestamp):
        '''
        Opens a temporary file with the configured editor and loads whatever
        prexisting content is passed in.

        :param load_content: str representation of content to load in editor
        :param timestamp: bool - True to add timestamp
        :returns: str of everything in the editor at exit
        '''
        with tempfile.NamedTemporaryFile(suffix='.{ext}'.format(ext=self.ext),
                                         prefix='snote_') as tf:
            tf.write(load_content)
            if timestamp:
                tf.write(self.time())
            tf.flush()
            subprocess.call([self.editor, tf.name])
            tf.seek(0)  # hang tight until subprocess is done
            new_content = tf.read()

        return new_content

    def get_note_path(self, filename=None):
        '''
        Return path to the most recently modified note in notebook, or the
        note with the specified filename
        '''
        if filename:
            notes = self._search_notes(filename)
            return self._select_note(notes)
        else:
            return self._last_note()

    def _list_notes(self, sort='name', reverse=False):
        '''
        Return list of notes in notebook (as os.DirEntry) sorted accordingly
        '''

        note_list = list()

        for entry in os.scandir(self.location):
            note_list.append(entry)

        if sort == 'name':
            note_list.sort(key=lambda e: e.name.lower(), reverse=reverse)
        elif sort == 'last':
            try:
                note_list.sort(key=lambda e: e.stat().st_birthtime,
                               reverse=reverse)
            except AttributeError:
                note_list.sort(key=lambda e: e.stat().st_ctime,
                               reverse=reverse)

        return note_list

    def display_note_info(self, file):
        note = file.name
        date = '.'.join(note.split('-')[0:3])  # separate date
        title = ' '.join(note.split('-')[3:])  # remove hyphens
        title = title.split('.')
        if len(title) > 1:
            title = title[0:-1]  # remove extension if there is one
        title = ''.join(title)
        return (date, title)

    def _show_note_list(self, note_list, max_list=None):
        note_name = '{:<12}{:<50}\n'
        all_len = len(note_list)
        if not max_list:  # no value passed, go to default
            max_list = self.max_list

        if max_list < 1:  # user did not set a default value OR passed in 0
            end_idx = all_len
        else:
            end_idx = min(all_len, max_list)

        with sys.stdout as stream:
            stream.write(note_name.format('Date', 'Title'))
            stream.write('{:=^62}\n'.format(''))
            for file in note_list[0:end_idx]:
                date, title = self.display_note_info(file)
                stream.write(note_name.format(date, title))

    def _select_note(self, note_list):  # FIXME refactor/make better thanks
        '''
        Prompt user with list of DirEntry objects from which to select
        '''

        selection = None
        if len(note_list) > 1:
            with sys.stdout as prompt:
                prompt.write('Multiple notes found\n')
                list_item = '{:>5} {:<12}{:<50}\n'
                prompt.write(list_item.format('', 'Date', 'Title'))
                for idx, file in enumerate(note_list):
                    selection_no = '[{}]'.format(idx + 1)
                    date, title = self.display_note_info(file)
                    note = list_item.format(selection_no, date, title)
                    prompt.write(note)
                prompt.write('Select: ')

            with sys.stdin as stream:
                selection = stream.readline()

        if selection:
            try:
                select_idx = int(selection) - 1
                note = note_list[select_idx]
                log.debug('Selected note %s', note.name)
                return note.path
            except IndexError as e:
                log.error('%s: Invalid selection entered', e)
                sys.exit(1)
        else:
            return note_list.pop().path

    def _last_note(self):
        '''
        Return path to the most recently created (not modified) note in
        notebook
        '''
        last_modified = self._list_notes(sort='last').pop()
        return last_modified.path

    def _search_notes(self, search_term):
        '''
        Return list of filenames in notebook directory that contain the search
        term
        '''
        matches = list()
        hypenated_search = '-'.join(search_term.split())
        search_pattern = re.compile(search_term, re.I)
        hyphenated_search_pattern = re.compile(hypenated_search, re.I)
        for note in self._list_notes():
            if search_pattern.search(note.name) or hyphenated_search_pattern.search(note.name):
                matches.append(note)

        if len(matches) > 0:
            return matches
        else:
            log.info('No file containing \'%s\' found', search_term)
            sys.exit(1)

    def new_note(self, filename=None, timestamp=False):  # FIXME refactor more
        '''
        Creates a new note, opens editor with template loaded, and saves to
        snotebook folder upon exit if any changes have been made
        '''
        if filename:
            title = filename
        else:
            title = self.default_title

        notepath = '{date}-{title}.{ext}'.format(date=self.date(),
                                                 title='-'.join(title.split()),
                                                 ext=self.ext)
        full_notepath = os.path.join(self.location, notepath)

        initial_content = lib.TEMPLATE_TITLE.sub(title, self.template)

        new_content = self.call_writer(initial_content.encode('utf-8'), timestamp)

        if initial_content != new_content:
            log.debug('Saving note')
            lib.write_note(full_notepath, new_content)
        else:
            log.debug('No change detected, not saving')

    def update_note(self, filename=None, timestamp=False):  # FIXME refactor
        '''
        Loads contents of the last modified note in snotebook folder into
        writer, saves to snotebook folder upon exit of any changes have been
        made
        '''
        full_notepath = self.get_note_path(filename)
        initial_content = lib.get_file_content(full_notepath)

        new_content = self.call_writer(initial_content, timestamp)

        if initial_content != new_content:
            log.debug('Saving note')
            lib.write_note(full_notepath, new_content)
        else:
            log.debug('No change detected, not saving')

    def list_notes(self, max_notes=0):
        note_list = self._list_notes(reverse=True)
        self._show_note_list(note_list, max_notes)

    def search_notes(self, search_term):
        note_list = self._search_notes(search_term)
        self._show_note_list(note_list)
