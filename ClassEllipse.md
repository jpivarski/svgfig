_(This page applies only to the 1.x branch of SVGFig.)_

# class Ellipse #

Ellipse draws ellipses and circles.  The shape may be non-elliptical
if passed through a non-linear coordinate transformation.

## Arguments ##

**Ellipse(x, y, ax, ay, b, attribute=value)**

| x, y | _**required**_ | the center of the ellipse/circle |
|:-----|:---------------|:---------------------------------|
| ax, ay | _**required**_ | a vector indicating the length and direction of the semimajor axis |
| b | _**required**_ | the length of the semiminor axis.  If equal to sqrt(ax<sup>2</sup> + ay<sup>2</sup>), the ellipse is a circle |
| attribute=value pairs | _keyword list_ | SVG attributes |

(If sqrt(ax<sup>2</sup> + ay<sup>2</sup>) is less than b, then (ax,ay) is actually the semiminor axis.)

## SVG method ##

Ellipse has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Path method ##

Ellipse has a **Path** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Defaults ##

Ellipse has the same defaults as [Curve](ClassCurve.md).  Defaults are described in [General features for all primitives](GeneralPrimitive.md).

| random\_sampling | True | if False, bisect with a point exactly halfway between pairs of points; if True, randomly choose a point between 30% and 70% |
|:-----------------|:-----|:----------------------------------------------------------------------------------------------------------------------------|
| recursion\_limit | 15 | number of subdivisions before giving up; if 15, sampling algorithm can visit _at most_ 2<sup>15</sup> points |
| linearity\_limit | 0.05 | maximum deviation (in SVG units) from a straight line |
| discontinuity\_limit | 5 | minimum deviation (in SVG units) between points that is considered continuous |