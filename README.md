# snote

[![Build Status](https://travis-ci.org/nicolemon/snote.svg?branch=master)](https://travis-ci.org/nicolemon/snote)

Rudimentary CLI to write and organize text.

## Install

`pip install snotebooks` will install whatever is on master

Downloading the repo and firing off `python setup.py install` works, too.

## Configuration

Reads configuration from whichever file to which environment variable `SNOTE`
points.

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
