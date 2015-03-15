[![](http://svgfig.googlecode.com/svn/wiki/svgfig_logo.png)](http://code.google.com/p/svgfig/wiki/SVGFigLogo)

# SVGFig (pronounced _svig-fig_) #

The SVGFig package lets you draw mathematical figures in Scalable Vector Graphics format (SVG), using the Python language.

As a tool, its usefulness lies somewhere between freehand drawing programs, which don't give you quantitative control over your figures, and traditional plotting packages, which fit your data into a prescribed template.  SVGFig allows you to draw anything you can express in Python.

SVGFig is particularly suited to handle non-linear geometries.  All lines, including the coordinate axis, curve if passed through a non-linear coordinate transformation, and coordinate systems can be nested in trees.  This generalizes all the tools necessary for making plots, so it is easy to create polar plots of radial data, Hammer-Aitoff projections of the sky, translations in hyperbolic spaces, or experiment with new representations.

SVGFig also maintains a convenient representation of SVG images as Python constructs, so you can load graphics from SVG files, dissect them, manipulate them with an automated script, and save them in batch.

## System Requirements ##

  * Written in pure Python, SVGFig will work on any computer with Python 2.4 or newer installed.  (It will _probably_ work with versions as old as 2.3.)

  * To view SVG images, you will need an SVG 1.1-compliant viewer and/or conversion programs to save to other file types.  Suggestions: [Mozilla Firefox](http://www.mozilla.org/projects/svg/) browser, [Opera](http://www.opera.com/products/desktop/svg/) browser, [Inkscape](http://www.inkscape.org/) drawing program, [librsvg](http://librsvg.sourceforge.net/) developer library, and [others](http://www.svgi.org/).

## Basic Idea ##

SVGFig defines two classes, SVG and Fig.

  * SVG is a "document object model" representation of an SVG image, representing it with a tree of Python objects rather than XML.

  * Fig and its associated primitives (Line, Rect, Ellipse, etc.) build graphics that can be transformed by an arbitrary Python function of two variables or on the complex plane.  Figs can be nested, allowing for convenient composition of transformations.

  * When evaluated, Fig primitives are drawn using an adaptive sampling algorithm which evaluates more points on curves than along straight lines.  If a function is discontinuous, it even breaks that curve at the appropriate places.

## Examples ##

[![](http://svgfig.googlecode.com/svn/wiki/introduction-2.png)](http://code.google.com/p/svgfig/wiki/Introduction) [![](http://svgfig.googlecode.com/svn/wiki/PlottingTutorial-4.png)](http://code.google.com/p/svgfig/wiki/PlottingTutorial) [![](http://svgfig.googlecode.com/svn/wiki/ExamplePoincare-200.png)](http://code.google.com/p/svgfig/wiki/ExamplePoincare)
[![](http://svgfig.googlecode.com/svn/wiki/ExampleRadialPlot-200.png)](http://code.google.com/p/svgfig/wiki/ExampleRadialPlot)

See the [Example Gallery](ExampleGallery.md) to get an idea of what SVGFig can do.

## History ##

This product has been in development for over five years.  As a graduate student in physics, I liked to make plots in [Mathematica](http://www.wolfram.com/), because it provides access to the underlying primitives.  It has limitations, however, in scope, syntax, and licencing.

At first I tried to find a similar open-source product in the Python language.  [PyX](http://pyx.sourceforge.net/) comes close: you can draw anything, including curved coordinate axes, but the syntax is lengthy, which is a liability in the heat of intense data analysis.  It also spawns an external LaTeX process to draw text, which lead to synchronization issues when I mistyped LaTeX commands.

I wrote several wrappers of [PyX](http://pyx.sourceforge.net/) and [matplotlib](http://matplotlib.sourceforge.net/) before admitting that I needed to create a new product.  The first version, called Plothon (the Barbarion!), drew primitives using [GTK+](http://www.gtk.org/) (9000 lines).  I hadn't thought carefully enough about the overall structure, so the result wasn't much better than existing plotting packages.

Inspired the beautiful idea of generic, nested coordinates systems, I re-wrote the whole project, this time in [QT](http://trolltech.com/products/qt) (11000 lines).  Unfortunately, this version became mired in excessive type-checking, which led to recursive loops and random crashes.

Realizing that simplicity is key, I re-wrote everything _again_, relying on SVG to encode the graphics (4000 lines).  In the process of development, this SVG-based version became a little messy and overstructured, so I purified it, maintaining functionality.  The present version, renamed SVGFig, is only 2300 lines.

Now it's done.  It's beautiful!  Enjoy it!

**Update:** after some brainstorming sessions with Jim B. months ago, we came up with an improved structure for the project.  I finally put these ideas together into a [2.0.0alpha2](http://svgfig.googlecode.com/files/svgfig-2.0.0alpha2.tgz) version that you can read about in [Version2Announcement](Version2Announcement.md).  As the name implies, it is neither complete nor guaranteed to be bug-free, but if you're interested in contributing, I would love the help!  All you need is a [Google/GMail account](https://www.google.com/accounts/NewAccount) (and [send me an e-mail](mailto:jpivarski@gmail.com)).