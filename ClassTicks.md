_(This page applies only to the 1.x branch of SVGFig.)_

# class Ticks #

Ticks is the superclass for everything that draws tickmarks.  By
itself, it can draw ticks along a curve which isn't itself drawn.
Maybe you'll find that useful.

## Arguments ##

**Ticks(f, low, high, ticks, miniticks, labels, logbase, arrow\_start, arrow\_end, text\_attr, attribute=value)**

| f | _**required**_ | parametric function along which ticks will be drawn; has the same format as the function used in [Curve](ClassCurve.md) |
|:--|:---------------|:------------------------------------------------------------------------------------------------------------------------|
| low, high | _**required**_ | range of the independent variable |
| ticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| miniticks | _default_=True | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| labels | True | request tick labels according to the [standard tick label specification](TickSpecification.md) |
| logbase | _default_=None | if a number, the axis is logarithmic with ticks at the given base (10 being the most common) |
| arrow\_start | _default_=None | if a new string identifier, draw an arrow at the low-end of the axis, referenced by that identifier; if an SVG marker object, use that marker |
| arrow\_end | _default_=None | if a new string identifier, draw an arrow at the high-end of the axis, referenced by that identifier; if an SVG marker object, use that marker |
| text\_attr | _default_={} | SVG attributes for the text labels |
| attribute=value pairs | _keyword list_ | SVG attributes for the tick marks |

## Defaults ##

Ticks has the following defaults, as described in [General features for all primitives](GeneralPrimitive.md).

| text\_defaults | {"stroke":"none", "fill":"black", "font-size":5} | default SVG attributes for text labels |
|:---------------|:-------------------------------------------------|:---------------------------------------|
| tick\_start | -1.5 | position relative to the axis (in SVG units) to start the ticks |
| tick\_end | 1.5 | position relative to the axis (in SVG units) to end the ticks |
| minitick\_start | -1.5 | position relative to the axis (in SVG units) to start the miniticks |
| minitick\_end | 1.5 | position relative to the axis (in SVG units) to end the miniticks |
| text\_start | 2.5 | position relative to the axis (in SVG units) to set text |
| text\_angle | 0 | angle (in degrees) to rotate text |

## Special data members ##

When a Ticks is evaluated with **SVG**, it will gain two members.

  * **last\_ticks**: explicit dict of value, label pairs for major ticks
  * **last\_miniticks**: explicit list of values for miniticks

## SVG method ##

Ticks has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Other methods ##

Ticks has a number of other methods which are usually only used internally.

  * **interpret()**: evaluate and return optimal ticks and miniticks according to the [standard minitick specification](TickSpecification.md)
  * **orient\_tickmark(t, trans=None)**: return the position, normalized local x vector, normalized local y vector, and angle of a tick at position t
  * **compute\_ticks(N, format)**: return less than -N or exactly N optimal linear ticks
  * **regular\_miniticks(N)**: return exactly N linear ticks
  * **compute\_miniticks(original\_ticks)**: return optimal linear miniticks, given a set of ticks
  * **compute\_logticks(base, N, format)**: return less than -N or exactly N optimal logarithmic ticks
  * **compute\_logminiticks(base)**: return optimal logarithmic miniticks, given a set of ticks