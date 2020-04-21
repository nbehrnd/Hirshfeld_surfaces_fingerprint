#!/usr/bin/env python
# name:    hirshfeld_moderator.py
# author:  nbehrnd@yahoo.com
# license: GPL version 2
# date:    2019-11-14 (YYYY-MM-DD)
# edit:    2020-04-21 (YYYY-MM-DD)
#
""" This is a moderator script for Python to either moderate a Difference
Hirshfeld surface analysis introduced with

"Difference Hirshfeld fingerprint plots: a tool for studying polymorphs."
Carter, D. J.; Raiteri, P.; Barnard, K. R.; Gielink, R.; Mocerino, M.;
Skelton, B. W.; Vaughan, J. G.; Ogden, M. I.; Rohl, A. L. in CrystEngComm,
2017, 19, 2207--2215; doi: 10.1039/c6ce02535h

This script provides a unified interface to the three individual scripts
shared by Andrew Rohl and Paolo Raiteri:
+ fingerprint.f90 (Fortran)
+ diff_finger.c (C), and
+ sum_abs_diff.rb (Ruby)
The first two require a compiler prior to their use -- gcc / gfortran for
fingerprint.f90, gcc for diff_finger.c -- and an installation of Ruby for
sum_abs_diff.rb.

Together with script fingerprint_kahan.py, this script equally allows to
perform all of the necessary computations with Python, too.  Note that
some of the computations may advance substantially faster, if the default
CPython compiler is replaced by pypy.

The script may relay the visualization of the results to gnuplot, or -- as
a fall-back alternative -- to Python's matplotlib library to yield bitmap
.png and vector .pdf images.  Note that only for the second option, the
script relies on matplotlib and numpy; which both are not in the Python's
standard library.

Written for the CLI in Linux, the script equally works in Windows with
Python 3.6.9, Python 2.7.17, and pypy 7.3.0.  The script's help menu may
be accessed by

python hirshfeld_moderator.py -h

The script consists of four sections:
+ definitions of functions to manage CrystalExplorer's .cxs files (start
  by line #66).
+ definition of functions to work on the .cxs files eventually yielding
  fingerprint .dat files, the difference maps, and the ruby number (start
  by line #216).
+ definition of functions to relay the optional display of results with
  either gnuplot, or matplotlib (start by line #522).
+ a section bundling the necessary toggles as arguments when calling the
  script e.g., by python moderator_hirshfeld.py --dpng e -a -g --zmax 0.08
  (start by line #1099).

For additional details about using the program, please read the separate
documentation. """

import argparse
import fnmatch
import math
import os
import platform
import shutil
import subprocess as sub
import sys


# Section A:  .cxs file management:
def create_workshop():
    """ Create a dedicated sub-folder for copies of .cxs to work on """
    # An already existing 'cxs_workshop' folder will be deleted.
    for element in os.listdir("."):
        test = os.path.isdir(os.path.join(os.getcwd(), element))
        if test:
            if fnmatch.fnmatch(element, "cxs_workshop"):
                try:
                    shutil.rmtree(element)
                except IOError:
                    print("Please remove 'csx_workshop' manually.")
                    sys.exit(0)

    try:
        os.mkdir("cxs_workshop")
    except IOError:
        print("\nProblem to create sub-folder 'cxs_workshop'.")
        print("Without alteration of data, the script closes now.\n")
        sys.exit(0)


def list_cxs(copy=False):
    """ List / copy .cxs files in the same project folder (cf. rename_cxs). """
    file_register = []
    counter = 0

    for file in os.listdir("."):
        if file.endswith(".cxs"):
            counter += 1
            print("{}\t{}".format(counter, file))
            file_register.append(file)

            if copy:
                try:
                    shutil.copy(file, "cxs_workshop")
                except IOError:
                    print("{} wasn't copied to 'cxs_workshop'.".format(file))
                    continue
    print("\n{} files of type {} were identified.\n".format(
        len(file_register), "*.cxs"))


def crawl_cxs(copy=False):
    """ Retrieve / copy .cxs files by means of an os.walk. """
    root = os.getcwd()
    counter = 0
    cxs_to_copy = []

    for _, subfolders, _ in os.walk(root):
        try:
            for subfolder in subfolders:
                os.chdir(subfolder)
                for file in os.listdir("."):
                    if file.endswith(".cxs"):
                        cxs_to_copy.append(os.path.abspath(file))
                        counter += 1
                        print("{}\t{}".format(counter, file))
                os.chdir(root)
        except IOError:
            continue

    if copy:  # not considered except on explicit consent.
        for entry in cxs_to_copy:
            try:
                shutil.copy(entry,
                            os.path.join(root, "cxs_workshop",
                                         os.path.basename(entry)))
            except IOError:
                print("Not copied to cxs_workshop: {}".format(entry))


def rename_cxs():
    """ Truncate file names of CrystalExplorer surface files.

    CrystalExplorer provides Hirshfeld surfaces named in a pattern of
    'example_example.cxs'.  Work is easier if their file name is truncated
    to 'example.cxs'.  This is applied only to copies of .cxs. """
    root = os.getcwd()
    os.chdir("cxs_workshop")

    for file in os.listdir("."):
        if file.endswith(".cxs"):
            if str("_") in file:
                new_filename = str(file.split("_")[0]) + str(".cxs")
                try:
                    shutil.move(file, new_filename)
                except IOError:
                    print("Renaming {} failed.".format(file))
                    continue
    os.chdir(root)


def file_listing():
    """ Survey of the .cxs files eventually to work with. """
    print("\nListing of the .cxs files accessible.  Press either")
    print("[0]  to leave the script.")
    print("[1]  .cxs files reside in the same folder as this script.")
    print("[2]  .cxs files reside in sub-folders to the current folder.\n")

    try:
        listing_choice = int(input())
    except IOError:
        sys.exit(0)
    if listing_choice == 0:
        print("\n Script's execution was ended.\n")
        sys.exit(0)
    if listing_choice == 1:
        print("")
        list_cxs()
    if listing_choice == 2:
        print("")
        crawl_cxs()


def assemble_cxs():
    """ Join copies of .cxs into one dedicated sub-folder / workshop. """
    print("\nCopies of .cxs files will be brought into 'cxs_workshop'.")
    print("Any 'cxs_workshop' folder of previous runs will be erased.")
    print("File names of .cxs copies are truncated at first underscore.")
    print("")
    print("[0]  to leave the script.")
    print("[1]  .cxs files reside in the same folder as this script.")
    print("[2]  .cxs files reside in sub-folders to the current folder.")
    root = os.getcwd()

    try:
        assemble_choice = int(input())
    except IOError:
        sys.exit(0)
    if assemble_choice == 0:
        print("\n Script's execution is ended.\n")
    try:
        create_workshop()
    except IOError:
        pass
    if assemble_choice == 1:
        print("")
        create_workshop()
        list_cxs(copy=True)
    if assemble_choice == 2:
        print("")
        create_workshop()
        crawl_cxs(copy=True)
    os.chdir(root)


# formal end of section # Section A:  .cxs file management.


# Section B:  Computation with .cxs and .dat files:
def compile_f90():
    """ Compile fingerprint.f90 with gfortran (default), or gcc. """
    compile_gfo_f90 = str("gfortran fingerprint.f90 -o fingerprint.x")
    compile_gcc_f90 = str("gcc fingerprint.f90 -o fingerprint.x")
    print("Compilation of fingerprint.f90 with either gfortran or gcc.")
    try:
        sub.call(compile_gfo_f90, shell=True)
    except IOError:
        print("Compilation attempt with gfortran failed.")
        print("Independent compilation attempt with gcc.")
        try:
            sub.call(compile_gcc_f90, shell=True)
        except IOError:
            print("Compilation attempt with gcc equally failed.")
            print("Maybe fingerprint.f90 is not in the project folder.")
            print("Equally ensure installation of gfortran or gcc.")
            sys.exit(0)
        print("fingerprint.f90 was compiled successfully (gcc).")
    print("fingerprint.f90 was compiled successfully (gfortran).")


def shuttle_f90():
    """ Shuttle the executable of fingerprint.f90 into the workshop. """
    try:
        shutil.copy("fingerprint.x", "cxs_workshop")
    except IOError:
        print("Error to copy Fortran .f90 executable to 'cxs_workshop'.")
        sys.exit(0)

    try:
        os.remove("fingerprint.x")  # space cleaning, root folder.
    except IOError:
        pass


def fingerprint_fortran():
    """ Generate extended normalized 2D fingerprint .dat of all .cxs """
    print("\nNormalization of .cxs files yielding 2D fingerprint .dat:")
    root = os.getcwd()
    os.chdir("cxs_workshop")

    register = []
    for file in os.listdir("."):
        if file.endswith(".cxs"):
            register.append(file)
    register.sort()

    for entry in register:
        dat_file = str(entry)[:-4] + str(".dat")
        # clause for Linux-based computers:
        if platform.system().startswith("Linux"):
            normalize = str("./fingerprint.x {} extended {}".format(
                entry, dat_file))
        # clause for Windows-based computers:
        if platform.system().startswith("Windows"):
            normalize = str("fingerprint.x {} extended {}".format(
                entry, dat_file))

        sub.call(normalize, shell=True)
    if platform.system().startswith("Linux"):
        try:
            os.remove("fingerprint.x")
        except IOError:
            pass
    os.chdir(root)
    print("\nNormalization of .cxs files is completed.")


def fingerprint_python():
    """ Normalized 2D Hirshfeld surface fingerprints, computed by Python.

    Requires presence of both moderator and 'fingerprint_kahan.py'. """

    print("Python-based computation of normalized 2D Hirshfeld fingerprints.")
    try:
        os.chdir("cxs_workshop")
        import fingerprint_kahan
        fingerprint_kahan.main()
    except IOError:
        print("""\nLacking script 'fingerprint_Kahan.py' in the same folder
        as the moderator script, the computation could not be performed. """)
        sys.exit()


def compile_c():
    """ Compile diff_finger.c with gcc. """
    print("\nCompilation of 'diff_finger.c' was started.")
    try:
        compile_diff = str("gcc diff_finger.c -o diff_finger")
        sub.call(compile_diff, shell=True)
        print("Successful compilation of 'diff_finger.c' with gcc.\n")
    except IOError:
        print("Compilation of diff_finger.c failed.")
        print(
            "Check for the presence of diff_finger.c in project's root folder."
        )
        print("Check for the presence of the gcc compiler, too.")
        sys.exit(0)


def shuttle_c():
    """ Shuttle the executable of diff_finger.c to the data. """
    # clause for Linux-based computers:
    if platform.system().startswith("Linux"):
        try:
            shutil.copy("diff_finger", "cxs_workshop")
        except IOError:
            print("Error while copying C executable to the data.")
            print("Check the presence of folder 'cxs_workshop'.")
            sys.exit(0)

        try:
            os.remove("diff_finger")  # space cleaning, root folder.
        except IOError:
            pass

    if platform.system().startswith("Windows"):
        try:
            shutil.copy("diff_finger.exe", "cxs_workshop")
        except IOError:
            print("Error while copying C executable to the data.")
            print("Check the presence of folder 'cxs_workshop'.")
            sys.exit(0)


def difference_maps_c():
    """ Compare the 2D fingerprints with each other, C script. """
    print("\nComputation of difference maps (C script) starts:")
    os.chdir("cxs_workshop")
    fingerprint_register = []

    for file in os.listdir("."):
        if file.endswith(".dat") and (file.startswith("diff") is False):
            fingerprint_register.append(file)
    fingerprint_register.sort()

    while len(fingerprint_register) > 1:
        for entry in fingerprint_register[1:]:
            reference_map = fingerprint_register[0]
            test_map = entry
            difference_map = (str("diff_") + str(reference_map)[:-4] +
                              str("_") + str(test_map))

            print("{} vs. {} to yield {}".format(reference_map, test_map,
                                                 difference_map))
            if platform.system().startswith("Linux"):
                difference_test = str("./diff_finger {} {} > {}".format(
                    reference_map, test_map, difference_map))
            if platform.system().startswith("Windows"):
                difference_test = str("diff_finger.exe {} {} > {}".format(
                    reference_map, test_map, difference_map))
            try:
                sub.call(difference_test, shell=True)
            except IOError:
                print("Problem to compute {}.".format(difference_map))

        del fingerprint_register[0]
    print("\nComputation of difference maps is completed.")
    if platform.system().startswith("Linux"):
        try:
            os.remove("diff_finger")
        except IOError:
            pass
    if platform.system().startswith("Windows"):
        try:
            os.remove("diff_finger.exe")
        except IOError:
            pass


def difference_maps_python():
    """ Compute difference maps by Python without numpy. """
    # identify the files to work with:
    os.chdir("cxs_workshop")
    diff_register = []

    for file in os.listdir("."):
        if file.endswith(".dat") and (file.startswith("diff") is False):
            diff_register.append(file)
    diff_register.sort()

    # compare the normalized 2D Hirshfeld surface maps
    print("\nComputation of difference maps (Python) starts:")
    while len(diff_register) > 1:
        for entry in diff_register[1:]:
            reference_file = diff_register[0]
            probe_file = entry
            print("Comparison {} ./. {}.".format(reference_file, probe_file))

            reference_map = []
            probe_map = []

            reference = open(reference_file, mode="r")
            reference_map = reference.readlines()
            reference.close()

            probe = open(probe_file, mode="r")
            probe_map = probe.readlines()
            probe.close()

            # consistency check for de/di
            start_reference_map = " ".join([
                reference_map[0].strip().split()[0],
                reference_map[1].strip().split()[0]
            ])
            start_probe_map = " ".join([
                probe_map[0].strip().split()[0],
                probe_map[1].strip().split()[0]
            ])

            line_count_reference_map = len(reference_map)
            line_count_probe_map = len(probe_map)

            if (start_reference_map == start_probe_map) and \
                    (line_count_reference_map == line_count_probe_map):
                pass  # i.e., interesting, inspect the current two .dat.
            else:
                continue  # i.e., incompatible, probe the next permutation.

            # .dat suitable for comparison will be analyzed:
            difference_map = []
            for reference, probe in zip(reference_map, probe_map):
                # retain the blank lines:
                if len(reference) < 5:
                    difference_map.append("\n")
                # entries with coordinates and any area element:
                if len(reference) > 5:
                    column_a = str("{:3.2f}".format(
                        float(reference.strip().split()[0])))
                    column_b = str("{:3.2f}".format(
                        float(reference.strip().split()[1])))
                    column_c = str("{:10.8f}".format(
                        (float(reference.strip().split()[2]) -
                         float(probe.strip().split()[2]))))
                    retain = " ".join([column_a, column_b, column_c, "\n"])
                    difference_map.append(retain)

            # generate the permanent record:
            output = "".join(["diff_", reference_file[:-4], "_", probe_file])
            with open(output, mode="w") as newfile:
                for report_entry in difference_map[:-1]:
                    newfile.write("{}\n".format(report_entry.strip()))
        del diff_register[0]


def shuttle_ruby_script():
    """ Bring sum_abs_diffs.rb to the difference map data. """
    try:
        shutil.copy("sum_abs_diffs.rb", "cxs_workshop")
    except IOError:
        print("Problem copying 'sum_abs_diffs.rb' to 'cxs_workshop'.")
        print("Maybe the Ruby script is missing.  Exit.")
        sys.exit(0)


def difference_number_ruby():
    """ Report the Ruby difference numbers from the diff*.dat data. """
    os.chdir("cxs_workshop")
    register = []

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "diff*.dat"):
            register.append(file)
    register.sort()

    print("Compute difference number with the Ruby script:\n")
    for entry in register:
        test = str("ruby sum_abs_diffs.rb {}".format(entry))
        try:
            sub.call(test, shell=True)
        except IOError:
            print("Problem to determine the difference number.")
            print("Ensure a callable installation of Ruby in first place.")
            sys.exit(0)

    try:
        os.remove('sum_abs_diffs.rb')
    except IOError:
        pass


def difference_number_python():
    """ Absolute values of differences per difference map, Python path. """
    # identification of the files to work with:
    os.chdir("cxs_workshop")
    register = []

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "diff*.dat"):
            register.append(file)
    register.sort()

    print("Compute difference number with Python:\n")
    for entry in register:
        diff_number = 0.0

        with open(entry, mode="r") as source:
            for line in source:
                if len(line) > 2:
                    diff_number += abs(float(str(line.strip()).split()[2]))
        print("{}:  {:6.4f}".format(entry, diff_number))


# formal end of Section B:  Computation with .cxs and .dat files.

# Section C:  Display, start:
# Ca: Definition of non-trivial gnuplot color palettes.
# The CrystalExplorer like rainbow (verbatim copy from fingerprint.f90.)
#
RAINBOW = str("""set palette defined (0  1.0 1.0 1.0, \
               0.00001  0.0 0.0 1.0, \
               1  0.0 0.5 1.0, \
               2  0.0 1.0 1.0, \
               3  0.5 1.0 0.5, \
               4  1.0 1.0 0.0, \
               5  1.0 0.5 0.0, \
               6  1.0 0.0 0.0 ) """)

# The three-level blue-white-red palette (copy from fingerprint.f90).
#
THREE_LEVEL_OLD = str("set palette defined (-1 'blue', 0 'white', 1 'red')")

# The softer three-level palette:
#
# Used by default for the screening .png to facilitate discern of tiles with
# z close to zero (otherwise print white) from the paper-white background.
THREE_LEVEL_NEW = str(
    "set palette defined (-1 'blue', 0 'light-gray', 1 'red')")

# The better diverging palette for the difference maps.
#
# This is based on Kenneth Moreland's suggested color palette
# "bent-cool-warm-table-float-0064.csv" [1] converted by csv2plt.py [2]
# into a format accessible to gnuplot.
#
# [1]
# https://github.com/kennethmoreland-com/kennethmoreland-com.github.io/blob/master/color-advice/bent-cool-warm/bent-cool-warm-table-float-0064.csv,
#     edit by Jan 17, 2016; md5sum f31b220283836b3ea61de2a5e586c807.
#
# [2] https://github.com/nbehrnd/moreland-gnuplot-palettes/blob/master/tools/csv2plt.py
#     edit by Dec 4, 2019; md5sum c9262530c06b7f364aa716131ac46c3d.
BENT_THREE_LEVEL_0064 = str("""set palette defined (\
  0.00000 0.33479 0.28308 0.75650 ,\
  0.01587 0.34619 0.30634 0.76684 ,\
  0.03175 0.35807 0.32923 0.77682 ,\
  0.04762 0.37046 0.35181 0.78642 ,\
  0.06349 0.38335 0.37416 0.79567 ,\
  0.07937 0.39676 0.39631 0.80456 ,\
  0.09524 0.41069 0.41829 0.81311 ,\
  0.11111 0.42515 0.44013 0.82132 ,\
  0.12698 0.44014 0.46186 0.82921 ,\
  0.14286 0.45568 0.48347 0.83679 ,\
  0.15873 0.47175 0.50500 0.84406 ,\
  0.17460 0.48836 0.52644 0.85104 ,\
  0.19048 0.50553 0.54780 0.85773 ,\
  0.20635 0.52323 0.56909 0.86415 ,\
  0.22222 0.54149 0.59031 0.87031 ,\
  0.23810 0.56030 0.61146 0.87623 ,\
  0.25397 0.57966 0.63255 0.88191 ,\
  0.26984 0.59956 0.65357 0.88736 ,\
  0.28571 0.62002 0.67453 0.89261 ,\
  0.30159 0.64103 0.69542 0.89765 ,\
  0.31746 0.66260 0.71624 0.90252 ,\
  0.33333 0.68471 0.73700 0.90721 ,\
  0.34921 0.70737 0.75768 0.91175 ,\
  0.36508 0.73059 0.77828 0.91614 ,\
  0.38095 0.75436 0.79881 0.92041 ,\
  0.39683 0.77867 0.81926 0.92457 ,\
  0.41270 0.80353 0.83963 0.92863 ,\
  0.42857 0.82894 0.85991 0.93261 ,\
  0.44444 0.85490 0.88010 0.93652 ,\
  0.46032 0.88140 0.90019 0.94039 ,\
  0.47619 0.90845 0.92019 0.94422 ,\
  0.49206 0.93604 0.94009 0.94803 ,\
  0.50794 0.94662 0.93812 0.93237 ,\
  0.52381 0.93983 0.91432 0.89762 ,\
  0.53968 0.93310 0.89044 0.86341 ,\
  0.55556 0.92639 0.86650 0.82975 ,\
  0.57143 0.91968 0.84248 0.79665 ,\
  0.58730 0.91297 0.81838 0.76413 ,\
  0.60317 0.90622 0.79421 0.73219 ,\
  0.61905 0.89942 0.76996 0.70084 ,\
  0.63492 0.89256 0.74562 0.67010 ,\
  0.65079 0.88562 0.72120 0.63998 ,\
  0.66667 0.87859 0.69667 0.61049 ,\
  0.68254 0.87146 0.67203 0.58164 ,\
  0.69841 0.86421 0.64728 0.55343 ,\
  0.71429 0.85684 0.62240 0.52588 ,\
  0.73016 0.84933 0.59736 0.49900 ,\
  0.74603 0.84168 0.57216 0.47280 ,\
  0.76190 0.83388 0.54676 0.44729 ,\
  0.77778 0.82592 0.52114 0.42247 ,\
  0.79365 0.81779 0.49526 0.39835 ,\
  0.80952 0.80949 0.46907 0.37496 ,\
  0.82540 0.80101 0.44250 0.35229 ,\
  0.84127 0.79235 0.41548 0.33036 ,\
  0.85714 0.78350 0.38791 0.30918 ,\
  0.87302 0.77445 0.35965 0.28876 ,\
  0.88889 0.76521 0.33051 0.26911 ,\
  0.90476 0.75576 0.30022 0.25026 ,\
  0.92063 0.74611 0.26838 0.23220 ,\
  0.93651 0.73625 0.23434 0.21497 ,\
  0.95238 0.72617 0.19698 0.19857 ,\
  0.96825 0.71588 0.15401 0.18303 ,\
  0.98413 0.70536 0.09922 0.16836 ,\
  1.0 0.694625624821 0.00296461045768 0.154581828278) """)


def search_dat(map_type="delta", SCREEN=False):
    """ Search for .dat files, assume difference maps of typical interest.

    Two cases: fingerprints (type fingerprint, files ending on *.dat), or
    difference maps (map type delta, files in pattern of diff*.dat). """
    root = os.getcwd()
    global DAT_REGISTER
    DAT_REGISTER = []
    os.chdir("cxs_workshop")

    if SCREEN:  # indiscriminate register population.
        for file in os.listdir("."):
            if fnmatch.fnmatch(file, "*.dat"):
                DAT_REGISTER.append(file)

    if SCREEN is False:  # discriminate register population (map type).
        for file in os.listdir("."):

            if map_type == "fingerprint":
                if fnmatch.fnmatch(file, "*.dat"):
                    if fnmatch.fnmatch(file, "diff*.dat") is False:
                        DAT_REGISTER.append(file)

            if map_type == "delta":
                if fnmatch.fnmatch(file, "diff*.dat"):
                    DAT_REGISTER.append(file)

    DAT_REGISTER.sort()
    os.chdir(root)


# yapf: disable
def png_map(X_MIN=0.4, X_MAX=3.0, Z_MAX=0.08, SCREEN=False, ALT_MAP=False,
            BACKGROUND=False):
    # yapf: enable
    """ The general pattern for any of the maps if deposit as .png.

    As experienced, toggling between gnuplot terminal definitions about
    pngcairo and pdfcairo breaks this script's reliable action.  Instead,
    it is best to sum up the relevant per gnuplot terminal; e.g. pngcairo.

    Contrasting to pdf_map, png_map includes screen instructions.  Their
    readouts (gp_log.txt) allow to adjust map range (de/di) and cbrange
    (z_max) in the high resolution plots.  To define conditional plots
    almost applicable for both Windows, or Linux, the -e string resides in
    double quotes, as backslashes escape $3 in Linux' prelast line. """

    os.chdir("cxs_workshop")
    print("\nMap data processed:")
    for entry in DAT_REGISTER:
        print(entry)

        if entry.startswith("diff"):
            difference_map = True
        else:
            difference_map = False

        # define for the deposit file:
        input_file = str(entry)
        file_stamp = str(entry)[:-4]
        output_file = str(entry)[:-4] + str(".png")

        plot = str('gnuplot -e "')
        plot += str("input = '{}'; set output '{}'; ".format(
            input_file, output_file))

        # brief statistics per .cxs file read:
        plot += str("stats input u 3 nooutput; ")
        plot += str("z_min = sprintf('%1.6f', STATS_min); ")
        plot += str("z_low = 'zmin: ' . z_min; ")
        plot += str("z_max = sprintf('%1.6f', STATS_max); ")

        if difference_map is False:
            plot += str("z_top = 'zmax: ' . z_max; ")
        if difference_map:
            # account for the then used minus sign reporting z_min:
            plot += str("z_top = 'zmax:  ' . z_max; ")

        if SCREEN:
            # provision of a permanent STATS record:
            plot += str(
                "report = 'file: ' . input . ' ' . z_low . ' ' . z_top; ")
            plot += str("set print 'gp_report.txt' append; ")
            plot += str("print(report); ")

        # screening format definition
        #
        # A plot in reduced dimension provides a preview, allows to adjust
        # map range de/di and zmax scale in later .png and .pdf outputs.
        if SCREEN:
            plot += str("set term pngcairo size 819,819 crop font 'Arial,13' \
                enha lw 2; ")
        # non-screening format definition:
        if SCREEN is False:
            plot += str(
                "set term pngcairo size 4096,4096 crop font 'Arial,64' \
                    enha lw 10; ")

        plot += str("set grid lw 0.5; set size square; ")
        plot += str("set xtics 0.4,0.2; set ytics 0.4,0.2; ")
        plot += str("set xtics format '%2.1f'; set ytics format '%2.1f'; ")
        if SCREEN is False:
            plot += str("set label 'd_e' at graph 0.05,0.90 left front \
                font 'Arial,104'; ")
            plot += str("set label 'd_i' at graph 0.90,0.05 left front \
                font 'Arial,104'; ")
            plot += str("set label \'{}\' at graph 0.05,0.05 left front \
                font 'Arial,104' noenhanced; ".format(file_stamp))

            plot += str("set label z_top at graph 0.70,0.20 left front \
                font 'Courier,70'; ")
            plot += str("set label z_low at graph 0.70,0.17 left front \
                font 'Courier,70'; ")

        if SCREEN:
            plot += str("set label 'd_e' at graph 0.05,0.90 left front \
                font 'Arial,21'; ")
            plot += str("set label 'd_i' at graph 0.90,0.05 left front \
                font 'Arial,21'; ")
            plot += str("set label \'{}\' at graph 0.05,0.05 left front \
                font 'Arial,21' noenhanced; ".format(file_stamp))

            plot += str("set label z_top at graph 0.70,0.20 left front \
                font 'Courier,14'; ")
            plot += str("set label z_low at graph 0.70,0.17 left front \
                font 'Courier,14'; ")

        if SCREEN:
            # range indicator "standard map" (de and di [0.4,2.6] A)
            plot += str(
                "set arrow nohead from 0.4,2.6 to 2.6,2.6 dt 2 front; ")
            plot += str(
                "set arrow nohead from 2.6,0.4 to 2.6,2.6 dt 2 front; ")
            # range indicator "translated map" (de and di [0.8,3.0 A)
            plot += str(
                "set arrow nohead from 0.8,0.8 to 0.8,3.0 dt 3 front; ")
            plot += str(
                "set arrow nohead from 0.8,0.8 to 3.0,0.8 dt 3 front; ")

        plot += str("set pm3d map; \
            set pm3d depthorder; set hidden; set hidden3d; ")
        plot += str("unset key; ")

        if BACKGROUND:  # provide an optional contrast enhancement
            plot += str("set object 1 rectangle from graph 0,0 to graph 1,1 \
                fillcolor '#808080' behind; ")

        # color scheme for fingerprint map:
        if (difference_map is False) and (ALT_MAP is False):
            plot += str(RAINBOW) + str("; ")
        if (difference_map is False) and ALT_MAP:
            plot += str(
                "set palette cubehelix start 0 cycles -1. saturation 1; ")

        # color scheme for difference map:
        if (difference_map is True) and SCREEN:
            plot += str(THREE_LEVEL_NEW) + str("; ")
        if (difference_map is True) and (SCREEN is False) and (ALT_MAP is
                                                               False):
            plot += str(THREE_LEVEL_OLD) + str("; ")
        if (difference_map is True) and (SCREEN is False) and ALT_MAP:
            plot += str(BENT_THREE_LEVEL_0064) + str("; ")

        plot += str("set xrange ['{}':'{}']; ".format(X_MIN, X_MAX))
        plot += str("set yrange ['{}':'{}']; ".format(X_MIN,
                                                      X_MAX))  # square matrix

        # adjustment of cbrange parameter
        if difference_map is False:
            plot += str("set cbrange [0:'{}']; ".format(Z_MAX))
        if (difference_map is False) and SCREEN:
            # This default is suggested by P. Raiteri and A. Rohl:
            plot += str("set cbrange [0:0.08]; ")

        if difference_map:
            plot += str("set cbrange [-'{}':'{}']; ".format(Z_MAX, Z_MAX))
        if (difference_map is True) and SCREEN:
            # This default is suggested by P. Raiteri and A. Rohl:
            plot += str("set cbrange [-0.025:0.025]; ")

        # A conditional plotting / tiling, as suggested by Ethan Merritt.
        #
        # To consider only tiles with z != 0 to populate the plots reduces
        # file sizes considerably, especially in the pdf_map function.

        if platform.system().startswith("Linux"):
            # working in Linux, form #1
            plot += str("sp '{}' u 1:2:((abs(\$3) > 0) ? \$3 : NaN) w p pt 5 \
                ps 0.05 lc palette z; ".format(entry))

        if platform.system().startswith("Windows"):
            plot += str("sp '{}' u 1:2:((abs($3) > 0) ? $3 : NaN) w p pt 5 \
                ps 0.05 lc palette z; ".format(entry))

        # Re-initiate gnuplot's memory prior to work on a new data set:
        plot += str("reset session\"")

        sub.call(plot, shell=True)
    if SCREEN:
        print("\nNote: z_ranges data written into file 'gp_log.txt'.")


def pdf_map(X_MIN=0.4, X_MAX=3.0, Z_MAX=0.08, ALT_MAP=False, BACKGROUND=False):
    """ The pattern for any of gnuplot's maps if deposit as .pdf. """

    os.chdir("cxs_workshop")
    print("\nMap data processed:")
    for entry in DAT_REGISTER:
        print(entry)

        if entry.startswith("diff"):
            difference_map = True
        else:
            difference_map = False

        # define the deposit file:
        input_file = str(entry)
        file_stamp = str(entry)[:-4]
        output_file = str(entry)[:-4] + str(".pdf")

        plot = str('gnuplot -e "')
        plot += str("input = '{}'; set output '{}'; ".format(
            input_file, output_file))

        # brief statistics per .cxs file read:
        plot += str("stats input u 3 nooutput; ")
        plot += str("z_min = sprintf('%1.6f', STATS_min); ")
        plot += str("z_low = 'zmin: ' . z_min; ")
        plot += str("z_max = sprintf('%1.6f', STATS_max); ")

        if difference_map is False:
            plot += str("z_top = 'zmax: ' . z_max; ")
        if difference_map:
            # account for the then used minus sign reporting z_min:
            plot += str("z_top = 'zmax:  ' . z_max; ")

        plot += str(
            "set term pdfcairo size 6cm,6cm font 'Arial,8' enha lw 1; ")
        plot += str("set grid lw 0.5; set size square; ")
        plot += str("set xtics 0.4,0.2; set ytics 0.4,0.2; ")
        plot += str("set xtics format '%2.1f'; set ytics format '%2.1f'; ")

        plot += str("set label 'd_e' at graph 0.05,0.90 left front; ")
        plot += str("set label 'd_i' at graph 0.90,0.05 left front; ")
        plot += str(
            "set label \'{}\' at graph 0.05,0.05 left front noenhanced; ".
            format(file_stamp))
        plot += str(
            "set label z_top at graph 0.65,0.20 left front font 'Courier,6'; ")
        plot += str(
            "set label z_low at graph 0.65,0.17 left front font 'Courier,6'; ")

        plot += str("set pm3d map; \
            set pm3d depthorder; set hidden; set hidden3d; ")
        plot += str("unset key; ")

        if BACKGROUND:
            # provide an optional contrast enhancement:
            plot += str(
                "set object 1 rectangle from graph 0.0,0.0 to graph 1,1 \
                fillcolor '#808080' behind; ")

        # default color scheme for fingerprint map:
        if (difference_map is False) and (ALT_MAP is False):
            plot += str(RAINBOW) + str("; ")
        if (difference_map is False) and ALT_MAP:
            plot += str(
                "set palette cubehelix start 0 cycles -1. saturation 1; ")

        # default color scheme for difference map:
        if (difference_map is True) and (ALT_MAP is False):
            plot += str(THREE_LEVEL_OLD) + str("; ")
        if (difference_map is True) and ALT_MAP:
            plot += str(BENT_THREE_LEVEL_0064) + str("; ")

        plot += str("set xrange ['{}':'{}']; ".format(X_MIN, X_MAX))
        plot += str("set yrange ['{}':'{}']; ".format(X_MIN,
                                                      X_MAX))  # square matrix
        plot += str("set cbrange [0:'{}']; ".format(Z_MAX))
        if difference_map:
            plot += str("set cbrange ['-{}':'{}']; ".format(Z_MAX, Z_MAX))

        # conditional tiling:  (significant savings for .pdf)
        if platform.system().startswith("Linux"):
            plot += str(
                "sp '{}' u 1:2:((abs(\$3) > 0) ? \$3 : NaN) w p pt 5 ps 0.001\
            lc palette z; ".format(entry))

        if platform.system().startswith("Windows"):
            plot += str(
                "sp '{}' u 1:2:((abs($3) > 0) ? $3 : NaN) w p pt 5 ps 0.001\
            lc palette z; ".format(entry))

        # Re-initiate gnuplot prior to work on a new data set:
        plot += str("reset session \"")
        sub.call(plot, shell=True)


# yapf: disable
def plot_matplotlib(MAP_RANGE="extended", Z_MAX=0.08, SCREEN=False,
                    BACKGROUND=False, COLOR_BAR=False, FILE_TYPE="png"):
    """ Backup: matplotlib-based visualization of the computed results. """
    # yapf: enable
    try:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
        import numpy as np
    except IOError:
        print("""Additional non-standard modules are not available.
              Install first numpy and matplotlib.""")
        sys.exit()

    os.chdir("cxs_workshop")
    print("\nMap data processed:")
    for entry in DAT_REGISTER:
        print(entry)

        if entry.startswith("diff"):
            difference_map = True
        else:
            difference_map = False

        # analysis of the .dat file:
        retainer = []  # record all except the blank lines
        z_register = []  # record only the entries about z
   
        with open(entry, mode='r') as source:
            for line in source:
                if len(line.strip().split()) == 3:
                    retainer.append(line.strip())
                    z_register.append(float(line.strip().split()[2]))

        # convert the list of z into an array suitable for display:
        array_z = np.array(z_register).astype(float)

        dimension_matrix_z = int(math.sqrt(len(array_z)))
        matrix_z = array_z.reshape(dimension_matrix_z, dimension_matrix_z)

        # align orientation of the array to the one in gnuplot's plots:
        matrix_z = matrix_z.transpose()

        # adjust working to the map range selection:
        if MAP_RANGE == "standard":  # i.e., 0.40(0.01)2.60 A.
            di_start, di_end = 0.40, 2.60
            matrix_z = matrix_z[:221, :221]
        if MAP_RANGE == "translated":  # i.e., 0.80(0.01)3.00 A
            di_start, di_end = 0.80, 3.00
            matrix_z = matrix_z[40:, 40:]
        if MAP_RANGE == "extended":  # i.e., 0.40(0.01)3.00 A
            di_start, di_end = 0.40, 3.00
            matrix_z = matrix_z[:, :]

        # identify zmin and zmax
        zmin_value = str("{:7.6f}".format(float(min(z_register))))
        zmin_report = " ".join(["zmin:", zmin_value.rjust(9)])

        zmax_value = str("{:7.6f}".format(float(max(z_register))))
        zmax_report = " ".join(["zmax:", zmax_value.rjust(9)])

        # Filter out entries not sufficiently away from zero:
        np.place(array_z, abs(array_z) < 1e-8, 'nan')

        # definition about the canvas:
        fig, ax = plt.subplots()
        plt.grid()
        ax.xaxis.set_major_locator(MultipleLocator(0.20))
        ax.yaxis.set_major_locator(MultipleLocator(0.20))
        ax.grid(which='major', color='#CCCCCC', linestyle=':', lw=0.5)

        # Change minor ticks to show every 0.05 A. (0.20 A / 4 = 0.05 A):
        ax.xaxis.set_minor_locator(AutoMinorLocator(4))
        ax.yaxis.set_minor_locator(AutoMinorLocator(4))

        ax.set_aspect(1.00 / 1.00)

        # yapf: disable
        # permanent decorum:
        plt.text(0.05, 0.90, r'$d_e$', transform=ax.transAxes)
        plt.text(0.90, 0.05, r'$d_i$', transform=ax.transAxes)

        bbox_props = dict(boxstyle="square", fc='white', ec='white',
                          lw=1, pad=0.1)
        plt.text(0.05, 0.05, r'{}'.format(entry[:-4]), bbox=bbox_props,
                 transform=ax.transAxes)
        plt.text(0.70, 0.20, r'{}'.format(zmax_report), family="monospace",
                 size="7", bbox=bbox_props, transform=ax.transAxes)
        plt.text(0.70, 0.17, r'{}'.format(zmin_report), family="monospace",
                 size="7", bbox=bbox_props, transform=ax.transAxes)

        if SCREEN:
            # indicator standard map range, dashed line:
            plt.plot([0.40, 2.60], [2.60, 2.60], '--', color='black')
            plt.plot([2.60, 2.60], [0.40, 2.60], '--', color='black')

            # indicator translated map range, dotted line:
            plt.plot([0.80, 0.80], [0.80, 3.00], ':', color='black')
            plt.plot([0.80, 3.00], [0.80, 0.80], ':', color='black')

        # the permanent records:
        # fixed z-ranges with values stipulated in fingerprint.f90.
        if SCREEN:
            if BACKGROUND:
                ax.set_facecolor("#808080")  # gray background

            if difference_map:
                plt.imshow(matrix_z, extent=[
                    di_start, di_end, di_start, di_end],
                           origin='lower', cmap='RdBu_r', aspect='equal',
                           interpolation='None', filternorm='False',
                           vmin=-0.025, vmax=0.025, zorder=15, resample=True)

            if difference_map is False:
                plt.imshow(matrix_z, extent=[
                    di_start, di_end, di_start, di_end],
                           origin='lower', cmap='cubehelix', aspect='equal',
                           interpolation='None', filternorm='False',
                           vmin=0.0, vmax=0.08, zorder=15, resample=True)

            ax.set_facecolor("#808080")  # gray background
            plt.colorbar()
            output_file = ''.join([entry[:-4], '.png'])
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            plt.close(fig)

        # adjustable z-scaling, high quality visualizations>
        if (SCREEN is False) and (FILE_TYPE == "png"):
            if BACKGROUND:
                ax.set_facecolor("#808080")  # gray background

            if difference_map:
                print("zmax: {}".format(Z_MAX))
                plt.imshow(matrix_z, extent=[
                    di_start, di_end, di_start, di_end],
                           origin='lower', cmap='RdBu_r', aspect='equal',
                           interpolation='None', filternorm='False',
                           vmin=-Z_MAX, vmax=Z_MAX, zorder=15, resample=True)

            if difference_map is False:
                plt.imshow(matrix_z, extent=[
                    di_start, di_end, di_start, di_end],
                           origin='lower', cmap='cubehelix', aspect='equal',
                           interpolation='None', filternorm='False',
                           vmin=0.0, vmax=Z_MAX, zorder=15, resample=True)
            if COLOR_BAR:
                plt.colorbar()
            output_file = ''.join([entry[:-4], '.png'])
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close(fig)

        if (SCREEN is False) and (FILE_TYPE == "pdf"):
            if BACKGROUND:
                ax.set_facecolor("#808080")  # gray background

            if difference_map:
                plt.imshow(matrix_z, extent=[
                    di_start, di_end, di_start, di_end],
                           origin='lower', cmap='RdBu_r', aspect='equal',
                           interpolation='None', filternorm='False',
                           vmin=-Z_MAX, vmax=Z_MAX, zorder=15, resample=True)

            if difference_map is False:
                plt.imshow(matrix_z, extent=[
                    di_start, di_end, di_start, di_end],
                           origin='lower', cmap='cubehelix', aspect='equal',
                           interpolation='None', filternorm='False',
                           vmin=0.0, vmax=Z_MAX, zorder=15, resample=True)
            if COLOR_BAR:
                plt.colorbar()
            output_file = ''.join([entry[:-4], '.pdf'])
            plt.savefig(output_file, bbox_inches='tight')
            plt.close(fig)
# End of section C, Display.


# Section D, Arguments / argparse section:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-l",
        "--list",
        help="List accessible .cxs files.  No further file processing.",
        action="store_true")

    parser.add_argument(
        "-j",
        "--join",
        help="""Copy .cxs into a dedicated sub-folder.  File names will be
        truncated at first underscore character.""",
        action="store_true")

    parser.add_argument(
        "-n",
        "--normalize_py",
        help="""Normalized fingerprints with Python and fingerprint_Kahan.py.
        Files in pattern of 'example.cxs' yield 'example.dat'.""",
        action="store_true")

    parser.add_argument(
        "-N",
        "--normalize_f",
        help="Normalized fingerprints by Fortran and fingerprint.f90.",
        action="store_true")

    parser.add_argument(
        "-c",
        "--compare_py",
        help="""Difference maps, computed by Python.  Output will be written
        into diff*.dat files.""",
        action="store_true")

    parser.add_argument(
        "-C",
        "--compare_c",
        help="Compute the differences maps with diff_finger.c. ",
        action="store_true")

    parser.add_argument(
        "-r",
        "--ruby_number_py",
        help="Compute the difference number per diff*.dat by Python.",
        action="store_true")

    parser.add_argument(
        "-R",
        "--ruby_number_r",
        help="Compute the difference number with the ruby script.",
        action="store_true")

    parser.add_argument(
        "-o",
        "--overview",
        action="store_true",
        help="""Preview fingerprint and difference maps as low resolution
        .png to adjust de/di map range (s, t, e) and z-scaling in the high
        quality maps (gnuplot).""")

    # Either .png or .pdf of fingerprint maps (in high resolution):
    group_fp = parser.add_mutually_exclusive_group()
    group_fp.add_argument(
        "--fpng",
        type=str,
        choices=["s", "t", "e"],
        help="""2D fingerprint maps in either map range [s]tandard,
        [t]ranslated, or [e]xtended as high quality .png.""")

    group_fp.add_argument(
        "--fpdf",
        type=str,
        choices=["s", "t", "e"],
        help="2D fingerprint maps in either map range as .pdf.")

    # Either .png or .pdf of difference maps (in high resolution):
    group_delta = parser.add_mutually_exclusive_group()
    group_delta.add_argument(
        "--dpng",
        type=str,
        choices=["s", "t", "e"],
        help="Difference maps of either map range as high res. .png.")

    group_delta.add_argument(
        "--dpdf",
        type=str,
        choices=["s", "t", "e"],
        help="Difference maps of either map range as .pdf.")

    parser.add_argument(
        "-O",
        "--overview_py",
        action="store_true",
        help="Survey .png generation with Python matplotlib.")

    # Either .png fingerprints by matplotlib
    group_fp = parser.add_mutually_exclusive_group()
    group_fp.add_argument(
        "--Fpng",
        type=str,
        choices=["s", "t", "e"],
        help="2D fingerprint .png of either map range, matplotlib.")

    # Either .pdf fingerprints by matplotlib
    group_fp = parser.add_mutually_exclusive_group()
    group_fp.add_argument(
        "--Fpdf",
        type=str,
        choices=["s", "t", "e"],
        help="2D fingerprint .pdf of either map range, matplotlib.")

    # Either .png difference maps by matplotlib
    group_fp = parser.add_mutually_exclusive_group()
    group_fp.add_argument(
        "--Dpng",
        type=str,
        choices=["s", "t", "e"],
        help="2D difference map .png, matplotlib.")

    # Either .pdf difference maps by matplotlib
    group_fp = parser.add_mutually_exclusive_group()
    group_fp.add_argument(
        "--Dpdf",
        type=str,
        choices=["s", "t", "e"],
        help="2D difference map .pdf, matplotlib.")

    # adjustment of zmax scaling in high resolution maps:
    parser.add_argument(
        "--zmax",
        type=float,
        help="""Use an other scaling than zmax = 0.08 (fingerprints) or
        |zmax| = 0.025 (difference maps) in high quality maps.""")

    parser.add_argument(
        "-g",
        "--bg",
        action="store_true",
        help="Add a gray background to the high quality maps.")

    parser.add_argument(
        "-a",
        "--alternate",
        action="store_true",
        help="Use the alternate palette definitions.")

    parser.add_argument(
        "-b",
        "--color_bar",
        action="store_true",
        help="""Add display of the color bar (default: off).  This Boolean
        is available only for plots by matplotlib.""")

    args = parser.parse_args()
    # yapf: enable

    if args.list:
        file_listing()  # list accessible .cxs files
    if args.join:
        assemble_cxs()  # copy .cxs into one place
        rename_cxs()  # truncate file names at underscore sign
    if args.normalize_py:  # fingerprint generation, Python
        fingerprint_python()
    if args.normalize_f:  # fingerprint generation, Fortran
        compile_f90()
        shuttle_f90()
        fingerprint_fortran()
    if args.compare_py:  # difference map generation, Python
        difference_maps_python()
    if args.compare_c:  # difference map generation, C
        compile_c()
        shuttle_c()
        difference_maps_c()
    if args.ruby_number_py:  # difference number by Python
        difference_number_python()
    if args.ruby_number_r:  # difference number by the ruby script
        shuttle_ruby_script()
        difference_number_ruby()
    if args.overview:  # quick survey with gnuplot
        search_dat(SCREEN=True)
        png_map(SCREEN=True)
    if args.overview_py:  # quick survey by matplotlib
        search_dat(SCREEN=True)
        plot_matplotlib(SCREEN=True)
    if args.bg:
        BACKGROUND = True  # an option: a neutral gray background
    if args.color_bar:
        COLOR_BAR = True  # add a color bar (matplotlib only)
    if args.alternate:
        ALT_MAP = True  # toggle to alternative color palettes

    # options fingerprints, .png; adjustable map range [s]tandard,
    # [t]ranslated, [e]extended -- mandatory; adjustable zmax, alternate
    # color palette, and background contrast enhancement -- optional.
    if args.fpng in ["s", "t", "e"]:  # fingerprints (gnuplot), png.
        if args.fpng == "s":
            X_MIN, X_MAX = 0.4, 2.6
        if args.fpng == "t":
            X_MIN, X_MAX = 0.8, 3.0
        if args.fpng == "e":
            X_MIN, X_MAX = 0.4, 3.0
        if args.zmax is None:
            Z_MAX = 0.08
        else:
            Z_MAX = args.zmax
        SCREEN = False
        ALT_MAP = args.alternate
        BACKGROUND = args.bg
        search_dat(map_type="fingerprint")
        png_map(X_MIN, X_MAX, Z_MAX, SCREEN, ALT_MAP, BACKGROUND)

    if args.fpdf in ["s", "t", "e"]:  # fingerprints, gnuplot, .pdf.
        if args.fpdf == "s":
            X_MIN, X_MAX = 0.4, 2.6
        if args.fpdf == "t":
            X_MIN, X_MAX = 0.8, 3.0
        if args.fpdf == "e":
            X_MIN, X_MAX = 0.4, 3.0
        if args.zmax is None:
            Z_MAX = 0.08
        else:
            Z_MAX = args.zmax
        ALT_MAP = args.alternate
        BACKGROUND = args.bg
        search_dat(map_type="fingerprint")
        pdf_map(X_MIN, X_MAX, Z_MAX, ALT_MAP, BACKGROUND)

    if args.dpng in ["s", "t", "e"]:  # difference maps, gnuplot, .png.
        if args.dpng == "s":
            X_MIN, X_MAX = 0.4, 2.6
        if args.dpng == "t":
            X_MIN, X_MAX = 0.8, 3.0
        if args.dpng == "e":
            X_MIN, X_MAX = 0.4, 3.0
        if args.zmax is None:
            Z_MAX = 0.025
        else:
            Z_MAX = args.zmax
        SCREEN = False
        ALT_MAP = args.alternate
        BACKGROUND = args.bg
        search_dat(map_type="delta")
        png_map(X_MIN, X_MAX, Z_MAX, SCREEN, ALT_MAP, BACKGROUND)

    if args.dpdf in ["s", "t", "e"]:  # difference maps, gnuplot, .pdf.
        if args.dpdf == "s":
            X_MIN, X_MAX = 0.4, 2.6
        if args.dpdf == "t":
            X_MIN, X_MAX = 0.8, 3.0
        if args.dpdf == "e":
            X_MIN, X_MAX = 0.4, 3.0
        if args.zmax is None:
            Z_MAX = 0.025
        else:
            Z_MAX = args.zmax
        ALT_MAP = args.alternate
        BACKGROUND = args.bg
        search_dat(map_type="delta")
        pdf_map(X_MIN, X_MAX, Z_MAX, ALT_MAP, BACKGROUND)

    if args.Fpng in ["s", "t", "e"]:  # fingerprint, Python, .png.
        search_dat(map_type="fingerprint")
        if args.Fpng == "s":
            MAP_RANGE = "standard"
        if args.Fpng == "t":
            MAP_RANGE = "translated"
        if args.Fpng == "e":
            MAP_RANGE = "extended"
        if args.zmax is None:
            Z_MAX = 0.025
        else:
            Z_MAX = args.zmax
        SCREEN = False
        BACKGROUND = args.bg
        COLOR_BAR = args.color_bar
        FILE_TYPE = "png"
        plot_matplotlib(MAP_RANGE, Z_MAX, SCREEN, BACKGROUND, COLOR_BAR,
                        FILE_TYPE)

    if args.Dpng in ["s", "t", "e"]:  # difference maps, Python, .png.
        search_dat(map_type="delta")
        if args.Dpng == "s":
            MAP_RANGE = "standard"
        if args.Dpng == "t":
            MAP_RANGE = "translated"
        if args.Dpng == "e":
            MAP_RANGE = "extended"
        if args.zmax is None:
            Z_MAX = 0.025
        else:
            Z_MAX = args.zmax
        SCREEN = False
        BACKGROUND = args.bg
        COLOR_BAR = args.color_bar
        FILE_TYPE = "png"
        plot_matplotlib(MAP_RANGE, Z_MAX, SCREEN, BACKGROUND, COLOR_BAR,
                        FILE_TYPE)

    if args.Fpdf in ["s", "t", "e"]:  # fingerprints, Python, pdf.
        search_dat(map_type="fingerprint")
        if args.Fpdf == "s":
            MAP_RANGE = "standard"
        if args.Fpdf == "t":
            MAP_RANGE = "translated"
        if args.Fpdf == "e":
            MAP_RANGE = "extended"
        if args.zmax is None:
            Z_MAX = 0.025
        else:
            Z_MAX = args.zmax
        SCREEN = False
        BACKGROUND = args.bg
        COLOR_BAR = args.color_bar
        FILE_TYPE = "pdf"
        plot_matplotlib(MAP_RANGE, Z_MAX, SCREEN, BACKGROUND, COLOR_BAR,
                        FILE_TYPE)

    if args.Dpdf in ["s", "t", "e"]:  # difference maps, Python, pdf.
        search_dat(map_type="delta")
        if args.Dpdf == "s":
            MAP_RANGE = "standard"
        if args.Dpdf == "t":
            MAP_RANGE = "translated"
        if args.Dpdf == "e":
            MAP_RANGE = "extended"
        if args.zmax is None:
            Z_MAX = 0.025
        else:
            Z_MAX = args.zmax
        SCREEN = False
        BACKGROUND = args.bg
        COLOR_BAR = args.color_bar
        FILE_TYPE = "pdf"
        plot_matplotlib(MAP_RANGE, Z_MAX, SCREEN, BACKGROUND, COLOR_BAR,
                        FILE_TYPE)
 
