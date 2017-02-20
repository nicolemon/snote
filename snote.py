#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import datetime
import libsnote
import tempfile
import subprocess
from subprocess import call
from libsnote import log

def main():
    args = libsnote.parse_commands()
    config = libsnote.read_config()

    try:
        libsnote.validate_notebook(args.notebook)
    except libsnote.UnknownNotebookError as e:
        log.error('%s: I do not know that notebook', e)
        sys.exit(1)
    except libsnote.InvalidNotebookPathError:
        log.error('%s: Way to configure paths, slick', e)
        sys.exit(1)

    notebook = args.notebook
    subcommand = args.subcommand
    timestamp = args.timestamp

    notebook_root = config[notebook]['path']
    post_folder = os.path.join(notebook_root, '_posts')

    if subcommand == 'update':
        libsnote.update_note(notebook, args.filename, args.timestamp)

    if subcommand == 'new':
        if args.filename is None:
            title = 'Untitled'
        else:
            title = args.filename[0]
        log.debug('Creating a new note in %s', notebook)

        date = datetime.date.today().strftime(libsnote.DATE_FMT)
        title_slug = '-'.join(title.split())
        filename = '-'.join([date, title_slug])
        full_filename = '.'.join([filename, 'md'])
        full_note_path = os.path.join(post_folder, full_filename)

        editor = libsnote.text_editor(notebook)
        initial_content = '---\ntitle: {0}\n\n---\n'.format(title)
        with tempfile.NamedTemporaryFile(suffix='.md') as tf:
            tf.write(initial_content.encode('utf-8'))
            if timestamp:
                tf.write(libsnote.create_timestamp())
            tf.flush()
            call([editor, tf.name])
            tf.seek(0)
            new_content = tf.read()
        libsnote.write_note_content(full_note_path, new_content)


        # TODO
        log.debug('working filename: %s', full_filename)
        log.debug('working filepath: %s', full_note_path)


if __name__ == '__main__':
    libsnote.print_header()
    main()
