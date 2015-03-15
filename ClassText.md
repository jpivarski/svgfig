_(This page applies only to the 1.x branch of SVGFig.)_

# class Text #

Draws at text string at a specified point in local coordinates.

## Arguments ##

**Text(x, y, d, attribute=value)**

| x, y | _**required**_ | location of the point in local coordinates |
|:-----|:---------------|:-------------------------------------------|
| d | _**required**_ | text/Unicode string |
| attribute=value pairs | _keyword list_ | SVG attributes |

## SVG method ##

Text has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).

## Defaults ##

Text has the following defaults, as described in [General features for all primitives](GeneralPrimitive.md).

| defaults | {"stroke":"none", "fill":"black", "font-size":5} |
|:---------|:-------------------------------------------------|