#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Unit tests for library and class function'''

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
            '2016-04-22-first-post',
            '2016-04-22-second-note',
            '2016-04-23-third-entry',
            '2016-05-02-another-note',
            '2016-07-15-Blockbuster-doesnt-exist-anymore-though',
            '2016-07-15-I-have-to-return-some-video-tapes',
            '2016-08-01-So-how-can-you-return-video-tapes'
        ]

        actual = [entry.name for entry in snotebook._list_notes()]

        assert actual == expected

    def test_list_notes_reverse_name(self, snotebook):
        expected = [
            '2016-08-01-So-how-can-you-return-video-tapes',
            '2016-07-15-I-have-to-return-some-video-tapes',
            '2016-07-15-Blockbuster-doesnt-exist-anymore-though',
            '2016-05-02-another-note',
            '2016-04-23-third-entry',
            '2016-04-22-second-note',
            '2016-04-22-first-post'
        ]

        actual = [entry.name for entry in snotebook._list_notes(reverse=True)]

        assert actual == expected

    def test_list_notes_last(self, snotebook):
        expected = [
            '2016-04-22-first-post',
            '2016-04-22-second-note',
            '2016-04-23-third-entry',
            '2016-05-02-another-note',
            '2016-07-15-Blockbuster-doesnt-exist-anymore-though',
            '2016-07-15-I-have-to-return-some-video-tapes',
            '2016-08-01-So-how-can-you-return-video-tapes'
        ]

        actual = [entry.name for entry in snotebook._list_notes('last')]

        assert actual == expected

    def test_list_notes_last_reverse(self, snotebook):
        expected = [
            '2016-08-01-So-how-can-you-return-video-tapes',
            '2016-07-15-I-have-to-return-some-video-tapes',
            '2016-07-15-Blockbuster-doesnt-exist-anymore-though',
            '2016-05-02-another-note',
            '2016-04-23-third-entry',
            '2016-04-22-second-note',
            '2016-04-22-first-post'
        ]

        actual = [entry.name for entry in snotebook._list_notes('last', True)]

        assert actual == expected

    def test_last_note(self, snotebook):
        head, tail = os.path.split(snotebook._last_note())
        assert tail == '2016-08-01-So-how-can-you-return-video-tapes'

    def test_search_one(self, snotebook):
        expected = [
            '2016-04-22-second-note',
            '2016-05-02-another-note'
        ]

        actual = [entry.name for entry in snotebook._search_notes('note')]

        assert actual == expected

    def test_search_two(self, snotebook):
        expected = [
            '2016-07-15-I-have-to-return-some-video-tapes',
            '2016-08-01-So-how-can-you-return-video-tapes'
        ]

        actual = [entry.name for entry in snotebook._search_notes('video')]

        assert actual == expected

    def test_search_hyphenated(self, snotebook):
        with_hyphen = [entry.name for entry in snotebook._search_notes('video-tapes')]
        without_hyphen = [entry.name for entry in snotebook._search_notes('video tapes')]
        mixed_case = [entry.name for entry in snotebook._search_notes('Video Tapes')]
        mixed_case_hyphen = [entry.name for entry in snotebook._search_notes('Video-tapes')]

        assert with_hyphen == without_hyphen
        assert mixed_case == mixed_case_hyphen
        assert with_hyphen == mixed_case
