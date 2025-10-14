from manim import *
import numpy as np
from typing import MutableSequence, Sequence, Iterable, Any

class BetterAxes(Axes):

    def __init__(
        self,
        x_range: Sequence[float] | None = None,
        y_range: Sequence[float] | None = None,
        x_length: float | None = round(config.frame_width) - 2,
        y_length: float | None = round(config.frame_height) - 2,
        axis_config: dict | None = None,
        x_axis_config: dict | None = None,
        y_axis_config: dict | None = None,
        tips: bool = True,
        **kwargs: Any,
    ):
        Axes.__init__(
            self,
            x_range=x_range,
            y_range=y_range,
            x_length=x_length,
            y_length=y_length,
            axis_config=axis_config,
            x_axis_config=x_axis_config,
            y_axis_config=y_axis_config,
            tips=tips,
            **kwargs
        )

    def _create_bar(self, x_value, y_value, width=0.5, double_sided=False):
        bottom_edge_center = self.c2p(x_value, 0)
        width_in_screen_space = self.c2p(width, 0)[0] - self.c2p(0, 0)[0]
        height_in_screen_space = self.c2p(0, y_value)[1] - self.c2p(0, 0)[1]

        if double_sided:
            height_in_screen_space *= 2

        bar = Rectangle(
            color=self.get_color(),
            height=height_in_screen_space,
            width=width_in_screen_space
        )
        bar.move_to(bottom_edge_center, aligned_edge=DOWN)
        return bar

    def bar_plot(self, values, x_range=None, width=0.5, double_sided=False):
        bars = VGroup()
        if x_range is None:
            x_range = (len(values),)

        for x, y in zip(x_range, values):
            bar = self._create_bar(x, y, width=width, double_sided=double_sided)
            bars.add(bar)

        return bars

    def stem_plot(
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