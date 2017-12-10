#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import (lib, exceptions)
from .snotebook import (SnoteParser, Snotebook)


VERSION = '0.0.2a'


def main():
    parser = SnoteParser()
    args = parser.parse_args()

    try:
        sb = Snotebook.get_snotebook(args.notebook)

        if args.subcommand == 'update':
            sb.update_note(args.filename, args.timestamp)

        if args.subcommand == 'new':
            sb.new_note(args.filename, args.timestamp)

    except exceptions.UnknownNotebookError as e:
        log.error(e)
    except exceptions.InvalidNotebookPathError as e:
        log.error(e)
