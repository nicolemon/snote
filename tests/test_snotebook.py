#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for library function"""

import os
import pytest
import snote
from snote.snotebook import Snotebook
from snote.exceptions import (ConfigError, UnknownNotebookError,
                              InvalidNotebookPathError)


@pytest.fixture
def file_config():
    return snote._read_configuration()


@pytest.fixture(params=['nb1', 'nb2', 'nb3'])
def snotebook(request):
    return snote._get_snotebook(request.param)


def test_instance(snotebook):
    assert isinstance(snotebook, Snotebook)


def test_bad_notebook():
    with pytest.raises(UnknownNotebookError):
        snote._get_snotebook('dne')


def test_bad_notebook_path():
    with pytest.raises(InvalidNotebookPathError):
        snote._get_snotebook('badpath')


def test_snotebook_properties(file_config, snotebook):
    name = snotebook.name
    assert snotebook.name in file_config.sections()
    assert snotebook.location == file_config.get(name, 'path')
    assert snotebook.editor == file_config.get(name, 'editor')
    assert snotebook.ext == file_config.get(name, 'ext')
