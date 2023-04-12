! name:    sum_abs_diffs02.f90
! author:  nbehrnd@yahoo.com
! license: GPLv2, 2023
! date:    [2023-04-12 Wed]
! edit:
!
! Within the line of thought of a Hirschfeld difference map analysis for which
! the principal computations are provided by Fortran, the compiled executable of
! this source code provides a mean to provide a difference number.  As such, it
! is an analogue of `sum_abs_diffs.rb` as initially provided by Andrew Rohl, and
! Paolo Raiteri for Ruby.
! This concept implementation accounts for knowing - and already at time of
! compilation - that the difference map with the most entries is the one about
! the extended range of de and di, 0.40 to 3.00 A in increments of 0.01 A, or
! 68121 lines at maximum.  Hence, to read all relevant raw data into an array
! of zeroes deemed large nough and subsequent computation of the difference
! number can be faster then a line-by-line file I/O and local computation as
! implemented in `sum_abs_diffs.f90`.

program diff_number02
   use iso_fortran_env, only: int8, real64

   implicit none
   character(len=100) :: filename
   integer(kind=int8) :: fileunit, error
   real(real64), dimension(3, 70000) :: array_data

   array_data = 0.0_real64

   if (command_argument_count() /= 1) stop "Provide delta.dat file as argument."
   call get_command_argument(1, filename)

   open (newunit=fileunit, file=trim(filename), status="old", iostat=error, &
         action="read")
   if (error /= 0) stop "The input file you indicated is inaccessible."

   read (fileunit, '(2(F4.2, 1x), F9.6)', iostat=error) array_data

   write (*, '(A, x, F9.5)') trim(filename), sum(abs(array_data(3, :)))
   close (fileunit)

end program diff_number02
