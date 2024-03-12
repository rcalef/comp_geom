This directory contains a demonstration of an algorithm for computing the closest pair
in a set of points in the 2D plane. The algorithm is the same as the one presented in
lecture, which is also described [here](https://www.geeksforgeeks.org/closest-pair-of-points-using-divide-and-conquer-algorithm/).

To run the demo, please install `matplotlib` and `numpy`:
```
pip install matplotlib numpy
```
and then run the demo with:
```
python gui_demo.py
```

In the visualization, one can either generate points by clicking or by entering a
number in the text box to generate that number of random points. Once you're ready,
start the visualization with the "Start" button. The visualization is constructed as
follows:
- Vertical dashed lines indicate splitting boundaries
- Inactive regions are shaded grey (i.e. the active region is the white one)
- Points and distances being tested are indicated by grey points and lines
- Current closest pairs and their distance in a region are indicated in red
- The "active" strip used in the merging step is shown as a transparent red strip
- The final closest pair and distance are shown in green at the end of the algorithm

Note that the graphics buttons on the bottom of the viewing area are auto-generated
by matplotlib and shouldn't be used.

For an implementation of the algorithm without the various plotting statements
from the demo, please see `closest_points.ipynb`. This notebook also contains
benchmarking against a brute force solution. On my 2022 MacbBook Pro with a M2 chip
and using 1000 points, the brute force algorithm runs in about 1 second, while the
binary splitting algorithm runs in about 7 ms$.