#!/usr/bin/env python

from distutils.core import setup, Extension
from distutils.command.build_ext import build_ext
import os

import svgfig.defaults

extension_features = {
  "_curve": None
  }

class my_build_ext(build_ext):
    def build_extension(self, extension):
        try:
            build_ext.build_extension(self, extension)
        except:
            for ext, feat in extension_features.items():
                if ext in extension.name and feat is None:
                    raise Exception, "Failed to compile %s" % ext

            print "************************************************************************************************"
            print ""
            print "Note: couldn't compile \"%s\", so you will be unable to use this feature:" % extension.name
            print ""
            for ext, feat in extension_features.items():
                if ext in extension.name:
                    print feat
                    break
            print ""
            print "************************************************************************************************"

curve_extension = Extension(os.path.join("svgfig", "_curve"), [os.path.join("svgfig", "_curve.c")], {})

setup(name="SVGFig",
      version=svgfig.defaults.version,
      description="SVGFig: Quantitative drawing in Python and SVG",
      author="Jim Pivarski",
      author_email="jpivarski@gmail.com",
      url="http://code.google.com/p/svgfig/",
      py_modules=[os.path.join("svgfig", "__init__"),
                  os.path.join("svgfig", "curve"),
                  os.path.join("svgfig", "defaults"),
                  os.path.join("svgfig", "glyphs"),
                  os.path.join("svgfig", "interactive"),
                  os.path.join("svgfig", "pathdata"),
                  os.path.join("svgfig", "plot"),
                  os.path.join("svgfig", "svg"),
                  os.path.join("svgfig", "trans"),
                  ],
      cmdclass={"build_ext": my_build_ext},
      ext_modules=[curve_extension],
     )
