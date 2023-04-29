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

## listpar.py
```
> python -m listpar
```

## License

The source code in this repository is licensed under the [MIT license](LICENSE.txt).
