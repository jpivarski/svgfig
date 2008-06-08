#!/usr/bin/env python

from distutils.core import setup, Extension
import os

setup(name="SVGFig",
      version="2.0.0",
      description="SVGFig: Quantitative drawing in Python and SVG",
      author="Jim Pivarski",
      author_email="jpivarski@gmail.com",
      url="http://code.google.com/p/svgfig/",
      py_modules=[os.path.join("svgfig", "__init__"),
                  os.path.join("svgfig", "svgfig"),
                  os.path.join("svgfig", "svg"),
                  os.path.join("svgfig", "fig"),
                  os.path.join("svgfig", "defaults"),
                  os.path.join("svgfig", "trans"),
                  os.path.join("svgfig", "pathdata"),
                  os.path.join("svgfig", "curve"),
                  ],
      ext_modules=[Extension(os.path.join("svgfig", "_curve"), [os.path.join("svgfig", "_curve.c")], {}),
                   ],
     )
