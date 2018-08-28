#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import (lib, exceptions)
from .snotebook import (EditSnoteParser, Snotebook)
import argparse


VERSION = '0.2.2'


def main():
    edit_args = EditSnoteParser()
    parser = argparse.ArgumentParser(parents=[edit_args])
    parser.add_argument('notebook', help='name of notebook to access')

    subparsers = parser.add_subparsers(title='actions',
                                       dest='note_action',
                                       help='notebook action, defaults to update')

    parser_update = subparsers.add_parser(
        'update',
        aliases=['u'],
        parents=[edit_args],
        help='edit note; default action'
    )

    parser_new = subparsers.add_parser(
        'new',
        aliases=['n'],
        parents=[edit_args],
        help='create new note'
    )

    parser_list = subparsers.add_parser(
        'list',
        aliases=['l', 'ls'],
        help='list note titles in notebook'
    )
    parser_list.add_argument(
        '-n',
        '--number',
        type=int,
        default=0,
        help='limit number of notes to list; 0 for all'
    )

    parser_search = subparsers.add_parser(
        'search',
        aliases=['s'],
        help='list note titles containing the search term'
    )
    parser_search.add_argument(
        'search_term',
        type=str,
        help='search term'
    )

    parser.set_defaults(note_action='update')

    args = parser.parse_args()
    sb = Snotebook.get_snotebook(args.notebook)

    if args.note_action in ['update', 'u']:
        sb.update_note(filename=args.filename, timestamp=args.timestamp)
    elif args.note_action in ['new', 'n']:
        sb.new_note(filename=args.filename, timestamp=args.timestamp)
    elif args.note_action in ['list', 'l', 'ls']:
        sb.list_notes(args.number)
    elif args.note_action in ['search', 's']:
        sb.search_notes(args.search_term)
