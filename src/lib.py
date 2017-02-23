#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import tempfile
import subprocess
import datetime
import os
import logging
import argparse
import configparser
from subprocess import call

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler(sys.stdout))

CONFIG_FILE = os.getenv('SNOTE', None)

debug = os.getenv('SNOTE_DEBUG', False)
if debug:
    log.setLevel(logging.DEBUG)

DATE_FMT = '%Y-%m-%d'
TIME_FMT = '%H:%M:%S'

def print_header():
    print('''
                 _       
                | |      
 ___ _ __   ___ | |_ ___ 
/ __| '_ \ / _ \| __/ _ \\
\__ \ | | | (_) | ||  __/
|___/_| |_|\___/ \__\___|

''')

def read_config():
    if CONFIG_FILE:
        config = configparser.ConfigParser()
        config.read([CONFIG_FILE])
        return config
    else:
        log.error('Config file not set, check documentation for more details.')
        sys.exit(1)

def parse_commands():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--timestamp', action='store_true', help='add a'
                       ' timestamp to the editor')
    parser.add_argument('-f', '--filename', nargs=1, default=None)
    parser.add_argument('notebook', help='access notebook')
    parser.add_argument('subcommand', nargs='?', choices=['new', 'update'],
                        default='update')
    args = parser.parse_args()
    log.debug('parse_commands: %s', args)
    return args

def most_recent(notebook):
    """Returns absolute path to most recently modified note in notebook."""

    config = read_config()
    post_folder = os.path.join(config[notebook]['path'], '_posts')
    last_modified_ts = 0.0
    last_modified = None
    with os.scandir(post_folder) as it:
        for entry in it:
            entry_stat = os.stat(entry).st_mtime
            if entry_stat > last_modified_ts:
                last_modified_ts = entry_stat
                last_modified = entry
    return last_modified.path

def validate_notebook(notebook):
    """Returns True if notebook is configured with a valid path."""
    config = read_config()
    config_nbs = [nb for nb in config.sections() if 'path' in config[nb]]

    if notebook in config_nbs:
        log.debug('Notebook exists, great success')
    else:
        raise UnknownNotebookError(notebook)

    abs_path = config[notebook]['path']

    if os.path.isdir(abs_path):
        log.debug('Notebook path exists, way to go')
    else:
        raise InvalidNotebookPathError(abs_path)

def text_editor(notebook):
    """Returns string representation of editor (vim, nano, emacs)."""
    config = read_config()
    if 'editor' in config[notebook]:
        editor = config[notebook]['editor']
    elif 'editor' in config['global']:
        editor = config['global']['editor']
    else:
        editor = 'vim'

    return editor

def get_note_content(infile):
    note = b''
    with open(infile, 'r+b') as content:
        note = content.read()
    return note

def write_note_content(outfile, note):
    with open(outfile, 'w+b') as content:
        content.write(note)
    log.info('Note saved')

def update_note(notebook, filename=None, timestamp=False):
    if filename is None:
        file = most_recent(notebook)
    else:
        raise NotImplementedError('Note searching not yet implemented')

    editor = text_editor(notebook)
    current_content = get_note_content(file)
    with tempfile.NamedTemporaryFile(suffix='.md') as tf:
        tf.write(current_content)
        if timestamp:
            tf.write(create_timestamp())
        tf.flush()
        call([editor, tf.name])
        tf.seek(0)
        new_content = tf.read()
    if current_content != new_content:
        log.info('Saving note')
        write_note_content(file, new_content)
    else:
        log.info('No change, note note saved or updated')

def new_note(notebook, filename=None, timestamp=False):
    config = read_config()
    if filename is None:
        title = 'Untitled'
    else:
        title = filename[0]
    log.debug('Creating a new note in %s', notebook)

    date = datetime.date.today().strftime(DATE_FMT)
    title_slug = '-'.join(title.split())
    filename = '-'.join([date, title_slug])
    full_filename = '.'.join([filename, 'md'])

    post_folder = os.path.join(config[notebook]['path'], '_posts')
    full_note_path = os.path.join(post_folder, full_filename)

    editor = text_editor(notebook)
    if 'template' in config[notebook]:
        initial_content = get_note_content(config[notebook]['template'])
    elif 'template' in config['global']:
        initial_content = get_note_content(config['global']['template'])
    else:
        initial_content = get_note_content('template.md')

    with tempfile.NamedTemporaryFile(suffix='.md') as tf:
        tf.write(initial_content)
        if timestamp:
            tf.write(lib.create_timestamp())
        tf.flush()
        call([editor, tf.name])
        tf.seek(0)
        new_content = tf.read()
    if initial_content != new_content:
        log.info('Saving note')
        write_note_content(full_note_path, new_content)
    else:
        log.info('No change, note note saved or updated')

def create_timestamp():
    time = datetime.datetime.now().strftime(TIME_FMT)
    timestamp = "\n[{0}]\n".format(time)
    return timestamp.encode('utf-8')


class NotebookError(BaseException):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownNotebookError(NotebookError):
    pass


class InvalidNotebookPathError(NotebookError):
    pass


if __name__ == "__main__":
    pass
