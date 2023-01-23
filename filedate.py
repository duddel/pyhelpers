import pathlib
import os
import glob
import time
import re
import exif


def rename_file_inplace(src, new_name, verbose=True):
    if verbose:
        print(f'    -> {src}')
        print(f'    -> {os.path.join(src.parent, new_name)}')
    os.rename(src, os.path.join(src.parent, new_name))


def main():
    file_pattern = '**/*'

    # matches file names starting with YYYY-MM-DD-hhmmss
    re_filedate = re.compile(r'^\d{4}-\d{2}-\d{2}-\d{6}.*$')

    # matching typical messenger media files. images, videos, audio, push-to-talk
    re_wa_filename = re.compile(r'^(IMG|VID|AUD|PTT)-(\d{8})-WA\d*.*$')

    for f in glob.glob(os.path.join(os.getcwd(), file_pattern), recursive=True):
        fp = pathlib.Path(f)

        print(f'{f}')

        if os.path.isdir(fp):
            print('    -> SKIP DIRECTORY')
            continue

        # Case 1: File name starts with YYYY-MM-DD-hhmmss. Skip file
        if re.fullmatch(re_filedate, fp.stem) != None:
            print('    -> SKIP')
            continue

        # Case 2: Creation date can be retrieved from original file name
        re_matches = re.match(re_wa_filename, fp.name)
        if re_matches != None:
            time_str = f'{re_matches[2][0:4]}-{re_matches[2][4:6]}-{re_matches[2][6:8]}-000000'
            file_name_new = f'{time_str}_{fp.stem}{fp.suffix}'
            print('    -> USING DATE FROM MESSENGER FILE NAME')
            rename_file_inplace(fp, file_name_new)
            continue

        # Case 3: We have a jpg and try to load date from EXIF data
        if fp.suffix in ['.jpg', '.jpeg', '.jpe', '.jif', '.jfif', '.jfi']:
            file_name_new = ''
            with open(fp, 'rb') as img_file:
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

            if file_name_new != '':
                rename_file_inplace(fp, file_name_new)
                continue

        # Case 4: We take the last modified date file modified timestamp
        mtime = os.path.getmtime(fp)

        # file modified struct_time
        mtime_struct = time.gmtime(mtime)

        # file modified time string
        mtime_str = time.strftime('%Y-%m-%d-%H%M%S', mtime_struct)

        file_name_new = f'{mtime_str}_{fp.stem}{fp.suffix}'
        print('    -> USING FILE MODIFIED DATE')
        rename_file_inplace(fp, file_name_new)


if __name__ == "__main__":
    main()
