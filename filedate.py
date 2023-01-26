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
import os
import glob
import time
import re
import exif
import argparse


def rename_file_inplace(src, new_name, dry_run=False, verbose=True):
    if verbose:
        print(f'    -> {src}')
        print(f'    -> {os.path.join(src.parent, new_name)}')
    if not dry_run:
        os.rename(src, os.path.join(src.parent, new_name))


def main(args):
    # matches filenames already starting with YYYY-MM-DD-hhmmss
    re_filedate = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{6}')

    # matches typical names of messenger media files (WA)
    re_date0 = re.compile(r'^(IMG|VID|AUD|PTT)-(\d{8})-WA')

    # matches filenames containing 10 isolated digits
    # might indicate unix timestamp after 2001-09-09-014640
    # todo: NOT IMPLEMENTED
    re_date1 = re.compile(r'(\D|^)(\d{10})\D')

    # matches filenames containing date, like this:
    # 2017-01-01_15-03-27_image.jpg
    # todo: NOT IMPLEMENTED
    re_date2 = re.compile(
        r'(\D|^)(\d{4})-(\d{2})-(\d{2})(_|-)(\d{2})-(\d{2})-(\d{2})\D')

    # matches filenames containing date, like these:
    # IMG_20210101_140216.jpg
    # IMG_20210101_173753227.jpg
    # Screenshot_20201001-220605.png
    re_date3 = re.compile(r'(\D|^)(\d{8})(_|-)(\d{9}|\d{6})\D')

    # matches files that are skipped
    re_skiplist = re.compile(r'^(Thumbs\.db)$')

    # counters for report
    num_glob_items = 0
    num_skipped_items = 0
    for f in glob.glob(os.path.join(os.getcwd(), args.file_pattern), recursive=True):
        num_glob_items += 1

        print(f'{f}')

        fp = pathlib.Path(f)

        # skip directories
        if os.path.isdir(fp):
            print('    -> SKIP DIRECTORY')
            continue

        # skip filenames in skiplist
        # skip files that already start with YYYY-MM-DD-hhmmss
        if re.search(re_skiplist, fp.name) != None or \
           re.search(re_filedate, fp.stem) != None:
            num_skipped_items += 1
            print('    -> SKIP')
            continue

        # date from EXIF data
        if fp.suffix in ['.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi']:
            file_name_new = ''
            with open(fp, 'rb') as img_file:
                try:
                    img = exif.Image(img_file)
                    if img.has_exif and hasattr(img, "datetime_original"):

                        # todo try except
                        # convert format from exif (YYYY:MM:DD hh:mm:ss) to YYYY-MM-DD-hhmmss
                        exif_time_struct = time.strptime(
                            img.datetime_original, '%Y:%m:%d %H:%M:%S')
                        exif_time_str = time.strftime(
                            '%Y-%m-%d-%H%M%S', exif_time_struct)

                        file_name_new = f'{exif_time_str}_{fp.stem}{fp.suffix}'
                        print('    -> USING DATE FROM EXIF DATA')
                except:
                    print('    -> FAILED TO LOAD EXIF DATA')

            if file_name_new != '':
                rename_file_inplace(fp, file_name_new, args.dry)
                continue

        # date from messenger filename
        re_matches = re.search(re_date0, fp.name)
        if re_matches != None:
            time_str = f'{re_matches[2][0:4]}-{re_matches[2][4:6]}-{re_matches[2][6:8]}-000000'
            file_name_new = f'{time_str}_{fp.stem}{fp.suffix}'
            print('    -> USING DATE FROM FILENAME (MESSENGER)')
            rename_file_inplace(fp, file_name_new, args.dry)
            continue

        # date from filename (re_date3)
        re_matches = re.search(re_date3, fp.name)
        if re_matches != None:
            time_str = f'{re_matches[2][0:4]}-{re_matches[2][4:6]}-{re_matches[2][6:8]}-{re_matches[4][0:6]}'
            file_name_new = f'{time_str}_{fp.stem}{fp.suffix}'
            print('    -> USING DATE FROM FILENAME')
            rename_file_inplace(fp, file_name_new, args.dry)
            continue

        # date from last modified date (fallback)
        mtime = os.path.getmtime(fp)
        # file modified struct_time
        mtime_struct = time.gmtime(mtime)
        # file modified time string
        mtime_str = time.strftime('%Y-%m-%d-%H%M%S', mtime_struct)
        file_name_new = f'{mtime_str}_{fp.stem}{fp.suffix}'
        print('    -> USING FILE MODIFIED DATE')
        rename_file_inplace(fp, file_name_new, args.dry)

    # report
    print(f'{num_glob_items} items, {num_skipped_items} skipped, {num_glob_items-num_skipped_items} processed')


if __name__ == "__main__":
    aPars = argparse.ArgumentParser(description="")
    aPars.add_argument("target_dir", type=str,
                       help='target directory. use \'.\' for in-place rename. NOT IMPLEMENTED')
    aPars.add_argument("file_pattern", type=str,
                       help='file pattern. base is cwd. use \'**/*\' for all files recursive')
    aPars.add_argument('--dry', action='store_true',
                       help='perform a dry-run only')
    args = aPars.parse_args()

    main(args)
