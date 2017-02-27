# snote

## Requirements

- Python 3.5+ (Sorry, I know)

## Installation

1. Clone repository
2. Add `snote` executable to the bin via symlinking or however you want
3. Environment variable `SNOTE` is the absolute path to your configuration file

## Configuration

### Global

- `global` setting support
    - `editor` default editor for writing notes
    - `ext` default extension for any notes
    - `template` (optional) default template for new notes

Global settings can be overwritten at a notebook level.

### Notebooks

- `[<notebok name>]`
    - `path` absolute path to where the notes are saved

## Usage

                     _
                    | |
     ___ _ __   ___ | |_ ___
    / __| '_ \ / _ \| __/ _ \
    \__ \ | | | (_) | ||  __/
    |___/_| |_|\___/ \__\___|


    usage: snote [-h] [-t] [-f FILENAME] notebook [{new,update}]

    positional arguments:
      notebook              access notebook
      {new,update}          defaults to update

    optional arguments:
      -h, --help            show this help message and exit
      -t, --timestamp       add a timestamp to the editor
      -f FILENAME, --filename FILENAME

