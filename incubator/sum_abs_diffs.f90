! name:    sum_abs_diffs.f90
! author:  nbehrnd@yahoo.com
! license: GPLv2, 2023
! date:    [2023-04-04 Tue]
! edit:    [2023-04-12 Wed]
!
! Within the line of thought of a Hirschfeld difference map analysis for which
! the principal computations are provided by Fortran, the compiled executable of
! this source code provides a mean to provide a difference number.  As such, it
! is an analogue of `sum_abs_diffs.rb` as initially provided by Andrew Rohl, and
! Paolo Raiteri for Ruby.
! Though functional, this implementation is considered as a concept study and
! hence a contribution to the incubator only.

program diff_number
   use iso_fortran_env, only: int8, real64

   implicit none
   character(len=100) :: filename
   integer(kind=int8) :: fileunit, error
   real(real64) :: x, y, z, difference_number

   difference_number = 0.0_real64

   if (command_argument_count() /= 1) stop "Provide delta.dat file as argument."
   call get_command_argument(1, filename)

   open (newunit=fileunit, file=trim(filename), status="old", iostat=error, &
         action="read")
   if (error /= 0) stop "The input file you indicated is inaccessible."

   do
      ! read (fileunit, *, iostat=error) x, y, z
      read (fileunit, '(2(F4.2, 1x), F15.12 )', iostat=error) x, y, z
      difference_number = difference_number + abs(z)

      if (error /= 0) then  ! reaching the end of the file is a plausible cause
         write (*, '(A, 1x, F9.5)') trim(filename), difference_number
         stop
      end if
   end do

   close (fileunit)
end program diff_number
