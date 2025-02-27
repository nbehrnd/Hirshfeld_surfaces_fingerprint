#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-2.0-only

# name:    diff_finger.py
# author:  nbehrnd@yahoo.com
# license: 2019, GPLv2
# date:    [2019-12-19 Thu]
# edit:    [2025-02-27 Thu]
"""Compute difference maps of normalized 2D Hirshfeld surface maps

In line with other Python scripts in this project, the overall goal to
add this script is to perform each step of the analysis with Python.
Similar to `diff_finger.c` provided by the authors of the publication,
this scripts provides computes a Hirschfeld difference map given two
normalized Hirschfeld maps where

```shell
python diff_finger.py data_a.dat data_b.dat
```

will write a new file `diff_data_a_data_b.dat` with the difference
Hirschfeld map.  In an operational system like Linux Debian, a call by

```bash
python ./diff_finger.py *.dat
```

attempts to process all `*.dat` files in the current working directory.
Compared to the compiled executable of `diff_finger.c` (or the equally
added `diff_finger.f90` for Fortran), despite relying on numpy, this
scripts performance will be a bit slower.  The numeric results, for
instance with `BZAMID01.dat` and `BZAMID11.dat` provided as test data
to yield `diff_BZAMID01_BZAMID11.dat` occasionally differ slightly from
the one provided by the compiled executable for C.  So far, they were
not significant at the scale of eventually plotting the difference maps,
nor in the eventual computation of the difference number.

Revised and tested in an instance of Linux Debian 13/trixie with
Python 3.13.1 and numpy 2.2.2."""

import argparse
import itertools
import numpy as np


def get_args():
    """collect the command line arguments"""
    parser = argparse.ArgumentParser(
        description="""
With two Hirschfeld maps A (provided by file `A.dat`) and B (file `B.dat`), a
difference map can be computed; the script writes the result of this into file
`diff_A_B.dat`.  More generally, for a list of maps e.g., A, B, C, D the script
launches a round-Robin approach to check all permutations (AB, AC, AD, BC, BD,
CD) and to store the results accordingly.""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "file",
        help="provide two, or more Hirshfeld map files to process",
        metavar="FILE",
        type=argparse.FileType("rt"),
        nargs="+",
    )

    return parser.parse_args()


def file_reader(file_name):
    """access the data of a normalized Hirschfeld map

    This returns the content of the .dat files as np arrays."""
    try:
        data = np.loadtxt(file_name, delimiter=" ")
    except ValueError as e:
        print(f"Problematic input by file '{file_name}' ({e}).")
        return None

    return data


def consistency_check(data_a, data_b):
    """identify mutually incompatible Hirshfeld maps

    Hirschfeld maps computed by CrystalExplorer have a lower
    limit of d_e = d_i, and a upper limit of d_e = d_i.  Hence
    a check if

    - the lower limit of d_e,
    - the upper limit of d_e, as well as
    - the line count of the array

    for data set a and b is deemed sufficient to identify a
    pair of two Hirschfeld maps mutually unsuitable to compute
    a difference map."""
    if data_a[0, 0] != data_b[0, 0]:
        return False
    if data_a[-1, 0] != data_b[-1, 0]:
        return False
    if data_a.shape[0] != data_b.shape[0]:
        return False

    return True


def compute_difference(data_a, data_b):
    """compute the difference of the z-component of array a and b"""
    difference_vector = data_a[:, 2] - data_b[:, 2]
    difference_map = np.column_stack((data_a[:, :2], difference_vector))

    return difference_map


def main():
    """join the functionalities"""
    args = get_args()
    list_of_files = args.file
    file_names = [data_file.name for data_file in list_of_files]
    file_names.sort()

    # ensure data_a and data_b are arrays of only floating numbers:
    for ref_file, probe_file in itertools.combinations(file_names, 2):
        data_a = file_reader(ref_file)
        if data_a is None:
            continue

        data_b = file_reader(probe_file)
        if data_b is None:
            continue

        if consistency_check(data_a, data_b):
            print(f"{ref_file} vs {probe_file}")
            difference_map = compute_difference(data_a, data_b)

            output_name = "_".join(["diff", ref_file[:-4], probe_file])
            output_format = "%4.2f %4.2f %9.6f"
            try:
                np.savetxt(output_name, difference_map, fmt=output_format)
            except OSError as e:
                print(f"Problem while writing '{output_name}' ({e}).")


if __name__ == "__main__":
    main()
