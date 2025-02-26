#!/usr/bin/env python3

# name:    diff_finger.py
# author:  nbehrnd@yahoo.com
# license: 2019, GPLv2
# date:    2019-12-19 (YYYY-MM-DD)
# edit:    [2025-02-26 Wed]
"""Compute difference maps of normalized 2D Hirshfeld surface maps

The number of programming languages around the computation of already
normalized 2D Hirshfeld surface maps and difference Hirshfeld surface
maps may be considered as higher, than necessary.  Potentially, their
number may be lowered.  There already is one moderator script written
in CPython, i.e., Hirshfeld_moderator.py, suggesting to continue with
this language, too.

This script serves as a proof-of-concept for the comparison of two 2D
Hirshfeld surface fingerprint maps (by fingerprint.f90)
in a round-Robin tournament.  It probes the two .dat files subject to
comparison match in terms of map ranges de/di: both the number of
entries (lines) must be equal, as the lowest y_value.  This allows to
probe standard, translated, or extended map range, respectively.

To work with, place the script in the directory of (then already
normalized) .dat files.  It is launched from the CLI by

python3 diff_finger.py

This script diff_finger.py still is independent to the actions by
hirshfeld_moderator.py.  It is neither called, nor are its results
explicitly used by hirshfeld_moderator.  This version relies on third
party numpy at version 2.1.0 or higher and is known to process with
Python 3.12.7 and numpy 2.2.0 (fetched via `requirements.txt` from PyPI)
in Linux Debian 13/trixie."""

import argparse
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

    # comparing the normalized 2D Hirshfeld surface maps
    while len(file_names) > 1:
        for entry in file_names[1:]:
            ref_file = file_names[0]
            probe_file = entry
            data_a, data_b = file_reader(ref_file), file_reader(probe_file)

            if consistency_check(data_a, data_b):
                print(f"{ref_file} vs {probe_file}")
                difference_map = compute_difference(data_a, data_b)

                output_name = "_".join(["diff", ref_file[:-4], probe_file])
                output_format = "%4.2f %4.2f %9.6f"
                try:
                    np.savetxt(output_name, difference_map, fmt=output_format)
                except OSError as e:
                    print(f"Problem while writing '{output_name}' ({e}).")

        # enter the next round of the Round robin tournament:
        del file_names[0]


if __name__ == "__main__":
    main()
