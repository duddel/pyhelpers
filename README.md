# pyhelpers

**Free-floating Python helper scripts, intended for personal usage. No packaging or whatsoever.**

## Usage

- Install requirements via `pip install -r requirements.txt`
- Set `src/` directory to `PYTHONPATH` environment variable
- Call script like so: `python -m <script_name>`

## filedate.py

```
> python -m filedate --help

usage: filedate.py [-h] [--noexif] [--dry] target_dir file_pattern

Renames files by prepending YYYY-MM-DD-hhmmss_ NO MATTER WHAT,
using different criteria, such as parsing date/time from the
original filename, reading exif data or using the file modification date.

positional arguments:
  target_dir    target directory. use '.' for in-place rename. NOT IMPLEMENTED
  file_pattern  file pattern. base is cwd. use '**/*' for all files recursive

options:
  -h, --help    show this help message and exit
  --noexif      do not use exif data at all
  --dry         perform a dry-run only
```

## treesum

```
> python -m treesum --help

usage: treesum.py [-h] [-left LEFT] [-right RIGHT] command

Tool for hash based, recursive, directory comparison.
Answers the question: which files in LEFT directory are (based on hash) also present in RIGHT directory,
even if moved or renamed?
  list: Creates a treesum list file containing all hashes of all files in cwd, recursively
  compare: use -left and -right args to compare 2 list files

positional arguments:
  command       Command to execute: [list, compare]

options:
  -h, --help    show this help message and exit
  -left LEFT    Left side for comparison [compare]. If directory, latest list file is used. Defaults to cwd.
  -right RIGHT  Right side for comparison [compare]. If directory, latest list file is used.
```

## videothumb

```
> python -m videothumb --help
usage: videothumb.py [-h]

Generates video preview images for all video files, recursively in cwd
see: https://github.com/hhtznr/pyvideothumbnailer

options:
  -h, --help  show this help message and exit
```

## License

The source code in this repository is licensed under the [MIT license](LICENSE.txt).
