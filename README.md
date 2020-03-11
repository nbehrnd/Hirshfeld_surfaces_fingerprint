

# Background

Reading crystallographic models as `*.cif` file,
CrystalExplorer<sup><a id="fnr.1" class="footref" href="#fn.1">1</a></sup> assess the electronic interactions of a
molecule with its surrounding crystal.  These are then visualized as
Hirshfeld surfaces,<sup><a id="fnr.2" class="footref" href="#fn.2">2</a></sup> and may be projected as a 2D fingerprint
map.<sup><a id="fnr.3" class="footref" href="#fn.3">3</a></sup>

Carter *et al.* suggest the inspection of *the differences* of these
2D fingerprint maps<sup><a id="fnr.4" class="footref" href="#fn.4">4</a></sup> to ease discern of similarities and
differences when comparing these fingerprints: Contrasting to a
qualitative discern of the maps (e.g. `compare` by
ImageMagick),<sup><a id="fnr.5" class="footref" href="#fn.5">5</a></sup> this approach allows both a visual as well as
numeric quantification of the differences.  This is illustrated
below with the example of two crystallographic model data describing
two polymorphs of benzamide (fig. [3](#org2e284c4)).  The scope of this
analysis may be extended to iso-structural materials, too.

![img](./doc_support/alignment_normal.png "2D fingerprint maps of Hirshfeld surfaces for CCDC model BZAMID01 and BZAMID11 (left and left center), derived from the analysis by CrystalExplorer at *very high* resolution (d<sub>e</sub> and d<sub>i</sub> in the range of 0.40&#x2013;3.00 &Aring;, with a 0.01 &Aring; increment in the plane).  Qualitative difference assignment by superposition as provided by ImageMagick (right center), red pixels indicate difference between the two images inspected.  Simultaneous qualitative and quantitative spatial information are provided by the *difference map* generated with the scripts of this repository (right).")


# Basic use

This type of analysis requires the `.cxs` computed by
CrystalExplorer.<sup><a id="fnr.1.100" class="footref" href="#fn.1">1</a></sup>  For CrystalExplorer, these are intermediate
files only; thus, to retain these, CrystalExplorer's default is to
be changed under File -> Preferences -> Expert.  This adjustment
remains active until you either intentionally set again the check
mark next to "remove working files", or press "Restore Expert
Settings".  After loading the `.cif` file in CrystalExplorer, chose
the "very high" resolution for the surface generation &#x2013; which is
one level above the default.

To continue the analysis, the `.cxs` files by CrystalExplorer are
normalized as 2D fingerprints (`.dat` files) with scripts of this
repository.  Their pairwise comparison yields difference maps, saved
as `diff*.dat` files.  Either map type may be visualized; here, the
interaction with either `gnuplot`, and Python's `matplotlib` serve
as examples.  As all data are stored in plain ASCII, you may use
other programs to visualize the results, too.  The information a
difference map contains may be condensed further to a single figure
of merit.

In the following, two approaches are outlined, which represent
either the

-   direct interaction with the original scripts and data, or
-   the moderated interaction with the data by Python script
    `hirshfeld_moderator.py`.


## Direct interaction

The direct interaction with the `.cxs` data relies on the scripts
provided by Andrew Rohl and Paolo Raiteri, namely
`fingerprint.f90`, `diff_finger.c`, and `sum_abs_diffs.rb`.

-   To compute the normalized 2D Hirshfeld surface *fingerprint
    maps*, the Fortran code has to be compiled.  Examples of freely
    available compilers include `gcc`,<sup><a id="fnr.6" class="footref" href="#fn.6">6</a></sup> or `gfortran.`<sup><a id="fnr.7" class="footref" href="#fn.7">7</a></sup>
    After accessing the folder containing `fingerprint.f90`, an
    executable is compiled by the instruction of
    
        gfortran fingerprint.f90 -o fingerprint.x
    
    In an environment of Unix / Linux / Cygwin, the executable is
    subsequently deployed in a a pattern of
    
        ./fingerprint.x  input.cxs [standard | translated | extended] output.dat
    
    Either `standard`, `translated`, or `extended` as map ranges
    about the interval of \((0.40,2.60)\), \((0.80,3.00)\), or
    \((0.40,3.00)\,\mathrm{\mbox{\AA}}\) along \((d_e,d_i)\) are available
    for normalized 2D fingerprints saved in file `output.dat`.
    
    If working in Windows, the instruction to use the compiled
    executable is in line of
    
        fingerprint.x  input.cxs [standard | translated | extended] output.dat
    
    without leading point and forward slash.

-   The computation of the *difference map* of 2D fingerprints
    requires the compilation of `diff_finger.c`.  Using the freely
    available `gcc`,<sup><a id="fnr.6.100" class="footref" href="#fn.6">6</a></sup> the instruction is
    
        gcc diff_finger.c -o diff_finger
    
    For the subsequent deployment of the executable, identify two
    normalized fingerprint `.dat` files of same map range type.  The
    instruction follows the pattern of
    
        ./diff_finger input_A.dat input_B.dat > difference.dat  # in Linux
        ./diff_finger input_A.dat input_B.dat > difference.dat  # in Windows
    
    to deposit the results in file `difference.dat`.

-   With an installation of Ruby, the difference maps may be
    condensed to a single figure of merit.  The instruction
    of
    
        ruby sum_abs_diffs.rb difference.dat
    
    will print the difference number about `difference.dat`
    scrutinized to the CLI.  Any difference in `difference.dat` will
    be add up as absolute contribution.  The larger the difference
    number, the more different the two fingerprints summed up to
    `difference.dat` are.


## Moderated interaction

Python script `hirshfeld_moderator.py` provides the user a unified
interface to access the functionalities of the original code.  The
script will manage the data by CrystalExplorer, launch of the
analyses, and provision of the results.

On Linux and Windows, the moderator script may relay the
visualization of the fingerprints or difference maps to an
installation of `gnuplot`.  In its absence, the scatter plots may
be drawn with Python's library of `matplotlib`, too.

With assisting `fingerprint_kahan.py`, the moderated analysis may
be performed exclusively in Python, too.  Core computations of
these scripts are written with portability in mind, allowing this
code to work with current Python3, legacy Python2, or performance
improved pypy.

The following sequence describes the analysis of the two benzamide
model data on Linux Xubuntu 18.04.3LTS, with results visualized
with `gnuplot` (version 5.2.7beta):

-   Deposit the Python script, `hirshfeld_moderator.py` either in the
    folder containing the `.cxs` of interest, or one level above the
    corresponding sub-folders.  In case you intend to perform the
    analysis with Python only, deposit its assistance script,
    `fingerprint_kahan.py` into the same folder as
    `hirshfeld_moderator.py`.  Check the accessibility of this folder
    for your Python environment (e.g., WinPython).
    
    If you want to benefit from any of the code `fingerprint.f90`
    (normalized fingerprints), `diff_finger.c` (difference maps), or
    `sum_abs_diffs.rb` (difference number), *i*) deposit the
    corresponding additional scripts in the same folder as
    `hirshfeld_moderator.py`, too.  Ensure you *ii*) equally have
    installed the compilers (`gcc`, `gfortran`) and Ruby, too.

-   You access the moderator interface from the CLI by
    
        1  python hirshfeld_moderator.py -h
    
    &#x2013; which works the same for either current Python 3, legacy
    Python 2, or pypy.

-   The `.cxs` files accessible for the moderator script are
    *listed*, and *copies* of these files are *joined* into a newly
    created working directory in common, `cxs_workshop`.  These
    actions are triggered by either
    
        1  python hirshfeld_moderator.py -l
        2  python hirshfeld_moderator.py -j
    
    Depending on the source of the `.cif` files read by
    CrystalExplorer, the `.cxs` files about the Hirshfeld surfaces
    may contain underscores, e.g., `example_example.cxs`.  To render
    file management (including optional visualization of the results)
    easier, the moderator script truncates the file names of these
    `.cxs` copied into folder `cxs_workshop` to yield the pattern of
    `example.cxs`.  &#x2013; The original `.cxs` files will not be altered.

-   To compute *normalized* 2D Hirshfeld surface *fingerprints*,
    call either one of the two instructions
    
        1  python hirshfeld_moderator.py -n
        2  python hirshfeld_moderator.py -N
    
    To work successfully, the Python-based approach (toggle `-n`)
    requires the simultaneous presence of `fingerprint_kahan.py` in
    the same folder as `hirshfeld_moderator.py`.  It is highly
    recommended to use `pypy` instead of "default Python" (especially
    `CPython3`).  For details, see the technical section.
    
    Otherwise, assuming either a callable installation of `gcc` or
    `gfortran`, toggle `-N` launches the compilation of
    `fingerprint.f90`, shuttles the executable to the data, and
    triggers the computation of the fingerprint maps.

-   The pairwise *comparison* of fingerprints yielding difference
    maps is triggered by either
    
        1  python hirshfeld_moderator.py -c
        2  python hirshfeld_moderator.py -C
    
    The toggle of `-c` triggers the analysis by Python, while toggle
    `-C` (upper case) triggers its analogue with `diff_finger.c`.
    Again, the moderator script attempts in the background the
    compilation of an executable (`gcc`), which is shuttled to the
    data to work there.
    
    While not as much demanding as the computation of normalized
    fingerprints, there is a noticeable gain in performance if the
    Python approach relies on `pypy` instead of `CPython`.

-   For the computation of the *difference number*, initially
    provided by the ruby script, use either of the instructions
    
        1  python hirshfeld_moderator -r
        2  python hirshfeld_moderator -R
    
    to perform the task with either Python (`-r`), or Ruby (`-R`).

The subsequent visualization of the results stored in
ASCII-readable files is optional.  If accessible, the moderator
script may relay the necessary instructions to `gnuplot`.<sup><a id="fnr.8" class="footref" href="#fn.8">8</a></sup> As
an alternative, Python's `matplotlib`<sup><a id="fnr.9" class="footref" href="#fn.9">9</a></sup> may be used instead.

-   To survey quickly the fingerprints and difference maps,
    call either
    
        1  python hirshfeld_moderator -o  # gnuplot instance
        2  python hirshfeld_moderator -O  # matplotlib instance
    
    which will generate bitmap `.png` intentionally kept at small
    dimension for *an overview*.  While displaying the *extended map
    range* \((0.40,3.00)\,\mathrm{\mbox{\AA}}\), dashed lines
    indicate the upper limit of the *standard map range* of
    \((0.40,3.00)\,\mathrm{\mbox{\AA}}\).  At the same time, the
    lower bounds of the *translated map range*
    \((0.80,3.00)\,\mathrm{\mbox{\AA}}\) are indicated by dotted
    lines.  These assist in the selection of a map range in common
    for the synoptic inspection of multiple fingerprints at higher
    quality.
    
    Both surveys equally read out the minimal and maximal
    \((d_i,d_e)\)-bin value per `*.dat` file.  These characteristics
    are both stamped on the `.png` generated, as well as deposit as
    ASCII-readable report (`gp_log.txt`) in the workshop directory
    and may be used to adjust the later `-zmax` scaling (*vide
    infra*).

-   The instructions yielding visualizations in higher quality
    combine the nature of the map (either fingerprint, or difference
    map), the output file format (either bitmap `.png`, or vector
    `.pdf`), as well as the map range (either [s]tandard,
    [t]ranslated, or [e]xtended).  Thus, basic instructions follow
    the *mandatory* pattern of
    
        3  python hirshfeld_moderator.py --fpng s  # calling a gnuplot instance
        4  python hirshfeld_moderator.py --Dpdf e  # calling a matplotlib instance
    
    to generate either a series of fingerprint maps as `.png` in the
    standard map range (example of the gnuplot instance), or generate
    a synoptic series of difference maps as `.pdf` using the extended
    map range (second example, Python `matplotlib`).

-   The moderator script equally offers four *optional* parameters
    which may be used in any combination of with each other in
    presence of the former mandatory parameters:
    
    -   `-a` to use an *alternative* color scheme.  This substitutes
        the jet-like color scheme used in the fingerprints by
        cubehelix, and the blue-white-red diverging map by Kenneth
        Moreland's "bent-cool-warm" map with 64 levels.  Both color
        schemes are perceptual safer, e.g., for some types of color
        blindness, than the default.  The cubehelix equally represents
        the continuous character of the data better than the jet-based
        scheme if constrained to gray scale (e.g., Xerox copies).
    
    -   `-g` to use a neuter gray background.  This may ease the visual
        inspection of the maps.
    
    -   `--zmax` adjusts the \(z\)-range of the scatter plots.  The
        visual surveys by either `gnuplot`, or `matplotlib`, constrain
        the projection of the third dimension to \(0 \le{} z \le{}
               0.08\) for fingerprints, and \(|0 \le{} z \le{} 0.025|\) for
        difference maps.  For each map, the actual readouts of minimal
        and maximal \((d_i,d_e)\)-bin entry are provided with
        `gp_log.txt` and the stamps on the images.
        
        Only the non-surveying visualizations offer to adjust these
        limits in combination of `--zmax` as the keyword. As example,
        the instruction
        
            5  python hirshfeld_moderator.py --dpdf e -a -g --zmax 0.01
        
        will trigger the synoptic fingerprint generation as `.pdf`
        files, generated by `gnuplot` for the extended map range with
        the alternative color scheme, gray background and \(z\)-range
        of \(-0.01 \le{} z \le{} +0.01\).  The significance of the
        \(z\)-range is described later.
    
    -   `-b`.  By default, the visualizations in higher quality
        provided by `matplotlib` *do not* contain the lateral color
        bar.  Using this optional parameter will add the color bar to
        the image.
        
        This responds to observations processing images further, e.g.,
        with inkscape.<sup><a id="fnr.10" class="footref" href="#fn.10">10</a></sup> Contrary to the `.pdf` generated by
        `gnuplot`, the optional use of the neuter gray background
        yields very dark images for export.
    
    ![img](./doc_support/survey.png "Example survey of 2D fingerprint maps (left, center) and difference map plot (right). Intended as guidance for setting up subsequent plots in high resolution, frames mark standard map range (left bottom, dashes) and translated map range (right atop, dots), respectively, while displaying the extended range.  The right bottom corner reports the maximal and minimal *z*-value read from the `.dat` file.")

Below, the effect of color palette and background selection is
illustrated.  They each display the fingerprint about either CSD
model `BZAMID01`, or `BZAMID11`; the difference plot for the two
fingerprints as determined by ImageMagick's `compare`, and the
computed difference map as displayed by gnuplot.

![img](./doc_support/alignment_normal.png "Gnuplot's output of 2D fingerprint maps (very left, left center), ImageMagick's difference with `compare` (right center), and gnuplot's difference map in default mode.")

![img](./doc_support/alignment_normal_gray.png "Processing the data with the optional optional neutral gray background (toggle `-g`), default color palettes.")

![img](./doc_support/alignment_alternate.png "Optional processing with the alternate, perceptual safer color palettes `cubehelix` in 2D fingerprints, and Kenneth Moreland's improved diverging palette `bent-cool-warm` (64 levels); toggle `-a`.")

![img](./doc_support/alignment_alternate_gray.png "Optional simultaneous processing with the alternate color palettes (toggle `-a`) and the optional neutral gray background (toggle `-g`).")

While preparing the diagrams plot as either `*.png`, or resolution
independent format `*.pdf`, the vector-based files tend to be the
smaller ones as their savings by the *conditional plotting*,<sup><a id="fnr.11" class="footref" href="#fn.11">11</a></sup>
are more pronounced, than for the bitmap images.


# Technical background


## Computation of the fingerprint maps

The difference Hirshfeld analysis uses a portion of
CrystalExplorer's results stored in the `.cxs` files.  They define
the Hirshfeld surface as a mesh of vertices with coordinates
\((x,y,z)\) listed below the keyword `begin vertices`.  Three
vertices each constitute an elementary triangle defined by the
indices of its vertices (section `begin indices`) as short hand for
the corresponding apex coordinates.  These later are used to
compute the individual triangle surfaces, eventually summed up to
the integral Hirshfeld surface area.

The vertices' \(d_i\) and \(d_e\) are listed in sections starting with
the keywords `begin d_i` and `begin d_e`, respectively.  The
previous vertices-based definition of individual triangles allows
to compute for each triangle the arithmetical mean value of its
apexes' \(d_i\) to yield the triangle's \(d_i\) value.  Similar to
this, the \(d_e\) value representative for the triangle is the
average of the three apex \(d_e\).

To yield a fingerprint map, the individual triangle areas are
binned along both \(d_i\) and \(d_e\) with an increment of 0.01 &Aring;.
The bin-wise sums of individual triangle areas are then normalized
against the integral Hirshfeld surface area, stored with their
corresponding \((d_i, d_e)\) as `*.dat` file.


## Determination of the triangle area

The reference implementation in `fingerprint.f90` by Andrew Rohl
and Paolo Raiteri relies on vector algebra outlined in the figure
below.  It considers triangles only if all three side lengths are
equal or longer than 10E-5 &Aring;.  The Fortran-based analysis is
accessed from the moderator by

    1  python hirshfeld_moderator.py -N

![img](./doc_support/triangle_equations.png "Computation of triangle area, probed approaches.")

Knowing the side lengths of a triangle, and hence equally its
semi-perimeter, allows to compute the triangle area by the Heron
formula.  Kahan presented an approach alternative to Heron,
improving the area computation of needle-shaped triangles.<sup><a id="fnr.12" class="footref" href="#fn.12">12</a></sup>  This
extends the general scope of the former.

All three approaches were implemented in Python scripts which may
work independently to the moderator script, `fingerprint_rr.py`,
`fingerprint_heron.py`, and `fingerprint_kahan.py`.  For the
Python-based generation of normalized surface fingerprints,

    1  python hirshfeld_moderator.py -n

the presence and module-like use of script `fingerprint_kahan.py`
by the moderator script is assumed as default.  By modification of
the `import fingerprint_kahan` instruction, the moderator script
may use the other assisting scripts instead.


## Computation of difference map

With \(n\) fingerprint `.dat` files in folder `cxs_workshop`, the
number of unique comparisons equates to \(n \cdot (n - 1)/2\) tests.
The moderator script however only submits pairs of fingerprints
with matching map range to this scrutiny.

If you compute the difference map directly with script
`diff_finger.c`, it is your responsibility to ensure both
fingerprints depict either the standard, translated, or extended
map range.


## Visualization of the results

*At present*, the default color schemes used by the higher quality
visualizations echo the ones initially proposed, i.e., a `rainbow`
/ `jet`-like scheme for the continuous character in the fingerprint
maps, and `blue-white-red` about the diverging character in the
difference maps.

*Perceptually*, these maps are not considered as save.  The
*alternate* color schemes, accessible in the moderator script by
optional toggle `-a` thus account for example Kenneth Moreland's
recommendations about this topic and use his `bent_cool_warm`
palette to plot the difference maps instead.

The `cubehelix` palette used as alternative to visualize
fingerprints benefits from a continuous increase of luminosity and
hence is perceptually save.  It is a much more robust palette than
`jet` if the output is constrained to gray scale only (e.g., a
Xerox copy) and accounts for some types of color blindness, too.


# Footnotes

<sup><a id="fn.1" href="#fnr.1">1</a></sup> <http://crystalexplorer.scb.uwa.edu.au/>

<sup><a id="fn.2" href="#fnr.2">2</a></sup> a) "A novel definition of a molecule in a crystal", Spackman,
M. A.; Byrom, P. G. in Chem. Phys. Lett., 1997, 267, 215&#x2013;220, doi
[10.1016/S0009-2614(97)00100-0](https://www.sciencedirect.com/science/article/pii/S0009261497001000?via%3Dihub). b) "Novel tools for visualizing and
exploring intermolecular interactions in molecular crystals",
McKinnon, J. J.; Spackman, M. A.; Mitchell, A. S. in Acta Cryst. B,
2004, 60, 627&#x2013; 668, doi [10.1107/S0108768104020300](http://scripts.iucr.org/cgi-bin/paper?S0108768104020300). c)
<http://130.95.176.70/wiki/index.php/The_Hirshfeld_Surface>

<sup><a id="fn.3" href="#fnr.3">3</a></sup> "Fingerprinting Intermolecular Interactions in Molecular
Crystals", Spackman, M. A.; McKinnon, J. J. in CrystEngComm, 2002, 4,
378&#x2013;392, doi [10.1039/B203191B](https://pubs.rsc.org/en/content/articlelanding/2002/ce/b203191b#!divAbstract).

<sup><a id="fn.4" href="#fnr.4">4</a></sup> "Difference Hirshfeld fingerprint plots: a tool for studying
polymorphs." Carter, D. J.; Raiteri, P.; Barnard, K. R.; Gielink, R.;
Mocerino, M.; Skelton, B. W.; Vaughan, J. G.; Ogden, M. I.; Rohl,
A. L. in CrystEngComm, 2017, 19, 2207&#x2013;2215, DOI: [10.1039/c6ce02535h](https://pubs.rsc.org/en/content/articlelanding/2017/ce/c6ce02535h#!divAbstract).

<sup><a id="fn.5" href="#fnr.5">5</a></sup> <https://imagemagick.org/> Within the bundle, the instruction
following the basic pattern of `compare image_A image_B` provides a
check.  Additional information on
<https://imagemagick.org/script/compare.php>.

<sup><a id="fn.6" href="#fnr.6">6</a></sup> In preparation of this guide, `gcc` in version 7.4.0 was used
successfully.

<sup><a id="fn.7" href="#fnr.7">7</a></sup> In preparation of this guide, `gfortran` in version 7.4.0 was
used successfully.

<sup><a id="fn.8" href="#fnr.8">8</a></sup> The `gnuplot` program is freely available at
<http://www.gnuplot.info>.

<sup><a id="fn.9" href="#fnr.9">9</a></sup> The `matplotlib`-based visualization is assisted by `numpy`.
Note, neither `numpy`, nor `matplotlib` are part of Python's standard
library.  It is thus possible that these have to be installed by
yourself in advance, e.g., with `pip`.  *The possible absence* of
Python modules `numpy` and `matplotlib` however does not hinder the
moderator's action to manage `.cxs` files and the analyses'
computations.

<sup><a id="fn.10" href="#fnr.10">10</a></sup> This editor is freely available at <https://www.inkscape.org>.

<sup><a id="fn.11" href="#fnr.11">11</a></sup> This implementation considers only scatter-plot bins for display
with (|z| > 10E-7).  Thanks to Ethan Merrit who suggested this
additional improvement in a private communication.

<sup><a id="fn.12" href="#fnr.12">12</a></sup> "Miscalculating Area and Angles of a Needle-like Triangle (from
Lecture Notes for Introductory Numerical Analysis Classes)", accessed at
<http://http.cs.berkeley.edu/~wkahan/Triangle.pdf>
