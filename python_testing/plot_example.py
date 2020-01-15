#!/usr/bin/env python3
# name:   plot_example.py
# author: nbehrnd@yahoo.com
# date:   2020-01-15 (YYYY-MM-DD)
# edit:
#
""" Aims to access gnuplot directly, without intermediate interface. """
import fnmatch
import os
import subprocess as sp
import sys

# placeholder, identification of the data to work on, start:
os.chdir("cxs_workshop")
register = []
for file in os.listdir("."):
    if fnmatch.fnmatch(file, "*.dat"):
        register.append(file)
register.sort()
print(register)
# placeholder, identification of the data to work on, end.


def plot_map():
    """ Analysis and plot inspired by the first answer seen. """
    for entry in register:
        # define the deposit file:
        input_file = str(entry)
        output_file = str(entry)[:-4] + str(".png")

        pl = ["set terminal pngcairo"]
        pl += ["input = '{}'".format(input_file)]
        pl += ["set output '{}'".format(output_file)]

        # brief statistics per .cxs file read:
        pl += ['stats input u 3 nooutput']
        pl += ['z_min = sprintf("%1.6f", STATS_min)']
        pl += ['z_low = "zmin: " . z_min']
        pl += ['z_max = sprintf("%1.6f", STATS_max)']
        print(pl)
#        pl += ["stats input u 3"]  # place holder

        pl += ["set title '{}' noenhanced".format(input_file)]
        pl += ["unset key"]

        pl += ["set size square; set pm3 map; set palette cubehelix"]
        pl += ["sp input u 1:2:3"]

        # pl += ['e']  # not accepted in Linux
        pt = '\n'.join(pl)
        sp.run(['gnuplot'], input=pt.encode('utf-8'), check=True)
        
        # os.remove(entry)

plot_map()
sys.exit(0)
