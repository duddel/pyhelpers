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
import datetime
import re
import exif
import argparse


def rename_file_inplace(src, new_name, dry_run=False, verbose=True):
    if verbose:
        print(f'    -> {src}')
        print(f'    -> {os.path.join(src.parent, new_name)}')
    if not dry_run:
        try:
            os.rename(src, os.path.join(src.parent, new_name))
        except:
            print('RENAME FAILED')


def main(args):
    # matches filenames already starting with YYYY-MM-DD-hhmmss
    re_filedate = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{6}')

    # matches typical names of messenger media files (WA)
    re_date1 = re.compile(r'^(IMG|VID|AUD|PTT)-(\d{8})-WA')

    # matches filenames containing date, like these:
    #            2017-01-01_15-03-27_image.jpg
    # Screenshot_2015-09-23-21-46-27.png
    #            2012-05-01_15-03-27_652.jpg
    #       C360_2012-05-01 15-03-27.jpg
    #       2010-07-30 19.55.42_e0.jpg
    re_date2 = re.compile(
        r'(\D|^)(\d{4}-\d{2}-\d{2})(_|-|\s)(\d{2})(-|\.)(\d{2})(-|\.)(\d{2})\D')

    # matches filenames containing date, like these:
    # IMG_20210101_140216.jpg
    # IMG_20210101_173753227.jpg
    # Screenshot_20201001-220605.png
    re_date3 = re.compile(r'(\D|^)(\d{8})(_|-)(\d{9}|\d{6})\D')

    # matches filenames containing date, like these:
    # 02-10-07_1659.jpg
    # 18-07-07_0953.JPG
    re_date4 = re.compile(r'^(\d{2})-(\d{2})-(\d{2})_(\d{4})\.(jpg|JPG)$')

    # 10 or 13 isolated digits might indicate unix timestamp
    # after 2001-09-09, in seconds (10 digits) or milliseconds (13 digits)
    re_date5 = re.compile(r'(\D|^)(\d{10}|\d{13})(\D|$)')

    # 14 or 17 isolated digits might indicate adjacent date information
    # like 20010501221015 (seconds) or 20010501221015123 (milliseconds)
    # the order is asumed to be like in the examples
    re_date6 = re.compile(r'(\D|^)(\d{14}|\d{17})(\D|$)')

    # matches files that are skipped
    re_skiplist = re.compile(r'^(Thumbs\.db)$')

    # counters for report
    num_glob_items = 0
    num_skipped_items = 0
    num_skipped_dirs = 0
    num_exif_used = 0
    num_modified_date_used = 0
    for f in glob.glob(os.path.join(os.getcwd(), args.file_pattern), recursive=True):
        print(f'{f}')

        fp = pathlib.Path(f)

        # skip directories
        if os.path.isdir(fp):
            num_skipped_dirs += 1
            print('    -> SKIP DIRECTORY')
            continue

        num_glob_items += 1

        # skip filenames in skiplist
        # skip files that already start with YYYY-MM-DD-hhmmss
        if re.search(re_skiplist, fp.name) != None or \
           re.search(re_filedate, fp.stem) != None:
            num_skipped_items += 1
            print('    -> SKIP')
            continue

        file_name_new = None

        # date from EXIF data
        if (not file_name_new) and \
            (not args.noexif) and \
                fp.suffix.lower() in ['.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi']:
            with open(fp, 'rb') as img_file:
                try:
                    img = exif.Image(img_file)
                    if img.has_exif and hasattr(img, "datetime_original"):
                        num_exif_used += 1
                        # convert format from exif (YYYY:MM:DD hh:mm:ss) to YYYY-MM-DD-hhmmss
                        exif_time_struct = time.strptime(
                            img.datetime_original, '%Y:%m:%d %H:%M:%S')
                        exif_time_str = time.strftime(
                            '%Y-%m-%d-%H%M%S', exif_time_struct)

                        file_name_new = f'{exif_time_str}_{fp.name}'
                        print('    -> USING DATE FROM EXIF DATA')
                except:
                    print('    -> FAILED TO LOAD EXIF DATA')

        # date from messenger filename
        if not file_name_new:
            re_matches = re.search(re_date1, fp.name)
            if re_matches != None:
                time_str = f'{re_matches[2][0:4]}-{re_matches[2][4:6]}-{re_matches[2][6:8]}-000000'
                file_name_new = f'{time_str}_{fp.name}'
                print('    -> USING DATE FROM FILENAME (MESSENGER)')

        # date from filename (re_date2)
        if not file_name_new:
            re_matches = re.search(re_date2, fp.name)
            if re_matches != None:
                time_str = f'{re_matches[2]}-{re_matches[4]}{re_matches[6]}{re_matches[8]}'
                file_name_new = f'{time_str}_{fp.name}'
                print('    -> USING DATE FROM FILENAME (2)')

        # date from filename (re_date3)
        if not file_name_new:
            re_matches = re.search(re_date3, fp.name)
            if re_matches != None:
                time_str = f'{re_matches[2][0:4]}-{re_matches[2][4:6]}-{re_matches[2][6:8]}-{re_matches[4][0:6]}'
                file_name_new = f'{time_str}_{fp.name}'
                print('    -> USING DATE FROM FILENAME (3)')

        # date from filename (re_date4)
        if not file_name_new:
            re_matches = re.search(re_date4, fp.name)
            if re_matches != None:
                # 2-digit year is prefixed with 20 (07 -> 2007)
                time_str = f'20{re_matches[3]}-{re_matches[2]}-{re_matches[1]}-{re_matches[4]}00'
                file_name_new = f'{time_str}_{fp.name}'
                print('    -> USING DATE FROM FILENAME (4)')

        # date from filename (re_date5)
        if not file_name_new:
            re_matches = re.search(re_date5, fp.name)
            if re_matches != None:
                # convert assumed timestamp to UTC time (we don't know it better)
                dt = datetime.datetime.utcfromtimestamp(
                    int(re_matches[2][:10]))
                time_str = dt.strftime("%Y-%m-%d-%H%M%S")
                file_name_new = f'{time_str}_{fp.name}'
                print('    -> USING DATE FROM FILENAME (5)')

        # date from filename (re_date6)
        if not file_name_new:
            re_matches = re.search(re_date6, fp.name)
            if re_matches != None:
                time_str = f'{re_matches[2][0:4]}-{re_matches[2][4:6]}-{re_matches[2][6:8]}-{re_matches[2][8:14]}'
                file_name_new = f'{time_str}_{fp.name}'
                print('    -> USING DATE FROM FILENAME (6)')

        # date from last modified date (fallback)
        if not file_name_new:
            num_modified_date_used += 1
            mtime = os.path.getmtime(fp)
            # file modified struct_time
            mtime_struct = time.gmtime(mtime)
            # file modified time string
            mtime_str = time.strftime('%Y-%m-%d-%H%M%S', mtime_struct)
            file_name_new = f'{mtime_str}_{fp.name}'
            print('    -> USING FILE MODIFIED DATE')

        # perform the actual rename
        if file_name_new:
            rename_file_inplace(fp, file_name_new, args.dry)

    # report
    print(f'{num_glob_items} items, {num_skipped_items} skipped, {num_glob_items-num_skipped_items} processed ({num_skipped_dirs} directories)')
    print(f'EXIF date used:     {num_exif_used}')
    print(f'modified date used: {num_modified_date_used}')
    print(
        f'other date used:    {num_glob_items-num_skipped_items-num_exif_used-num_modified_date_used}')


if __name__ == "__main__":
    aPars = argparse.ArgumentParser(description="Renames files by prepending YYYY-MM-DD-hhmmss_ NO MATTER WHAT,\n\
using different criteria, such as parsing date/time from the\n\
original filename, reading exif data or using the file modification date.",
                                    formatter_class=argparse.RawTextHelpFormatter)
    aPars.add_argument("target_dir", type=str,
                       help='target directory. use \'.\' for in-place rename. NOT IMPLEMENTED')
    aPars.add_argument("file_pattern", type=str,
                       help='file pattern. base is cwd. use \'**/*\' for all files recursive')
    aPars.add_argument('--noexif', action='store_true',
                       help='do not use exif data at all')
    aPars.add_argument('--dry', action='store_true',
                       help='perform a dry-run only')
    args = aPars.parse_args()

    main(args)
