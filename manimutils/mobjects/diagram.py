from manim import *
from .varray import VArray


class Diagram(VArray):

    def __init__(self, n_rows, n_cols):
        placeholders = np.empty((n_rows, n_cols), dtype=object)
        for i in range(n_rows):
            for j in range(n_cols):
                placeholders[i, j] = VectorizedPoint().fade(1.)#.set_stroke(opacity=0.).set_fill(opacity=0.)

        super().__init__(placeholders)