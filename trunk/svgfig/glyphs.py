### standard glyphs, may be modifed at runtime by importing glyphs

import svg # don't use glyphs in anything that gets imported into svg.py!

# things that get attached to Curves as marks should assume that the line is horizontal, points to the right, and passes through 0
# these marks are effectively like Pins at (0,0)

arrowhead = svg.SVG("path", "M0 0L-0.75 -1.8 4.5 0 -0.75 1.8 0 0Z", stroke="none", fill="black")

tick = svg.SVG("path", "M0 -1.5L0 1.5")
minitick = svg.SVG("path", "M0 -0.75L0 0.75")
frametick = svg.SVG("path", "M0 0L0 1.5")
frameminitick = svg.SVG("path", "M0 0L0 0.75")

