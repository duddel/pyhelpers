'''
Copyright (c) 2024 Alexander Scholz

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
import os
import glob
import time
import datetime
import argparse
import hashlib
import sys
import re
import pathlib


TIME_FORMAT = "%Y-%m-%d-%H%M%S"
DST_LIST_FILENAME_PRE = "treesum"
DST_COMP_FILENAME_PRE = "treecompare"
DST_FILENAME_EXT = "txt"
RE_DST_LIST_FILENAME = re.compile("^treesum_\\d{4}-\\d{2}-\\d{2}-\\d{6}\.txt$")
RE_LIST_FILE_LINE = re.compile(
    r"^([0-9A-F]{64})\s(\d{4}-\d{2}-\d{2}-\d{6})\s(\d+)\s(.*)$")


def get_file_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest().upper()


def get_tree_files(path):
    t_files = glob.glob(os.path.join(path, f"{DST_LIST_FILENAME_PRE}_*"))
    t_files = sorted(t_files, reverse=True)
    if t_files:
        return t_files
    else:
        return []


def parse_treesum_file(path):
    with open(path, "r") as f:
        lines = f.readlines()

    data = []
    for l in lines:
        matches = RE_LIST_FILE_LINE.search(l)
        if matches:
            data.append([matches[1], matches[2], matches[3], matches[4]])
        else:
            print(f"ERROR: parsing file {path} failed")
            sys.exit(3)
    return data


def main_list(args):
    now_str = datetime.datetime.now().strftime(TIME_FORMAT)

    with open(f"{DST_LIST_FILENAME_PRE}_{now_str}.{DST_FILENAME_EXT}", "w") as f_dst:
        tree_files = glob.glob(os.path.join(
            os.getcwd(), "**/*"), recursive=True)
        tree_files.extend(glob.glob(os.path.join(
            os.getcwd(), "**/.*"), recursive=True))
        tree_files = [t for t in tree_files if os.path.isfile(t)]
        tree_files = [t for t in tree_files if not RE_DST_LIST_FILENAME.match(
            pathlib.Path(t).name)]

        t_ctr = 1
        t_len = len(tree_files)
        for t in tree_files:
            print(f"\r{t_ctr}/{t_len} {t}", end='', flush=True)

            # Hash
            t_hash = get_file_hash(t)
            # File modification time
            t_mtime = os.path.getmtime(t)
            mtime_struct = time.gmtime(t_mtime)
            mtime_str = time.strftime(TIME_FORMAT, mtime_struct)
            # Size
            t_size = os.path.getsize(t)

            f_dst.write(f"{t_hash} {mtime_str} {t_size} {t}\n")
            t_ctr += 1


def main_compare(args):
    file_l = None
    file_r = None

    if not args.right:
        if not args.left:
            path_l = os.getcwd()
        elif os.path.isdir(args.left):
            path_l = args.left
        else:
            print(f"ERROR: Only one (LEFT) file given to compare: {args.left}")
            sys.exit(5)

        print(f"Comparing latest 2 treesum files in {path_l}...")
        tree_files = get_tree_files(path_l)
        if len(tree_files) < 2:
            print(
                f"ERROR: At least 2 treesum files required in {path_l}, found: {len(tree_files)}")
            sys.exit(6)
        file_l = tree_files[0]
        file_r = tree_files[1]
    elif os.path.isdir(args.right):
        path_l = None
        if not args.left:
            path_l = os.getcwd()
        elif os.path.isdir(args.left):
            path_l = args.left
        else:
            file_l = args.left

        # Get latest treesum file from LEFT directory
        if path_l:
            print(
                f"Comparing latest treesum file from {path_l} and {args.right}...")
            tree_files = get_tree_files(path_l)
            if len(tree_files) < 1:
                print(f"ERROR: No treesum file found in {path_l}")
                sys.exit(7)
            file_l = tree_files[0]

        # Get latest treesum file from RIGHT directory
        tree_files = get_tree_files(args.right)
        if len(tree_files) < 1:
            print(f"ERROR: No treesum file found in {args.right}")
            sys.exit(8)
        file_r = tree_files[0]
    else:
        path_l = None
        if not args.left:
            path_l = os.getcwd()
        elif os.path.isdir(args.left):
            path_l = args.left
        else:
            file_l = args.left

        # Get latest treesum file from LEFT directory
        if path_l:
            tree_files = get_tree_files(path_l)
            if len(tree_files) < 1:
                print(f"ERROR: No treesum file found in {path_l}")
                sys.exit(9)
            file_l = tree_files[0]
        file_r = args.right

    file_l = os.path.abspath(file_l)
    file_r = os.path.abspath(file_r)

    print(f"  LEFT:  {file_l}")
    print(f"  RIGHT: {file_r}")

    # Load the actual data from files
    data_l = parse_treesum_file(file_l)
    data_r = parse_treesum_file(file_r)

    hash_r = [d[0] for d in data_r]
    data_l_not_found_in_r = [l for l in data_l if l[0] not in hash_r]

    print("*******************************************************")
    print(
        f"These {len(data_l_not_found_in_r)} files exist in LEFT, but were not found in RIGHT:")
    for d in data_l_not_found_in_r:
        print(f"  {d[3]} {d[1]} {d[2]} {d[0]}")
    print("*******************************************************")

    print("ALL files from LEFT:")
    for d in data_l:
        print(f"{d[0]}\n  {d[1]} (modified)\n  {d[2]} (size)\n  (LEFT)  {d[3]}")
        d_in_r = [r for r in data_r if d[0] == r[0]]
        for dr in d_in_r:
            print(f"  (RIGHT) {dr[3]}")
        if len(d_in_r) == 0:
            print("  (RIGHT) NOT FOUND")


if __name__ == "__main__":
    aPars = argparse.ArgumentParser(description="Tool for hash based, recursive, directory comparison.\n\
Answers the question: which files in LEFT directory are (based on hash) also present in RIGHT directory,\n\
even if moved or renamed?\n\
  list: Creates a treesum list file containing all hashes of all files in cwd, recursively\n\
  compare: use -left and -right args to compare 2 list files",
                                    formatter_class=argparse.RawTextHelpFormatter)
    aPars.add_argument("command", type=str,
                       help="Command to execute: [list, compare]")
    aPars.add_argument("-left", type=str,
                       help="Left side for comparison [compare]. If directory, latest list file is used. Defaults to cwd.")
    aPars.add_argument("-right", type=str,
                       help="Right side for comparison [compare]. If directory, latest list file is used.")
    args = aPars.parse_args()

    if args.command == "list":
        main_list(args)
    elif args.command == "compare":
        main_compare(args)
    else:
        print(f"ERROR: Unknown command {args.command}")
        sys.exit(1)
