_(This page applies only to the 1.x branch of SVGFig.)_

# make\_marker #

Creates a new instance of an SVG marker to avoid cross-linking objects.  The user must supply a new identifier.

## Arguments ##

**make\_marker(id, shape, attribute=value)**

| id | _**required**_ | a new identifier (string/Unicode) |
|:---|:---------------|:----------------------------------|
| shape | _**required**_ | the shape name from **marker\_templates** |
| attribute=value list | _keyword list_ | modify the SVG attributes of the new marker, e.g. stroke="blue" |

## Templates ##

Symbol templates come from a dictionary in the svgfig namespace called **marker\_templates**.

| "arrow\_start" | an arrow suitable for the start of a line or path |
|:---------------|:--------------------------------------------------|
| "arrow\_end" | an arrow suitable for the end of a line or path |

```
>>> import svgfig
>>> svgfig.marker_templates
{'arrow_end': <marker (1 sub) refY='3.6' refX='1.5' markerUnits='strokeWidth'...
```