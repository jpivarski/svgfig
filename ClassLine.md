_(This page applies only to the 1.x branch of SVGFig.)_

# class Line #

Line draws a line between two points, but this line is mutable by
coordinate transformations.  If the coordinates curve, the line will
curve.

## Arguments ##

**Line(x1, y1, x2, y2, arrow\_start, arrow\_end, attribute=value)**

| x1, y1 | _**required**_ | the starting point |
|:-------|:---------------|:-------------------|
| x2, y2 | _**required**_ | the ending point |
| arrow\_start | default=None | if an identifier string/Unicode, draw a new arrow object at the beginning of the line; if a marker, draw that marker instead |
| arrow\_end | default=None | same for the end of the line |
| attribute=value pairs | _keyword list_ | SVG attributes |

To add arrows to the ends of the line, you need to supply a _new_ identifier.  If the identifier references another object (SVG `id` attribute), the renderer will attempt to place that object instead (if it's a marker).

Adding an arrow changes the structure of the output SVG.

## SVG method ##

Line has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Path method ##

Line has a **Path** method, as described in [General features for all primitives](GeneralPrimitive.md).

Arrows are ignored by the Path method.

## Defaults ##

Line has the same defaults as [Curve](ClassCurve.md).  Defaults are described in [General features for all primitives](GeneralPrimitive.md).

| random\_sampling | True | if False, bisect with a point exactly halfway between pairs of points; if True, randomly choose a point between 30% and 70% |
|:-----------------|:-----|:----------------------------------------------------------------------------------------------------------------------------|
| recursion\_limit | 15 | number of subdivisions before giving up; if 15, sampling algorithm can visit _at most_ 2<sup>15</sup> points |
| linearity\_limit | 0.05 | maximum deviation (in SVG units) from a straight line |
| discontinuity\_limit | 5 | minimum deviation (in SVG units) between points that is considered continuous |