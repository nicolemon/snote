#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import (lib, exceptions)
from .snotebook import (EditSnoteParser, Snotebook)
import argparse


VERSION = '0.1.0'


def main():
    edit_args = EditSnoteParser()
    parser = argparse.ArgumentParser(parents=[edit_args])
    parser.add_argument('notebook', help='access notebook')
    subparsers = parser.add_subparsers(title='actions',
                                       metavar='{new|update|list}',
                                       dest='note_action',
                                       help='notebook action, defaults to update')
    parser.set_defaults(note_action='update')
    parser_update = subparsers.add_parser('update', parents=[edit_args], help='edit note; default action')
    parser_list = subparsers.add_parser('list', help='list notes in notebook')
    parser_list.add_argument(
        '-n',
        '--number',
        type=int,
        default=0,
        help='limit number of notes to list; 0 for all'
    )
    parser_new = subparsers.add_parser('new', parents=[edit_args], help='create new note')

    args = parser.parse_args()
    sb = Snotebook.get_snotebook(args.notebook)

    if args.note_action == 'update':
        sb.update_note(filename=args.filename, timestamp=args.timestamp)
    elif args.note_action == 'new':
        sb.new_note(filename=args.filename, timestamp=args.timestamp)
    elif args.note_action == 'list':
        sb.list_notes(args.number)
