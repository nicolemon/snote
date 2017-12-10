# snote

[![Build Status](https://travis-ci.org/nicolemon/snote.svg?branch=master)](https://travis-ci.org/nicolemon/snote)

Rudimentary CLI to write and organize text.

## Install

`pip install snotebooks` will install whatever is on master

Downloading the repo and firing off `python setup.py install` works, too.

## Configuration

Reads configuration from whichever file to which environment variable `SNOTE`
points.

Each notebook requires a valid path, where notes will be saved. Global settings
apply to all notebooks, and are overwritten at a notebook level.

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

    usage: snote [-h] [-t] [-f FILENAME] notebook [{new,update}]

    positional arguments:
      notebook              access notebook
      {new,update}          defaults to update

    optional arguments:
      -h, --help            show this help message and exit
      -t, --timestamp       add a timestamp to the editor
      -f FILENAME, --filename FILENAME

## Motivaton

I wrote this for myself as a way to catalog my stream of consciousness, and an
exercise in packaging.
