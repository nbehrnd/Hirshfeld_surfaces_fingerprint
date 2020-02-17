#!/usr/bin/env python3

# name:    hirshfeld_moderator.py
# author:  nbehrnd@yahoo.com
# license: GPL version 2
# date:    2019-11-14 (YYYY-MM-DD)
# edit:    2020-02-17 (YYYY-MM-DD)
#
""" This wrapper assists the analysis of 2D fingerprints of Hirshfeld
surface files (.cxs) computed with CrystalExplorer.  Intended for the CLI
of CPython 3, known to work for either Linux, or Windows.  It equally may
work with legacy Python 2.7.17.

This script running in Python moderates the action of the scripts provided
by Andrew Rohl and Paolo Raiteri.  For this reason, in addition to Python,
you need

+ a Fortran compiler (either gfortran, or gcc) for fingerprint.f90, to
  read CrystalExplorer's .cxs files and normalize 2D Hirshfeld surface
  maps as .dat files

+ a C compiler (gcc) for diff_finger.c, for the computation of Hirshfeld
  difference maps

+ ruby for sum_abs_diffs.rb to compute the 'ruby difference number' about
  the Hirshfeld difference maps.

+ a gnuplot installation if you want to visualize either normalized 2D
  Hirshfeld surface maps or / and difference maps -- which is optional

Note the presence of a sibling script, hirshfeld_moderator_windows.py,
requiring only Python and Fortran for the computation, and -- if you want
to visualize the maps -- gnuplot.  (See hirshfeld_moderator_windows.py for
further details.)  This moderator script was written to retain the
computational performance the original scripts provide, the other to lower
the number of languages to be used to access the same results.

The help menu is accessed from the command prompt of Python 3.5 with

python hirshfeld_moderator -h

to provide an overview about the functions available.  To work with this
script, put this its dependencies into the folder containing the .cxs to
be scrutinized.  Typically, you

1) want to inform yourself about the .cxs files present.  Then, call

   python hirshfeld_moderator.py -l

   to generate a non-permanent listing about them.

2) want to put copies of the .cxs files into a dedicated folder.  This
   one, cxs_workshop, is created by

   python hirshfeld_moderator.py -j

   At present, CrystalExplorer (version 17.5, built 2017-05-01) provides
   the output in files named in a pattern of 'example_example.cxs'.  To
   facilitate the work ahead, this script truncates the file names of these
   copies at their first underscore, to yield file names as 'example.cxs'.

3) to generate normalized 2D Hirshfeld surface fingerprints.  The script
   attempts compilation of fingerprint.f90 with either gfortran (default),
   or gcc (backup); shuttles the executable to the copied data and works
   with them by call of

   python hirshfeld_moderator.py -n

   to write .dat files (e.g., 'example.dat') about the extended map range,
   i.e. de and di of 0.4 to 3.0 A.

4) to compare the normalized fingerprints.  Difference maps then will be
   computed by

   python hirshfeld_moderator.py -c

   This triggers the compilation of diff_finger.c by gcc, transfer of the
   executable to the data, and computation and eventual report of results
   in diff*.dat files (e.g., 'diff_example1_example2.dat').

5) to assign a characteristic figure of difference about the difference
   map.  The greater this 'ruby difference number', the greater the
   difference of the two Hirshfeld surfaces yielding the corresponding
   diff*.dat scrutinized by

   python hirshfeld_moderator.py -r

   Note your terminal may allow to redirect the output to a permanent
   record.  On Linux' bash shell, you could do so by

   python hirshfeld_moderator.py -r > record.txt

   to retain these results.

The results of normalization of 2D Hirshfeld surface fingerprints (*.dat
files) and the subsequently computed difference maps (diff*.dat files) may
be visualized.  In both ASCII-based map types, the outer loop about d_i
is recorded as the first column entry -- the abscissa in the diagrams if
plot by gnuplot --, followed by the inner loop about d_e (second column /
ordinate in plots by gnuplot), and the third column entries about the
z-value (the intensity projection in plots by gnuplot).  Each increment of
the outer loop about d_e is separated by the former by a blank line.

6) Running a

   python hirshfeld_moderator.py -o

   triggers the provision of an overview about these results, intended as
   a screen.  These diagnostic plots (as .png) of small dimension include
   an indication about the standard map range (0.4 to 2.6 A; by dashed
   lines) and translated map range (0.8 to 3.0 A, by dotted lines) in the
   display of the extended map range (0.4 to 3.0 A) you subsequently
   choose from (vide infra).

   To identify rapidly pixels representing a z equal or close to zero, the
   zero-level of the three level map was redefined as light-gray, rather
   than to white.

   For each file, gnuplot states the range of z values (rounded to six
   decimals) to the plotted map.  A survey equally creates the permanent
   record gp_report.txt which may be used to adjust the subsequent
   intensity scaling (vide infra).

7) The visualization of fingerprints or difference maps in higher quality
   is mutually exclusive, yet may be performed one after the other.  At
   first, determine if the target file format is either a bitmap .png, or
   a resolution independent .pdf.  Second, based on the previous survey,
   determine which map range will cover all the information in the de/di
   plane as either one of [s]tandard, [t]ranslated, or [e]xtended is used
   as mandatory parameter of to plot the maps with gnuplot.  As an example

   python hirshfeld_moderator.py --dpng e

   will trigger gnuplot to iterate on all difference maps diff*.dat to
   be plot with the extended map range as .png (3674 x 3229 px), while

   python hirshfeld_moderator.py --fpdf s

   works only on fingerprint *.dat (but not diff*.dat) files to generate
   .pdf (6 x 6 cm) in standard map range, which easier may be processed
   further (e.g., inkscape).  Empirically, the generation of .pdf tends to
   advance faster than the one of .png; equally, the .pdf benefit more
   than the .png from conditional plotting to yield smaller file sizes.

   As long as you kept the .dat or diff*.dat files in folder cxs_workshop,
   you may alter the map representation (e.g., map range, or use of any of
   the optional parameters [vide infra]) just by call of the corresponding
   visualization command (from section #7 or #8 of this guide) again.

8) Additional optional parameters for fingerprint and difference mapping

   Any of the following parameters may be used for either fingerprint, or
   difference map in high resolution; their consecution is insignificant:

   + Background substitution

     A call in line of

     python hirshfeld_moderator.py --dpng e -g

     provides a neuter gray background.  This is especially helpful for
     the diverging three level map if the discern of "white" (reporting
     about data close to z = 0) vs. "white" (to report absence of data) is
     important.

   + Palette substitution

     A call in line of

     python hirshfeld_moderator.py --dpng e -a

     substitutes the color palettes.  There are alternatives safer to
     perception than the classical rainbow / jet, for example if the
     output is constrained to gray scale (e.g., a black-and-white printer)
     or in case of color blindness.  Thus, -a toggles the CrystalExplorer
     like rainbow color map to gnuplot's implemented continuous cubehelix,
     and substitutes the classical three level blue_white_red diverging\
     map by one of Kenneth Moreland's definitions of a bent_cool_map
     accentuating the transient around 'neuter z = 0'.

   + Adjustable intensity scaling

     The default projection of the intensity scale ("z") is limited to
     0 < z < 0.08 (fingerprint maps), or |z| < 0.025 (difference maps).
     These ranges are a suggestion found in the code basis by Andrew Rohl
     and Paolo Raiteri.  These may be overwritten in line of

     python hirshfeld_moderator.py --dpng e -zmax 0.03

     which in case of difference maps would then constrain the projection
     symmetrically to -0.03 < z < 0.03.  By the same token

     python hirshfeld_moderator.py --fpng e -zmax 0.03

     constrains the display of fingerprints to 0 < z < 0.03. """

import argparse
import fnmatch
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
                except OSError:
                    print("{} wasn't copied to 'cxs_workshop'.".format(file))
    print("\n{} files of type {} were identified.\n".format(
        len(file_register), extension))


def file_crawl(copy=False):
    """ Retrieve / copy .cxs by means of an os.walk. """
    counter = 0
    cxs_to_copy = []

    for folder, subfolders, files in os.walk(root):
        for subfolder in subfolders:
            os.chdir(subfolder)
            for file in os.listdir("."):
                if file.endswith(".cxs"):
                    cxs_to_copy.append(os.path.abspath(file))
                    if copy is False:
                        counter += 1
                        print("{}\t{}".format(counter, file))
            os.chdir(root)

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


def compile_C():
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


def shuttle_C():
    """ Shuttle the executable of diff_finger.c to the data. """
    try:
        shutil.copy("diff_finger", "cxs_workshop")
    except IOError:
        print("Error while copying C executable to the data.")
        print("Check the presence of folder 'cxs_workshop'.")
        sys.exit(0)

    # space cleaning of the project's root folder:
    try:
        os.remove("diff_finger")
    except IOError:
        pass


def map_differences():
    """ Compare each of the 2D fingerprints with each other. """
    print("\nComputation of difference maps starts:")

    os.chdir("cxs_workshop")
    fingerprint_register = []

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "*.dat"):
            if fnmatch.fnmatch(file, "diff*.dat") is False:
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
            difference_test = str("./diff_finger {} {} > {}".format(
                reference_map, test_map, difference_map))
            try:
                sub.call(difference_test, shell=True)
            except IOError:
                print("Problem to compute {}.".format(difference_map))

        del fingerprint_register[0]
    print("\nComputation of difference maps is completed.")

    os.remove("diff_finger")
    os.chdir(root)


def shuttle_ruby_script():
    """ If possible, shuttle sum_abs_diffs.rb to the data. """
    script_missing = "True"
    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "sum_abs_diffs.rb"):
            script_missing = "False"
            break
    if script_missing == "True":
        print("Script 'sum_abs_diffs.rb' is missing, script stops. ")
        sys.exit(0)
    if script_missing == "False":
        try:
            shutil.copy("sum_abs_diffs.rb", "cxs_workshop")
        except IOError:
            print("Problem copying 'sum_abs_diffs.rb' to 'cxs_workshop'.")
            print("Maybe the Ruby script is missing.  Exit.")
            sys.exit(0)


def ruby_difference_number():
    """ Report the Ruby difference numbers from the diff*.dat data. """
    os.chdir("cxs_workshop")
    register = []

    for file in os.listdir("."):
        if fnmatch.fnmatch(file, "diff*.dat"):
            register.append(file)
    register.sort()

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
    except OSError:
        pass
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
                fillcolor rgb "gray30" behind; ')

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
        pl += str('set label "d_i" at graph 0.90,0.05 left front;  ')
        pl += str('set label "{}" at graph 0.05,0.05 left front noenhanced;  '.
                  format(file_stamp))
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
                fillcolor rgb "gray30" behind; ')

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
    if args.compare:
        compile_C()  # render diff_finger.c executable
        shuttle_C()  # shuttle the executable to the data.
        map_differences()
    if args.ruby_number:
        shuttle_ruby_script()
        ruby_difference_number()
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

        
