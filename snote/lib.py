#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import argparse
import copy
import configparser
from .snotebook import Snotebook
from .exceptions import (ConfigError, UnknownNotebookError, InvalidNotebookPathError)

log = logging.getLogger("snote library")
log.addHandler(logging.StreamHandler(sys.stdout))

DEFAULTS = {
    'editor': 'vim',
    'ext': 'md',
    'datefmt': '%Y-%m-%d',
    'timefmt': '%H:%M:%S',
    'timestamp': '\n{time}',
    'template': None,
    'default_title': 'untitled'
}

debug = os.getenv('SNOTE_DEBUG', False)
if debug:
    log.setLevel(logging.DEBUG)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-t', '--timestamp', action='store_true', help='add a'
                        ' timestamp to the editor')
    parser.add_argument('-f', '--filename', nargs=1, default=None)
    parser.add_argument('notebook', help='access notebook')
    parser.add_argument('subcommand', nargs='?', choices=['new', 'update'],
                        default='update', help='defaults to update')
    args = parser.parse_args()

    log.debug('parse_commands: %s', args)

    try:
        sb = _get_snotebook(args.notebook)
    except UnknownNotebookError as e:
        log.error(e)
        sys.exit(1)
    except InvalidNotebookPathError as e:
        log.error(e)
        sys.exit(1)

    if args.subcommand == 'update':
        sb.update_note(args.filename, args.timestamp)

    if args.subcommand == 'new':
        sb.new_note(args.filename, args.timestamp)


def _get_configuration_filepath(snoteenv='SNOTE'):
    config_file = os.getenv(snoteenv, None)
    if config_file and os.path.exists(config_file):
        log.info('Configuration file path is configured and exists')
        return config_file
    else:
        raise ConfigError('Configuration file %s path not configured' %
                          config_file)


def _read_configuration():
    try:
        config_file = _get_configuration_filepath()
    except ConfigError as e:
        log.error(e)
        sys.exit(1)

    config = configparser.ConfigParser(defaults=DEFAULTS,
                                       default_section='global',
                                       interpolation=None)
    with open(config_file, 'r') as cfg:
        cfg_txt = os.path.expandvars(cfg.read())
    config.read_string(cfg_txt)
    return config


def _get_snotebook(notebook):
    """Returns Snotebook object if given the name of a configured Snotebook."""

    config = _read_configuration()

    if config.has_section(notebook):
        log.debug('Notebook exists, great success')
    else:
        raise UnknownNotebookError(notebook)

    if os.path.exists(config.get(notebook, 'path')):
        log.debug('Configured path exists, great success')
    else:
        raise InvalidNotebookPathError(config.get(notebook, 'path'))

    snotebook_cfg = {
        'name': notebook,
        'location': config.get(notebook, 'path'),
        'editor': config.get(notebook, 'editor'),
        'ext': config.get(notebook, 'ext'),
        'datefmt': config.get(notebook, 'datefmt'),
        'timefmt': config.get(notebook, 'timefmt'),
        'timestamp': config.get(notebook, 'timestamp'),
        'template': config.get(notebook, 'template'),
        'default_title': config.get(notebook, 'default_title')
    }

    return Snotebook(**snotebook_cfg)
