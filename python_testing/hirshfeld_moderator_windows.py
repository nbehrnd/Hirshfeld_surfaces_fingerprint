#!/usr/bin/env python3

# name:    hirshfeld_moderator_windows.py
# author:  nbehrnd@yahoo.com
# license: GPL version 2
# date:    2020-01-06 (YYYY-MM-DD)
# edit:    2020-01-13 (YYYY-MM-DD)
#
""" Simplified moderator script for the DeltaHirshfeld analysis.

To work with (under eiter Linux or Windows CPython2 or 3) from the CLI, deposit
this script altogether with fingerprint.f90 in the folder containing the .cxs
CrystalExplorer files about the Hirshfeld surfaces computed at very high
resolution.  Launch, from the CLI

python3 hirshfeld_moderator.py -h

to enter the help menu.  Launch

python3 hirshfeld_moderator.py -l

to list, -j to join the .cxs files into an automatically generated directory,
cxs_workshop.  Use then toggle -n to generate normalized 2D Hirshfeld surface
fingerprints.  Their subsequent comparison (-c) yields difference maps about
which you may compute the ruby difference number (-r).

If you have an installation of gnuplot (www.gnuplot.info) and CPython module
PyGnuplot.py (from PyPi package index), you then may generate an overview (-o)
about the computations.  These intentionally small images allow you to adjust
the map range to use in the subsequent generation of high resolution fingerprint
or difference maps.  Call for example either 

python hirshfeld_moderator_windows --fpng e

for fingerprint maps of extended map range, or

python hirshfeld_moderator_windows --dpng s

for difference maps of standard map range.  Both map types require one of the
following parameters:

s   standard map range (0.6 to 2.6 A)
t   translated map range (0.8 to 3.0 A), or
e   extended map range (0.6 to 3.0 A)

An additional adjustment of the representation is to use a different intensity
scaling (--z_max parameter) than the default constrain of 0.080 for fingerpring,
and |0.025| for difference maps; which may be set as an option.  As a help, the
z_min and z_max values met in the .dat file currently read are print on the
corresponding .png / .pdf map.  The overview (-o) equally writes these data into
gp_report.txt, too.

In addition to these parameters, you may add -- ein either consecution or number
-- the toggle -a for an alternative set of color scheme for either map type.
Secondly, -g changes the background from colorless / bright white (default) to a
neuter gray. """

import argparse
from decimal import Decimal
import fnmatch
import os
import platform
import shutil
import subprocess as sub
import sys

# import of the lesser common / non-standard modules:
try:
    import numpy as np
except:
    print("\nThis script requires the CPython module numpy.  Exit.")
    sys.exit(0)

try:
    import PyGnuplot as gp
except:
    print("\nWithout CPython module PyGnuplot (available e.g. on PyPi)")
    print("this script is not able to reach for gnuplot to visualize")
    print("the results of the computation.  This does not affect the")
    print("computations with and of the maps, though.")

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
    except IOError:
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
                except IOError:
                    print("{} wasn't copied to 'cxs_workshop'.".format(file))
    print("\n{} files of type {} were identified.\n".format(
        len(file_register), extension))


def file_crawl(copy=False):
    """ Retrieve / copy .cxs by means of an os.walk. """
    counter = 0
    for folder, subfolders, files in os.walk(root):
        for file in files:
            if fnmatch.fnmatch(file, "*.cxs"):
                counter += 1
                print("{}\t{}".format(counter, file))

                if copy is True:
                    try:
                        shutil.copy(
                            os.path.join(os.getcwd(), file),
                            os.path.join(root, "cxs_workshop"))
                    except IOError:
                        print("{} wasn't copied to workshop.".format(file))


def rename_cxs():
    """ Truncate file names of CrystalExplorer surface files.

/media/norwid2/TOSHIBA/joining_back/possible_merger_hirshfeld_moderator_windows.pyz_v    CrystalExplorer provides Hirshfeld surfaces named in a pattern of
    'example_example.cxs'.  Work is easier if their file name is truncated
    to 'example.cxs'.  This applies only to copies of .cxs. """
    os.chdir("cxs_workshop")

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.cxs"):
            if str("_") in file:
                new_filename = str(file.split("_")[1])
                try:
                    shutil.move(file, new_filename)
                except:
                    print("Renaming {} failed.".format(file))

    os.chdir(root)


def compile_f90():
    """ Compile fingerprint.f90 with either gfortran (default), or gcc. """
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
            print("Equally ensure gfortran's or gcc compiler's installation.")
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


def difference_maps():
    """ Round-Robin tournament of the normalized 2D fingerprint maps. """

    # identification of the files to work with:
    os.chdir("cxs_workshop")
    diff_register = []

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

            if (len(ref_screen) == len(probe_screen)) and \
                    (ref_y_min == probe_y_min):
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
            # return from array to list level, start a moderated formatting
            result_list = result.tolist()

            output = str("diff_") + str(ref_file)[:-4] + \
                        str("_") + str(probe_file)

            with open(output, mode="w") as newfile:
                for result_entry in result_list:
                    to_reformat = str(result_entry).split()

                    x_value = round(Decimal(str(to_reformat[0])[1:-1]), 2)
                    y_value = round(Decimal(str(to_reformat[1])[0:-1]), 2)
                    z_value = round(Decimal(str(to_reformat[2])[0:-1]), 8)

                    # re-insert the blanks met in normalized 2D fingerprints:
                    if float(y_value) == float(ref_y_min):
                        newfile.write("\n")

                    retain = str("{}, {}, {}\n".format(x_value, y_value,
                                                       z_value))
                    newfile.write(retain)

            # Remove the very first line in the report file (a blank one):
            interim = []
            with open(output, mode='r') as source:
                for line in source:
                    interim.append(line)
            with open(output, mode='w') as newfile:
                for entry in interim[1:]:
                    newfile.write(str(entry))

        # enter next round Robin tournament:
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
# part of gnuplot's built-in defaults.  Their later use follows a pattern
# like gp.c('color_palette').

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
# As for the CrystalExplorer-like rainbow, this is a legacy from the
# code basis by Andrew Rohl and Paolo Raiteri.
three_level_old = str("set palette defined (-1 'blue', 0 'white', 1 'red')")
#
# Because its neuter level "white" is indiscernible from "paper white",
# the screening mode uses the softer three-level palette (below, transient
# with neuter gray) instead.  This selection shall facilitate parameter
# adjustments for the high-quality maps.

# The softer three-level palette:
#
# A heavily constrained implementation of Kenneth Moreland's suggestions
# for diverging color palettes.  Even if the output does not benefit from
# the optional background / contrast toggle -g, the tiles indicating a
# difference close to zero are easier to discern from a white background
# (of paper), than in a palette considering only blue, white and read.
#
# Note to toggle --alt to benefit from Kenneth Moreland's
# bent-cool-warm palette below.
three_level_new = str(
    "set palette defined (-1 'blue', 0 'light-gray', 1 'red')")

# The better diverging palette for the difference maps.
#
# This is based on Kenneth Moreland's suggested color palette
# "bent-cool-warm-table-float-0064.csv" [1] converted by csv2plt.py [2]
# into a format accessible to gnuplot.  From a perceptual perspective,
# it improves the detail of representation about the difference map
# data either the classical three level blue_white_red palette, or the
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


def search_dat(map_type="delta"):
    """ Search for .dat files, assume difference maps of typical interest.

    Two cases: fingerprints (type fingerprint, files ending on *.dat), or
    difference maps (map type delta, files in pattern of diff*.dat). """
    global dat_register
    dat_register = []
    os.chdir("cxs_workshop")

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
    pngcairo <-> pdfcairo breaks this script's reliable action.  Instead,
    it is best to sum up the relevant per gnuplot terminal; e.g. pngcairo.

    Contrasting to pdf_map, png_map includes instructions to screen the
    two map types.  Use this to adjust map range (de/di) and cbrange
    (z_max) in the high resolution plots. """

    os.chdir("cxs_workshop")
    print("\nMap data processed:")
    for entry in dat_register:
        # surface the .dat file a level:
        shutil.copy(entry, root)
        print(entry)

        if entry.startswith("diff"):
            difference_map = True
        else:
            difference_map = False

        # define the deposit file:
        gp.c('input = "{}"'.format(entry))
        gp.c('len_root = strlen(input) - 4')
        gp.c('root = substr(input, 1, len_root)')
        gp.c('output_file = root . ".png"')
        gp.c('set output(output_file)')

        # brief statistics per .cxs file read:
        gp.c('stats input u 3 nooutput')
        gp.c('z_min = sprintf("%1.6f", STATS_min)')
        gp.c('z_low = "zmin: " . z_min')
        gp.c('z_max = sprintf("%1.6f", STATS_max)')

        if difference_map is False:
            gp.c('z_top = "zmax: " . z_max')
        if difference_map is True:
            # account for the then used minus sign reporting z_min:
            gp.c('z_top = "zmax:  " . z_max')

        gp.c('report = "file: " . input . " " . z_low . " " . z_top')
        if screen == "on":
            # provision of a a permanent STATS record:
            gp.c('set print "gp_report.txt" append')
            gp.c('print(report)')

        # screening format definition
        #
        # A plot in reduced dimension suffices to provide a preview,
        # equally allows adjustment map range de/di and z-scaling in
        # subsequent high resolution .png and .pdf output.
        if screen == "on":
            gp.c('set term pngcairo size 819,819 crop font "Arial,13" \
                enha lw 2')
        # non-screening format definition:
        if screen == "off":
            gp.c('set term pngcairo size 4096,4096 crop font "Arial,64" \
                    enha lw 10')

        gp.c('set grid lw 0.5; set size square')
        gp.c('set xtics 0.4,0.2; set ytics 0.4,0.2')
        gp.c('set xtics format "%2.1f"; set ytics format "%2.1f"')
        if screen == "off":
            gp.c('set label "d_e" at graph 0.05,0.90 left front \
                font "Arial,104"')
            gp.c('set label "d_i" at graph 0.90,0.05 left front \
                font "Arial,104"')
            gp.c('set label root at graph 0.05,0.05 left front \
                font "Arial,104" noenhanced')

            gp.c('set label z_top at graph 0.70,0.20 left front \
                font "Courier,70"')
            gp.c('set label z_low at graph 0.70,0.17 left front \
                font "Courier,70"')

        if screen == "on":
            gp.c('set label "d_e" at graph 0.05,0.90 left front \
                font "Arial,21"')
            gp.c('set label "d_i" at graph 0.90,0.05 left front \
                font "Arial,21"')
            gp.c('set label root at graph 0.05,0.05 left front \
                font "Arial,21" noenhanced')

            gp.c('set label z_top at graph 0.70,0.20 left front \
                font "Courier,14"')
            gp.c('set label z_low at graph 0.70,0.17 left front \
                font "Courier,14"')

        if screen == "on":
            # range indicator "standard map" (de and di [0.4,2.6] A)
            gp.c('set arrow nohead from 0.4,2.6 to 2.6,2.6 dt 2 front')
            gp.c('set arrow nohead from 2.6,0.4 to 2.6,2.6 dt 2 front')
            # range indicator "translated map" (de and di [0.8,3.0 A)
            gp.c('set arrow nohead from 0.8,0.8 to 0.8,3.0 dt 3 front')
            gp.c('set arrow nohead from 0.8,0.8 to 3.0,0.8 dt 3 front')

        gp.c('set pm3d map; \
            set pm3d depthorder; set hidden; set hidden3d')
        gp.c('unset key')

        if bg == 1:  # provide an optional contrast enhancement
            gp.c('set object 1 rectangle from graph 0,0 to graph 1,1 \
                fillcolor rgb "gray30" behind')

        # color scheme for fingerprint map:
        if (difference_map is False) and (alt == 0):
            gp.c(rainbow)
        if (difference_map is False) and (alt == 1):
            gp.c('set palette cubehelix start 0 cycles -1. saturation 1')

        # color scheme for difference map:
        if (difference_map is True) and (screen == "on"):
            gp.c(three_level_new)
        if (difference_map is True) and (screen == "off") and (alt == 0):
            gp.c(three_level_old)
        if (difference_map is True) and (screen == "off") and (alt == 1):
            gp.c(bent_three_level_0064)

        gp.c('set xrange ["{}":"{}"]'.format(xmin, xmax))
        gp.c('set yrange ["{}":"{}"]'.format(xmin, xmax))  # square shaped plot

        # adjustment of cbrange parameter
        if difference_map is False:
            gp.c('set cbrange [0:"{}"]'.format(zmax))
        if (difference_map is False) and (screen == "on"):
            # This default is suggested by P. Raiteri and A. Rohl:
            gp.c('set cbrange [0:0.08]')

        if difference_map is True:
            gp.c('set cbrange [-"{}":"{}"]'.format(zmax, zmax))
        if (difference_map is True) and (screen == "on"):
            # This default is suggested by P. Raiteri and A. Rohl:
            gp.c('set cbrange [-0.025:0.025]')

        # A conditional plotting / tiling, as suggested by Ethan Merritt.
        #
        # To consider only tiles with z != 0 to populate the plots may
        # save considerably file size.  This is especially experienced
        # while working with the analogue pdf_map function.


#        gp.c('sp "{}" u 1:2:((abs($3) > 0) ? $3 : NaN) w p pt 5 \
#            ps 0.001 lc palette z'.format(entry))

        gp.c('sp "{}" u 1:2:((abs($3) > 0) ? $3 : NaN) w p pt 5 \
            ps 0.05 lc palette z'.format(entry))

        # Re-initiate gnuplot prior to work on a new data set:
        gp.c('reset session')

    os.chdir(root)


def pdf_map(xmin=0.4, xmax=3.0, zmax=0.08, screen="off", alt=0, bg=0):
    """ The general pattern for any of the maps if deposit as .pdf.

    With minor modifications, the design pattern follows the instructions
    in png_map in the above definitions. """

    os.chdir("cxs_workshop")
    print("\nMap data processed:")
    for entry in dat_register:
        # surface the .dat file a level:
        shutil.copy(entry, root)
        print(entry)

        if entry.startswith("diff"):
            difference_map = True
        else:
            difference_map = False

        # define the deposit file:
        gp.c('input = "{}"'.format(entry))
        gp.c('len_root = strlen(input) - 4')
        gp.c('root = substr(input, 1, len_root)')
        gp.c('output_file = root . ".pdf"')
        gp.c('set output(output_file)')

        # brief statistics per .cxs file read:
        gp.c('stats input u 3 nooutput')
        gp.c('z_min = sprintf("%1.6f", STATS_min)')
        gp.c('z_low = "zmin: " . z_min')
        gp.c('z_max = sprintf("%1.6f", STATS_max)')

        if difference_map is False:
            gp.c('z_top = "zmax: " . z_max')
        if difference_map is True:
            # account for the then used minus sign reporting z_min:
            gp.c('z_top = "zmax:  " . z_max')

        gp.c('set term pdfcairo size 6cm,6cm font "Arial,8" enha lw 1')
        gp.c('set grid lw 0.5; set size square')
        gp.c('set xtics 0.4,0.2; set ytics 0.4,0.2')
        gp.c('set xtics format "%2.1f"; set ytics format "%2.1f"')

        gp.c('set label "d_e" at graph 0.05,0.90 left front')
        gp.c('set label "d_i" at graph 0.90,0.05 left front ')
        gp.c('set label root at graph 0.05,0.05 left front noenhanced')
        gp.c('set label z_top at graph 0.65,0.20 left front font "Courier,7"')
        gp.c('set label z_low at graph 0.65,0.17 left front font "Courier,7"')

        gp.c(
            'set pm3d map')  #; set pm3d depthorder; set hidden; set hidden3d')
        gp.c('unset key')

        if bg == 1:
            # provide an optional contrast enhancement:
            gp.c('set object 1 rectangle from graph 0.0,0.0 to graph 1,1 \
                fillcolor rgb "gray30" behind')

        # default color scheme for fingerprint map:
        if (difference_map is False) and (alt == 0):
            gp.c(rainbow)
        if (difference_map is False) and (alt == 1):
            gp.c('set palette cubehelix start 0 cycles -1. saturation 1')

        # default color scheme for difference map:
        if (difference_map is True) and (alt == 0):
            gp.c(three_level_old)
        if (difference_map is True) and (alt == 1):
            gp.c(bent_three_level_0064)

        gp.c('set xrange ["{}":"{}"]'.format(xmin, xmax))
        gp.c('set yrange ["{}":"{}"]'.format(xmin, xmax))  # square shaped plot
        if difference_map is False:
            gp.c('set cbrange [0:"{}"]'.format(zmax))
        if difference_map is True:
            gp.c('set cbrange ["-{}":"{}"]'.format(zmax, zmax))

        # conditional tiling:  (significant savings for .pdf)

        gp.c('sp "{}" u 1:2:((abs($3) > 0) ? $3:NaN) w p pt 5 ps 0.001\
            lc palette z'.format(entry))

        # Re-initiate gnuplot prior to work on a new data set:
        gp.c('reset session')

    os.chdir(root)


# argparse section:
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
        "--compute",
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
        "Use it to adjust de/di map range (s, t, e) and z-scaling in the high resolution maps below."
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
        help="Use 'gray30' as background in high resolution maps.")

    parser.add_argument(
        "-a",
        "--alternate",
        action="store_true",
        help="Use the alternate palette definitions.")
    args = parser.parse_args()

    if args.list:
        file_listing()  # list accessible .cxs files
    if args.join:
        assemble_cxs()  # copy .cxs into one place
        rename_cxs()  # truncate file names at underscore sign
    if args.normalize:
        compile_f90()  # render fingerprint.f90 executable
        shuttle_f90()  # bring the .f90 executable to the data
        normalize_cxs()  # generate 2D fingerprint .dat files
    if args.compute:
        difference_maps()  # comparison of the 2D fingerprint maps
    if args.ruby_number:
        ruby_number()
    if args.bg:
        global bg  # an option: a neutral gray background
    if args.alternate:
        global alternate  # toggle to alternative color palettes

    # quick overviews with fixed extended range de/di and default z:
    if args.overview:
        # import Gnuplot as gp
        search_dat(map_type="fingerprint")
        xmin = 0.4
        xmax = 3.0
        screen = "on"
        zmax = 0.08
        png_map(xmin, xmax, zmax, screen)

        search_dat(map_type="delta")
        xmin = 0.4
        xmax = 3.0
        screen = "on"
        zmax = 0.025
        png_map(xmin, xmax, zmax, screen)

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
