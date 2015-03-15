_(The following applies only to the 1.x branch of SVGFig.  For version 2.x, see [Version2Announcement](Version2Announcement.md).)_

# Reference #

## Table of Contents ##
  1. **[Graphics Primitives](#Graphics_Primitives.md)** ([general features](GeneralPrimitive.md))
    1. **[Curves](#Curves.md)**
      * [Curve](ClassCurve.md), [funcRtoR2()](DefFuncRtoR2.md), [funcRtoC()](DefFuncRtoC.md), [funcRtoR()](DefFuncRtoR.md), [Line](ClassLine.md), [HLine and VLine](ClassVLine.md), [Rect](ClassRect.md), [Ellipse](ClassEllipse.md)
    1. **[Ticks, Axes, and Gridlines](http://code.google.com/p/svgfig/wiki/CodeReference#Ticks%2C_Axes%2C_and_Gridlines)**
      * [tick specification](TickSpecification.md), [Ticks](ClassTicks.md), [CurveAxis](ClassCurveAxis.md), [LineAxis](ClassLineAxis.md), [XAxis, YAxis, and Axes](ClassAxes.md), [Grid, HGrid, and VGrid](ClassGrid.md)
    1. **[Miscellaneous Graphics Primitives](#Miscellaneous_Graphics_Primitives.md)**
      * [Path](ClassPath.md), [pathtoPath()](DefPathtoPath.md), [Poly](ClassPoly.md), [Dots](ClassDots.md), [YErrorBars and XErrorBars](ClassYErrorBars.md), [LineGlobal](ClassLine.md), [Text](ClassText.md), [TextGlobal](ClassTextGlobal.md)
    1. **[Figures](#Figures.md)**
      * [class Fig](ClassFig.md), [class Plot](ClassPlot.md), [class Frame](ClassFrame.md)
    1. **[Transformations](#Transformations.md)**
      * [totrans()](DefTotrans.md), [window()](DefWindow.md), [rotate()](DefRotate.md)
  1. **[SVG Objects](#SVG_Objects.md)**
    * [SVG](ClassSVG.md), [canvas() and canvas\_outline()](DefCanvas.md), [load() and load\_stream()](Defload.md), [template()](DefTemplate.md), [make\_symbol()](DefMake_symbol.md), [make\_marker()](DefMake_marker.md)
  1. **[Other Functions](#Other_Functions.md)**
    * [rgb()](DefRgb.md)


## Graphics Primitives ##
A _graphics primitive_ is any one graphics object, such as a line, curve, or polygon.  You can apply coordinate transformations to graphics primitives, group them together into figures, and then convert them to SVG objects.
  * [General features](GeneralPrimitive.md) of all graphics primitives

### Curves ###
A _curve_ is a graphics primitive representing a parametric curve.  Curves map correctly under coordinate transformations -- SVGFig uses an adaptive sampling algorithm to convert the end result to SVG.
  * [class Curve](ClassCurve.md): a parametric curve defined by a function; svgfig uses an adaptive sampling algorithm to convert Curves to SVG path elements.
You can use the functions [funcRtoR2()](DefFuncRtoR2.md), [funcRtoC()](DefFuncRtoC.md), and [funcRtoR()](DefFuncRtoR.md) to assist in the creation of parametric equations.

Curve has the following child classes:
  * [class Line](ClassLine.md): a straight line connecting two points, may become curved after a nonlinear coordinate transformation
    * [class HLine and class VLine](ClassVLine.md) (children of Line): a horizontal or vertical line
  * [class Rect](ClassRect.md): a horizontal or vertical rectangle
  * [class Ellipse](ClassEllipse.md): an arbitrary ellipse or circle

### Ticks, Axes, and Gridlines ###
Ticks are graphics primitive representing sequences of tickmarks.  These may be drawn using any of the [standard tick specification methods](TickSpecification.md).
  * [class Ticks](ClassTicks.md): a collection of tick marks drawn along a parametric curve (draws the ticks, but not the curve)
  * [class CurveAxis](ClassCurveAxis.md) (child of Curve and Ticks): a Curve with Ticks
  * [class LineAxis](ClassLineAxis.md) (child of Line and Ticks): a Line with Ticks
    * [class XAxis and class YAxis](ClassAxes.md) (children of LineAxis): a horizontal or vertical axis with ticks
    * [class Axes](ClassAxes.md): Both an XAxis and a YAxis
  * [class Grid, class HGrid, and class VGrid](ClassGrid.md) (children of Ticks): a sequence of horizontal and/or vertical gridlines

### Miscellaneous Graphics Primitives ###
  * [class Path](ClassPath.md) any collection of straight or curved arcs, similar to an SVG path element
    * [pathtoPath()](DefPathtoPath.md) A function to convert an SVG path element into an object of class Path
  * [class Poly](ClassPoly.md): a smooth or piecewise-linear curve defined by a sequence of points
  * [class Dots](ClassDots.md): a collection of SVG symbols drawn at specified coordinates
  * [class YErrorBars and class XErrorBars](ClassYErrorBars.md): a collection of error bars
  * [class LineGlobal](ClassLine.md): a straight line connecting two points, remains straight under coordinate transformations.  One or both endpoints may be specified in global coordinates
  * [class Text](ClassText.md): text placed at specified local coordinates
  * [class TextGlobal](ClassTextGlobal.md): text placed at specified global coordinate

### Figures ###
A _figure_ is any set of graphics primitive.  A figure is itself a primitive, making it possible to create nested collections.  Any transformation applied to a figure is applied separately to each of its members.

There are three classes for creating figures:
  * [class Fig](ClassFig.md): any collection of graphics primitives
  * [class Plot](ClassPlot.md): a figure with coordinate axes
  * [class Frame](ClassFrame.md): a figure with a coordinate frame

### Transformations ###
Each of the graphics primitives above is subject to _coordinate transformations_.  The following functions can be helpful in creating these transformations:
  * [totrans()](DefTotrans.md): turns a string expression or complex function into an R<sup>2</sup>-to-R<sup>2</sup> function
  * [window()](DefWindow.md): creates a transformation by mapping a rectangle of "inner" coordinates to a rectangle of "outer" coordinates
  * [rotate()](DefRotate.md): rotates the plane around a specified point

## SVG Objects ##
An _SVG object_ is a python representation of an SVG element (or group of elements).  Graphics primitives can be converted to SVG objects, which can then be assembled and written to SVG image files.
  * [class SVG](ClassSVG.md): any SVG element (e.g. an SVG canvas, an SVG path, an SVG group element, an SVG defs element, etc.)
SVG elements can be created directly using the [SVG constructor](ClassSVG.md), or from any graphics primitive by using the (graphics primitive object).SVG() member function.  The following functions also create SVG elements:
  * [canvas() and canvas\_outline()](DefCanvas.md): functions to create a top-level SVG element; good for changing the aspect ratio
  * [load() and load\_stream()](Defload.md): functions to create an SVG element from an SVG file or XML stream
  * [template()](DefTemplate.md): function to create an SVG element from an SVG template file
  * [make\_symbol()](DefMake_symbol.md): function to create a SVG symbol element from a template of standard shapes
  * [make\_marker()](DefMake_marker.md): function to create a SVG marker element from a template of standard shapes

## Other functions ##
The following helper functions may be useful when working with graphics primitives or SVGs:
  * [rgb()](DefRgb.md): expresses an rgb triple as a hex string