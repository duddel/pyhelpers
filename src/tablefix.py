'''
Copyright (c) 2025 Alexander Scholz

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
import pandas as pd
import re
import datetime


INPUT_FILE = "input.ods"
OUTPUT_FILE = "output.ods"

RE_NUM_COMMA = re.compile(r"^(\d+)\,(\d+)$")
RE_NUM_DOT = re.compile(r"^(\d+)\.(\d+)$")
RE_NUM_DOT_COMMA = re.compile(r"^(\d+)\.(\d+)\,(\d+)$")
RE_INT = re.compile(r"^(\d+)$")
RE_DATE_1 = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")
RE_DATE_2 = re.compile(r"^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}$")
RE_EMPTY = re.compile(r"^\s+$")


def col2num(df, col_id):
    rows = df.shape[0]

    for i in range(rows):
        if type(df.loc[i, col_id]) == float:
            continue

        re_matches = re.search(RE_NUM_COMMA, df.loc[i, col_id])
        if re_matches != None:
            num_str = f"{re_matches[1]}.{re_matches[2]}"
            df.loc[i, col_id] = float(num_str)
            continue

        re_matches = re.search(RE_NUM_DOT, df.loc[i, col_id])
        if re_matches != None:
            df.loc[i, col_id] = float(df.loc[i, col_id])
            continue

        re_matches = re.search(RE_NUM_DOT_COMMA, df.loc[i, col_id])
        if re_matches != None:
            num_str = f"{re_matches[1]}{re_matches[2]}.{re_matches[3]}"
            df.loc[i, col_id] = float(num_str)
            continue

        re_matches = re.search(RE_INT, df.loc[i, col_id])
        if re_matches != None:
            df.loc[i, col_id] = float(df.loc[i, col_id])
            continue

        raise ValueError(f"Could not parse number {df.loc[i, col_id]}")


def col2date(df, col_id):
    rows = df.shape[0]

    for i in range(rows):
        if type(df.loc[i, col_id]) == float:
            continue

        re_matches = re.search(RE_EMPTY, df.loc[i, col_id])
        if re_matches != None:
            df.loc[i, col_id] = float("NaN")
            continue

        re_matches = re.search(RE_DATE_1, df.loc[i, col_id])
        if re_matches != None:
            df.loc[i, col_id] = datetime.datetime.strptime(re_matches[0], "%d.%m.%Y")
            continue

        re_matches = re.search(RE_DATE_2, df.loc[i, col_id])
        if re_matches != None:
            df.loc[i, col_id] = datetime.datetime.strptime(re_matches[0], "%Y-%m-%d %H:%M:%S")
            continue

        raise ValueError(f"Could not parse date {df.loc[i, col_id]}")


def main():
    # Loading sheet as 'str'.
    # Values might be parsed anyway (dates, numbers) and handed over as str.
    # Then, we try to match these strings with regex and convert them to consistent type (date, float)
    df = pd.read_excel(INPUT_FILE,
                       sheet_name=0,
                       header=None,
                       engine="odf",
                       dtype=str)

    col2num(df, 2)
    col2num(df, 3)
    col2date(df, 1)
    col2date(df, 4)

    writer = pd.ExcelWriter(OUTPUT_FILE, engine="odf")
  
    df.to_excel(writer, sheet_name="Tabelle1", header=None, index=None)

    writer.close()

    pass

if __name__ == "__main__":
    main()
