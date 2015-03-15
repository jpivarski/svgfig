_(This page applies only to the 1.x branch of SVGFig.)_

The original motivation for arbitrary coordinate transformations was
to generalize the process of making different kinds of plots.  Many
plotting packages have a special function for generating radial plots,
but no way to draw other projections.  If you know the transformation
function for a given projection, you can draw it.

There should probably be a convenience function for this very common
special case, but internally, it would do the following.

```
from svgfig import *
from math import *
import random

angle_axis = LineAxis(5, 0, 5, 2*pi, 0, 2*pi)
angle_axis.text_start = -2.5
angle_axis.text_angle = 180.
angle_axis.ticks = [x*2*pi/8 for x in range(8)]
angle_axis.labels = lambda x: "%g" % (x*180/pi)
angle_axis.miniticks = [x*2*pi/8/9 for x in range(8*9)]

radial_axis = XAxis(0, 5, aty=pi/2)
radial_axis.text_start = 5
radial_axis.text_angle = 90.
radial_axis.ticks = range(5)

points = [(max(0.5, random.gauss(2.5, 1)), random.uniform(-pi, pi), max(0.1, random.gauss(0.3, 0.1))) for i in range(10)]
xerr = XErrorBars(points)
yerr = YErrorBars(points)
dots = Dots(points, make_symbol("name", stroke="black", fill="red", stroke_width="0.25pt"))
Fig(Fig(angle_axis, radial_axis, xerr, yerr, dots, trans="x*cos(y), x*sin(y)")).SVG(window(-6, 6, -6, 6)).inkview()
```

| ![![](http://svgfig.googlecode.com/svn/wiki/ExampleRadialPlot.png)](http://svgfig.googlecode.com/svn/wiki/ExampleRadialPlot.svg) |
|:---------------------------------------------------------------------------------------------------------------------------------|
| [ExampleRadialPlot.svg](http://svgfig.googlecode.com/svn/wiki/ExampleRadialPlot.svg) |