/* name:    diff_finger.c
** authors: Paolo Raiteri (p.raiteri@curtin.edu.au),
**          Andrew Rohl (a.rohl@curtin.edu.au),
**          Norwid Behrnd (nbehrnd@yahoo.com)
** license: GPLv2 or (at your option) any later
** edit:    2022-10-10 (YYYY-MM-DD)
**
** This C program was developed in the Computational Materials Science
** group at Curtin University (Australia) to extend the analysis of
** fingerprints of Hirshfeld surfaces assessed by CrystalExplorer.  Its
** first presentation to the scientific community was in CrystEngComm,
** 2017, 19, 2207--2215 (doi 10.1039/c6ce02535h).
**
** Firstly, compile this code into an executable.  With gcc, for example,
** your input on the CLI is
**
** gcc diff_finger.c -o diff_finger
**
** Subsequently, indicate two fingerprint .dat files to be compared with
** each other, and where to store permanently the results.  The later is
** again a map, now about the differences of the two fingerprint maps
** just read.  On the CLI, your instruction follows the pattern of
**
** ./diff_finger input_A.dat input_B.dat > difference.dat
**
** You may visualize the result for example with gnuplot.  While this is
** not a task for this code, a minimal set of instructions to relay this
** to gnuplot is offered below.  It assumes file "difference.dat" to be
** read and yields the map as "difference.png":
**
** ### ---- gnuplot script ---- ####
** set output "difference.png"
**
** set terminal pngcairo size 4096,4096 font "Arial, 64" enha lw 10
** set grid
** set xtics 0.4, 0.2
** set ytics 0.4, 0.2
** set label 'd_e' at graph 0.05, 0.90 left front font 'Arial, 104'
** set label 'd_i' at graph 0.90, 0.05 left front font 'Arial, 104'
**
** set pm3d map
** unset key
** set palette defined (-1 "blue", 0 "white", 1 "red")
** set g
** set cbrange [-0.025:0.025]
** sp "difference.dat" u 1:2:3  w p pt 5 ps 0.05 lc palette z
** ### ------------------------ ####
**
** The script is known to work with gnuplot (release 5.2.7beta).  There
** is additional information provided on the project's github sites,
** including test data. */

#include <stdlib.h>
#include <stdio.h>

int main (int argc, char *argv[]) {
  if ( argc != 3 ) {/* argc should be 3 for correct execution */
     printf("usage: %s file1 file2\n", argv[0]);
     exit(EXIT_FAILURE);
  }

  FILE *fp1 = fopen(argv[1], "r");

  /* fopen returns 0, the NULL pointer, on failure */
  if (fp1 == 0) {
    printf("Could not open file %s\n", argv[1]);
    exit(EXIT_FAILURE);
  }

  FILE *fp2 = fopen(argv[2], "r");

  /* fopen returns 0, the NULL pointer, on failure */
  if (fp2 == 0) {
    printf("Could not open file %s\n", argv[2]);
    exit(EXIT_FAILURE);
  }

  char line_file1[256];
  char line_file2[256];
  float x1,y1,z1;
  float x2,y2,z2;
  int args_assigned1;
  int args_assigned2;

  while (fgets(line_file1, sizeof line_file1, fp1) != NULL) { /* read a line */
    if (fgets(line_file2, sizeof line_file2, fp2) == NULL) {
      printf("File %s is longer than file %s\n", argv[1], argv[2]);
      exit(EXIT_FAILURE);
    }
    args_assigned1 = sscanf(line_file1, "%f %f %f", &x1, &y1, &z1);
    args_assigned2 = sscanf(line_file2, "%f %f %f", &x2, &y2, &z2);
    if (args_assigned1 == -1) { /* blank line in file 1 */
      if (args_assigned2 == -1) { /* corresponding blank line in file 2 */
        printf("\n");
      }
      else {
        printf("blank line in %s but not %s\n", argv[1], argv[2]);
        exit(EXIT_FAILURE);
      }
    }
    else if (args_assigned1 == 3) { /* have x, y, z triplet from file 1 */
      if (args_assigned2 == 3) { /* and triplet in file 2 */
        printf("%4.2f %4.2f %9.6f\n", x1, y1, z1-z2);
      }
      else {
        printf("Invalid line in %s: %s", argv[2], line_file2);
        printf("args_assigned1 = %d, args_assigned2 = %d\n", args_assigned1, args_assigned2);
        exit(EXIT_FAILURE);
      }
    }
    else {
      printf("Invalid line in %s: %s", argv[1], line_file1);
      printf("args_assigned1 = %d, args_assigned2 = %d\n", args_assigned1, args_assigned2);
      exit(EXIT_FAILURE);
    }
  }
  if (fgets(line_file2, sizeof line_file2, fp2) != NULL) {
    printf("File %s is shorter than file %s\n", argv[1], argv[2]);
     exit(EXIT_FAILURE);
  }
  fclose(fp1);
  fclose(fp2);
}

