#Draws an immutable object at given local coordinates

_(This page applies only to the 1.x branch of SVGFig.)_

# class Pinned (not yet implemented) #

Pinned draws a given graphics object at a certain location (the "anchor point").  Only the anchor point of a Pinned object is affected by coordinate transformations.

## Arguments ##

**Pinned(x, y, d, basex, basey, attribute = value)**

| x, y | _**required**_ | the anchor point |
|:-----|:---------------|:-----------------|
| d | _**required**_ | an SVG object or graphics primitive |
| basex, basey | default=0,0 | internal position of the anchor point |
| attribute=value pairs | _keyword list_ | SVG attributes |

The `basex` and `basey` parameters specify which point of the SVG object `d` should act as the pinning point.  When a `Pinned` object is converted to SVG, the tranformation `translate(x-basex,y-basey)` is prepended to the `transform` attribute of `d`.

Note that all lengths in 'd' are interpreted using global units (i.e. pixels).

## SVG method ##

Pinned has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).