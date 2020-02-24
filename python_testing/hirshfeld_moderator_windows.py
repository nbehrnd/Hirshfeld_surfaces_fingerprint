#!/usr/bin/env python3

# name:    hirshfeld_moderator_windows.py
# author:  nbehrnd@yahoo.com
# license: GPL version 2
# date:    2020-01-06 (YYYY-MM-DD)
# edit:    2020-02-24 (YYYY-MM-DD)
#
""" Simplified moderator script for the DeltaHirshfeld analysis.

The addition of 'windows' to this script's name only reflects some initial
difficulties to access both Fortran and C compiler, ruby, and eventually
moderating Python on one and the same computer.  Different to its brother,
hirshfeld_moderator.py, the Hirshfeld analysis with this script requires
only a working installation of Python and Fortran for the computations.

Note that the eased, now almost unified, Python-based access to this type
of scrutiny may equate to a drop in computational performance compared of
the C-based comparison of already normalized fingerprints.  This is why a)
hirshfeld_moderator.py still is provided side-by-side to this script.
This is b) why the task of generation of normalized 2D Hirshfeld surface
fingerprints still is relayed to the Fortran script fingerprint.f90, which
is the sole other file beside this script (hirshfeld_moderator_windows.py)
you need to put into the folder of .cxs to analyze.

In the course of running the script, fingerprint.f90 needs to be compiled.
The script attempts to do this on the fly with either gfortran, or gcc,
both freely available.  It is optional to visualize the maps computed from
within this script, relaying to gnuplot (www.gnuplot.info).

In case of using Windows as hosting operational system, add Python, your
Fortran compiler (gfortran or gcc), and gnuplot -- if you want to display
the results on the fly -- to the system's PATH variable.

This moderator script offers the same functions as its sibling and equally
is launched from the terminal, e.g. by

python hirshfeld_moderator_windows.py -h

Hints how to use the program are provided both in hirshfeld_moderator.py,
and the README.org.

source WinPython: http://winpython.github.io/
source TortoiseGit:  https://tortoisegit.org
source gnuplot: http://www.gnuplot.info
"""

import argparse
from decimal import Decimal
import fnmatch
import math
import os
import platform
import shutil
import subprocess as sub
import sys

global root
root = os.getcwd()


# Section 1, tool generation
def create_workshop():
    """ Create a dedicated sub-folder for copies of .cxs to work on """
    # An already existing 'cxs_workshop' folder will be deleted.
    for element in os.listdir("."):
        test = os.path.isdir(os.path.join(os.getcwd(), element))
        if test is True:
            if fnmatch.fnmatch(element, "cxs_workshop"):
                try:
                    shutil.rmtree(element)
                except IOError:
                    print("Please remove 'csx_workshop' manually.")
                    sys.exit(0)

    # Creation of a workshop.
    try:
        os.mkdir("cxs_workshop")
    except:
        print("\nProblem to create sub-folder 'cxs_workshop'.")
        print("Without alteration of data, the script closes now.\n")
        sys.exit(0)


def listing(extension="*.cxs", copy=False):
    """ List or copy .cxs files residing in the same project folder.

    File listing is the default.  For file renaming, see rename_cxs(). """
    file_register = []
    counter = 0

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, extension):
            counter += 1
            print("{}\t{}".format(counter, file))
            file_register.append(file)

            if copy is True:
                try:
                    shutil.copy(file, "cxs_workshop")
                except OSError:
                    print("{} wasn't copied to 'cxs_workshop'.".format(file))
    print("\n{} files of type {} were identified.\n".format(
        len(file_register), extension))


def file_crawl(copy=False):
    """ Retrieve / copy .cxs by means of an os.walk. """
    counter = 0
    cxs_to_copy = []

    for folder, subfolders, files in os.walk(root):
        try:
            for subfolder in subfolders:
                os.chdir(subfolder)
                for file in os.listdir("."):
                    if file.endswith(".cxs"):
                        cxs_to_copy.append(os.path.abspath(file))
                        counter += 1
                        print("{}\t{}".format(counter, file))
                os.chdir(root)
        except:
            continue

    if copy is True:  # not considered execpt on explicit consent.
        for entry in cxs_to_copy:
            try:
                shutil.copy(entry,
                            os.path.join(root, "cxs_workshop",
                                         os.path.basename(entry)))
            except:
                print("Not copied to cxs_workshop: {}".format(entry))


def rename_cxs():
    """ Truncate file names of CrystalExplorer surface files.

    CrystalExplorer provides Hirshfeld surfaces named in a pattern of
    'example_example.cxs'.  Work is easier if their file name is truncated
    to 'example.cxs'.  This is applied only to copies of .cxs. """
    os.chdir("cxs_workshop")

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.cxs"):
            if str("_") in file:
                new_filename = str(file.split("_")[0]) + str(".cxs")
                try:
                    shutil.move(file, new_filename)
                except OSError:
                    print("Renaming {} failed.".format(file))

    os.chdir(root)


def compile_f90():
    """ Compile fingerprint.f90 with gfortran (default), or gcc. """
    compile_gfo_f90 = str("gfortran fingerprint.f90 -o fingerprint.x")
    compile_gcc_f90 = str("gcc fingerprint.f90 -o fingerprint.x")
    print("Compilation of fingerprint.f90 with either gfortran or gcc.")
    try:
        sub.call(compile_gfo_f90, shell=True)
        print("fingerprint.f90 was compiled successfully (gfortran).")
    except IOError:
        print("Compilation attempt with gfortran failed.")
        print("Independent compilation attempt with gcc.")
        try:
            sub.call(compile_gcc_f90, shell=True)
            print("fingerprint.f90 was compiled successfully (gcc).")
        except IOError:
            print("Compilation attempt with gcc equally failed.")
            print("Maybe fingerprint.f90 is not in the project folder.")
            print("Equally ensure installation of gfortran or gcc.")
            sys.exit(0)


def shuttle_f90():
    """ Shuttle the executable of fingerprint.f90 into the workshop. """
    try:
        shutil.copy("fingerprint.x", "cxs_workshop")
    except IOError:
        print("Error to copy Fortran .f90 executable to 'cxs_workshop'.")
        sys.exit(0)

    # space cleaning, root folder of the project:
    try:
        os.remove("fingerprint.x")
    except IOError:
        pass


def normalize_cxs():
    """ Generate extended normalized 2D fingerprint .dat of all .cxs """
    print("\nNormalization of .cxs files yielding 2D fingerprint .dat:")
    os.chdir("cxs_workshop")

    register = []
    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.cxs"):
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

    os.remove("fingerprint.x")
    os.chdir(root)
    print("\nNormalization of .cxs files is completed.")


def numpy_independent_differences():
    """ A computation of the fingerprints without numpy. """
    # identify the files to work with:
    os.chdir("cxs_workshop")
    diff_register = []

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.dat") and \
                (fnmatch.fnmatch(file, "diff*.dat") is False):
            diff_register.append(file)
    diff_register.sort()

    # compare the normalized 2D Hirshfeld surface maps
    while len(diff_register) > 1:
        for entry in diff_register[1:]:
            reference_file = diff_register[0]
            probe_file = entry
            print("Comparison {} ./. {}.".format(reference_file, probe_file))

            reference_map = []
            probe_map = []

            f = open(reference_file, mode="r")
            reference_map = f.readlines()
            f.close()

            f = open(probe_file, mode="r")
            probe_map = f.readlines()
            f.close()

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
                for entry in difference_map[:-1]:
                    newfile.write("{}\n".format(entry.strip()))
        del diff_register[0]
    os.chdir(root)


def ruby_number():
    """ Add the absolute values of differences per difference map. """
    # identification of the files to work with:
    os.chdir("cxs_workshop")
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

    os.chdir(root)


# Section 1b, Definition of non-trivial color palettes which are not
# part of gnuplot's built-in defaults, but eventually used.

# The CrystalExplorer like rainbow about 2D fingerprints.
#
# This is a verbatim copy from fingerprint.f90, set up and shared by Paolo
# Raiteri and Andrew Rohl.  Like many other rainbow / jet-like palettes,
# there are possible perceptual problems with this, e.g. for an output on
# gray-scale, and for some types of color blindness.  (See, for example,
# Kenneth Moreland's recommendations about this topic.)   Which is why
# gnuplot's built-in palette 'cubehelix' (accessible in this script's -a /
# --alt toggle) is recommended to be used instead of 'rainbow'.
rainbow = str("""set palette defined (0  1.0 1.0 1.0, \
               0.00001  0.0 0.0 1.0, \
               1  0.0 0.5 1.0, \
               2  0.0 1.0 1.0, \
               3  0.5 1.0 0.5, \
               4  1.0 1.0 0.0, \
               5  1.0 0.5 0.0, \
               6  1.0 0.0 0.0 ) """)

# The classical three-level blue-white-red palette
#
# This equally is defined in the code basis by Andrew Rohl and Paolo Raiteri.
three_level_old = str('set palette defined (-1 "blue", 0 "white", 1 "red")')
#
# Because its neuter level "white" is indiscernible from "paper white",
# the screening mode uses the softer three-level palette (below, transient
# with neuter gray) instead.

# The softer three-level palette:
#
# Used by default for the screening .png to faciliate discern of tiles with
# z close to zero (otherwise print white) from the paper-white background.
# A heavily constrained implementation of Kenneth Morelands suggestions
# for diverging color palettes.  If not screening, you may either enhance the
# contrast to the background (toggle -g) or use the alternative (toggle -a)
# bent-cool-warm palette by Kenneth Moreland.
three_level_new = str(
    'set palette defined (-1 "blue", 0 "light-gray", 1 "red")')

# The better diverging palette for the difference maps.
#
# This is based on Kenneth Moreland's suggested color palette
# "bent-cool-warm-table-float-0064.csv" [1] converted by csv2plt.py [2]
# into a format accessible to gnuplot.  From a perceptual perspective,
# it improves the detail of representation about the difference map
# beyond what the classical three level blue_white_red palette, or the
# already improved blue_light-gray_red palette offer.
#
# [1]
# https://github.com/kennethmoreland-com/kennethmoreland-com.github.io/blob/master/color-advice/bent-cool-warm/bent-cool-warm-table-float-0064.csv,
#     edit by Jan 17, 2016; md5sum f31b220283836b3ea61de2a5e586c807.
#
# [2] https://github.com/nbehrnd/moreland-gnuplot-palettes/blob/master/tools/csv2plt.py
#     edit by Dec 4, 2019; md5sum c9262530c06b7f364aa716131ac46c3d.
bent_three_level_0064 = str("""set palette defined (\
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


# section 2, joining unit operations:
def file_listing():
    """ Survey of the .cxs files eventually to work with. """
    print("\nListing of the .cxs files accessible.  Press either")
    print("[0]  to leave the script.")
    print("[1]  .cxs files reside in the same folder as this script.")
    print("[2]  .cxs files reside in sub-folders to the current folder.")
    print("")

    try:
        listing_choice = int(input())
    except IOError:
        sys.exit(0)
    if listing_choice == 0:
        print("\n Script's execution was ended.\n")
        sys.exit(0)
    if listing_choice == 1:
        print("")
        listing()
    if listing_choice == 2:
        print("")
        file_crawl()


def assemble_cxs():
    """ Bring the .cxs all into one dedicated sub-folder / workshop. """
    print("\nCopies of .cxs files will be brought into 'cxs_workshop'.")
    print("Any 'cxs_workshop' folder of previous runs will be erased.")
    print("File names of .cxs copies are truncated at the underscore.")
    print("")
    print("[0]  to leave the script.")
    print("[1]  .cxs files reside in the same folder as this script.")
    print("[2]  .cxs files reside in sub-folders to the current folder.")

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
        listing(copy=True)
    if assemble_choice == 2:
        print("")
        create_workshop()
        file_crawl(copy=True)
    os.chdir(root)


def search_dat(map_type="delta", screen="off"):
    """ Search for .dat files, assume difference maps of typical interest.

    Two cases: fingerprints (type fingerprint, files ending on *.dat), or
    difference maps (map type delta, files in pattern of diff*.dat). """
    global dat_register
    dat_register = []
    os.chdir("cxs_workshop")

    # indiscriminate register population (i.e., screening):
    if screen == "on":
        for file in os.listdir("."):
            if fnmatch.fnmatch(file, "*.dat"):
                dat_register.append(file)

    # discriminate register population (i.e., either map type):
    if screen == "off":
        for file in os.listdir("."):
            # branch about fingerprint .dat:
            if map_type == "fingerprint":
                if fnmatch.fnmatch(file, "*.dat"):
                    if fnmatch.fnmatch(file, "diff*.dat") is False:
                        dat_register.append(file)

            # branch about difference map .dat:
            if map_type == "delta":
                if fnmatch.fnmatch(file, "diff*.dat"):
                    dat_register.append(file)

    dat_register.sort()
    os.chdir(root)


def png_map(xmin=0.4, xmax=3.0, zmax=0.08, screen="off", alt=0, bg=0):
    """ The general pattern for any of the maps if deposit as .png.

    As experienced, toggling between gnuplot terminal definitions about
    pngcairo and pdfcairo breaks this script's reliable action.  Instead,
    it is best to sum up the relevant per gnuplot terminal; e.g. pngcairo.

    Contrasting to pdf_map, png_map includes instructions to screen the
    two map types.  Use this to adjust map range (de/di) and cbrange
    (z_max) in the high resolution plots. """

    os.chdir("cxs_workshop")
    print("\nMap data processed:")
    for entry in dat_register:
        print(entry)

        if entry.startswith("diff"):
            difference_map = True
        else:
            difference_map = False

        # define for the deposit file:
        input_file = str(entry)
        file_stamp = str(entry)[:-4]
        output_file = str(entry)[:-4] + str(".png")

        pl = str("gnuplot -e '")
        pl += str('input = "{}"; '.format(input_file))
        pl += str('set output "{}"; '.format(output_file))

        # brief statistics per .cxs file read:
        pl += str('stats input u 3 nooutput; ')
        pl += str('z_min = sprintf("%1.6f", STATS_min); ')
        pl += str('z_low = "zmin: " . z_min; ')
        pl += str('z_max = sprintf("%1.6f", STATS_max); ')

        if difference_map is False:
            pl += str('z_top = "zmax: " . z_max; ')
        if difference_map is True:
            # account for the then used minus sign reporting z_min:
            pl += str('z_top = "zmax:  " . z_max; ')

        if screen == "on":
            # provision of a a permanent STATS record:
            pl += str(
                'report = "file: " . input . " " . z_low . " " . z_top; ')
            pl += str('set print "gp_report.txt" append; ')
            pl += str('print(report); ')

        # screening format definition
        #
        # A plot in reduced dimension suffices to provide a preview,
        # equally allows adjustment map range de/di and z-scaling in
        # subsequent high resolution .png and .pdf output.
        if screen == "on":
            pl += str('set term pngcairo size 819,819 crop font "Arial,13" \
                enha lw 2; ')
        # non-screening format definition:
        if screen == "off":
            pl += str('set term pngcairo size 4096,4096 crop font "Arial,64" \
                    enha lw 10; ')

        pl += str('set grid lw 0.5; set size square; ')
        pl += str('set xtics 0.4,0.2; set ytics 0.4,0.2; ')
        pl += str('set xtics format "%2.1f"; set ytics format "%2.1f"; ')
        if screen == "off":
            pl += str('set label "d_e" at graph 0.05,0.90 left front \
                font "Arial,104"; ')
            pl += str('set label "d_i" at graph 0.90,0.05 left front \
                font "Arial,104"; ')
            pl += str('set label "{}" at graph 0.05,0.05 left front \
                font "Arial,104" noenhanced; '.format(file_stamp))

            pl += str('set label z_top at graph 0.70,0.20 left front \
                font "Courier,70"; ')
            pl += str('set label z_low at graph 0.70,0.17 left front \
                font "Courier,70"; ')

        if screen == "on":
            pl += str('set label "d_e" at graph 0.05,0.90 left front \
                font "Arial,21"; ')
            pl += str('set label "d_i" at graph 0.90,0.05 left front \
                font "Arial,21"; ')
            pl += str('set label "{}" at graph 0.05,0.05 left front \
                font "Arial,21" noenhanced; '.format(file_stamp))

            pl += str('set label z_top at graph 0.70,0.20 left front \
                font "Courier,14"; ')
            pl += str('set label z_low at graph 0.70,0.17 left front \
                font "Courier,14"; ')

        if screen == "on":
            # range indicator "standard map" (de and di [0.4,2.6] A)
            pl += str('set arrow nohead from 0.4,2.6 to 2.6,2.6 dt 2 front; ')
            pl += str('set arrow nohead from 2.6,0.4 to 2.6,2.6 dt 2 front; ')
            # range indicator "translated map" (de and di [0.8,3.0 A)
            pl += str('set arrow nohead from 0.8,0.8 to 0.8,3.0 dt 3 front; ')
            pl += str('set arrow nohead from 0.8,0.8 to 3.0,0.8 dt 3 front; ')

        pl += str('set pm3d map; \
            set pm3d depthorder; set hidden; set hidden3d; ')
        pl += str('unset key; ')

        if bg == 1:  # provide an optional contrast enhancement
            pl += str('set object 1 rectangle from graph 0,0 to graph 1,1 \
                fillcolor "#808080" behind; ')

        # color scheme for fingerprint map:
        if (difference_map is False) and (alt == 0):
            pl += str(rainbow) + str('; ')
        if (difference_map is False) and (alt == 1):
            pl += str(
                'set palette cubehelix start 0 cycles -1. saturation 1; ')

        # color scheme for difference map:
        if (difference_map is True) and (screen == "on"):
            pl += str(three_level_new) + str('; ')
        if (difference_map is True) and (screen == "off") and (alt == 0):
            pl += str(three_level_old) + str('; ')
        if (difference_map is True) and (screen == "off") and (alt == 1):
            pl += str(bent_three_level_0064) + str('; ')

        pl += str('set xrange ["{}":"{}"]; '.format(xmin, xmax))
        pl += str('set yrange ["{}":"{}"]; '.format(xmin,
                                                    xmax))  # square matrix

        # adjustment of cbrange parameter
        if difference_map is False:
            pl += str('set cbrange [0:"{}"]; '.format(zmax))
        if (difference_map is False) and (screen == "on"):
            # This default is suggested by P. Raiteri and A. Rohl:
            pl += str('set cbrange [0:0.08]; ')

        if difference_map is True:
            pl += str('set cbrange [-"{}":"{}"]; '.format(zmax, zmax))
        if (difference_map is True) and (screen == "on"):
            # This default is suggested by P. Raiteri and A. Rohl:
            pl += str('set cbrange [-0.025:0.025]; ')

        # A conditional plotting / tiling, as suggested by Ethan Merritt.
        #
        # To consider only tiles with z != 0 to populate the plots may
        # save considerably file size.  This is especially experienced
        # while working with the analogue pdf_map function.
        pl += str('sp "{}" u 1:2:((abs($3) > 0) ? $3 : NaN) w p pt 5 \
            ps 0.05 lc palette z; '.format(entry))

        # Re-initiate gnuplot's memory prior to work on a new data set:
        pl += str('reset session ') + str("'")
        sub.call(pl, shell=True)


def pdf_map(xmin=0.4, xmax=3.0, zmax=0.08, screen="off", alt=0, bg=0):
    """ The general pattern for any of the maps if deposit as .pdf.

    The design pattern follows the instructions in png_map. """

    os.chdir("cxs_workshop")
    print("\nMap data processed:")
    for entry in dat_register:
        print(entry)

        if entry.startswith("diff"):
            difference_map = True
        else:
            difference_map = False

        # define the deposit file:
        input_file = str(entry)
        file_stamp = str(entry)[:-4]
        output_file = str(entry)[:-4] + str(".pdf")

        pl = str("gnuplot -e '")
        pl += str('input = "{}" ; '.format(input_file))
        pl += str('set output "{}"; '.format(output_file))

        # brief statistics per .cxs file read:
        pl += str('stats input u 3 nooutput; ')
        pl += str('z_min = sprintf("%1.6f", STATS_min); ')
        pl += str('z_low = "zmin: " . z_min; ')
        pl += str('z_max = sprintf("%1.6f", STATS_max); ')

        if difference_map is False:
            pl += str('z_top = "zmax: " . z_max; ')
        if difference_map is True:
            # account for the then used minus sign reporting z_min:
            pl += str('z_top = "zmax:  " . z_max; ')

        pl += str('set term pdfcairo size 6cm,6cm font "Arial,8" enha lw 1; ')
        pl += str('set grid lw 0.5; set size square; ')
        pl += str('set xtics 0.4,0.2; set ytics 0.4,0.2; ')
        pl += str('set xtics format "%2.1f"; set ytics format "%2.1f"; ')

        pl += str('set label "d_e" at graph 0.05,0.90 left front; ')
        pl += str('set label "d_i" at graph 0.90,0.05 left front; ')
        pl += str(
            'set label "{}" at graph 0.05,0.05 left front noenhanced; '.format(
                file_stamp))
        pl += str(
            'set label z_top at graph 0.65,0.20 left front font "Courier,7"; ')
        pl += str(
            'set label z_low at graph 0.65,0.17 left front font "Courier,7"; ')

        pl += str('set pm3d map; \
            set pm3d depthorder; set hidden; set hidden3d; ')
        pl += str('unset key; ')

        if bg == 1:
            # provide an optional contrast enhancement:
            pl += str('set object 1 rectangle from graph 0.0,0.0 to graph 1,1 \
                fillcolor "#808080" behind; ')

        # default color scheme for fingerprint map:
        if (difference_map is False) and (alt == 0):
            pl += str(rainbow) + str('; ')
        if (difference_map is False) and (alt == 1):
            pl += str(
                'set palette cubehelix start 0 cycles -1. saturation 1; ')

        # default color scheme for difference map:
        if (difference_map is True) and (alt == 0):
            pl += str(three_level_old) + str('; ')
        if (difference_map is True) and (alt == 1):
            pl += str(bent_three_level_0064) + str('; ')

        pl += str('set xrange ["{}":"{}"]; '.format(xmin, xmax))
        pl += str('set yrange ["{}":"{}"]; '.format(xmin,
                                                    xmax))  # square matrix
        pl += str('set cbrange [0:"{}"]; '.format(zmax))
        if difference_map is True:
            pl += str('set cbrange ["-{}":"{}"]; '.format(zmax, zmax))

        # conditional tiling:  (significant savings for .pdf)
        pl += str('sp "{}" u 1:2:((abs($3) > 0) ? $3:NaN) w p pt 5 ps 0.001\
            lc palette z; '.format(entry))

        # Re-initiate gnuplot prior to work on a new data set:
        pl += str('reset session ') + str("'")
        sub.call(pl, shell=True)


def fall_back_display():
    """ Map visualization without gnuplot with non-default modules. """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)
        import numpy as np
    except:
        print("Additional non-standard modules are not available.")
        print("Install first numpy and matplotlib.")
        sys.exit()
    print(2 * "\n")
    print("Surveying fingerprint and difference maps by matplotlib and numpy.")
    print("This is a fall back should gnuplot not be available to you.")
    print("\n")

    # identify the .dat to work with:
    dat_register = []
    os.chdir('cxs_workshop')
    for file in os.listdir('.'):
        if file.endswith('.dat'):
            dat_register.append(file)
    dat_register.sort()

    # analysis of the .dat file:
    for input_file in dat_register:
        print("Work on {}".format(input_file))

        retainer = []  # record all execpt the blank lines
        z_register = []  # record only the entries about z

        # analysis of the .dat file:
        with open(input_file, mode='r') as source:
            for line in source:
                if len(line.strip().split()) == 3:
                    retainer.append(line.strip())
                    z_register.append(float(line.strip().split()[2]))

        # identify start and end of di:
        di_start = float(str("{:3.2f}".format(float(retainer[0].split()[0]))))
        di_end = float(str("{:3.2f}".format(float(retainer[-1].split()[0]))))

        # identify zmin and zmax
        zmin_value = str("{:7.6f}".format(float(min(z_register))))
        zmin = " ".join(["zmin:", zmin_value.rjust(9)])

        zmax_value = str("{:7.6f}".format(float(max(z_register))))
        zmax = " ".join(["zmax:", zmax_value.rjust(9)])

        # convert the list of z into an array suitable for display:
        array_z = np.array(z_register)
        array_z = array_z.astype(float)

        dimension_matrix_z = int(math.sqrt(len(array_z)))
        matrix_z = array_z.reshape(dimension_matrix_z, dimension_matrix_z)

        # align orientation of the array to the one used in gnuplot's plots:
        matrix_z = matrix_z.transpose()

        # Filter out entries not sufficiently away from zero:
        np.place(array_z, abs(array_z) < 1e-8, 'nan')

        # definition about the canvas:
        fig, ax = plt.subplots()
        plt.grid()
        ax.xaxis.set_major_locator(MultipleLocator(0.20))
        ax.yaxis.set_major_locator(MultipleLocator(0.20))
        ax.grid(which='major', color='#CCCCCC', linestyle=':', lw=0.5)

        # Change minor ticks to show every 5. (20/4 = 5)
        ax.xaxis.set_minor_locator(AutoMinorLocator(4))
        ax.yaxis.set_minor_locator(AutoMinorLocator(4))

        ax.set_aspect(1.00 / 1.00)

        # yapf: disable
        # permanent decorum:
        plt.text(0.50, 2.70, r'$d_e$')
        plt.text(2.70, 0.50, r'$d_i$')

        bbox_props = dict(boxstyle="square", fc='white', ec='white',
            lw=1, pad=0.1)
        plt.text(0.60, 0.60, r'{}'.format(input_file[:-4]), bbox=bbox_props)
        plt.text(2.25, 0.90, r'{}'.format(zmax), family="monospace",
            size="7", bbox=bbox_props)
        plt.text(2.25, 0.81, r'{}'.format(zmin), family="monospace",
            size="7", bbox=bbox_props)

        # indicator standard map range, dasshed line:
        plt.plot([0.40, 2.60], [2.60, 2.60], '--', color='black')
        plt.plot([2.60, 2.60], [0.40, 2.60], '--', color='black')

        # indicator translated map range, dotted line:
        plt.plot([0.80, 0.80], [0.80, 3.00], ':', color='black')
        plt.plot([0.80, 3.00], [0.80, 0.80], ':', color='black')

        # the optional change of background to gray:
        ax.set_facecolor("#808080")

        # the permanent record:
        if input_file.startswith("diff_"):
            plt.imshow(matrix_z, extent=[di_start, di_end, di_start, di_end],
                origin='lower', cmap='RdBu_r', aspect='equal',
                interpolation='nearest', filternorm='False',
                vmin=-0.025, vmax=0.025, zorder=15, resample=True)

        else:
            plt.imshow(matrix_z, extent=[di_start, di_end, di_start, di_end],
                origin='lower', cmap='cubehelix', aspect='equal',
                interpolation='nearest', filternorm='False',
                vmin=0.0, vmax=0.08, zorder=15, resample=True)
        # yapf: enable

        # the optional color bar:
        plt.colorbar()

        # creation of the permanent record, screening conditions:
        output_file = ''.join([input_file[:-4], '.png'])
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        plt.close(fig)

        with open("screening_log.txt", mode="a") as newfile:
            retain = '\t'.join([input_file, zmin, zmax, '\n'])
            newfile.write(retain)


def fall_back_normalization():
    """ Compute normalized 2D fingerprints (Kahan approach) as backup.

    This is a fall back if there is no Fortran compiler to work with.  Put
    file fingerprint_Kahan.py into the same folder as this moderator which
    will reach out for the secondary script. """
    import fingerprint_Kahan


# argparse section:
# yapf: disable
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
        help="Copy .cxs into a dedicated sub-folder. "
        "File names will be truncated at underscore character.",
        action="store_true")
    parser.add_argument(
        "-n",
        "--normalize",
        help="Normalize the .cxs files with fingerprint.f90. "
        "Files in pattern of 'example.cxs' yield 'example.dat'.",
        action="store_true")
    parser.add_argument(
        "-c",
        "--compare",
        help="Compute the differences between the 2D fingerprints. "
        "Output will be provided in files 'diff*.dat'.",
        action="store_true")

    parser.add_argument(
        "-r",
        "--ruby_number",
        help="Compute the difference number (ruby script).",
        action="store_true")
    parser.add_argument(
        "-o",
        "--overview",
        action="store_true",
        help=
        "Preview 2D fingerprint and difference maps as low resolution .png. "
        "Use it to adjust de/di map range (s, t, e) and z-scaling in the high resolution maps."
    )

    # Either .png or .pdf of fingerprint maps (in high resolution):
    group_fp = parser.add_mutually_exclusive_group()
    group_fp.add_argument(
        "--fpng",
        type=str,
        choices=["s", "t", "e"],
        help=
        "2D fingerprint maps in either map range [s]tandard, [t]ranslated, or [e]xtended as high resolution .png."
    )
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
        help="Difference maps in either map range as high resolution .png.")
    group_delta.add_argument(
        "--dpdf",
        type=str,
        choices=["s", "t", "e"],
        help="Difference maps in either map range as .pdf.")

    # adjustment of zmax scaling in high resolution maps:
    parser.add_argument(
        "--zmax",
        type=float,
        help=
        "Use an other scaling than zmax = 0.08 (fingerprints) or |zmax| = 0.025 (difference maps) in high resolution maps."
    )

    parser.add_argument(
        "-g",
        "--bg",
        action="store_true",
        help="Use a gray background in high resolution maps.")

    parser.add_argument(
        "-a",
        "--alternate",
        action="store_true",
        help="Use the alternate palette definitions.")

    parser.add_argument(
        "-fd",
        "--fall_back_display",
        action="store_true",
        help="Preview generation with numpy and matplotlib.")

    parser.add_argument(
        "-fc",
        "--fall_back_normalization",
        action ="store_true",
        help="Slow, Fortran independent, fingerprint computation.")
    args = parser.parse_args()
    # yapf: enable

    if args.list:
        file_listing()  # list accessible .cxs files
    if args.join:
        assemble_cxs()  # copy .cxs into one place
        rename_cxs()  # truncate file names at underscore sign
    if args.normalize:
        compile_f90()  # render fingerprint.f90 executable
        shuttle_f90()  # bring the .f90 executable to the data
        normalize_cxs()  # generate 2D fingerprint .dat files
    if args.fall_back_normalization:
        fall_back_normalization()
    if args.compare:
        numpy_independent_differences()  # compute the difference maps
    if args.fall_back_display:
        fall_back_display()
    if args.ruby_number:
        ruby_number()  # compute the difference number
    if args.bg:
        global bg  # an option: a neutral gray background
    if args.alternate:
        global alternate  # toggle to alternative color palettes

    # quick overviews with fixed extended range de/di and default z:
    if args.overview:
        search_dat(screen="on")
        png_map(screen="on")
        print("")
        print("File 'gp_report.txt' provides a permanent record.")

    # options fingerprints, .png; adjustable map range [s]tandard,
    # [t]ranslated, [e]extended -- mandatory; adjustable zmax, alternate
    # color palette, and background contrast enhancement -- optional.
    if args.fpng == "s":
        xmin = 0.4
        xmax = 2.6
        if args.zmax is None:
            zmax = 0.08
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="fingerprint")
        png_map(xmin, xmax, zmax, screen, alt, bg)

    if args.fpng == "t":
        xmin = 0.8
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.08
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="fingerprint")
        png_map(xmin, xmax, zmax, screen, alt, bg)

    if args.fpng == "e":
        xmin = 0.4
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.08
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="fingerprint")
        png_map(xmin, xmax, zmax, screen, alt, bg)

    # options fingerprints, .pdf:
    if args.fpdf == "s":
        xmin = 0.4
        xmax = 2.6
        if args.zmax is None:
            zmax = 0.08
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="fingerprint")
        pdf_map(xmin, xmax, zmax, screen, alt, bg)

    if args.fpdf == "t":
        xmin = 0.8
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.08
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="fingerprint")
        pdf_map(xmin, xmax, zmax, screen, alt, bg)

    if args.fpdf == "e":
        xmin = 0.4
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.08
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="fingerprint")
        pdf_map(xmin, xmax, zmax, screen, alt, bg)

    # options difference maps, .png:
    if args.dpng == "s":
        xmin = 0.4
        xmax = 2.6
        if args.zmax is None:
            zmax = 0.025
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="delta")
        png_map(xmin, xmax, zmax, screen, alt, bg)

    if args.dpng == "t":
        xmin = 0.8
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.025
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="delta")
        png_map(xmin, xmax, zmax, screen, alt, bg)

    if args.dpng == "e":
        xmin = 0.4
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.025
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="delta")
        png_map(xmin, xmax, zmax, screen, alt, bg)

    # options difference maps, .pdf:
    if args.dpdf == "s":
        xmin = 0.4
        xmax = 2.6
        if args.zmax is None:
            zmax = 0.025
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="delta")
        pdf_map(xmin, xmax, zmax, screen, alt, bg)

    if args.dpdf == "t":
        xmin = 0.8
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.025
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="delta")
        pdf_map(xmin, xmax, zmax, screen, alt, bg)

    if args.dpdf == "e":
        xmin = 0.4
        xmax = 3.0
        if args.zmax is None:
            zmax = 0.025
        else:
            zmax = args.zmax
        screen = "off"
        alt = args.alternate
        bg = args.bg
        search_dat(map_type="delta")
        pdf_map(xmin, xmax, zmax, screen, alt, bg)

os.chdir(root)
sys.exit(0)
