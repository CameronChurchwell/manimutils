from manim import *
import numpy as np

class StemPlotAxes(Axes):

    def plot(
        self,
        points,
        x_range=None,
        radius=None,
        stroke_width=1
    ):
        dots = VGroup()
        if x_range is None:
            x_range = (len(points),)

        if radius is None:
            radius = 0.25 * (self.c2p(1, 0)[0] - self.c2p(0, 0)[0])
        for x, y in zip(np.arange(*x_range), points):
            dot = Dot(self.coords_to_point(x, y), radius=radius)
            stem = self.get_line_from_axis_to_point(
                0,
                dot.get_bottom(),
                color=dot.color,
                stroke_width=stroke_width
            )
            dot_and_stem = VDict({
                'dot': dot,
                'stem': stem
            })

            dots.add(dot_and_stem)
        return dots