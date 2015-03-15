_(This page applies only to the 1.x branch of SVGFig.)_

# class Dots #

Dots draws SVG symbols at a set of points.

## Arguments ##

**Dots(d, symbol, width, height, attribute=value)**

| d | _**required**_ | list of (x,y) points |
|:--|:---------------|:---------------------|
| symbol | _default_=None | SVG symbol or a new identifier to label an auto-generated symbol; if None, use pre-defined `circular_dot` |
| width, height | _default_=1, 1 | width and height of the symbols in SVG coordinates |
| attribute=value pairs | _keyword list_ | SVG attributes |

Note that a list of (x,y) points can be constructed with Python's
`zip` function.  This can be useful for constructing `d`.
```
>>> x = [1,2,3,4,5]
>>> y = [1,4,9,16,25]
>>> zip(x,y)
[(1, 1), (2, 4), (3, 9), (4, 16), (5, 25)]
```

The `symbol` can be a new SVG object constructed like this
```
>>> SVG("symbol", SVG("circle", cx=0, cy=0, r=1, stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible", id="new_identifier")
```
or using the [make\_symbol](DefMake_symbol.md) function.  You can also just supply a
new identifier, and Dots will call [make\_symbol](DefMake_symbol.md) for you.

You need to supply an identifier that hasn't already been used in your
SVG image, so that the dots link to the right reference.

## SVG method ##

Dots has an **SVG** method, as described in [General features for all primitives](GeneralPrimitive.md).