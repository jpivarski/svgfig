_(This page applies only to the 1.x branch of SVGFig.)_

# class Rect #

Rect draws a rectangle connecting two points, but the sides are
mutable by coordinate transformations.  If the coordinates curve, the
sides will curve.

## Arguments ##

**Rect(x1, y1, x2, y2, attribute=value)**

| x1, y1 | _**required**_ | the starting point |
|:-------|:---------------|:-------------------|
| x2, y2 | _**required**_ | the ending point |
| attribute=value pairs | _keyword list_ | SVG attributes |

## SVG method ##

Rect has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Path method ##

Rect has a **Path** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Defaults ##

Rect has the same defaults as [Curve](ClassCurve.md).  Defaults are described in [General features for all primitives](GeneralPrimitive.md).

| random\_sampling | True | if False, bisect with a point exactly halfway between pairs of points; if True, randomly choose a point between 30% and 70% |
|:-----------------|:-----|:----------------------------------------------------------------------------------------------------------------------------|
| recursion\_limit | 15 | number of subdivisions before giving up; if 15, sampling algorithm can visit _at most_ 2<sup>15</sup> points |
| linearity\_limit | 0.05 | maximum deviation (in SVG units) from a straight line |
| discontinuity\_limit | 5 | minimum deviation (in SVG units) between points that is considered continuous |