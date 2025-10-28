from manim import *
from math import sqrt

def radical_linear_quadratic(m: float, s: float, r: float, c: float):
    """
    Creates a rate function which is initially radical, then smoothly transitions
    to linear, and then smoothly transitions to quadratic.

    
    Args:
        m: slope of the linear portion
        s: transition point from radical to linear
        r: transition point from linear to quadratic
        c: y-intercept of the linear portion

    Return:
        rate_func: the rate function with the above values
    """

    # assert 0<m<1
    # assert 0<=s<1
    # assert 0<

    a=2*c/(sqrt(s))
    b=m-a/(2*sqrt(s))

    alpha = (c+m-1)/(2*r-r**2-1)
    beta = m-2*alpha*r
    d = 1-alpha-beta

    def radical(x):
        return a*sqrt(x)+b*x
    def linear(x):
        return m*x+c
    def quadratic(x):
        return alpha*x**2+beta*x+d

    @rate_functions.unit_interval
    def piecewise(x):
        if x < s:
            return radical(x)
        elif x <= r:
            return linear(x)
        else:
            return quadratic(x)

    return piecewise