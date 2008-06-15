import defaults, svg, glyphs, trans, pathdata, curve, plot

# Only bring into the namespace the functions and classes that the user will need
# This distinguishes user interface from internal functions
# (Though the user can still access them, it intentionally requires more typing)
# Internal class members are preceeded by an underscore

from svg import SVG, template, load, load_stream, rgb
from glyphs import uni
from trans import transform, transformation_angle, transformation_jacobian, Delay, Freeze, Pin, window, rotation
from pathdata import poly, bezier, velocity, foreback, smooth
from curve import Curve, format_number, unicode_number, ticks, logticks
from plot import Fig

