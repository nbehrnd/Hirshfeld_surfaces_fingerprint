#!/bin/bash

# name:    plot_diff_finger_png_sparse.sh
# authors: Paolo Raiteri, Andrew Rohl, Norwid Behrnd
# license: GPLv2, or later
# edit:    2019-11-04 (YYYY-MM-DD)
#
# Bash script to plot differences of Hirshfeld fingerprints with gnuplot
#
# The script anticipates the .dat file previously generated by the 
# executable of diff_finger.c as input.  It will truncate the last four
# # characters (.dat) of the file name to use this as an internal label on
# the plot provided as .png bitmap.  The color scheme deployed in the map
# discerns blue (negative), white (zero-level), and red (positive) for the
# difference of normalized fingerprint_A minus normalized fingerprint_B.
# In line with the concept of 'conditional printing' in the .pdf generating
# sparse scripts, only 'non-zero pixels' are put on the explicitly
# transparent canvas.
#
# On the CLI, your instructions follow the pattern of:
#
# chmod u+x plot_diff_finger_png_sparse.sh      # provision of the executable bit
# ./plot_diff_finger_png_sparse.sh example.dat  # generation of the .png plot
#
# to generate example.png.
#
# After drawing, the initial canvas of # 4096 x 4096 px (with 300 dpi,
# this is about 13.7 x 13.7 in or about 5.4 x 5.4 cm) is cropped ('crop'
# instruction) on the fly by pngcairo to box of 3672 x 3229 px (about
# 12.2 x 10.8 in or about 4.8 x 4.2 cm).

gnuplot  -e "
  input = '$1';
  len_root = strlen(input) - 4;
  root = substr(input, 1, len_root);
  output_file = root . '.png';
  set output(output_file);

  stats input u 1 nooutput;
  x_min = STATS_min;
  y_min = STATS_min;
  x_max = STATS_max;
  y_max = STATS_max;
  set term pngcairo transparent size 4096,4096 crop font 'Arial,64' enha lw 10;

  set grid lw 0.5; set size square;
  set xtics 0.4,0.2; set ytics 0.4,0.2;
  set xtics format '%2.1f'; set ytics format '%2.1f';
  set label 'd_e' at graph 0.05,0.90 left front font 'Arial,104';
  set label 'd_i' at graph 0.90,0.05 left front font 'Arial,104';
  set label root at graph 0.05,0.05 left front font 'Arial,104' noenhanced;

  set pm3d map;
  unset key;
  set palette defined (-1 'blue', 0 'white', 1 'red');
  set g;
  set cbrange [-0.025:0.025];
  set xrange [x_min:x_max];
  set yrange [y_min:y_max];
  sp '$1' u 1:2:((abs(\$3)>0) ? \$3 : NaN) w p pt 5 ps 0.001 lc palette z"

# END
