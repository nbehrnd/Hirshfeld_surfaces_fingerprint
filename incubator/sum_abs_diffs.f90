! name:    sum_abs_diffs.f90
! author:  nbehrnd@yahoo.com
! license: GPL v2
! date:    [2022-10-19 Wed]
! edit:
!
! Compute the difference number with Fortran.
!
! The aim of this proof of concept is twofold:
! + The provision of the computation of the difference number in Fortran
!   may eventually reduce the number of programming languages to be used
!   to perform the numeric analysis.
! + Contrasting to the "all Python approach" already available, an analogue
!   "all Fortran approach" is anticipated to process CrystalExplorer's data
!   considerably faster, than the former.
!
! The intended use is to process one file/difference map at a time:
!
! ```shell
! gfortran sum_abs_diffs.f90 -o sum_abs_diffs  # compilation
! ./sum_abs_diffs delta_BZAMID00_BZAMID01.dat  # example of application
! ```
!
! To process multiple files in a batch, you may consider a sequential
! do-loop in your shell, or using GNU Parallel.  An example of the later
! option is
!
! ```shell
! ls delta_BZAMID00_BZAMID*.dat | parallel -j 4 "./sum_abs_diffs {}"
! ```
! for up to four concurrent jobs.
!
! The source code was written and tested in Linux Debian 12/bookworm (branch
! testing) with GNU Fortran ((Debian 12.2.0-3) 12.2.0).

program diff_number
   implicit none
   integer :: CLI_parameters
   character(len=255) :: filename

   integer :: unit, error
   real :: x, y
   integer, parameter :: ikind = selected_real_kind(15, 9)
   real(kind=ikind) :: z, difference_number

   difference_number = 0.0

! Identify the file to process.
   CLI_parameters = command_argument_count()

   select case (CLI_parameters)
   case (1)
      call get_command_argument(1, filename)
      filename = trim(filename)

   case default
      write (*, '(A)') "After compilation of the source code, e.g."
      write (*, '(A)') ""
      write (*, '(A)') "    gfortran sum_abs_diffs.f90 -o sum_abs_diffs"
      write (*, '(A)') ""
      write (*, '(A)') "use exactly one file to process, e.g."
      write (*, '(A)') ""
      write (*, '(A)') "    ./sum_abs_diffs [delta_BZAMID00_BZAMID01.dat]"
      stop 1
   end select

! Compute the difference number while reading the raw data.
   open (newunit=unit, file=filename, status="old", action="read", iostat=error)
   if (error /= 0) then
      write (*, '(A)') "Input error; this file is inaccessible.  Exit."
      stop 2
   end if

   do
      read (unit, '(2F5.2, F9.6)', iostat=error) x, y, z
      if (error == 0) then
         difference_number = difference_number + abs(z)
      else
         exit
      end if
   end do
   close (unit)

! Report filename and difference number to the CLI.
   write (*, '(A, F9.4)') trim(filename), difference_number
end program diff_number
