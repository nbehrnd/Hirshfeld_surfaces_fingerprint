! name:    diff_finger.f90
! author:  nbehrnd@yahoo.com
! license: GPLv2, 2023
! date:    [2023-04-04 Tue]
! edit:
!
! Within the greater aim to provide a delta-Hirshfeld analysis where the
! principal computations are provided by Fortran, the compiled executable of
! this source code provides an analogue to C-based `diff_finger.c` (by Andrew
! Rohl and Paolo Raiteri) to compute a difference map of two normalized 2D
! projections `fingerprint.f90` provides.
! Though already functional, it still is considered as concept study (and hence
! kept in the incubator).

program diff_finger_f90
   use iso_fortran_env, only: ip => int32, dp => real64
   implicit none
   character(len=100) :: filename_a, filename_b
   real(kind=dp), dimension(:, :), allocatable :: array_a, array_b, array_c
   integer(kind=ip):: i, length_a, length_b

! get to know the data to process
   if (command_argument_count() /= 2) then
      print *, "After compilation of an executable `exe`, the anticipated input"
      print *, "   ./exe input1.dat input2.dat > output.dat"
      print *, "requires exactly two input files (100 characters maximum)."
      stop
   end if

   call get_command_argument(1, filename_a)
   call get_command_argument(2, filename_b)

! perform some characterization of the data files, i.e.
!! number of lines in the file
   length_a = linecount(filename_a)
   length_b = linecount(filename_b)
!! read the arrays
   array_a = array_reader(filename_a, length_a)
   array_b = array_reader(filename_b, length_b)

!! only consider maps with same (detail of) coverage of de/di
   if (size(array_a) /= size(array_b)) stop "Difference: map coverage."
   if (array_a(1, 1) /= array_b(1, 1)) stop "Difference: lower map boundery."
   if (array_a(1, length_a) /= array_b(1, length_a)) stop "Difference: upper map boundery."

! the eventual computation of the difference
   allocate (array_c(3, length_a))
   array_c(1:2, :) = array_a(1:2, :)
   array_c(3, :) = array_a(3, :) - array_b(3, :)

   do i = 1, length_a
      write (*, "(2(F4.2, x), F9.6)") array_c(:, i)
   end do

contains

   integer(kind=sp) function linecount(filename) result(nlines)
      ! report the number of lines in a given file as an integer number
      use iso_fortran_env, only: int8, sp => int32
      character(len=*), intent(in) :: filename
      integer(int8) :: fileunit, error
      nlines = 0

      open (newunit=fileunit, file=filename, status="old", action="read", &
            iostat=error)
      if (error /= 0) stop "The indicated input file is inaccessible."

      do
         read (fileunit, *, iostat=error)
         if (error /= 0) exit
         nlines = nlines + 1
      end do

      close (fileunit)
   end function linecount

   function array_reader(filename, length) result(array)
      ! read the array from the dat file
      use iso_fortran_env, only: ip => int32, dp => real64
      character(len=*), intent(in) :: filename
      integer(kind=ip), intent(in) :: length
      integer(kind=ip) :: fileunit, error, i, j
      real(kind=dp), dimension(:, :), allocatable :: array

      open (newunit=fileunit, file=filename, status="old", action="read", &
            iostat=error)
      if (error /= 0) stop "Function array_reader can not access the input file."

      ! At time of compilation, the length of the 3-column array (x,y,z) is
      ! unknown, yet this variable is determined by function linecount.
      allocate (array(3, length))
      read (fileunit, '(2(F4.2, 1x), F14.12)') ( &
         (array(i, j), i=1, 3), j=1, length - 1)
      if (error /= 0) stop ! reaching the file end is a plausible cause

      close (fileunit)
   end function array_reader

end program diff_finger_f90
