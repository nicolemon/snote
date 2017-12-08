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
log.addHandler(logging.StreamHandler(sys.stdout))


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
            tf.seek(0)  # hand tight until subprocess is done!
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

    def find_note(self, filename=None):  # TODO file searching
        '''
        Return path to the most recently modified note in notebook, or the
        note with the specified filename
        '''
        if filename is None:
            last_modified_ts = 0.0
            last_modified = None
            with os.scandir(self.location) as it:
                for entry in it:
                    entry_stat = os.stat(entry).st_mtime
                    if entry_stat > last_modified_ts:
                        last_modified_ts = entry_stat
                        last_modified = entry
            return last_modified.path
        else:
            raise NotImplementedError('Note searching not yet implemented')

    def new_note(self, filename=None, timestamp=False):  # FIXME refactor more
        '''
        Creates a new note, opens editor with template loaded, and saves to
        snotebook folder upon exit if any changes have been made
        '''
        if filename:
            title = filename[0]
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
        try:
            full_notepath = self.find_note(filename)
        except NotImplementedError as e:
            log.error(e)
            sys.exit(1)

        initial_content = Snotebook.get_note(full_notepath)

        new_content = self.call_writer(initial_content, timestamp)

        if initial_content != new_content:
            log.info('Saving note')
            Snotebook.write_note(full_notepath, new_content)
        else:
            log.info('No change detected, not saving')
