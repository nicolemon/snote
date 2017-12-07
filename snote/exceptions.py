#!/usr/bin/env python
# -*- coding: utf-8 -*-


class ConfigError(BaseException):

    def __init__(self, value=None):
        if value:
            self.value = value
        else:
            self.value = "Configuration file not found"

    def __str__(self):
        return repr(self.value)


class NotebookError(BaseException):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnknownNotebookError(NotebookError):

    def __init__(self, value):
        self.value = 'Notebook \'{}\' unknown'.format(value)


class InvalidNotebookPathError(NotebookError):

    def __init__(self, value):
        self.value = 'Notebook path \'{}\' unknown'.format(value)
