_(The following applies only to the 1.x branch of SVGFig.  For version 2.x, see [Version2Announcement](Version2Announcement.md).)_

# Tutorials #

  * [Introduction](Introduction.md): how SVGFig basically works
  * [Plotting Tutorial](PlottingTutorial.md): tutorial for plotting mathematical functions
  * [Example Gallery](ExampleGallery.md): shows what SVG can do


---


# Alphabetized Index #

[Click here](http://code.google.com/p/svgfig/w/list?q=label:Reference) for an alphabetized list of all SVGFig reference pages.  (Note that you can search their contents.)

[![](http://svgfig.googlecode.com/svn/wiki/alphabetized_list.png)](http://code.google.com/p/svgfig/w/list?q=label:Reference)


---


# Reference Table of Contents #

## Fundamentals ##

  * [SVG](ClassSVG.md): class representing an SVG image
    * [canvas and canvas\_outline](DefCanvas.md): functions for explicitly laying out the SVG canvas; good for changing the aspect ratio
    * [load and load\_stream](Defload.md): functions for loading SVG files from files or XML streams
    * [template](DefTemplate.md): loads an SVG template, replacing all instances of "

&lt;REPLACEME /&gt;

" with an SVG object

  * SVG graphics helpers
    * [rgb](DefRgb.md): expresses an rgb triple as a hex string
    * [make\_symbol](DefMake_symbol.md): makes a 

&lt;symbol /&gt;

 element from a template of standard shapes
    * [make\_marker](DefMake_marker.md): makes a 

&lt;marker /&gt;

 element from a template

  * [Fig](ClassFig.md): holds a set of transformable primitives and globally-positioned SVG objects, composes transformations when nested
  * [Plot](ClassPlot.md): a Fig with coordinate axes
  * [Frame](ClassFrame.md): a Fig in a coordinate frame

  * for making transformation functions
    * [totrans](DefTotrans.md): turns a string expression or complex function into an R<sup>2</sup>-to-R<sup>2</sup> function
    * [window](DefWindow.md): creates a transformation by mapping a rectangle of "inner" coordinates to a rectangle of "outer" coordinates
    * [rotate](DefRotate.md): creates a simple rotation of the plane

## Fig Primitives ##

  * [General features of all primitives](GeneralPrimitive.md)

  * [Path](ClassPath.md): a transformable representation of an SVG path
    * [pathtoPath](DefPathtoPath.md): converts SVG 

&lt;path /&gt;

 objects into transformable Paths
  * [Curve](ClassCurve.md): draws a parametric function; implements the adaptive sampling algorithm
    * [funcRtoR2](DefFuncRtoR2.md): turns a string expression into a parametric function suitable for drawing with Curve
    * [funcRtoC](DefFuncRtoC.md): turns a complex string expression into a parametric function
    * [funcRtoR](DefFuncRtoR.md): turns a one-dimensional function into a parametric function
  * [Poly](ClassPoly.md): draws a line through a sequence of points; may be piecewise linear, Bézier, a velocity curve, or smooth
  * [Dots](ClassDots.md): draws SVG symbols at a set of points
  * [YErrorBars and XErrorBars](ClassYErrorBars.md): draw error bars (usually used with Dots), including multiple bars (e.g. for correlated and uncorrelated errors)

  * [Line](ClassLine.md): draws a line between two points; if the coordinate transformation is non-linear, the line may be curved
  * [LineGlobal](ClassLineGlobal.md): draws a straight line between two points, one or both of which are in global coordinates
  * [VLine and HLine](ClassVLine.md): draws vertical and horizontal lines (provided as a convenience)
  * [Rect](ClassRect.md): draws a rectangle joining four points
  * [Ellipse](ClassEllipse.md): draws an ellipse with semimajor axis and a semiminor length (does not need to be aligned with the X-Y axis)
  * [Grid, HGrid, and VGrid](ClassGrid.md): draws a set of horizontal and vertical lines

  * [Text](ClassText.md): places text at a local coordinate
  * [TextGlobal](ClassTextGlobal.md): places text at a global coordinate

## Coordinate Axes ##

  * [Standard tick specification methods](TickSpecification.md)

  * [Axes](ClassAxes.md): draws an orthogonal coordinate axis in the local coordinate system
  * [Ticks](ClassTicks.md): superclass of everything with tick marks; implements the tick-guessing algorithm
  * [CurveAxis](ClassCurveAxis.md): draws ticks along a parametric function
  * [LineAxis](ClassLineAxis.md): draws ticks along a line; useful for measuring the distance between points