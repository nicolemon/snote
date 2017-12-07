# snote

Rudimentary CLI to write and organize text.

## Requirements

- ~=Python 3.5

## Configuration

### Global

- `global` setting support
    - `editor` default editor for writing notes
    - `ext` default extension for any notes
    - `template` (optional) default template for new notes

All global settings can be overwritten at a notebook level.

### Notebooks

- `[<notebok name>]`
    - `path` absolute path to where the notes are saved

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

I wrote this for myself as a way to catalog my stream of consciousness.
