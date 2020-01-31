#!/usr/bin/env python3

# name:    diff_finger.py
# author:  nbehrnd@yahoo.com
# license: 2019, GPLv2
# date:    2019-12-19 (YYYY-MM-DD)
# edit:    2020-01-31 (YYYY-MM-DD)
""" Compute difference maps of normalized 2D Hirshfeld surface maps

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
    explicitly used by hirshfeld_moderator.  Except for numpy (1.13.3),
    all of this script's dependencies are met by the default installation
    of CPython (version 3.6.9) in Linux Xubuntu 18.04.3 LTS."""

import fnmatch
import os
import sys

import numpy as np

diff_register = []

# identification of the files to work with:
for file in os.listdir("."):
    if fnmatch.fnmatch(file, "*.dat") and \
            (fnmatch.fnmatch(file, "diff*.dat") is False):

        diff_register.append(file)
diff_register.sort()

# comparing the normalized 2D Hirshfeld surface maps
while len(diff_register) > 1:
    for entry in diff_register[1:]:
        ref_file = diff_register[0]
        probe_file = entry
        print("Comparing {} with {}.".format(ref_file, probe_file))

        # consistency check for de/di
        ref_screen = []
        with open(ref_file, mode="r") as ref_source:
            for line in ref_source:
                ref_screen.append(str(line.strip()))
        ref_y_min = str(ref_screen[0].split()[1])[:4]

        probe_screen = []
        with open(probe_file, mode="r") as probe_source:
            for line in probe_source:
                probe_screen.append(str(line.strip()))
        probe_y_min = str(probe_screen[0].split()[1])[:4]

        if (len(ref_screen) == len(probe_screen)) and (
                ref_y_min == probe_y_min):
            pass
        else:
            continue

        # branch about the reference file:
        content_ref_file = []
        with open(ref_file, mode="r") as source_ref:
            for line in source_ref:
                trimmed_line = str(line).strip()  # remove line feed

                split = trimmed_line.split()
                # branch about lines just prior to y-reset:
                if len(split) is None:
                    pass
                # branch about lines 'with visible entries':
                if len(split) == 3:
                    retain = split
                    content_ref_file.append(retain)

        # convert the list into an array, treat entries as floats
        ref_array = np.array(content_ref_file)
        ref_array = ref_array.astype(np.float)

        # branch about the probe file
        content_probe_file = []
        with open(probe_file, mode="r") as source_probe:
            for line2 in source_probe:
                trimmed_line2 = str(line2).strip()  # remove line feed

                split2 = trimmed_line2.split()
                # branch about lines just prior to y-reset:
                if len(split2) is None:
                    pass
                # branch about lines 'with visible entries':
                if len(split2) == 3:
                    retain2 = split2
                    content_probe_file.append(retain2)

        # convert the list into an array, treat entries as floats
        probe_array = np.array(content_probe_file)
        probe_array = probe_array.astype(np.float)

        # work at level of the matrix-like arrays
        # construct an array of the first two columns of the ref_array
        coordinates_array = ref_array
        coordinates_array = np.delete(coordinates_array, 2, axis=1)

        # subtract z-values of probe_file from z-values of ref_file;
        # prior to this, remove 'x-' and 'y-coordinate column'
        z_probe_array = np.delete(probe_array, 0, axis=1)
        z_probe_array = np.delete(z_probe_array, 0, axis=1)

        z_ref_array = np.delete(ref_array, 0, axis=1)
        z_ref_array = np.delete(z_ref_array, 0, axis=1)

        diff_array = z_ref_array - z_probe_array

        # append diff_array to the coordinates_array:
        result = np.append(coordinates_array, diff_array, axis=1)

        # deposit a permanent record of results by numpy 'as-such'
        # This lacks the linefeed to be re-inserted, and often carries
        # many more decimals, than wished.
        # np.savetxt("result_subtraction.csv", result)

        # return from array to list level, start a moderated formatting
        result_list = result.tolist()

        output = str("diff_") + str(ref_file)[:-4] + \
                    str("_") + str(probe_file)

        with open(output, mode="w") as newfile:
            for result_entry in result_list:
                to_reformat = str(result_entry).split()

                x_value = str("{:3.2f}".format(
                    float(str(to_reformat[0])[1:-1])))
                y_value = str("{:3.2f}".format(
                    float(str(to_reformat[1])[0:-1])))
                z_value = str("{:10.8f}".format(
                    round(float(str(to_reformat[2])[0:-1]), 8)))

                # re-insert the blanks met in normalized 2D fingerprints:
                if float(y_value) == float(ref_y_min):
                    newfile.write("\n")

                retain = str("{} {} {}\n".format(x_value, y_value, z_value))
                newfile.write(retain)

        # Remove the very first line in the report file (a blank one):
        interim = []
        with open(output, mode='r') as source:
            for line in source:
                interim.append(line)
        with open(output, mode='w') as newfile:
            for entry in interim[1:]:
                newfile.write(str(entry))

    # enter the next round of the Round robin tournament:
    del diff_register[0]
print("done")
sys.exit(0)
