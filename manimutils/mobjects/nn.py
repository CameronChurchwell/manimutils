from manim import *
import numpy as np
from copy import deepcopy

from manimutils.animations import *

class NeuralNetwork(VDict):

    def __init__(self, layer_sizes: list):
        assert len(layer_sizes) > 1
        neurons = VGroup()
        for layer_size in layer_sizes:
            layer_neurons = VGroup()
            for i in range(0, layer_size):
                layer_neurons.add(Circle(color=WHITE, stroke_width=2))
            layer_neurons.arrange(DOWN)
            neurons.add(layer_neurons)
        neurons.arrange(RIGHT, buff=layer_neurons[0].width)
        connections = VGroup()
        for i in range(0, len(neurons)-1):
            layer_connections = VGroup()
            left = neurons[i]
            right = neurons[i+1]
            for l in left:
                for r in right:
                    conn = Line(l.get_right(), r.get_left(), stroke_width=2)
                    layer_connections.add(conn)
            connections.add(layer_connections)
        super().__init__({
            'neurons': neurons,
            'connections': connections
        })