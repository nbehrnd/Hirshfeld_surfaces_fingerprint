# name:   fingerprint_heron.py
# author: nbehrnd@yahoo.com
# date:   2020-01-21 (YYYY-MM-DD)
# edit:   2020-03-02 (YYYY-MM-DD)
#
""" Compute normalized 2D Hirshfeld surface fingerprints, Heron formula

This script computates normalized 2D Hirshfeld surface fingerprints.  Surfaces
of individual triangles yielding the integral Hirshfeld surface are assessed by
the Heron approach:

+ find semi-perimeter s with side lengths a, b, and c by s = (a + b + c) / 2
+ compute triangle area by area = sqrt[s * (s - a) * (s - b) * (s - c)].

For comparison of the results, there is both an implementation of the Kahan
formula (fingerprint_kahan.py), as well as of the algorithm used by Andrew Rohl
and Paolo Raiteri (fingerprint_rr.py).

If used to assist script hirshfeld_surface.py, deposit this file in the
same folder as the moderator and alter the import statement of

import fingerprint_kahan

into the statemet of

import fingerprint_heron

The moderator script will call its action.

If to be used independently, deposit the script into the folder with the
.cxs files of interest.  Launch from the CLI

python fingerprint_heron.py

to write for each example.cxs a fingerprint example.dat.  Only modules
of the standard library are called, offering use in pypy, too. """

import itertools
import math
import os


def cxs_search():
    """ Identification of the .cxs files to work with. """
    global CXS_REGISTER
    CXS_REGISTER = []

    for file in os.listdir("."):
        if file.endswith(".cxs"):
            CXS_REGISTER.append(file)
    CXS_REGISTER.sort()
    return CXS_REGISTER


def file_reader(cxs_file=""):
    """ Read the .cxs once as a list accessible throughout the script. """
    global PER_FILE_REGISTER
    PER_FILE_REGISTER = []
    print("\nAnalysis of file {}:".format(cxs_file))

    # Only a third of the .cxs file lines contain relevant information.  Thus,
    # the manual file file management with selective remove of line feeds later
    # is more efficient, than to call for
    # "with open(file, mode='r') as source" and subsequent iterative
    # global line feed removal.
    file = open(cxs_file, mode="r")
    PER_FILE_REGISTER = file.readlines()
    file.close()


def readout_vertices_count():
    """ Report .cxs' number of vertices and vertices' coordinates. """
    vertices_count = ""
    global VERTICES_COORDINATES
    VERTICES_COORDINATES = []
    tester = False  # assume, the line is not of interest

    for line in PER_FILE_REGISTER:
        if line.startswith("begin vertices "):
            vertices_count = int(line.split()[2])
            report_start = str("{:<21}".format("Number of vertices:"))
            report_end = str("{:>10}".format(vertices_count))
            print("{}{}".format(report_start, report_end))
            tester = True  # start word collecting coordinates
        if line.startswith("end vertices"):
            tester = False
            break

        if tester:
            VERTICES_COORDINATES.append(str(line.strip()))
    del VERTICES_COORDINATES[0]  # remove the start line's entry.


def readout_indices_count():
    """ State .cxs' indices number, list triangles by their indices.  """
    indices_count = ""
    global INDICES_LIST
    INDICES_LIST = []
    tester = False  # assume the line is not of interest

    for line in PER_FILE_REGISTER:
        if line.startswith("begin indices "):
            indices_count = int(line.split()[2])
            report_start = str("{:<21}".format("Number of indices:"))
            report_end = str("{:>10}".format(indices_count))
            print("{}{}".format(report_start, report_end))
            tester = True  # start collecting indices
        if line.startswith("end indices"):
            tester = False
            break

        if tester:
            INDICES_LIST.append(str(line.strip()))
    del INDICES_LIST[0]  # remove the start line's entry.


def readout_di_count():
    """ Report .cxs' number of d_i points, collect the entries. """
    di_count = ""
    global DI_LIST
    DI_LIST = []
    tester = False  # assume the line is not of interest

    for _, line in enumerate(PER_FILE_REGISTER):
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
            DI_LIST.append(str(line.strip()))
    del DI_LIST[0]  # remove the start line's entry.


def readout_de_count():
    """ Report .cxs' number of d_e points, collect the entries. """
    de_count = ""
    global DE_LIST
    DE_LIST = []
    tester = False  # assume the line is not of interest

    for line in PER_FILE_REGISTER:
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
            DE_LIST.append(str(line.strip()))
    del DE_LIST[0]  # remove the start line's entry.


def triangle_surfaces():
    """ Computation of the surface of the surface triangles.

    The distance d between points A(x_1, y_1, z_1) and B(x_2, y_2, z_2)
    equals to
    d = sqrt[(x_2 - x_1)^2 + (y_2 - y_1)^2 + (z_2 - z_1)^2].

    The Heron formula allows to compute the triangle area based on known
    side lengths a, b, and c.  With semi-perimeter s = (a + b + c) / 2,

    area = sqrt[s * (s - a) * (s - b) * (s - c)]

    fingerprint.f90 bars the computation of of areas if any of the three
    sides is shorter than 1e-5 (line #211).  Despite fingerprint.f90 does
    not use Heron's formula, aiming for consistency with fingerprint.f90,
    this constraint is equally used here, too. """
    global COMPUTED_TRIANGLES
    COMPUTED_TRIANGLES = []

    # Each line in 'INDICES_LIST' is one triangle to consider here.
    for triangle in INDICES_LIST:
        # define a triangle by indices of points A, B, and C:
        index_A = int(triangle.split()[0])
        index_B = int(triangle.split()[1])
        index_C = int(triangle.split()[2])

        # define a triangle by coordinates of point A, B, and C:
        point_A = (float(VERTICES_COORDINATES[index_A].split()[0]),
                   float(VERTICES_COORDINATES[index_A].split()[1]),
                   float(VERTICES_COORDINATES[index_A].split()[2]))

        point_B = (float(VERTICES_COORDINATES[index_B].split()[0]),
                   float(VERTICES_COORDINATES[index_B].split()[1]),
                   float(VERTICES_COORDINATES[index_B].split()[2]))

        point_C = (float(VERTICES_COORDINATES[index_C].split()[0]),
                   float(VERTICES_COORDINATES[index_C].split()[1]),
                   float(VERTICES_COORDINATES[index_C].split()[2]))

        # compute the distance BC, i.e. dist_a
        delta_x_a_squared = (point_B[0] - point_C[0])**2
        delta_y_a_squared = (point_B[1] - point_C[1])**2
        delta_z_a_squared = (point_B[2] - point_C[2])**2
        dist_a = math.sqrt(
            delta_x_a_squared + delta_y_a_squared + delta_z_a_squared)

        # compute the distance AC, i.e. dist_b
        delta_x_b_squared = (point_A[0] - point_C[0])**2
        delta_y_b_squared = (point_A[1] - point_C[1])**2
        delta_z_b_squared = (point_A[2] - point_C[2])**2
        dist_b = math.sqrt(
            delta_x_b_squared + delta_y_b_squared + delta_z_b_squared)

        # compute the distance AB, i.e. dist_c
        delta_x_c_squared = (point_A[0] - point_B[0])**2
        delta_y_c_squared = (point_A[1] - point_B[1])**2
        delta_z_c_squared = (point_A[2] - point_B[2])**2
        dist_c = math.sqrt(
            delta_x_c_squared + delta_y_c_squared + delta_z_c_squared)

        # test guard: continue if all side lengths exceed 10^-5 Angstrom:
        if (dist_a > float(10E-5)) and (dist_b > float(10E-5)) and (
                dist_c > float(10E-5)):

            # compute the semi-perimeter s:
            sps = (dist_a + dist_b + dist_c) * 0.5
            # compute single triangle surface area (Heron's equation):
            area = math.sqrt(sps * (sps - dist_a) * (sps - dist_b) *
                             (sps - dist_c))

            # collect d_e of A, B, C for triangle's average:
            de_A = float(DE_LIST[index_A])
            de_B = float(DE_LIST[index_B])
            de_C = float(DE_LIST[index_C])
            average_de = (de_A + de_B + de_C) / float(3)

            # collect d_i of A, B, C for triangle's average:
            di_A = float(DI_LIST[index_A])
            di_B = float(DI_LIST[index_B])
            di_C = float(DI_LIST[index_C])
            average_di = (di_A + di_B + di_C) / float(3)

            # concatenate the results about the individual triangle:
            retain = str("{} {} {}".format(average_de, average_di, area))
            COMPUTED_TRIANGLES.append(retain)
    COMPUTED_TRIANGLES.sort()


def numpy_free_area_binning():
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
    for ready_triangle in COMPUTED_TRIANGLES:
        new_di = float(ready_triangle.split()[1])
        new_de = float(ready_triangle.split()[0])
        area = str(ready_triangle.split()[2])

        retain = str("{:3.2f} {:3.2f} {}".format(new_di, new_de, area))
        pre_binned.append(retain)
    pre_binned.sort()

    # binning the surfaces of individual triangles:
    global RECORDER_REGISTER
    RECORDER_REGISTER = []
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
            RECORDER_REGISTER.append(retain)
            # initiate the collection of new information:
            local_area = 0.0
            local_area += float(entry.split()[2])
            old_key = key

    del RECORDER_REGISTER[0]  # delete the heading zero entry
    #     # test deposit as permanent file, only non-zero (de,di) bins:
    #     with open("sparse_export.txt", mode="w") as newfile:
    #         for entry in RECORDER_REGISTER:
    #             newfile.write("{}\n".format(entry))
    report_start = str("{:<21}".format("non-zero (de,di)-bins:"))
    report_end = str("{:>9}".format(len(RECORDER_REGISTER)))
    print("\n{}{}".format(report_start, report_end))

    # report integral_area:
    report_start = str("{:<21}".format("Total surface area:"))
    report_end = str("{:>10}".format(round(integral_area, 5)))
    print("{}{}".format(report_start, report_end))

    # normalization of the results
    global NORMALIZED_REGISTER
    NORMALIZED_REGISTER = []
    for entry in RECORDER_REGISTER:
        normalized_entry = (float(entry.split()[2]) / integral_area) * 100.00
        retain = ' '.join([
            entry.split()[0],
            entry.split()[1], "{:9.8f}".format(normalized_entry)
        ])
        NORMALIZED_REGISTER.append(retain)


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
    raw_sum_list = NORMALIZED_REGISTER + blank_list
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
    for cxs_file in CXS_REGISTER:
        file_reader(cxs_file)
        readout_vertices_count()
        readout_indices_count()
        readout_de_count()
        readout_di_count()

        triangle_surfaces()
        numpy_free_area_binning()
        dat_file_generation(cxs_file)


# action calls:
if __name__ == '__main__':
    cxs_search()
    worker()
