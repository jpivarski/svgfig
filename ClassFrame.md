_(This page applies only to the 1.x branch of SVGFig.)_

# class Frame #

Acts like [Fig](ClassFig.md), but draws a coordinate frame around the data.  You also need to supply plot ranges.

## Arguments ##

**Frame(xmin, xmax, ymin, ymax, obj, obj, obj..., keyword options...)**

| xmin, xmax | _**required**_ | minimum and maximum x values (in the objs' coordinates) |
|:-----------|:---------------|:--------------------------------------------------------|
| ymin, ymax | _**required**_ | minimum and maximum y values (in the objs' coordinates) |
| obj | _optional list_ | drawing primitives |
| keyword options | _keyword list_ | options defined below |

The drawing primitives must implement the **SVG** method, as described
in the [Fig](ClassFig.md) documentation.

Unlike [Fig](ClassFig.md), Frame has an implicit coordinate transformation:
from (xmin, xmax), (ymin, ymax) to its bounding box.  This coordinate
transformation (a [window](DefWindow.md) transformation) flips the
direction of the y axis (SVG coordinates have y increasing downward,
local Frame coordinates have y increasing upward).

The following are keyword options, with their default values:

| x, y | 20, 5 | upper-left corner of the Frame in SVG coordinates |
|:-----|:------|:--------------------------------------------------|
| width, height | 75, 80 | width and height of the Frame in SVG coordinates |
| flipx, flipy | False, True | flip the sign of the coordinate axis |
| minusInfinity | -1000 | if an axis is logarithmic and an object is plotted at 0 or a negative value, -1000 will be used as a stand-in for NaN |
| xtitle | None | if a string, label the x axis |
| xticks | -10 | request ticks according to the [standard tick specification](TickSpecification.md) |
| xminiticks | True | request miniticks according to the [standard minitick specification](TickSpecification.md) |
| xlabels | True | request tick labels according to the [standard tick label specification](TickSpecification.md) |
| xlogbase | None | if a number, the axis and transformation are logarithmic with ticks at the given base (10 being the most common) |
| same for y |  |  |
| text\_attr | {} | a dictionary of attributes for label text |
| axis\_attr | {} | a dictionary of attributes for the axis lines |

## Member data ##

These data may be changed at any time.  You do not need to make a list
of all graphics before creating a Frame; you can create an empty Frame and
append items to its `d` member.

| d | list of plottable objects |
|:--|:--------------------------|
| all keyword options | same meaning as above |

## Default values ##

Frame has several default values which affect the drawing output.
They may be set for a single Frame instance, affecting only that
object, or for the class itself, affecting all Frame objects created
for that time onward.

| text\_defaults | {"stroke":"none", "fill":"black", "font-size":5} | SVG attributes for the xtitle and ytitle |
|:---------------|:-------------------------------------------------|:-----------------------------------------|
| axis\_defaults | {} | SVG attributes for the axis lines and ticks |
| tick\_length | 1.5 | length of (one-sided) ticks along the inside of the frame (SVG units) |
| minitick\_length | 0.75 | length of (one-sided) miniticks (SVG units) |
| text\_xaxis\_offset | 1. | distance between the x axis and the x labels (SVG units) |
| text\_yaxis\_offset | 2. | distance between the y axis and the y labels (SVG units) |
| text\_xtitle\_offset | 6. | distance between the x axis and the xtitle (SVG units) |
| text\_ytitle\_offset | 12. | distance between the y axis and the ytitle (SVG units) |

## SVG method ##

Just like [Fig](ClassFig.md), Frame has an **SVG** method to convert its objects into [SVG](ClassSVG.md).

All graphics primitives must supply a **SVG** method with the same arguments.