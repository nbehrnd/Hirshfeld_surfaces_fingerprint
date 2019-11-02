#!/bin/bash
gnuplot  -e "set term png size 4096,4096 font \"Arial,64\" enha lw 10; set output '$1.png'; unset key; set pm3d map ;set palette defined (-1 \"blue\", 0 \"white\", 1 \"red\") ; set grid lw 0.25; set size square ; set xtics format \"%3.1f\"; set ytics format \"%3.1f\"; set xtics 0.4,0.2 ; set ytics 0.4,0.2 ; set g ;set cbrange [-0.025:0.025]; sp'$1.fprnt' u 1:2:3  w p pt 5 lc palette z"

