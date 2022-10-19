#!/usr/bin/awk -f

# name:    sum_abs_diffs.awk
# author:  nbehrnd@yahoo.com
# license: GPL v2
# date:    [2022-10-19 Wed]
# edit:

# Compute the difference number on difference Hirshfeld maps with AWK.
#
# The script partially re-implements the Ruby script sum_abs_diff.rb by
# Andrew Rohl and Paolo Raiteri to check if there is a faster access to this
# characteristic.  In difference to the original implementation, this script
# does accepts only one input file at a time, e.g.
#
# ```shell
# awk -f sum_abs_diffs.awk delta_BZAMID00_BZAMID01.dat
# ```
#
# or, after provision of the executable bit (chmod u+x)
#
# ```shell
# ./sum_abs_diffs.awk delta_BZAMID00_BZAMID01.dat
# ```
#
# however is known to work equally well within a shell do-loop, e.g.
#
# ```shell
# for file in delta*.dat; do ./sum_abs_diffs.awk "$file"; done
# ```

$3<0 {sum -= $3}; $3>0 {sum += $3};
END {printf("%s \t %.4f \n", FILENAME, sum)}
