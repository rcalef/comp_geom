This directory contains a demonstration of an algorithm for computing an approximate
disk packing in the plane, that is, given a set of unit disks in the plane, compute
an approximation of the largest disjoint subset. To accomplish this, we use an
algorithm where we impose a randomly shifted grid, remove from consideration disks
that are not completely contained in any grid cell, and then solve the problem exactly
via exhaustive enumeration within each cell. The approximation is controlled by $k$, the
width of the grid cells (larger grids -> more computation -> better approximation).
The key insight is that within a cell, there can be at most $k^2$ disjoint unit disks,
allowing us to bound the amount of computation we do by only checking subsets of at
most $k^2$ disks within each cell.

To run the demo, please install `matplotlib` and `numpy`:
```
pip install matplotlib numpy
```
and then run the demo with:
```
python gui_demo.py
```

In the visualization, one can either generate unit disks by clicking or by entering a
number in the text box to generate that number of random unit disks. You can then
select the width of the grid cells with the "Grid width" slider. Note that the
demonstration space is set to [50, 50]. Once you're ready, start the visualization with
the "Start" button. The visualization is constructed as follows:
- Randomly shifted grid lines are displayed
- Disks that intersect the grid lines, and thus are not considered are colored red
- The disks contained in the approximate solution obtained by performing the exhaustive
  computation within cells are then shown in purple.

Note that the graphics buttons on the bottom of the viewing area are auto-generated
by matplotlib and shouldn't be used.
