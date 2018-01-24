#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
import logging
import configparser
from .exceptions import ConfigError

log = logging.getLogger(__name__)

TEMPLATE_TITLE = re.compile('%TITLE%')
DEFAULTS = {
    'editor': 'vim',
    'ext': 'md',
    'datefmt': '%Y-%m-%d',
    'timefmt': '%H:%M:%S',
    'timestamp': '\n{time}',
    'template': None,
    'default_title': 'untitled'
}


def get_file_content(filepath):  # returns bytes
    '''
    Load and return content of file object at filepath

    :param filepath: valid filepath as str
    :returns: as bytes object
    '''
    note = b''
    with open(filepath, 'r+b') as content:
        note = content.read()
    return note


def write_note(filepath, note):  # write bytes
    '''
    Writes to filepath with the content of note

    :param filepath: valid filepath as str
    :param note: str representation of content to write
    '''
    with open(filepath, 'w+b') as content:
        content.write(note)
    log.info('Note saved')


def get_config(envvar='SNOTE'):

    config_path = os.getenv(envvar, None)

    if config_path and os.path.exists(config_path):
        log.debug('Configuration file path is configured and exists')
    else:
        raise FileNotFoundError(config_path)

    config = configparser.ConfigParser(defaults=DEFAULTS,
                                       default_section='global',
                                       interpolation=None,
                                       allow_no_value=True)

    with open(config_path, 'r') as cfg:
        cfg_txt = os.path.expandvars(cfg.read())

    config.read_string(cfg_txt)

    return config
