! name:    fingerprint.f90
! authors: Paolo Raiteri (praiteri@curtins.edu.au)
!          Andrew Rohl (arohl@curtins.edu.au)
!          Norwid Behrnd (nbehrnd@yahoo.com)
! licence: GPLv2 or (at your option) any later version
! edit:    [2023-04-03 Mon]
!
! Program developed in the Computational Materials Science group
! at Curtin University for the calculation of the fingerprints
! of Hirshfeld surfaces produced by Crystal Explorer
! http://crystalexplorer.scb.uwa.edu.au/index.html
!
! This program is free software; you can redistribute it and/or
! modify it under the terms of the GNU General Public License
! as published by the Free Software Foundation; either version 2
! of the License, or (at your option) any later version.
!
! This program is distributed in the hope that it will be useful,
! but WITHOUT ANY WARRANTY; without even the implied warranty of
! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
! GNU General Public License for more details.
!
! The GNU GPL can also be found at http://www.gnu.org
!
! Compilation instructions:
! The program can be compiled with gfortran
! gfortran fingerprint.f90 -o fingerprint.x
!
! or the intel fortran compiler
! ifort fingerprint.f90 -o fingerprint.x
!
! Usage instructions:
! ./fingerprint.x  input.cxs [standard | translated | extended] output.dat
!
! input.cxs contains the Hirshfeld surfaces generated using the
! CrystalExplorer code at very high resolution by unchecking
! the Remove working files option with the Expert plane
! of the Preferences dialog box
!
! output.dat contains the 2D fingerprint map that can be plotted
! using for example the gnuplot program (a sample plotting script
! is provided below)
!
! ###--- gnuplot script ---###
! set term png size 4096,4096 font "Arial,64" enha lw 10
! set output 'output.png'
! set pm3d map
! set palette defined (0  1.0 1.0 1.0, \
!                    0.00001  0.0 0.0 1.0, \
!                    1  0.0 0.5 1.0, \
!                    2  0.0 1.0 1.0, \
!                    3  0.5 1.0 0.5, \
!                    4  1.0 1.0 0.0, \
!                    5  1.0 0.5 0.0, \
!                    6  1.0 0.0 0.0 )
! set grid lw 0.25
! set size square
! set xtics format "%3.1f"
! set ytics format "%3.1f"
! set xtics 0.4,0.2
! set ytics 0.4,0.2
! set cbrange [0:0.08]
! sp[0.4:2.6][0.4:2.6][:]'output.dat' u 1:2:3  w p pt 5 lc palette z
! #--------------------------#
!
program fingerprint
  use iso_fortran_env, only : ip => int32, dp => real64

  implicit none
! vertices
  integer(kind=ip) :: nvert
  real(kind=dp), allocatable, dimension(:,:) :: vert

! indices
  integer(kind=ip) :: nidx, itmp(3)
  integer(kind=ip), allocatable, dimension(:,:) :: idx

! d_i and d_e
  integer(kind=ip) :: nd
  real(kind=dp) :: ddi, dde
  integer(kind=ip) :: idi, ide
  real(kind=dp), allocatable, dimension(:) :: di, de

  integer(kind=ip) :: i, j

! distribution
  integer(kind=ip) :: nbin
  real(kind=dp) :: xmin, xmax, dx, area, rtmp
  real(kind=dp) :: v1(3), v2(3), v3(3), cost, sint, l1, l2, l3
  real(kind=dp), allocatable, dimension(:,:) :: dist

  character(len=5) :: chr, field
  character(len=100) :: inpfile, outfile, line , lrange

  logical :: lflag

! Parameters for the definition of the grid as in Crystal Explorer
  dx=0.01_dp

! a minimal check and reminder for the CLI
  if (command_argument_count() /= 3) then
    print *, "After compilation of an executable `exe`, the anticipated input is"
    print *, ""
    print *, "    ./exe input.cxs [standard | translated | extended] output.dat"
    print *, ""
    print *, "to cover de and di in a range of [0.4-2.6], [0.8-3.0], or [0.4-3.0] Angstrom."
    stop
  end if

! Reading the first command line argument - cxs input filename
  call getarg(1,inpfile)
  write(*,'(a,a)')"Opening input file        :: ",trim(inpfile)
  open(11,file=inpfile,status='old',form='formatted')

! Reading the type of range for the fingerprint map
  call getarg(2,lrange)
  if (lrange=="standard") then
    xmin=0.4_dp
    xmax=2.6_dp
    write(*,'(a)')"Fingerprint map range     :: standard"
  elseif (lrange=="translated") then
    xmin=0.8_dp
    xmax=3.0_dp
    write(*,'(a)')"Fingerprint map range     :: translated"
  elseif (lrange=="extended") then
    xmin=0.4_dp
    xmax=3.0_dp
    write(*,'(a)')"Fingerprint map range     :: extended"
  else
    write(0,'(a)')"Invalid fingerprint map range type"
    write(0,'(a)')"Choose from standard, translated or extended"
    stop
  endif
  nbin=int((xmax-xmin)/dx)+1

! Reading the second command line argument - fingerprint output filename
  call getarg(3,outfile)
  write(*,'(a,a)')"Opening output file       :: ",trim(outfile)
  open(123,file=outfile,status='unknown',form='formatted')

! Reading the input file
! The Hirshfeld surface is constructed by a collection of edges-sharing triangles
! The input file contains:
! - the cartesian coordinates of the vertices
! - the indices of the three vertices of each triangle
! - the distance of each vertex to the closest internal atom (d_i)
! - the distance of each vertex to the closest external atom (d_e)
  do
    read(11,'(a100)',end=100,err=100)line
    if (len_trim(line)==0) cycle
    read(line,*)chr
    if (chr/="begin") cycle
    read(line,*)chr,field

! Reading the cartesian coordinates of vertices of the surface
    if (field=="verti") then
      read(line,*)chr,field,nvert
      write(*,'(a,i10  )')"Number of vertices points :: ",nvert
      allocate(vert(3,nvert))
      do i=1,nvert
        read(11,*)vert(1:3,i)
      enddo
    endif

! Reading indices of the vertices that form each the triangle
    if (field=="indic") then
      read(line,*)chr,field,nidx
      write(*,'(a,i10  )')"Number of indices points  :: ",nidx
      allocate(idx(3,nidx))
      do i=1,nidx
        read(11,*)itmp(1:3)
        idx(1:3,i)=itmp(1:3)+1
      enddo

    endif

! d_i
! Reading the distance of each vertex to the closest atom inside the surface
    if (field=="d_i") then
      read(line,*)chr,field,nd
      write(*,'(a,i10  )')"Number of d_i points      :: ",nd
      allocate(di(nd))
      do i=1,nd
        read(11,*)di(i)
      enddo
    endif

! d_e
! Reading the distance of each vertex to the closest atom outsiden the surface
    if (field=="d_e") then
      read(line,*)chr,field,nd
      write(*,'(a,i10  )')"Number of d_e points      :: ",nd
      allocate(de(nd))
      do i=1,nd
        read(11,*)de(i)
      enddo
      exit
    endif

  enddo
  close(11)

! Allocate the fingerprint array
  allocate(dist(nbin,nbin))
  dist=0.0_dp

  write(*,'(a,f10.5)')"xmin                      :: ",xmin
  write(*,'(a,f10.5)')"xmax                      :: ",xmax
  write(*,'(a,f10.5)')"dx                        :: ",dx
  write(*,'(a,i10  )')"nbin                      :: ",nbin

! Loop over the surface triangles
  do i=1,nidx

! Calculating the lengths of the triangles' sides
    v1(1:3) = vert(:,idx(2,i)) - vert(:,idx(1,i))
    v2(1:3) = vert(:,idx(3,i)) - vert(:,idx(1,i))
    v3(1:3) = vert(:,idx(3,i)) - vert(:,idx(2,i))
    l1 = sqrt(sum(v1*v1))
    l2 = sqrt(sum(v2*v2))
    l3 = sqrt(sum(v3*v3))

! Sanity check that the 3 points are non degenerate
    if (abs(l1)<1.e-5 .or. abs(l2)<1.e-5 .or. abs(l3)<1.e-5) then
      area=0.
! Calculating the area of each surface triangle
    else
      cost = sum(v1*v2) / l1 / l2
      sint = 1. - cost**2
      if (sint>1.) sint=1.
      if (sint<0.) sint=0.
      sint = sqrt(sint)
      area = 0.5 * l1 * l2 * sint
    endif

! Calculating the d_i for each triangle as the average of the d_i of the vertices
    ddi=0.0_dp
    do j=1,3
      ddi=ddi+di(idx(j,i))
    enddo
    ddi=ddi/3.

! Calculating the d_e for each triangle as the average of the d_i of the vertices
    dde=0.0_dp
    do j=1,3
      dde=dde+de(idx(j,i))
    enddo
    dde=dde/3.

! Calculating the 2D fingerprint of the surface
! indices of the bins
    idi = (ddi-xmin) / dx + 1
    ide = (dde-xmin) / dx + 1

    if (idi>nbin) cycle
    if (ide>nbin) cycle
    if (idi<=0) cycle
    if (ide<=0) cycle

! Tally of the fingerprint map
    dist(idi,ide) = dist(idi,ide) + area

! #ifdef DEBUG
!   write(0,*)i
!   write(0,*)'indices : ',idx(:,i)
!   write(0,*)'vertex 1: ',vert(:,idx(1,i))
!   write(0,*)'vertex 2: ',vert(:,idx(2,i))
!   write(0,*)'vertex 3: ',vert(:,idx(3,i))
!   write(0,*)'area    : ',area
!   write(0,*)'di      : ',ddi,idi
!   write(0,*)'de      : ',dde,ide
! #endif

  enddo
  write(*,'(a,f10.5)')"Total surface area        :: ",sum(dist)
  write(*,*) " " ! place holder between multiple data sets

! Writing the fingerprint map to a file
  dist=100.*dist/sum(dist)
  do idi=1,nbin
    do ide=1,nbin
!      write(123,*)xmin+dx*(idi-1),xmin+dx*(ide-1),dist(idi,ide)
      write(123,'(2F5.2, F15.12)')xmin+dx*(idi-1),xmin+dx*(ide-1),dist(idi,ide)
    enddo
!    write(123,*)  ! Visualizations by gnuplot don't require this separator.
  enddo
  close(123)

  stop
100 write(0,*)"Error in reading the data file"

  stop
end program fingerprint
