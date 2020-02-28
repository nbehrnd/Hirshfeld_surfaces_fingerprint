# name:   fingerprint_RR.py
# author: nbehrnd@yahoo.com
# date:   2020-02-11 (YYYY-MM-DD)
# edit:   2020-02-26 (YYYY-MM-DD)
#
""" Compute normalized 2D Hirshfeld surface fingerprints, 'RR formula' .

This script probes the computation of the normalized 2D Hirshfeld surface
fingerprints, where the surface of the areas of individual triangles
constituting the integral Hirshfeld surface are computed by the
trigonometric used by Andrew Rohl and Paolo Raiteri.

Note that for comparison of the results, there is both an implementation
of the Heron formula (fingerprint_Heron.py), as well as of the by Kahan
(fingerprint_Kahan.py).

If used to assist script hirshfeld_surface.py, deposit this file in the
same folder as the moderator and alter the import statement of

import fingerprint_Kahan

into the statemet of

import fingerprint_RR

The moderator script will call its action.

If to be used independently, deposit the script into the folder with the
.cxs files of interest.  Launch from the CLI

python fingerprint_RR.py

to write for each example.cxs a fingerprint example.dat.  Only modules
of the standard library are called, offering use in pypy, too. """

import array
import itertools
import math
import os
import sys


def file_search():
    """ Identification of the files to work with. """
    global cxs_register
    cxs_register = []

    for file in os.listdir("."):
        if file.endswith(".cxs"):
            cxs_register.append(file)
    cxs_register.sort()


def file_reader(cxs_file=""):
    """ Read the .cxs once as a list accessible throughout the script. """
    global per_file_register
    per_file_register = []
    print("\nAnalysis of file {}:".format(cxs_file))

    # The computation uses only about a third of the lines of the .cxs
    # file.  Thus, the manual file file management here and selective
    # remove of line feeds later is more efficient, than to call for
    # "with open(file, mode='r') as source" and subsequent iterative
    # global line feed removal.
    file = open(cxs_file, mode="r")
    per_file_register = file.readlines()
    file.close()


def readout_vertices_count():
    """ Report .cxs' number of vertices and vertices' coordinates. """
    vertices_count = ""
    global vertices_coordinates
    vertices_coordinates = []
    tester = False  # assume, the line is not of interest

    for line in per_file_register:
        if line.startswith("begin vertices "):
            vertices_count = int(line.split()[2])
            report_start = str("{:<21}".format("Number of vertices:"))
            report_end = str("{:>10}".format(vertices_count))
            print("{}{}".format(report_start, report_end))
            tester = True  # start word collecting coordinates
        if line.startswith("end vertices"):
            tester = False
            break

        if tester is True:
            vertices_coordinates.append(str(line.strip()))
    del vertices_coordinates[0]  # remove the start line's entry.


def readout_indices_count():
    """ State .cxs' indices number, list triangles by their indices.  """
    indices_count = ""
    global indices_list
    indices_list = []
    tester = False  # assume the line is not of interest

    for line in per_file_register:
        if line.startswith("begin indices "):
            indices_count = int(line.split()[2])
            report_start = str("{:<21}".format("Number of indices:"))
            report_end = str("{:>10}".format(indices_count))
            print("{}{}".format(report_start, report_end))
            tester = True  # start collecting indices
        if line.startswith("end indices"):
            tester = False
            break

        if tester is True:
            indices_list.append(str(line.strip()))
    del indices_list[0]  # remove the start line's entry.


def readout_di_count():
    """ Report .cxs' number of d_i points, collect the entries. """
    di_count = ""
    global di_list
    di_list = []
    tester = False  # assume the line is not of interest

    for _, line in enumerate(per_file_register):
        if line.startswith("begin d_i "):
            di_count = int(line.split()[2])
            report_start = str("{:<21}".format("Number of di:"))
            report_end = str("{:>10}".format(di_count))
            print("{}{}".format(report_start, report_end))
            tester = True
        if line.startswith("end d_i"):
            tester = False
            break

        if tester is True:
            di_list.append(str(line.strip()))
    del di_list[0]  # remove the start line's entry.


def readout_de_count():
    """ Report .cxs' number of d_e points, collect the entries. """
    de_count = ""
    global de_list
    de_list = []
    tester = False  # assume the line is not of interest

    for line in per_file_register:
        if line.startswith("begin d_e "):
            de_count = int(line.split()[2])
            report_start = str("{:<21}".format("Number of de:"))
            report_end = str("{:>10}".format(de_count))
            print("{}{}".format(report_start, report_end))
            tester = True
        if line.startswith("end d_e"):
            tester = False
            break

        if tester is True:
            de_list.append(str(line.strip()))
    del de_list[0]  # remove the start line's entry.


def triangle_surfaces(cxs_files=""):
    """ Computation of the surface of the surface triangles.

    The approach follows the pattern found in fingerprint.f90, outlined
    in further detail by Paolo Raiteri's sketch. The constraint to admit
    only triangles with all side lengths either equal to, or longer than
    1E-5 units is retained. """
    global computed_triangles
    computed_triangles = []

    # Each line in 'indices_list' is one triangle to consider here.
    for triangle in indices_list:
        # define a triangle by indices of points A, B, and C:
        index_A = int(triangle.split()[0])
        index_B = int(triangle.split()[1])
        index_C = int(triangle.split()[2])

        # define a triangle by coordinates of point A, B, and C:
        point_A = (float(vertices_coordinates[index_A].split()[0]),
                   float(vertices_coordinates[index_A].split()[1]),
                   float(vertices_coordinates[index_A].split()[2]))

        point_B = (float(vertices_coordinates[index_B].split()[0]),
                   float(vertices_coordinates[index_B].split()[1]),
                   float(vertices_coordinates[index_B].split()[2]))

        point_C = (float(vertices_coordinates[index_C].split()[0]),
                   float(vertices_coordinates[index_C].split()[1]),
                   float(vertices_coordinates[index_C].split()[2]))

        # start of the inner of the algorithm by fingerprint.f90:
        # compute the vectors:
        vector_1 = array.array('f', [
            point_B[0] - point_A[0], point_B[1] - point_A[1],
            point_B[2] - point_A[2]
        ])
        vector_2 = array.array('f', [
            point_C[0] - point_A[0], point_C[1] - point_A[1],
            point_C[2] - point_A[2]
        ])
        vector_3 = array.array('f', [
            point_C[0] - point_B[0], point_C[1] - point_B[1],
            point_C[2] - point_B[2]
        ])
        # compute triangle side lengths:
        length_1 = math.sqrt(vector_1[0]**2 + vector_1[1]**2 + vector_1[2]**2)
        length_2 = math.sqrt(vector_2[0]**2 + vector_2[1]**2 + vector_2[2]**2)
        length_3 = math.sqrt(vector_3[0]**2 + vector_3[1]**2 + vector_3[2]**2)

        # test guard: all side lengths at least 10^-5 Angstrom:
        if (length_1 > float(10E-5)) and (length_2 > float(10E-5)) and (
                length_3 > float(10E-5)):

            # compute the cosine of angle theta enclosed by the vectors:
            cost = ((vector_1[0] * vector_2[0]) + (vector_1[1] * vector_2[1]) +
                    (vector_1[2] * vector_2[2])) / (length_1 * length_2)

            # compute the sinus of angle theta enclosed by the vectors:
            # preliminary check, as in fingerprint.f90:
            pre_sint = 1.0 - cost**2
            if pre_sint > 1.0:
                pre_sint = 1.0
            if pre_sint < 1e-7:
                continue
            sint = math.sqrt(pre_sint)

            # compute the area of the individual triangle:
            area = 0.0
            area = 0.5 * length_1 * length_2 * sint

            # collect d_e of A, B, C for triangle's average:
            de_A = float(de_list[index_A])
            de_B = float(de_list[index_B])
            de_C = float(de_list[index_C])
            average_de = (de_A + de_B + de_C) / float(3)

            # collect d_i of A, B, C for triangle's average:
            di_A = float(di_list[index_A])
            di_B = float(di_list[index_B])
            di_C = float(di_list[index_C])
            average_di = (di_A + di_B + di_C) / float(3)

            # concatenate the results about the individual triangle:
            retain = str("{} {} {}".format(average_de, average_di, area))
            computed_triangles.append(retain)
    computed_triangles.sort()


def numpy_free_area_binning(cxs_file=""):
    """ A two-step binning without numpy; 1) de, di, 2) surfaces.

    A grid increment of 0.01 A during work with CrystalExplorer is the
    recommendation by by Rohl et al. to perform this analysis.  Thus,
    the binning applied here equally imposes a grid of this granularity,
    reflected by the interval about (di, de) = 0.40(0.01)3.00 A.

    The subsequent, bin-wise addition of individual triangle surfaces
    equally was tested both with a three-column np.array, as well as with
    a square-matrix like array approach, too.  So far, the approach here
    -- independent on numpy -- however retains best the portability of the
    script with an acceptable rate of processing (e.g., with pypy). """

    # binning along de and di:
    pre_binned = []
    for ready_triangle in computed_triangles:
        new_di = float(ready_triangle.split()[1])
        new_de = float(ready_triangle.split()[0])
        area = str(ready_triangle.split()[2])

        retain = str("{:3.2f} {:3.2f} {}".format(new_di, new_de, area))
        pre_binned.append(retain)
    pre_binned.sort()

    # binning the surfaces of individual triangles:
    global recorder_register
    recorder_register = []
    local_area = 0.0  # collect surface specific to (de,di) bin
    integral_area = 0.0  # to sum up all triangles' surfaces
    old_key = ""
    pre_binned.append("0 0 0")  # the STOP word to process the data

    for entry in pre_binned:
        key = ' '.join([entry.split()[0], entry.split()[1]])
        if key == old_key:
            local_area += float(entry.split()[2])
        if key != old_key:
            # save the information collected so far:
            retain = str("{} {:9.8f}".format(old_key, local_area))
            integral_area += local_area
            recorder_register.append(retain)
            # initiate the collection of new information:
            local_area = 0.0
            local_area += float(entry.split()[2])
            old_key = key

    del recorder_register[0]  # delete the heading zero entry
    #     # test deposit as permanent file, only non-zero (de,di) bins:
    #     with open("sparse_export.txt", mode="w") as newfile:
    #         for entry in recorder_register:
    #             newfile.write("{}\n".format(entry))
    report_start = str("{:<21}".format("non-zero (de,di)-bins:"))
    report_end = str("{:>9}".format(len(recorder_register)))
    print("\n{}{}".format(report_start, report_end))

    # report integral_area:
    report_start = str("{:<21}".format("Total surface area:"))
    report_end = str("{:>10}".format(round(integral_area, 5)))
    print("{}{}".format(report_start, report_end))

    # normalization of the results
    global normalized_register
    normalized_register = []
    for entry in recorder_register:
        normalized_entry = (float(entry.split()[2]) / integral_area) * 100.00
        retain = ' '.join([
            entry.split()[0],
            entry.split()[1], "{:9.8f}".format(normalized_entry)
        ])
        normalized_register.append(retain)


def dat_file_generation(cxs_file=""):
    """ Prepare a .dat file / the Hirshfeld surface 2D fingerprint map.

    Further work with the 2D fingerprints such as to map their differences
    requires a uniform dimension, i.e., (0.40,0.01,3.00) A for de and di.
    This is achieved by adding zero-entries to (di,de)-bins otherwise
    not yet populated to the recorded (di,de)-bins. """
    # prepare a blank list:
    assistance = []
    blank_list = []

    for i in range(40, 301, 1):
        retain = float(i) / float(100)
        assistance.append("{:3.2f}".format(retain))

    for entry in itertools.product(assistance, assistance):
        retain = ' '.join([entry[0], entry[1], "0.0"])
        blank_list.append(retain)

    # join blank_list and recorded list about normalized (di,de)-bins:
    raw_sum_list = normalized_register + blank_list
    raw_sum_list.sort()

    # If known to both lists now merged, bins with non-zero entries
    # are sorted after those by the blank list.  Areas will thus be
    # added locally until the key (di,de) of next entry changes;
    # this then triggers the deposit in the dat_register eventually
    # used to write .dat about the normalized 2D fingerprints.
    dat_register = []
    local_area = 0.0
    old_key = ""
    raw_sum_list.append("0 0 0")  # the STOP word to process the data

    for entry in raw_sum_list:
        key = ' '.join([entry.split()[0], entry.split()[1]])
        if key == old_key:
            local_area += float(str(entry.split()[2]))
        if key != old_key:
            # save the information collected so far:
            retain = str("{} {:9.8f}".format(old_key, local_area))
            dat_register.append(retain)
            # initiate the collection of new information:
            local_area = 0.0
            local_area += float(str(entry.split()[2]))
            old_key = key

    del dat_register[0]  # delete the heading zero entry:

    # permanent record as .dat file:
    output_file = str(cxs_file)[:-4] + str(".dat")
    with open(output_file, mode="w") as newfile:
        for entry in dat_register:
            if str("3.00") in entry.split()[1]:
                retain = str("{}\n\n".format(entry))
            else:
                retain = str("{}\n".format(entry))
            newfile.write(retain)


def worker():
    """ Bundle the individual actions per .cxs file. """
    for cxs_file in cxs_register:
        file_reader(cxs_file)
        readout_vertices_count()
        readout_indices_count()
        readout_de_count()
        readout_di_count()

        triangle_surfaces()
        numpy_free_area_binning()
        dat_file_generation(cxs_file)


# action calls:
file_search()
worker()
print("\nThe computation of normalized fingerprints is complete.\n")
sys.exit(0)
