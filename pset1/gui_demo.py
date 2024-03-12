from functools import partial

import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import Button, Slider, TextBox

global delay
global points
global running

def min_dist_bf(pts, ax=None):
    min_i = 0
    min_j = 0
    min_dist = float("inf")
    for i in range(len(pts)-1):
        for j in range(i+1, len(pts)):
            dist = np.sqrt(np.sum((pts[i] - pts[j]) ** 2))

            if ax is not None:
                cleanup = []
                cleanup.append(ax.scatter([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color="gray"))
                cleanup.extend(ax.plot([pts[i, 0], pts[j, 0]], [pts[i, 1], pts[j, 1]], color="gray"))
                plt.draw()
                plt.pause(delay)

                for a in cleanup:
                    a.remove()
            if dist < min_dist:
                min_dist = dist
                min_i = i
                min_j = j
    return min_i, min_j, min_dist

def min_dist_splitting(ax, data):
    global running
    if running:
        return
    running = True
    print(f"brute force: {min_dist_bf(data)}")
    sorted_x = np.argsort(data[:, 0])
    xmin, xmax = ax.get_xlim()


    final = min_dist_recurse(ax,data, sorted_x, xmin, xmax)
    final_i, final_j, _ = final
    xi, yi = data[final_i]
    xj, yj = data[final_j]
    cleanup = []
    cleanup.append(ax.scatter([xi, xj], [yi, yj], color="green"))
    cleanup.extend(ax.plot([xi, xj], [yi, yj], color="green"))
    plt.draw()
    plt.pause(delay)

    print(final)
    running = False
    return final

def min_dist_recurse(ax, data, sorted_x, xmin, xmax):
    if len(sorted_x) == 3 or len(sorted_x) == 2:
        got = min_dist_bf(data[sorted_x], ax)
        i, j, d = got

        cleanup = []
        xi, yi = data[sorted_x[i]]
        xj, yj = data[sorted_x[j]]

        cleanup.append(ax.scatter([xi, xj], [yi, yj], color="red"))
        cleanup.extend(ax.plot([xi, xj], [yi, yj], color="red"))
        plt.draw()
        plt.pause(delay)
        for a in cleanup:
            a.remove()

        return sorted_x[i], sorted_x[j], d

    mid = len(sorted_x) // 2
    mid_x = data[sorted_x[mid]][0]

    # Store this so shading doesn't change limits
    ymin, ymax = ax.get_ylim()
    gen_cleanup = []
    best_cleanup = []

    # Show midline
    gen_cleanup.append(ax.axvline(mid_x, linestyle='--', color="black", alpha = 0.7))
    plt.draw()
    plt.pause(delay)

    # Shade region not in recursion
    tmp = ax.fill_betweenx(y=[ymin, ymax], x1=mid_x, x2=xmax, alpha=0.5, color ="black")
    ax.set_ylim(ymin, ymax)
    plt.draw()
    plt.pause(delay)

    # Begin left recursion
    min_i, min_j, min_d = min_dist_recurse(ax, data, sorted_x[:mid], xmin, mid_x)
    tmp.remove()
    xi, yi = data[min_i]
    xj, yj = data[min_j]
    best_cleanup.append(ax.scatter([xi, xj], [yi, yj], color="red"))
    best_cleanup.extend(ax.plot([xi, xj], [yi, yj], color="red"))

    # Shade region not in recursion
    tmp = ax.fill_betweenx(y=[ymin, ymax], x1=xmin, x2=mid_x, alpha=0.5, color ="black")
    ax.set_ylim(ymin, ymax)
    plt.draw()
    plt.pause(delay)

    r_i, r_j, r_d = min_dist_recurse(ax, data, sorted_x[mid:], mid_x, xmax)
    tmp.remove()
    xi, yi = data[r_i]
    xj, yj = data[r_j]
    best_cleanup.append(ax.scatter([xi, xj], [yi, yj], color="red"))
    best_cleanup.extend(ax.plot([xi, xj], [yi, yj], color="red"))
    plt.draw()
    plt.pause(delay)

    if r_d < min_d:
        min_i = r_i
        min_j = r_j
        min_d = r_d

    strip_l = max(mid_x - min_d, xmin)
    strip_r = min(mid_x + min_d, xmax)
    sorted_y_data = np.argsort(data[sorted_x, 1])
    gen_cleanup.append(ax.fill_betweenx(y=[ymin, ymax], x1=strip_l, x2=strip_r, alpha=0.3, color ="red"))
    plt.draw()
    plt.pause(delay)

    for i in range(1, len(sorted_y_data)):
        real_i = sorted_x[sorted_y_data[i]]
        xi, yi = data[real_i]
        if xi < strip_l or xi > strip_r:
            continue
        for j in range(i-1, -1, -1):
            real_j = sorted_x[sorted_y_data[j]]
            xj, yj = data[real_j]
            if yi - yj > min_d:
                break
            if xj < strip_l or xj > strip_r:
                continue
            d = np.sqrt(np.sum((data[real_i] - data[real_j]) ** 2))

            this_cleanup = []
            this_cleanup.append(ax.scatter([xi, xj], [yi, yj], color="gray"))
            this_cleanup.extend(ax.plot([xi, xj], [yi, yj], color="gray"))
            plt.draw()
            plt.pause(delay)
            for a in this_cleanup:
                a.remove()

            if d < min_d:
                for a in best_cleanup:
                    a.remove()
                best_cleanup = []
                best_cleanup.append(ax.scatter([xi, xj], [yi, yj], color="red"))
                best_cleanup.extend(ax.plot([xi, xj], [yi, yj], color="red"))
                plt.draw()
                plt.pause(delay)

                min_d = d
                min_i = real_i
                min_j = real_j
    for a in gen_cleanup:
        a.remove()
    for a in best_cleanup:
        a.remove()
    plt.draw()
    return min_i, min_j, min_d

def gen_random_points(n=20, xmin = 0, xmax = 10, ymin = 0, ymax = 10, seed = 42):
    pts = np.random.rand(n, 2)

    xrange = xmax - xmin
    pts[:, 0] *= xrange
    pts[:, 0] += xmin

    yrange = ymax - ymin
    pts[:, 1] *= yrange
    pts[:, 1] += ymin
    return pts

class MyText:
    def __init__(
        self,
        ax,
        points,
        message="Enter an int for random points",
    ):
        self.text_box = TextBox(ax, "", textalignment="center")
        self.message = message
        self.points = points

        self.text_box.on_submit(self.__update__)
        self.text_box.set_val(self.message)

    def __update__(self, expr):
        n = None
        try:
            n = int(expr)
        except ValueError:
            self.text_box.set_val("Enter an int for random points")
            return
        if not running:
            self.points.extend(gen_random_points(n=n).tolist())
            update_plot()
            self.text_box.set_val(self.message)


def add_points(expr, points=None, box=None):
    n = None
    try:
        n = int(expr)
    except ValueError:
        box.set_val("Enter an int for random points")
        return
    if not running:
        points.extend(gen_random_points(n=n).tolist())
        update_plot()


def onclick(event):
    if event.button == 1 and event.inaxes == main_ax and not running:  # Left mouse button
        x = event.xdata
        y = event.ydata
        points.append((x, y))
        update_plot()

def update_plot():
    x, y = zip(*points)
    main_ax.scatter(x, y, color="blue")
    plt.draw()

def clear_plot(event):
    if not running:
        points.clear()
        main_ax.cla()
        main_ax.set_xlim(0, 10)
        main_ax.set_ylim(0, 10)
        plt.draw()


# Create a figure and axis
fig, main_ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)
main_ax.set_xlim(0, 10)
main_ax.set_ylim(0, 10)


running = False
delay = 2

axclear = fig.add_axes([0.7, 0.05, 0.1, 0.075])
axnext = fig.add_axes([0.81, 0.05, 0.1, 0.075])
axbox = fig.add_axes([0.1, 0.08, 0.5, 0.05])
axdelay = fig.add_axes([0.2, 0.01, 0.4, 0.05])
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


# Placeholder for storing points
points = []

text_box = MyText(axbox, points)

bnext = Button(axnext, "Start")
bnext.on_clicked(lambda x: min_dist_splitting(main_ax, np.array(points)))
bprev = Button(axclear, "Clear")
bprev.on_clicked(clear_plot)

# Register the onclick event handler
fig.canvas.mpl_connect('button_press_event', onclick)

points


plt.show()