#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    sum_abs_diffs.py
# author:  nbehrnd@yahoo.com
# license: 2019, GPLv2
# date:    [2019-12-19 Thu]
# edit:    [2025-02-25 Tue]
#
""" computation of the maps' difference number

    Similar to sum_abs_diff.rb provided by Andrew Rohl and Paolo
    Raiteri, this Python script computes and eventually reports
    the absolute difference values of previously calculated
    Hirshfeld surface difference maps.

    The script was equally was written with the intent to offer
    an analysis in Python alone.  This particular script only
    requires modules of Python's standard library."""

import argparse
from decimal import Decimal


def get_args():
    """collect the command line arguments"""
    parser = argparse.ArgumentParser(
        description="compute the map's difference number",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        help="One or multiple difference map files to process",
        metavar="FILE",
        type=argparse.FileType("rt"),
        nargs="+",
    )

    return parser.parse_args()


def compute_difference_number(map_file):
    """compute the a map_file's difference number"""
    diff_number = 0

    try:
        with open(map_file, mode="r", encoding="utf-8") as source:
            for line in source:
                if len(line) > 2:
                    diff_number += abs(Decimal(str(line.strip()).split()[2]))
        print(f"{map_file}:  {diff_number}")
    except OSError as e:
        print(f"Problem to access '{map_file}' ({e})")


def main():
    """join the functionalities"""
    args = get_args()
    list_of_files = args.file
    for map_file in list_of_files:
        compute_difference_number(map_file.name)


if __name__ == "__main__":
    main()
