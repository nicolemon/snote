#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Unit tests for library and class function"""

import os
import pytest
import snote
from snote.snotebook import Snotebook
from snote.exceptions import (ConfigError, UnknownNotebookError,
                              InvalidNotebookPathError)


@pytest.fixture(params=['nb1', 'nb2', 'nb3'])
def snotebook(request):
    return Snotebook.get_snotebook(request.param)


class TestTrueExceptions:

    def test_bad_notebook(self):
        with pytest.raises(UnknownNotebookError):
            Snotebook.get_snotebook('dne')

    def test_bad_notebook_path(self):
        with pytest.raises(InvalidNotebookPathError):
            Snotebook.get_snotebook('badpath')


class TestSnotebookConfig:

    @pytest.fixture
    def file_config(self):
        return snote.lib.get_config()

    def test_instance(self, snotebook):
        assert isinstance(snotebook, Snotebook)

    def test_snotebook_properties(self, file_config, snotebook):
        name = snotebook.name
        assert snotebook.name in file_config.sections()
        assert snotebook.location == file_config.get(name, 'path')
        assert snotebook.editor == file_config.get(name, 'editor')
        assert snotebook.ext == file_config.get(name, 'ext')
        assert snotebook.default_title == file_config.get(name, 'default_title')
        assert snotebook._timestamp == file_config.get(name, 'timestamp')


class TestNoteRetrieval:

    def test_list_notes_name(self, snotebook):
        expected = [
            'another-note',
            'Blockbuster-doesnt-exist-anymore-though',
            'first-post',
            'I-have-to-return-some-video-tapes',
            'second-note',
            'So-how-can-you-return-video-tapes',
            'third-entry'
        ]

        actual = [entry.name for entry in snotebook._list_notes()]

        assert actual == expected

    def test_list_notes_reverse_name(self, snotebook):
        expected = [
            'third-entry',
            'So-how-can-you-return-video-tapes',
            'second-note',
            'I-have-to-return-some-video-tapes',
            'first-post',
            'Blockbuster-doesnt-exist-anymore-though',
            'another-note'
        ]

        actual = [entry.name for entry in snotebook._list_notes(reverse=True)]

        assert actual == expected

    def test_list_notes_last(self, snotebook):
        expected = [
            'first-post',
            'second-note',
            'third-entry',
            'another-note',
            'I-have-to-return-some-video-tapes',
            'Blockbuster-doesnt-exist-anymore-though',
            'So-how-can-you-return-video-tapes'
        ]

        actual = [entry.name for entry in snotebook._list_notes('last')]

        assert actual == expected

    def test_list_notes_last(self, snotebook):
        expected = [
            'So-how-can-you-return-video-tapes',
            'Blockbuster-doesnt-exist-anymore-though',
            'I-have-to-return-some-video-tapes',
            'another-note',
            'third-entry',
            'second-note',
            'first-post'
        ]

        actual = [entry.name for entry in snotebook._list_notes('last', True)]

        assert actual == expected

    def test_last_note(self, snotebook):
        head, tail = os.path.split(snotebook._last_note())
        assert tail == 'So-how-can-you-return-video-tapes'
