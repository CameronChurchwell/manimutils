from manim import *
import numpy as np
from typing import Iterable
from manim.typing import Vector3D

class VArray(VMobject):

    def __init__(self, array: np.ndarray, **kwargs):
        self.submob_array = array
        super().__init__(**kwargs)

    @property
    def submobjects(self):
        return self.submob_array.flatten().tolist()

    @submobjects.setter
    def submobjects(self, _):
        pass

    @property
    def shape(self):
        return self.submob_array.shape

    def __getitem__(self, slices):
        result = self.submob_array[slices]

        if isinstance(result, np.ndarray):
            slice = VArray(result)
            return slice
        else:
            return result

    def __setitem__(self, idx, value):
        self.submob_array[idx] = value

    def arrange_in_grid(
        self,
        buff: float | tuple[float, float] = LARGE_BUFF,
        cell_alignment: Vector3D = ORIGIN,
        row_alignments: str | None = None,  # "ucd"
        col_alignments: str | None = None,  # "lcr"
        row_heights: Iterable[float | None] | None = None,
        col_widths: Iterable[float | None] | None = None,
        flow_order: str = "rd",
        **kwargs,
    ):
        return super().arrange_in_grid(*self.shape, buff, cell_alignment, row_alignments, col_alignments, row_heights, col_widths, flow_order, **kwargs)
