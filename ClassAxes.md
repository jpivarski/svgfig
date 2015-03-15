_(This page applies only to the 1.x branch of SVGFig.)_

# class Axes #

Axes draws coordinate axes.  The grid will be curved in
non-linear transformations, and can be a good way to "feel" the shape
of the transformation.

## Arguments ##

**Axes(xmin, xmax, ymin, ymax, atx, aty, xticks, xminiticks, xlabels, xlogbase, yticks, yminiticks, ylabels, ylogbase, arrows, text\_attr, attribute=value)**

| xmin, xmax | _**required**_ | the x range |
|:-----------|:---------------|:------------|
| ymin, ymax | _**required**_ | the y range |
| atx, aty | _default_=0, 0 | point where the axes try to cross; if outside the range, the axes will cross at the closest corner |
| xticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| xminiticks | _default_=True | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| xlabels | True | request tick labels according to the [standard tick label specification](TickSpecification.md) |
| xlogbase | _default_=None | if a number, the x axis is logarithmic with ticks at the given base (10 being the most common) |
| yticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| yminiticks | _default_=True | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| ylabels | True | request tick labels according to the [standard tick label specification](TickSpecification.md) |
| ylogbase | _default_=None | if a number, the y axis is logarithmic with ticks at the given base (10 being the most common) |
| arrows | _default_=None | if a new string identifier, draw arrows referenced by that identifier |
| text\_attr | _default_={} | SVG attributes for the text labels |
| attribute=value pairs | _keyword list_ | SVG attributes for all lines |

To draw arrows on the ends of the axes, pass a new text identifier to
`arrows`.  Axes will then create four new SVG marker objects with this
structure:
```
SVG("marker", SVG("path", d="M 9 3.6 L 10.5 0 L 0 3.6 L 10.5 7.2 L 9 3.6 Z"), \
              viewBox="0 0 10.5 7.2", refX="9", refY="3.6", markerWidth="10.5", markerHeight="7.2", \
              markerUnits="strokeWidth", orient="auto", stroke="none", fill="black")
```
and identifiers ending in ".xstart", ".xend", ".ystart", ".yend".
These identifiers must be unique, or the axes will reference the wrong markers.

## Defaults ##

Axes have the following defaults, as described in [General features for all primitives](GeneralPrimitive.md).

| defaults | {"stroke-width":"0.25pt"} |
|:---------|:--------------------------|
| text\_defaults | {"stroke":"none", "fill":"black", "font-size":5} |

# class XAxis #

Only draws the x axis.

## Arguments ##

**XAxis(xmin, xmax, aty, ticks, miniticks, labels, logbase, arrow\_start, arrow\_end, exclude, text\_attr, attribute=value)**

| xmin, xmax | _**required**_ | the x range |
|:-----------|:---------------|:------------|
| aty | _default_=0 | y position to draw the axis |
| ticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| miniticks | _default_=True | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| labels | True | request tick labels according to the [standard tick label specification](TickSpecification.md) |
| logbase | _default_=None | if a number, the x axis is logarithmic with ticks at the given base (10 being the most common) |
| arrow\_start | _default_=None | if a new string identifier, draw an arrow at the low-end of the axis, referenced by that identifier; if an SVG marker object, use that marker |
| arrow\_end | _default_=None | if a new string identifier, draw an arrow at the high-end of the axis, referenced by that identifier; if an SVG marker object, use that marker |
| exclude | _default_=None | if a (low, high) pair, don't draw text labels within this range |
| text\_attr | _default_={} | SVG attributes for the text labels |
| attribute=value pairs | _keyword list_ | SVG attributes for all lines |

The `exclude` option is provided for Axes to keep text from
overlapping where the axes cross.  Normal users are not likely to need
it.

## Defaults ##

XAxis has the following defaults, as described in [General features for all primitives](GeneralPrimitive.md).

| defaults | {"stroke-width":"0.25pt"} | default SVG attributes for all lines |
|:---------|:--------------------------|:-------------------------------------|
| text\_defaults | {"stroke":"none", "fill":"black", "font-size":5, "dominant-baseline":"text-before-edge"} | default SVG attributes for text labels |
| text\_start | -1 | position relative to the axis (in SVG units) to set text labels |
| text\_angle | 0 | angle (in degrees) to rotate text |
| tick\_start | -1.5 | position relative to the axis (in SVG units) to start the ticks |
| tick\_end | 1.5 | position relative to the axis (in SVG units) to end the ticks |
| minitick\_start | -1.5 | position relative to the axis (in SVG units) to start the miniticks |
| minitick\_end | 1.5 | position relative to the axis (in SVG units) to end the miniticks |

XAxis also has the same defaults as [Curve](ClassCurve.md).

| random\_sampling | True | if False, bisect with a point exactly halfway between pairs of points; if True, randomly choose a point between 30% and 70% |
|:-----------------|:-----|:----------------------------------------------------------------------------------------------------------------------------|
| recursion\_limit | 15 | number of subdivisions before giving up; if 15, sampling algorithm can visit _at most_ 2<sup>15</sup> points |
| linearity\_limit | 0.05 | maximum deviation (in SVG units) from a straight line |
| discontinuity\_limit | 5 | minimum deviation (in SVG units) between points that is considered continuous |

# class YAxis #

Only draws the y axis; arguments are similar to XAxis.

## Defaults ##

YAxis has the following defaults, as described in [General features for all primitives](GeneralPrimitive.md).

| defaults | {"stroke-width":"0.25pt"} | default SVG attributes for all lines |
|:---------|:--------------------------|:-------------------------------------|
| text\_defaults | {"stroke":"none", "fill":"black", "font-size":5, "text-anchor":"end", "dominant-baseline":"middle"} | default SVG attributes for text labels |
| text\_start | 2.5 | position relative to the axis (in SVG units) to set text labels |
| text\_angle | 90 | angle (in degrees) to rotate text |
| tick\_start | -1.5 | position relative to the axis (in SVG units) to start the ticks |
| tick\_end | 1.5 | position relative to the axis (in SVG units) to end the ticks |
| minitick\_start | -1.5 | position relative to the axis (in SVG units) to start the miniticks |
| minitick\_end | 1.5 | position relative to the axis (in SVG units) to end the miniticks |

YAxis also has the same defaults as [Curve](ClassCurve.md).

## Special data members ##

When an XAxis or a YAxis is evaluated with **SVG**, it will gain two members.

  * **last\_ticks**: explicit dict of value, label pairs for major ticks
  * **last\_miniticks**: explicit list of values for miniticks

## SVG method ##

Axes, XAxis, and YAxis have **SVG** methods, as described in [General features for all primitives](GeneralPrimitive.md).