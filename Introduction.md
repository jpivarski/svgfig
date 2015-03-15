_(This page applies only to the 1.x branch of SVGFig.)_

SVGFig is a [Python](http://www.python.org) extension module that defines two main classes, [SVG](ClassSVG.md) (_svig_) and [Fig](ClassFig.md) (_fig_).

[SVG](ClassSVG.md) represents an image in [Scalable Vector Graphics](http://www.svg.org/) format, a markup language similar to HTML.  By making Scalable Vector Graphics commands accessible to the Python language, the [SVG](ClassSVG.md) class broadens the user's capabilities in much the same way that dynamically-generated HTML did for webpages.  You can write programs that create images.

[Fig](ClassFig.md) builds a mathematical figure by applying a coordinate transformation to graphics primitives.  Unlike the the strictly linear transformations in the Scalable Vector Graphics command-set, [Fig](ClassFig.md) transformations can be any Python function.  Moreover, one often wants to transform only the mathematically-meaningful coordinates and not the widths of lines, lengths of tick marks, or radii of circular points, so [Fig](ClassFig.md) allows you to make such a distinction.  [Fig](ClassFig.md) transformations are composed by nesting, so you can make self-similar images by recursion.

# The SVG Part #

The [SVG](ClassSVG.md) class is a document object model of a Scalable Vector Graphics image, meaning that the tree of objects normally represented in XML is represented instead in linked Python data structures.

### Constructing SVG images ###

In XML-SVG, a rectangle can be expressed with the following command.
```
<rect x="10" y="10" width="60" height="60" />
```
To do the same in Python, load SVGFig and assign `s` to a new instance of the [SVG](ClassSVG.md) class.  (See ["How to Install"](HowToInstall.md) if the `import` command doesn't work.)
```
>>> from svgfig import *
>>> 
>>> s = SVG("rect", x=10, y=10, width=60, height=60)
>>> 
>>> print s.xml()
<rect y=10 width=60 height=60 x=10 />
```

In XML, elements can be nested, and the resulting tree structure is meaningful for images.  Graphical objects can be organized by grouping them in "g" elements, and many attributes can be inherited.  Let's create two rectangles and group them in a "g".
```
>>> s = SVG("rect", x=10, y=10, width=60, height=60, fill="red")
>>> s2 = SVG("rect", x=30, y=30, width=60, height=60, fill="blue")
>>> g = SVG("g", s, s2, fill_opacity="50%")
>>> g.save("tmp.svg")
```
Look at "tmp.svg" in a web browser or other Scalable Vector Graphics renderer.  You should see two overlapping, translucent squares.  In a graphics program like [Inkscape](http://www.inkscape.org/), the two squares should be grouped and moveable as a single object.

![http://svgfig.googlecode.com/svn/wiki/introduction-1.png](http://svgfig.googlecode.com/svn/wiki/introduction-1.png)

When we applied the `fill_opacity="50%"` attribute to the group, it was applied to all objects inside the group.  That can be overridden by giving one of the rectangles an explicit `fill_opacity`.  In the Scalable Vector Graphics specification, this attribute is actually called "fill-opacity", with a hyphen, not an underscore.  Python would interpret the hyphen as an attempt to subtract "opacity" from "fill", so we need to make some character substitutions.  An underscore (`_`) is mapped to a hyphen (`-`), and two underscores (`__`) are mapped to a colon (`:`).  Python uses the correct attribute names whenever they are quoted, e.g,
```
>>> g.attr
{'fill-opacity': '50%'}
```

### Saving and viewing ###

The `save` method didn't simply call `xml` and write the output to disk.  If you look at "tmp.svg", you would see that the contents include a header and a top-level 

&lt;svg /&gt;

 object.
```
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">

<svg style="stroke:black; fill:none; stroke-width:0.5pt; stroke-linejoin:round; text-anchor:middle"
xmlns="http://www.w3.org/2000/svg" height="400px" width="400px" version="1.1"
xmlns:xlink="http://www.w3.org/1999/xlink" font-family="Helvetica,Arial,FreeSans,Sans,sans,sans-serif"
viewBox="0 0 100 100">

<g fill-opacity="50%">

<rect y="10" width="60" fill="red" x="10" height="60" />

<rect y="30" width="60" fill="blue" x="30" height="60" />

</g>

</svg>
```

The header is a necessary part of a Scalable Vector Graphics image, but it would be inconvenient to have to construct it every time you want to look at a graphics fragment.  The `save` method determines whether it is being called from a whole image or a fragment, and constructs the appropriate output.  (See [canvas](DefCanvas.md) to make canvases explicitly.)

It was also unnecessary to specify a file name.  Without an argument, `save` overwrites "tmp.svg" in the current directory.  **Be careful that you don't keep anything important in "tmp.svg"!**

Building images by calling `save` and reloading in a web browser is reminiscent of writing web pages in HTML, but you can also call a viewer from Python, assuming that you have it installed on your system.  The [SVG](ClassSVG.md) class has `firefox`, `inkview`, and `inkscape` methods, which write to a file just like `save`, but then immediately load it in a renderer.

To load Scalable Vector Graphics files from XML into Python, use the [load](Defload.md) function.

### Navigating SVG images in Python ###

Fairly often, you'll also want to explore the [SVG](ClassSVG.md) object to see what's in it without looking at the full XML output.  Python's `print` command outputs the tree structure.
```
>>> print g
None                 <g (2 sub) fill-opacity='50%' />                                                
[0]                      <rect y=10 width=60 fill='red' x=10 height=60 />                            
[1]                      <rect y=30 width=60 fill='blue' x=30 height=60 />                           
```

The numbers on the left are tree indexes: you can reference any sub-element with a list of numbers and strings.  This is similar to the sections and subsections of a book or legal document.  Our tree isn't interesting enough, so let's make a bigger one.
```
>>> g2 = SVG("g", SVG("g", SVG("g", g)))
>>> print g2
None                 <g (1 sub) />                                                                   
[0]                      <g (1 sub) />                                                               
[0, 0]                       <g (1 sub) />                                                           
[0, 0, 0]                        <g (2 sub) fill-opacity='50%' />                                    
[0, 0, 0, 0]                         <rect y=10 width=60 fill='red' x=10 height=60 />                
[0, 0, 0, 1]                         <rect y=30 width=60 fill='blue' x=30 height=60 />               
```
The blue square is the second sub-element (1) of the first sub-element (0) of the first sub-element (0) of the first sub-element (0) of `g2`.  We can reference it with
```
>>> g2[0, 0, 0, 1]
<rect y=30 width=60 fill='blue' x=30 height=60 />
```

This kind of indexing replaces and deletes elements, too.
```
>>> g2[0, 0, 0, 1] = SVG("circle", cx=60, cy=60, r=30, fill="blue")
>>> print g2
None                 <g (1 sub) />                                                                   
[0]                      <g (1 sub) />                                                               
[0, 0]                       <g (1 sub) />                                                           
[0, 0, 0]                        <g (2 sub) fill-opacity='50%' />                                    
[0, 0, 0, 0]                         <rect y=10 width=60 fill='red' x=10 height=60 />                
[0, 0, 0, 1]                         <circle cy=60 cx=60 r=30 fill='blue' />                         
>>> g2.inkview()   # to look at it
```
![http://svgfig.googlecode.com/svn/wiki/introduction-2.png](http://svgfig.googlecode.com/svn/wiki/introduction-2.png)

```
>>> del g2[0, 0, 0, 0]
>>> print g2
None                 <g (1 sub) />                                                                   
[0]                      <g (1 sub) />                                                               
[0, 0]                       <g (1 sub) />                                                           
[0, 0, 0]                        <g (1 sub) fill-opacity='50%' />                                    
[0, 0, 0, 0]                         <circle cy=60 cx=60 r=30 fill='blue' />                         
>>> g2.inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-3.png](http://svgfig.googlecode.com/svn/wiki/introduction-3.png)

Tree indexes ending in strings reference attributes (no underscore/hyphen substitution).
```
>>> g2[0, 0, 0, "fill-opacity"]
'50%'
```

Just about everything in Python can be used in a `for` loop, and [SVG](ClassSVG.md) is no exception.  Iterating over an [SVG](ClassSVG.md) object performs a depth-first walk over all the sub-elements and attributes, returning (tree index, element) pairs.  The only thing you don't step over in the loop is the top-level object (which has no tree index).
```
>>> for ti, s in g2:
...     print ti, repr(s)
... 
(0,) <g (1 sub) />
(0, 0) <g (1 sub) />
(0, 0, 0) <g (1 sub) fill-opacity='50%' />
(0, 0, 0, 0) <circle cy=60 cx=60 r=30 fill='blue' />
(0, 0, 0, 0, 'cy') 60
(0, 0, 0, 0, 'cx') 60
(0, 0, 0, 0, 'r') 30
(0, 0, 0, 0, 'fill') 'blue'
(0, 0, 0, 'fill-opacity') '50%'
```

### More documentation ###

Now that you know how to build a Scalable Vector Graphic image in principle, you may be asking, "what are the commands?"
  * [The W3C specification](http://www.w3.org/Graphics/SVG/) is the definitive reference, but it can sometimes be hard to follow.
  * I often draw what I want to learn in [Inkscape](http://www.inkscape.org) and save as "Plain SVG," then look at the output.
  * [W3 Schools](http://www.w3schools.com/svg/default.asp) has a good tutorial.

If you need to know more about the Python language, see the [official website](http://www.python.org/).  If you just need to look up a command, see [Richard Gruet's quick reference pages](http://rgruet.free.fr/).

Of course, all the SVGFig documentation is available [on this site](Reference.md) and through Python's `help` command.

# The Fig Part #

The [Fig](ClassFig.md) class doesn't do much by itself; it's an organizing structure.  SVGFig defines a number of classes that draw graphics primitives, including
  * [Line](ClassLine.md): connecting two points
  * [Poly](ClassPoly.md): connecting a list of points
  * [Rect](ClassRect.md) and [Ellipse](ClassEllipse.md): rectangles/squares and ellipses/circles
  * [Dots](ClassDots.md) and [YErrorBars](ClassYErrorBars.md): data points and error bars
  * [Curve](ClassCurve.md): functions and parametric curves
  * [Path](ClassPath.md): SVG-like paths
  * [Axes](ClassAxes.md), [LineAxis](ClassLineAxis.md), [CurveAxis](ClassCurveAxis.md): coordinate axis along various shapes.

Each of these has a SVG method that "draws" the primitive by applying a coordinate transform and producing a [SVG](ClassSVG.md) object.
```
>>> Line(0, 0, 1, 1).SVG("x, 2*y")
<path d='M0 0L1 2' />
```

[Fig](ClassFig.md) collects a list of primitives and applies a transformation to all of them all.
```
>>> f = Fig(Line(0,0,1,1), Line(1,1,2,3), Line(2,3,0,0), trans="x, 2*y")
>>> f
<Fig (3 items) x,y -> x, 2*y>
>>> print f.SVG()
None                 <g (3 sub) />                                                                   
[0]                      <path d='M0 0L1 2' />                                                       
[1]                      <path d='M1 2L2 6' />                                                       
[2]                      <path d='M2 6L0 0' />                                                       
```

Moreover, nesting [Figs](ClassFig.md) composes transformations.
```
>>> print Fig(f, trans="y, x").SVG()
None                 <g (3 sub) />                                                                   
[0]                      <path d='M0 0L2 1' />                                                       
[1]                      <path d='M2 1L6 2' />                                                       
[2]                      <path d='M6 2L0 0' />                                                  
```

This can be used to make self-similar figures from recursion.  (I'm not sure why I think that's as wonderful as I do...)
```
>>> t = "0.1 + 0.4*x, 0.1 + 0.4*y"
>>> rect = Rect(0.05, 0.05, 0.95, 0.95, fill="blue", fill_opacity=0.3)
>>> def recursive(depth=0):
...     if depth < 4:
...         return Fig(rect, recursive(depth + 1), trans=t)
...     else:
...         return Fig()
... 
>>> recursive().SVG(window(0,1,0,1)).inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-4.png](http://svgfig.googlecode.com/svn/wiki/introduction-4.png)

[Plot](ClassPlot.md) and [Frame](ClassFrame.md) are alternatives for [Fig](ClassFig.md) which draw coordinate axes.  This is merely a convenience: [Axes](ClassAxes.md) are graphics primitives like anything else.
```
>>> import random
>>> scribble = Poly([(random.gauss(0,1), random.gauss(0,1)) for i in xrange(30)], "smooth", loop=True, stroke="blue")
>>> Plot(-3, 3, -3, 3, scribble, arrows="a").SVG().firefox()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-5.png](http://svgfig.googlecode.com/svn/wiki/introduction-5.png)

(Note: as of version 0.45, Inkscape does not properly apply Scalable Vector Graphics "baseline" attributes.  Use
```
>>> hacks["inkscape-text-vertical-shift"] = True
```
to adjust the text labels.)

### Coordinate Transformations ###

Transformations must be Python functions that map (x,y) to (x',y'), but there are several ways to make them.  The easiest way is with a string in "x', y'" form.  When a primitive sees such a string, it converts it into a callable function using the [totrans](DefTotrans.md) function.
```
>>> Line(0,0,1,1).SVG(totrans("2*x,2*y")), Line(0,0,1,1).SVG("2*x,2*y")
(<path d='M0 0L2 2' />, <path d='M0 0L2 2' />)
>>> 
>>> t = totrans("2*x, 2*y")
>>> t
<function x,y -> 2*x, 2*y at 0xb7ca43ac>
>>> t(1, 1)
(2, 2)
```

Transformations can also be functions from the complex plane to itself.  The [totrans](DefTotrans.md) function converts such functions into standard form, whether they are strings or functions of one argument.
```
>>> from svgfig import *
>>> t = lambda z: z*(1 + 0.3j) + 0.4*z**2
>>> Fig(Fig(Grid(-1, 1, -1, 1, stroke="blue", stroke_width=0.5), trans=totrans(t)), \
...     trans=window(-1.8, 2.2, -1.7, 2.3)).SVG().inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-6.png](http://svgfig.googlecode.com/svn/wiki/introduction-6.png)

Often the outermost transformation will be a [window](DefWindow.md), which maps a rectangle in your working coordinates to a rectangle on the canvas (usually (0,0), (100,100)).
```
>>> window(-1, 1, -1, 1)
<function (-1, 1), (-1, 1) -> (0, 100), (100, 0) at 0xb7c03304>
```
By default, windows flip the y axis, because Scalable Vector Graphics increases y downward, the opposite of the usual coordinate plane.  Windows can also be logarithmic and semi-log, a feature usually used in [Plot](ClassPlot.md) and [Frame](ClassFrame.md).

### (Almost) Everything's a Parametric Function ###

The [Curve](ClassCurve.md) class draws parametric functions.
```
>>> Curve("0.3*t*cos(t), 0.3*t*sin(t)", 0, 30.5, loop=True).SVG(window(-10, 10, -10, 10)).inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-7.png](http://svgfig.googlecode.com/svn/wiki/introduction-7.png)

Just like coordinate transformations, there are helper functions ([funcRtoR](DefFuncRtoR.md), [funcRtoR2](DefFuncRtoR2.md), [funcRtoC](DefFuncRtoC.md)) for putting an expression into standard form: a function from a real variable (usually "t") to the plane.

The special thing about [Curve](ClassCurve.md) is that it chooses its sample points dynamically.  If part of a curve is nearly linear, [Curve](ClassCurve.md) will evaluate fewer points in that region, and more points if it's highly curved.  The sample points are chosen in the SVG method, because they depend on the current coordinate transformation.
```
>>> w = window(-12, 12, 0, 12)
>>> curve = Curve(funcRtoR("sqrt(x**2 + 1)"), -10, 10, stroke="blue")
>>> curve.SVG(w)
<path stroke='blue' d='M8.33333 16.251L39.3219 77.0754L43.6266 84.7708L45.9844 88.4265L47.4307 90.2097L48.48 91.1295L49.2988
91.5495L50.3579 91.636L51.2118 91.3214L52.2612 90.5186L53.566 89.0314L55.7353 85.8218L62.0265 74.5443L91.6667 16.251' />
>>> dots = Dots([(s.x, s.y) for s in curve.last_samples], width=1.5, height=1.5)
>>> Fig(curve, dots, trans=w).SVG().inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-8.png](http://svgfig.googlecode.com/svn/wiki/introduction-8.png)

The adaptive sampling algorithm even detects discontinuities and breaks the curve, rather than draw a mathematically-inaccurate step.
```
>>> def f(x):
...     if x < 1: return x, 1
...     else: return x, 2
... 
>>> Plot(-1, 4, -1, 4, Curve(f, -1, 4, stroke="red"), arrows="a").SVG().inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-9.png](http://svgfig.googlecode.com/svn/wiki/introduction-9.png)

Since this is such a great algorithm, most of the graphics primitives use it.  [Line](ClassLine.md), [Rect](ClassRect.md), [Ellipse](ClassEllipse.md), etc. are all drawn by calling [Curve](ClassCurve.md).  Thus, straight lines (and even coordinate axes) become curves when passed through a curvy coordinate system.
```
>>> from math import *
>>> def vortex(x, y):
...     r = sqrt(x**2 + y**2)
...     return cos(r)*x + sin(r)*y, -sin(r)*x + cos(r)*y
... 
>>> Plot(-1.5, 1.5, -1.5, 1.5, Rect(-1,-1,1,1, stroke="blue"), arrows="a", trans=vortex).SVG().inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-10.png](http://svgfig.googlecode.com/svn/wiki/introduction-10.png)

This also gives us the opportunity to make arbitrarily-curved coordinate axes.  It could be used to express the parameterization of a curve.
```
>>> curve = CurveAxis("t*cos(t), t*sin(t)", 0, 10, ticks=11, arrow_end="a")
>>> curve.SVG()
<g (15 sub) />
>>> curve.last_ticks
{0: '', 1.0: '', 2.0: u'2', 3.0: u'3', 4.0: u'4', 5.0: u'5', 6.0: u'6', 7.0: u'7', 8.0: u'8', 9.0: u'9', 10.0: u'10'}
>>> curve.ticks = curve.last_ticks
>>> curve.ticks[0] = ""
>>> curve.ticks[1] = ""
>>> curve.SVG(window(-10, 10, -10, 10)).inkview()
```
![http://svgfig.googlecode.com/svn/wiki/introduction-11.png](http://svgfig.googlecode.com/svn/wiki/introduction-11.png)

# Closing the Loop #

[Figs](ClassFig.md) can make [SVGs](ClassSVG.md), but can [SVGs](ClassSVG.md) make [Figs](ClassFig.md)?  To a limited extent, yes.  One of SVGFig's graphics primitives, [Path](ClassPath.md), represents a Scalable Vector Graphics 

&lt;path /&gt;

.  [Path](ClassPath.md) parses the path data string, converting it into a list of tuples that can be distorted by coordinate transformations.  This is how the SVGFig logo was constructed: see [SVGFigLogo](SVGFigLogo.md).

[![](http://svgfig.googlecode.com/svn/wiki/introduction-12.png)](http://code.google.com/p/svgfig/wiki/SVGFigLogo)

And, of course, see [Reference](Reference.md) for full documentation.