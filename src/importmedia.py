'''
Copyright (c) 2023 Alexander Scholz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import pathlib
import glob
import os
import argparse
import filedate


def main(args):
    target_dir = os.getcwd()

    source_files_search_path = os.path.join(args.source_dir, args.file_pattern)

    source_files = glob.glob(source_files_search_path, recursive=True)

    for f in source_files:
        fp = pathlib.Path(f)
        print(f"{fp}")

        # check if file with new_name exists under target_dir
        # optionally compare size or hash
        # do not copy if it exists already
        # also, never overwrite (only if requested by user arg)

        # add args: force_copy/force_overwrite, subdir_y/ym/ymd

        new_name = filedate.get_new_filename(fp)[0]
        print(f"    -> {os.path.join(target_dir, new_name)}")


if __name__ == "__main__":
    aPars = argparse.ArgumentParser(
        description="Imports media", formatter_class=argparse.RawTextHelpFormatter)
    aPars.add_argument("source_dir", type=pathlib.Path,
                       help='source directory')
    aPars.add_argument("file_pattern", type=str,
                       help='file pattern. use \'**/*\' for all files recursive')
    aPars.add_argument('--dry', action='store_true',
                       help='perform a dry-run only')
    args = aPars.parse_args()

    main(args)
