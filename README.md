# snote

[![Build Status](https://travis-ci.org/nicolemon/snote.svg?branch=master)](https://travis-ci.org/nicolemon/snote)

Rudimentary CLI to write and organize text.

I've got a ways to go in terms of features and documentation. Pull requests are
neat.

## Install

Downloading the repo and firing off `python setup.py install` does the trick.

## Configuration

Reads configuration from whichever file to which environment variable `SNOTE`
points.

Each notebook requires a valid path, where notes will be saved. Global settings
apply to all notebooks, and may be overwritten at a notebook level.

    [global]
    editor=vim
    ext=md
    datefmt=%Y-%m-%d
    timefmt=%H:%M:%S
    timestamp=[{time}]
    template=/path/to/template/file
    default_title='no title'

    [my-notebook]
    path=/path/to/directory

    [another]
    path=/path/to/another/directory
    editor=nano
    ext=rst

## Usage

    usage: snote [-h] [-t] [-f FILENAME] notebook {new|update|list} ...

    positional arguments:
      notebook              access notebook

    optional arguments:
      -h, --help            show this help message and exit
      -t, --timestamp       add a timestamp to the note
      -f FILENAME, --filename FILENAME
                            name a new note, or search for a note to update

    actions:
      {new|update|list}     notebook action, defaults to update
        update              edit note; default action
        list                list notes in notebook
        new                 create new note

## Motivaton

I wrote this for myself as a way to catalog my stream of consciousness, and an
exercise in packaging.
