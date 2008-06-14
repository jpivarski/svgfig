### standard glyphs, may be modifed at runtime by importing glyphs

import svg # don't use glyphs in anything that gets imported into svg.py!

# things that get attached to Curves as marks should assume that the line is horizontal, points to the right, and passes through 0
# these marks are effectively like Pins at (0,0)

farrowhead = svg.SVG("path", "M0 0L-0.5 -1.2 3 0 -0.5 1.2 0 0Z", stroke="none", fill="black")
farrowhead.repr = "<farrowhead>"

barrowhead = svg.SVG("path", "M0 0L0.5 -1.2 -3 0 0.5 1.2 0 0Z", stroke="none", fill="black")
barrowhead.repr = "<barrowhead>"

tick = svg.SVG("path", "M0 -1.5L0 1.5")
tick.repr = "<tick>"

minitick = svg.SVG("path", "M0 -0.75L0 0.75")
minitick.repr = "<minitick>"

frtick = svg.SVG("path", "M0 0L0 1.5")
frtick.repr = "<frtick>"

frminitick = svg.SVG("path", "M0 0L0 0.75")
frminitick.repr = "<frminitick>"
