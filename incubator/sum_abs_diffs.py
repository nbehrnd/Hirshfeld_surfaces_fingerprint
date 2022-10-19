#!/usr/bin/env python3

# name:    sum_abs_diffs.py
# author:  nbehrnd@yahoo.com
# license: 2019, GPLv2
# date:    2019-12-19 (YYYY-MM-DD)
#
""" computation of the difference number

    This script rebuilds the ruby script of same name,
    sum_abs_diff.rb, from the code basis shared by Andrew Rohl
    and Paolo Raiteri, as CPython script.  The script's action is
    to add the absolute difference values, stored as the third
    dimension in the Hirshfeld surface difference maps, and state
    the corresponding sum:  the larger this difference number,
    the more the two normalized 2D Hirshfeld surface fingerprints
    compared with each other differ.

    The script is written with the same intent; to ease access to the
    computation and eventual, comprehension of difference Hirshfeld
    surface maps by offering a less diverge code basis.  As there
    already is a moderating script, hirshfeld-moderator.py, and to
    compute the differences between 2D Hirshfeld surface fingerprints,
    diff_finger.py, this is an extension of the 'concept study'.

    Written for the CLI of Python (version 3.6.8) of Linux Xubuntu
    (version 18.04.3 LTS), independent in its action to the by
    hirshfeld-moderator.py.  All modules imported are members of the
    Python standard library. """

import fnmatch
import os
import sys
from decimal import Decimal

# identification of the files to work on:
file_register = []
for file in os.listdir("."):
    if fnmatch.fnmatch(file, "diff*.dat"):
        file_register.append(file)
file_register.sort()

# computation of the difference number:
for entry in file_register:
    diff_number = 0

    with open(entry, mode="r") as source:
        for line in source:
            if len(line) > 2:
                diff_number += abs(Decimal(str(line.strip()).split()[2]))
    print("{}:  {}".format(entry, diff_number))

sys.exit(0)
