#!/usr/bin/env python
# name:   fingerprint_kahan.py
# author: nbehrnd@yahoo.com
# date:   2020-01-30 (YYYY-MM-DD)
# edit:   2020-04-21 (YYYY-MM-DD)
#
""" Normalized 2D Hirshfeld surface fingerprints by Kahan formula.

Reading .cxs files computed by CrystalExplorer in very high resolution,
this script computes normalized 2D Hirshfeld surface fingerprints as .dat.
The surface area of individual triangles yielding the integral Hirshfeld
surface is assessed by the Kahan equation.

Contrasting to the equation attributed to Heron -- Kahan's equation works
equally on needle-shaped triangles.  See equation #2 (page 3 / 23) in his
document "Miscalculating Area and Angles of a Needle-like Triangle (from
Lecture Notes for Introductory Numerical Analysis Classes)", accessed at
http://http.cs.berkeley.edu/~wkahan/Triangle.pdf.

On table 1 on page 5 in above mentioned .pdf, examples provide comparison
between computations with Heron's formula, and Kahan's alternative.  His
algorithm consists of the following steps:

+ order the side lengths (a,b,c) such that a >= b >= c
+ check if the triangle is possible.  If c - (a - b) < 0, then 'the data
  are not side-lengths of a real triangle' and the computation stops
  right away here.  Else,
+ area = 0.25 * \sqrt(A * B * C * D) where /these/ ABCD stand for
  A = (a + (b + c)),
  B = (c - (a - b)),
  C = (c + (a - b)), and
  D = (a + (b - c)).

To compare the results, there is both an implementation of the Heron
formula (fingerprint_heron.py), as well as of the algorithm used by Andrew
Rohl and Paolo Raiteri (fingerprint_rr.py) in fingerprint.f90 as well.
If used to assists hirshfeld_surface.py, deposit this file in the same
folder as the moderator; then, the moderator script will call its action.

If to be used independently, deposit this file into the folder with the
.cxs files of interest.  Launch its action from the CLI with

python fingerprint_heron.py

to write for each example.cxs a fingerprint example.dat.

The script uses only modules of Python's standard library.  For batch-wise
scrutinies, an increase of performance is achieved by using either Python2
(instead of Python3), or pypy. """

import itertools
import math
import os


class Worker():
    """ Work on an .cxs to yield normalized 2D fingerprints. """

    def __init__(self, cxs_file):
        """ Initiate the work session. """
        self.cxs_file = cxs_file
        self.cxs_content = []
        self.vertices_count = 0
        self.vertices_coordinates = []
        self.indices_count = 0
        self.indices_list = []
        self.di_count = 0
        self.di_list = []
        self.de_count = 0
        self.de_list = []
        self.recorder_register = []
        self.normalized_register = []
        self.computed_triangles = []

    def file_list(self):
        """ Report to the CLI the .cxs file identified. """
        print("{}:".format(self.cxs_file))

    def file_reader(self):
        """Read the .cxs file content. """
        file = open(self.cxs_file, mode="r")
        self.cxs_content = file.readlines()
        file.close()

    def readout_vertices_count(self):
        """Report .cxs' number of vertices and vertices' coordinates. """
        tester = False

        # for line in per_file_register:
        for line in self.cxs_content:
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
                self.vertices_coordinates.append(str(line.strip()))
        del self.vertices_coordinates[0]  # remove the start line's entry.

    def readout_indices_count(self):
        """ State .cxs' indices number, list triangles by their indices. """
        tester = False  # assume the line is not of interest

        for line in self.cxs_content:
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
                self.indices_list.append(str(line.strip()))
        del self.indices_list[0]  # remove the start line's entry.

    def readout_di_count(self):
        """ Report .cxs' number of d_i points, collect the entries. """
        tester = False  # assume the line is not of interest

        for _, line in enumerate(self.cxs_content):
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
                self.di_list.append(str(line.strip()))
        del self.di_list[0]  # remove the start line's entry.

    def readout_de_count(self):
        """ Report .cxs' number of d_e points, collect the entries. """
        tester = False  # assume the line is not of interest

        for line in self.cxs_content:
            if line.startswith("begin d_e "):
                de_count = int(line.split()[2])
                report_start = str("{:<21}".format("Number of de:"))
                report_end = str("{:>10}".format(de_count))
                print("{}{}".format(report_start, report_end))
                tester = True
            if line.startswith("end d_e"):
                tester = False
                break

            if tester:
                self.de_list.append(str(line.strip()))
        del self.de_list[0]  # remove the start line's entry

    def triangle_surfaces(self):
        """ Compute the surface of the surface triangles (Kahan formula)

        The distance d between points A(x_1, y_1, z_1) and B(x_2, y_2, z_2)
        equals to

        d = sqrt[(x_2 - x_1)^2 + (y_2 - y_1)^2 + (z_2 - z_1)^2].

        The triangle side lengths are sorted in decreasing order, labeled
        newly as to match the condition of a >= b >= c.  The individual
        triangle area then is computed by

        area = 0.25 * \sqrt(A * B * C * D) where /these/ ABCD stand for

        A = (a + (b + c)),
        B = (c - (a - b)),
        C = (c + (a - b)), and
        D = (a + (b - c)).

        The side length constraint present in Fortran code fingerprint.f90
        -- all sides at least 10E-5 A -- thus is not applied here. """

        # Each line in 'indices_list' is one triangle to consider here.
        for triangle in self.indices_list:
            # define a triangle by indices of points A, B, and C:
            index_A = int(triangle.split()[0])
            index_B = int(triangle.split()[1])
            index_C = int(triangle.split()[2])

            # define a triangle by coordinates of point A, B, and C:
            point_A = (float(self.vertices_coordinates[index_A].split()[0]),
                       float(self.vertices_coordinates[index_A].split()[1]),
                       float(self.vertices_coordinates[index_A].split()[2]))

            point_B = (float(self.vertices_coordinates[index_B].split()[0]),
                       float(self.vertices_coordinates[index_B].split()[1]),
                       float(self.vertices_coordinates[index_B].split()[2]))

            point_C = (float(self.vertices_coordinates[index_C].split()[0]),
                       float(self.vertices_coordinates[index_C].split()[1]),
                       float(self.vertices_coordinates[index_C].split()[2]))

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

            # sort the triangle side lengths:
            length_register = [dist_a, dist_b, dist_c]
            length_register.sort()
            Kahan_a = float(length_register[2])
            Kahan_b = float(length_register[1])
            Kahan_c = float(length_register[0])

            # if passing the triangle condition, compute the triangle area
            if (Kahan_c - (Kahan_a - Kahan_b)) < 0:
                print("This is not a valid triangle.")
                continue  # equates to 'start with the next triangle instead'
            else:
                Kahan_A = Kahan_a + (Kahan_b + Kahan_c)
                Kahan_B = Kahan_c - (Kahan_a - Kahan_b)
                Kahan_C = Kahan_c + (Kahan_a - Kahan_b)
                Kahan_D = Kahan_a + (Kahan_b - Kahan_c)

                area = 0.25 * math.sqrt(Kahan_A * Kahan_B * Kahan_C * Kahan_D)

                # collect d_e of A, B, C for triangle's average:
                de_A = float(self.de_list[index_A])
                de_B = float(self.de_list[index_B])
                de_C = float(self.de_list[index_C])
                average_de = (de_A + de_B + de_C) / float(3)

                # collect d_i of A, B, C for triangle's average:
                di_A = float(self.di_list[index_A])
                di_B = float(self.di_list[index_B])
                di_C = float(self.di_list[index_C])
                average_di = (di_A + di_B + di_C) / float(3)

                # concatenate the results about the individual triangle:
                retain = str("{} {} {}".format(average_de, average_di, area))
                self.computed_triangles.append(retain)
        self.computed_triangles.sort()

    def numpy_free_area_binning(self):
        """ A two-step binning without numpy; 1) de, di, 2) surfaces.

        For this type of analysis, Rohl et al. recommend a grid increment
        of 0.01 A during work with CrystalExplorer.  Thus, this binning
        uses a grid of this granularity, (di, de) = 0.40(0.01)3.00 A, too.

        The subsequent, bin-wise addition of individual triangle surfaces
        equally was tested both with a three-column np.array, as well as
        with a square-matrix like array approach, too.  The approach here
        -- independent on numpy -- however retains best the portability of
        the script with an acceptable rate of processing (e.g., pypy). """

        # binning along de and di:
        pre_binned = []
        for ready_triangle in self.computed_triangles:
            new_di = float(ready_triangle.split()[1])
            new_de = float(ready_triangle.split()[0])
            area = str(ready_triangle.split()[2])

            retain = str("{:3.2f} {:3.2f} {}".format(new_di, new_de, area))
            pre_binned.append(retain)
        pre_binned.sort()

        # binning the surfaces of individual triangles:
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
                self.recorder_register.append(retain)
                # initiate the collection of new information:
                local_area = 0.0
                local_area += float(entry.split()[2])
                old_key = key

        del self.recorder_register[0]  # delete the heading zero entry
        #     # test deposit as permanent file, only non-zero (de,di) bins:
        #     with open("sparse_export.txt", mode="w") as newfile:
        #         for entry in self.recorder_register:
        #             newfile.write("{}\n".format(entry))
        report_start = str("{:<21}".format("non-zero (de,di)-bins:"))
        report_end = str("{:>9}".format(len(self.recorder_register)))
        print("\n{}{}".format(report_start, report_end))

        # report integral_area:
        report_start = str("{:<21}".format("Total surface area:"))
        report_end = str("{:>10}".format(round(integral_area, 5)))
        print("{}{}\n".format(report_start, report_end))

        # normalization of the results
        for entry in self.recorder_register:
            normalized_entry = (
                float(entry.split()[2]) / integral_area) * 100.00
            retain = ' '.join([
                entry.split()[0],
                entry.split()[1], "{:9.8f}".format(normalized_entry)
            ])
            self.normalized_register.append(retain)

    def dat_file_generation(self):
        """ Prepare a .dat file / the Hirshfeld surface 2D fingerprint map.

        To map their differences, 2D fingerprints need to share a uniform
        dimension, i.e., (0.40,0.01,3.00) A for de and di.  Thus, zero-
        entry (di,de)-bins are added to already recorded (di,de)-bins. """
        # prepare blank lists:
        assistance = []
        blank_list = []

        for i in range(40, 301, 1):
            retain = float(i) / float(100)
            assistance.append("{:3.2f}".format(retain))

        for entry in itertools.product(assistance, assistance):
            retain = ' '.join([entry[0], entry[1], "0.0"])
            blank_list.append(retain)

        # join blank_list and recorded list about normalized (di,de)-bins:
        raw_sum_list = self.normalized_register + blank_list
        raw_sum_list.sort()

        # If known to both lists now merged, bins with non-zero entries
        # are sorted after those by the blank list.  Areas will thus be
        # added locally until the key (di,de) of next entry changes; this
        # then triggers the deposit in the dat_register eventually  used
        # to write .dat about the normalized 2D fingerprints. """
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
        output_file = str(self.cxs_file)[:-4] + str(".dat")
        with open(output_file, mode="w") as newfile:
            for entry in dat_register:
                if str("3.00") in entry.split()[1]:
                    retain = str("{}\n\n".format(entry))
                else:
                    retain = str("{}\n".format(entry))
                newfile.write(retain)


def main():
    """ Process the .cxs files identified in the current directory. """
    cxs_register = []

    for file in os.listdir("."):
        if file.endswith(".cxs"):
            cxs_register.append(file)
    cxs_register.sort()

    for element in cxs_register:
        cxs_file = Worker(element)
        cxs_file.file_list()
        cxs_file.file_reader()
        cxs_file.readout_vertices_count()
        cxs_file.readout_indices_count()
        cxs_file.readout_di_count()
        cxs_file.readout_de_count()
        cxs_file.triangle_surfaces()
        cxs_file.numpy_free_area_binning()
        cxs_file.dat_file_generation()


# Enable independent use of this script, directly, without a moderator:
if __name__ == '__main__':
    main()
