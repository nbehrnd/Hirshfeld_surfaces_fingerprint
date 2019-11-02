#include <stdlib.h>
#include <stdio.h>

int main (int argc, char *argv[]) {
  if ( argc != 3 ) {/* argc should be 2 for correct execution */
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
        printf("%f %f %f\n", x1, y1, z1-z2);
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

