from collections import defaultdict, namedtuple
from math import ceil
from itertools import combinations
from typing import List, Optional

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.collections import PatchCollection
from matplotlib.patches import Circle

from matplotlib.widgets import Button, Slider, TextBox

global delay
global disks
global running
global disk_artist

disk = namedtuple("disk", ["x", "y"])

def draw_plot(m=1):
    global delay
    plt.draw()
    plt.pause(delay * m)

def get_disks(
    n: int = 10,
    canvas_size: float = 50,
    seed: float = 42,
):
    rng = np.random.default_rng(seed)
    xs = rng.random(n) * canvas_size
    ys = rng.random(n) * canvas_size
    return [disk(x, y) for x, y in zip(xs, ys)]

def disks_overlap(d1: disk, d2: disk) -> bool:
    dist = np.sqrt((d1.x - d2.x) ** 2 + (d1.y - d2.y) ** 2)
    return dist <= 2

def get_cell_idx_pt(
    coord: float,
    cell_width: float,
    offset: float,
):
    return (coord - offset) // cell_width

def contained_in_cell(
    coord: float,
    cell_width: float,
    offset: float,
    radius: float = 1,
):
    low_cell = get_cell_idx_pt(coord - radius, cell_width, offset)
    mid_cell = get_cell_idx_pt(coord, cell_width, offset)
    hi_cell = get_cell_idx_pt(coord + radius, cell_width, offset)
    return low_cell == mid_cell and mid_cell == hi_cell

def get_disk_cell_idx(
    d: disk,
    cell_width: float,
    grid_offset_x: float,
    grid_offset_y: float,
    grid_width: int,
) -> Optional[int]:
    if not contained_in_cell(d.x, cell_width, grid_offset_x):
        return None
    if not contained_in_cell(d.y, cell_width, grid_offset_y):
        return None

    # Disk positions are lower bounded by 0, so lowest grid position is 0.
    # Explicitly add the max here to avoid weird behavior around 0 with
    # the offset.
    x_bin = max(get_cell_idx_pt(d.x, cell_width, grid_offset_x), 0)
    y_bin = max(get_cell_idx_pt(d.y, cell_width, grid_offset_y), 0)

    return int(x_bin + (y_bin * grid_width))

def plot_disks(disks, ax, **kwargs):
    patches = []
    for disk in disks:
        patches.append(Circle([disk.x, disk.y], radius=1))
    p = PatchCollection(patches, alpha=0.4, **kwargs)
    return ax.add_collection(p)


def is_disjoint_set(disks: List[disk]) -> bool:
    for (i, d1) in enumerate(disks[:-1]):
        for d2 in disks[i+1:]:
            if disks_overlap(d1, d2):
                return False
    return True

def minimal_set_cell(disks: List[disk], k: float) -> List[disk]:
    max_num = int(k**2)
    for num in range(max_num, 0, -1):
        for check_set in combinations(disks, r=num):
            if is_disjoint_set(check_set):
                return check_set
    raise ValueError(f"must be a disjoint set of some size: {disks}")

def compute_approxmate_packed_set(
    ax: plt.Axes,
    disks: List[disk],
    canvas_size: float,
    k: float,
):
    global disk_artist
    global running
    if running:
        return
    running = True

    grid_offset_x = np.random.random() * k
    grid_offset_y = np.random.random() * k

    num_lines = ceil(canvas_size / k)
    vlines = [i*k + grid_offset_x for i in range(0, num_lines)]
    hlines = [i*k + grid_offset_y for i in range(0, num_lines)]
    for x,y in zip(vlines, hlines):
        ax.axvline(x=x)
        ax.axhline(y=y)
    draw_plot()

    contained = []
    not_contained = []
    binned = defaultdict(list)
    for d in disks:
        idx = get_disk_cell_idx(d, k, grid_offset_x, grid_offset_y, num_lines+1)
        if idx is None:
            not_contained.append(d)
        else:
            contained.append(d)
            binned[idx].append(d)
    disk_artist.remove()

    cleanup = []
    cleanup.append(plot_disks(contained, ax, color="blue"))
    cleanup.append(plot_disks(not_contained, ax, color="red"))
    draw_plot()

    for a in cleanup:
        a.remove()
    cleanup.clear()

    min_disks = []
    for bin_idx, bin_disks in binned.items():
        bin_min_set = minimal_set_cell(bin_disks, k)
        print(f"{bin_idx}: {len(bin_min_set)}")
        min_disks.extend(bin_min_set)
    print(f"min set size: {len(min_disks)}")

    cleanup.append(plot_disks(disks, ax, color="red"))
    cleanup.append(plot_disks(min_disks, ax, color="blue"))
    draw_plot()


    running = False
    return min_disks



class MyText:
    def __init__(
        self,
        ax,
        disks,
        canvas_size,
        message="Enter an int for random disks",
    ):
        self.text_box = TextBox(ax, "", textalignment="center")
        self.message = message
        self.disks = disks
        self.canvas_size = canvas_size

        self.text_box.on_submit(self.__update__)
        self.text_box.set_val(self.message)

    def __update__(self, expr):
        n = None
        try:
            n = int(expr)
        except ValueError:
            self.text_box.set_val("Enter an int for random disks")
            return
        if not running:
            self.disks.extend(get_disks(
                n=n,
                canvas_size=self.canvas_size,
                seed=n,
            ))
            update_plot()
            self.text_box.set_val(self.message)

def onclick(event):
    if event.button == 1 and event.inaxes == main_ax and not running:  # Left mouse button
        x = event.xdata
        y = event.ydata
        disks.append(disk(x, y))
        update_plot()

def update_plot():
    global disk_artist
    main_ax.cla()
    main_ax.set_xlim(0, canvas_size)
    main_ax.set_ylim(0, canvas_size)
    disk_artist = plot_disks(disks, main_ax, color="blue")
    plt.draw()

def clear_plot(event):
    if not running:
        disks.clear()
        main_ax.cla()
        main_ax.set_xlim(0, canvas_size)
        main_ax.set_ylim(0, canvas_size)
        plt.draw()

canvas_size = 50

# Create a figure and axis
fig, main_ax = plt.subplots(figsize=(5, 6))
fig.subplots_adjust(bottom=0.25)
main_ax.set_xlim(0, canvas_size)
main_ax.set_ylim(0, canvas_size)

running = False
delay = 2

axwidth = fig.add_axes([0.2, 0.15, 0.4, 0.05])
axclear = fig.add_axes([0.7, 0.05, 0.1, 0.075])
axnext = fig.add_axes([0.81, 0.05, 0.1, 0.075])
axbox = fig.add_axes([0.1, 0.08, 0.5, 0.05])
axdelay = fig.add_axes([0.2, 0.01, 0.4, 0.05])

width_slider = Slider(
    ax=axwidth,
    label='Grid width',
    valstep=0.5,
    valmin=1,
    valmax=50,
    valinit=5,
)
def update_width(val):
    global k
    k = val
width_slider.on_changed(update_width)


delay_slider = Slider(
    ax=axdelay,
    label='Delay (s)',
    valstep=0.05,
    valmin=0.05,
    valmax=5,
    valinit=1,
)
def update(val):
    global delay
    delay = val
delay_slider.on_changed(update)

k = 5
n = 100
grid_offset_x = np.random.random() * k
grid_offset_y = np.random.random() * k

# Placeholder for storing points
disks = []

text_box = MyText(axbox, disks, canvas_size=canvas_size)

bnext = Button(axnext, "Start")
bnext.on_clicked(lambda x: compute_approxmate_packed_set(main_ax, disks, canvas_size, k))
bprev = Button(axclear, "Clear")
bprev.on_clicked(clear_plot)

# Register the onclick event handler
fig.canvas.mpl_connect('button_press_event', onclick)


plt.show()