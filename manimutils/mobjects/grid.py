from manim import *
import numpy as np
from copy import deepcopy

from manimutils.animations import *

class Grid(VGroup):
    def __init__(self, N, M, square_size, **kwargs):
        self.squares = np.array([[]])
        super().__init__()
        self.N = N
        self.M = M
        self.square_size = square_size
        self.squares = np.empty((N, M), dtype=object)

        # create squares
        for i in range(0, N):
            for j in range(0, M):
                square = Square(side_length=square_size, **kwargs)
                if 'stroke_width' not in kwargs:
                    square.set_stroke(width=2)
                square.move_to([j*square_size, -i*square_size, 0])
                self.squares[i,j] = square
                self.add(square)
        self.center()

    def clone(self):
        return deepcopy(self)

    def __getitem__(self, slices):
        result = self.squares[slices]
        if isinstance(result, np.ndarray):
            slice = Grid(result.shape[0], result.shape[1], self.square_size)
            slice.squares = result
            slice.submobjects = []
            slice.add(list(result.flatten()))
            return slice
        else:
            return result