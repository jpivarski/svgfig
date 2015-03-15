_(This page applies only to the 1.x branch of SVGFig.)_

# class Curve #

Curve draws a Python callable as a path.  Curves are adaptively
sampled, meaning that the function is evaluated at more points near
corners and along curves and at fewer points along straight segments.
If the function is discontinuous (like a step function), the path will
be a broken line.

The sampling algorithm starts at the endpoints and bisects until three
consecutive points are nearly linear, or until reaching a recursion limit.

## Arguments ##

**Curve(f, low, high, loop, attribute=value)**

| f | _**required**_ | a Python callable or string in the form "f(t), g(t)" |
|:--|:---------------|:-----------------------------------------------------|
| low, high | _**required**_ | left and right endpoints |
| loop | _default_=False | if True, connect the endpoints |
| attribute=value pairs | _keyword list_ | SVG attributes |

The function must take one argument and return two values.  If it is a
string, it will be passed to [funcRtoR2](DefFuncRtoR2.md).  For complex
functions, use an explicit call to [funcRtoC](DefFuncRtoC.md) and for real
functions, use an explicit call to [funcRtoR](DefFuncRtoR.md), which
return a function in the right format.

The following are all equivalent:
  * `Curve(lambda t: t, t**2, 0, 1)`
  * `Curve("t, t**2", 0, 1)`
  * `Curve(funcRtoR2("t, t**2"), 0, 1)`
  * `Curve(funcRtoC("t + (1j)*t**2"), 0, 1)`
  * `Curve(funcRtoR("x**2"), 0, 1)`

## SVG method ##

Curve has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Path method ##

Curve has a **Path** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Defaults ##

Curve has the following defaults, as described in [General features for all primitives](GeneralPrimitive.md).

| random\_sampling | True | if False, bisect with a point exactly halfway between pairs of points; if True, randomly choose a point between 30% and 70% |
|:-----------------|:-----|:----------------------------------------------------------------------------------------------------------------------------|
| recursion\_limit | 15 | number of subdivisions before giving up; if 15, sampling algorithm can visit _at most_ 2<sup>15</sup> points |
| linearity\_limit | 0.05 | maximum deviation (in SVG units) from a straight line |
| discontinuity\_limit | 5 | minimum deviation (in SVG units) between points that is considered continuous |

## Special data members ##

After the Curve has been evaluated with **SVG** or **Path**, it gains a
new data memeber, `last_samples`.  This is an iterable of
Curve.Sample objects:
```
>>> c = Curve(funcRtoR("x**2"), 0, 1)
>>> c.SVG()
>>> for s in c.last_samples:
...     print s.x, s.y, s.X, s.Y
...
```

Curve.Sample has four data members, `x`, `y`, `X`, `Y`.  These are
coordinates in local (lowercase) and global (uppercase) coordinates.
If a coordinate is `None`, there is a break in the curve, due to a
discontinuity in the supplied function.

This iterable is actually a doubly-linked list, not a Python
construct, connected through data members called `left` and `right`.