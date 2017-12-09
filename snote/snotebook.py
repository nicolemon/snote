#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import re
import datetime
import subprocess
import tempfile
import logging

log = logging.getLogger("snotebook")


def filestat_name(dir_entry):  # TODO look into making lambda functions tho
    return dir_entry.name.lower()


def filestat_created(dir_entry):
    try:
        return dir_entry.stat().st_birthtime
    except AttributeError:
        return dir_entry.stat().st_ctime


class Snotebook(object):
    """container class to simplify access to configuration settings"""

    TEMPLATE_TITLE = re.compile('%TITLE%')

    @staticmethod
    def get_note(filepath):  # returns bytes
        '''
        Load and return content of file object at filepath

        :param filepath: valid filepath
        :returns: as bytes object
        '''
        note = b''
        with open(filepath, 'r+b') as content:
            note = content.read()
        return note

    @staticmethod
    def write_note(filepath, note):  # write bytes
        '''
        Writes to filepath with the content of note

        :param filepath: valid filepath
        :param note: str representation of content to write
        '''
        with open(filepath, 'w+b') as content:
            content.write(note)
        log.info('Note saved')

    def call_writer(self, load_content, timestamp):
        '''
        Opens a temporary file with the configured editor and loads whatever
        prexisting content is passed in.

        :param load_content: str representation of content to load in editor
        :param timestamp: bool - True to add timestamp
        :returns: str of everything in the editor at exit
        '''
        with tempfile.NamedTemporaryFile(suffix='.{ext}'.format(ext=self.ext),
                                         prefix='newsnote_',
                                         dir=self.location) as tf:
            tf.write(load_content)
            if timestamp:
                tf.write(self.time())
            tf.flush()
            subprocess.call([self.editor, tf.name])
            tf.seek(0)  # hang tight until subprocess is done
            new_content = tf.read()

        return new_content

    def __init__(self, name, location, editor='vim', ext='md',
                 datefmt='%Y-%m-%d', timefmt='%H:%M:%S',
                 timestamp='\n{time}', template=None, default_title=None):
        self._name = name
        self._location = location
        self._editor = editor
        self._ext = ext
        self._datefmt = datefmt
        self._timefmt = timefmt
        self._timestamp = timestamp
        self._template = template
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
            return Snotebook.get_note(self._template).decode('utf-8')
        else:
            return ''

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

    def find_note(self, filename=None):
        '''
        Return path to the most recently modified note in notebook, or the
        note with the specified filename
        '''
        if filename:
            notes = self._search_notes(filename.pop())
            return self._select_note(notes)
        else:
            return self._last_note()

    def _list_notes(self, sort_by='name', reverse=False):
        '''
        Return list of notes in notebook (as os.DirEntry) sorted accordingly
        '''

        note_list = list()
        for entry in os.scandir(self.location):
            note_list.append(entry)

        if sort_by == 'name':
            note_list.sort(key=filestat_name, reverse=reverse)
        elif sort_by == 'last':
            note_list.sort(key=filestat_created, reverse=reverse)

        return note_list

    def _select_note(self, note_list):  # FIXME refactor/make better thanks
        '''
        Prompt user with list of DirEntry objects from which to select
        '''
        selection = None
        if len(note_list) > 1:
            with sys.stdout as prompt:
                prompt.write('Multiple notes found\n')
                for idx, file in enumerate(note_list):
                    note = '[{idx}] {filename}\n'.format(idx=idx + 1, filename=file.name)
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
            return self._last_note()

    def _last_note(self):
        '''
        Return path to the most recently created (not modified) note in
        notebook
        '''
        last_modified = self._list_notes('last').pop()
        return last_modified.path

    def _search_notes(self, search):
        '''
        Return list of files in notebook directory that contain the search term
        '''
        matches = list()
        for note in self._list_notes():
            if search in note.name:
                matches.append(note)

        if len(matches) > 0:
            return matches
        else:
            log.info('No note name containing \'%s\' found', search)
            sys.exit(1)

    def new_note(self, filename=None, timestamp=False):  # FIXME refactor more
        '''
        Creates a new note, opens editor with template loaded, and saves to
        snotebook folder upon exit if any changes have been made
        '''
        if filename:
            title = filename.pop()
        else:
            title = self.default_title

        notepath = '{date}-{title}.{ext}'.format(date=self.date(),
                                                 title='-'.join(title.split()),
                                                 ext=self.ext)
        full_notepath = os.path.join(self.location, notepath)

        initial_content = Snotebook.TEMPLATE_TITLE.sub(title, self.template)

        new_content = self.call_writer(initial_content.encode('utf-8'), timestamp)

        if initial_content != new_content:
            log.info('Saving note')
            Snotebook.write_note(full_notepath, new_content)
        else:
            log.info('No change detected, not saving')

    def update_note(self, filename=None, timestamp=False):  # FIXME refactor
        '''
        Loads contents of the last modified note in snotebook folder into
        writer, saves to snotebook folder upon exit of any changes have been
        made
        '''
        full_notepath = self.find_note(filename)

        initial_content = Snotebook.get_note(full_notepath)

        new_content = self.call_writer(initial_content, timestamp)

        if initial_content != new_content:
            log.info('Saving note')
            Snotebook.write_note(full_notepath, new_content)
        else:
            log.info('No change detected, not saving')
