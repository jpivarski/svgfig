_(This page applies only to the 1.x branch of SVGFig.)_

# class LineAxis #

LineAxis draws an axis along an arbitrary line.  If the coordinate
transformation is curved, the axis will curve with it.

## Arguments ##

**LineAxis(x1, y1, x2, y2, start, end, ticks, miniticks, labels, logbase, arrow\_start, arrow\_end, text\_attr, attribute=value)**

| x1, y1 | _**required**_ | starting point |
|:-------|:---------------|:---------------|
| x2, y2 | _**required**_ | ending point |
| start, end | _default_=0, 1 | values to start and end labeling |
| ticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| miniticks | _default_=True | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| labels | True | request tick labels according to the [standard tick label specification](TickSpecification.md) |
| logbase | _default_=None | if a number, the x axis is logarithmic with ticks at the given base (10 being the most common) |
| arrow\_start | _default_=None | if a new string identifier, draw an arrow at the low-end of the axis, referenced by that identifier; if an SVG marker object, use that marker |
| arrow\_end | _default_=None | if a new string identifier, draw an arrow at the high-end of the axis, referenced by that identifier; if an SVG marker object, use that marker |
| text\_attr | _default_={} | SVG attributes for the text labels |
| attribute=value pairs | _keyword list_ | SVG attributes |

Tick labels on a LineAxis do not need to specify real coordinate positions; they are uniformly spaced between `start` and `end`.

Arrows must be referenced by new string identifiers, otherwise, they
could reference the wrong markers.

## SVG method ##

LineAxis has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Defaults ##

LineAxis has defaults as described in [General features for all primitives](GeneralPrimitive.md).

| defaults | {"stroke-width":"0.25pt"} | default SVG attributes for the curve and tick marks |
|:---------|:--------------------------|:----------------------------------------------------|
| text\_defaults | {"stroke":"none", "fill":"black", "font-size":5} | default SVG attributes for the text |

LineAxis also has the same defaults as [Curve](ClassCurve.md).

| random\_sampling | True | if False, bisect with a point exactly halfway between pairs of points; if True, randomly choose a point between 30% and 70% |
|:-----------------|:-----|:----------------------------------------------------------------------------------------------------------------------------|
| recursion\_limit | 15 | number of subdivisions before giving up; if 15, sampling algorithm can visit _at most_ 2<sup>15</sup> points |
| linearity\_limit | 0.05 | maximum deviation (in SVG units) from a straight line |
| discontinuity\_limit | 5 | minimum deviation (in SVG units) between points that is considered continuous |

## Special data members ##

After the LineAxis has been evaluated with **SVG**, it gains three
new data memebers.
  * **last\_ticks**: explicit dict of value, label pairs for major ticks
  * **last\_miniticks**: explicit list of values for miniticks
  * **last\_samples**: an iterable of Curve.Sample objects:
```
>>> c = LineAxis(funcRtoR("x**2"), 0, 1)
>>> c.SVG()
>>> for s in c.last_samples:
...     print s.x, s.y, s.X, s.Y
...
```

Curve.Sample has four data members, `x`, `y`, `X`, `Y`.  These are
coordinates in local (lowercase) and global (uppercase) coordinates.
If a coordinate is `None`, there is a break in the curve, due to a
discontinuity in the supplied function.