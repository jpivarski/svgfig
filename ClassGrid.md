_(This page applies only to the 1.x branch of SVGFig.)_

# class Grid #

Grid draws a grid over a specified region using [standard tick specification](TickSpecification.md)
to place the grid lines.  The grid will be curved in
non-linear transformations, and can be a good way to "feel" the shape
of the transformation.

## Arguments ##

**Grid(xmin, xmax, ymin, ymax, ticks, miniticks, logbase, mini\_attr, attribute=value)**

| xmin, xmax | _**required**_ | the x range |
|:-----------|:---------------|:------------|
| ymin, ymax | _**required**_ | the y range |
| ticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| miniticks | _default_=False | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| logbase | _default_=None | if a number, the axis is logarithmic with ticks at the given base (10 being the most common) |
| mini\_attr | _default_={} | SVG attributes for the minitick-lines (if miniticks != False) |
| attribute=value pairs | _keyword list_ | SVG attributes for the major tick lines |

# class HGrid #

Only draws the horizontal lines of a grid.

## Arguments ##

**HGrid(xmin, xmax, low, high, ticks, miniticks, logbase, mini\_attr, attribute=value)**

| xmin, xmax | _**required**_ | the x range |
|:-----------|:---------------|:------------|
| low, high | _**required**_ | the y range |
| ticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| miniticks | _default_=False | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| logbase | _default_=None | if a number, the axis is logarithmic with ticks at the given base (10 being the most common) |
| mini\_attr | _default_={} | SVG attributes for the minitick-lines (if miniticks != False) |
| attribute=value pairs | _keyword list_ | SVG attributes for the major tick lines |

# class VGrid #

Only draws the vertical lines of a grid.

## Arguments ##

**VGrid(ymin, ymax, low, high, ticks, miniticks, logbase, mini\_attr, attribute=value)**

| ymin, ymax | _**required**_ | the y range |
|:-----------|:---------------|:------------|
| low, high | _**required**_ | the x range |
| ticks | _default_=-10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| miniticks | _default_=False | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| logbase | _default_=None | if a number, the axis is logarithmic with ticks at the given base (10 being the most common) |
| mini\_attr | _default_={} | SVG attributes for the minitick-lines (if miniticks != False) |
| attribute=value pairs | _keyword list_ | SVG attributes for the major tick lines |

## SVG method ##

Grid, HGrid, and VGrid have **SVG** methods, as described in [General features for all primitives](GeneralPrimitive.md).

## Defaults ##

Grid, HGrid, and VGrid have the following defaults, as described in [General features for all primitives](GeneralPrimitive.md).

| defaults | {"stroke-width":"0.25pt", "stroke":"gray"} |
|:---------|:-------------------------------------------|
| mini\_defaults | {"stroke-width":"0.25pt", "stroke":"lightgray", "stroke-dasharray":"1,1"} |