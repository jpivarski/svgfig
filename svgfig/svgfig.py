import svg, defaults, trans, pathdata, curve

# Only bring into the namespace the functions and classes that the user will need
from svg import SVG, rgb, template, load, load_stream
from trans import transform, Delay, Freeze, Pin, window, rotation
from pathdata import poly, bezier, velocity, foreback, smooth
from curve import Curve
