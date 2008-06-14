### default values, may be modified at runtime by importing defaults

import math, os, re, platform
import pathdata

##############################################################################

if re.search("windows", platform.system(), re.I):
  try:
    import _winreg
    directory = _winreg.QueryValueEx(_winreg.OpenKey(_winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\Current Version\Explorer\Shell Folders"), "Desktop")[0]
  except:
    directory = os.path.expanduser("~") + os.sep + "Desktop"

xml_header = """\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
"""

##############################################################################

# "inline" and "signature" are mutually exclusive (inline wins if there's a conflict, but that's poor design)
inline = []
signature = {}

# "require" items and "defaults" keys are mutually exclusive and everything in the signature must fall into one or the other
require = {}
defaults = {}

# In general, transformation rules should be good enough to faithfully represent any linear transformation
# (Since we only have a small set of vertices, we can't do the kind of
# conformance to arbitrary non-linear transformations that we do for Curves)

##### a
##### altGlyph
##### altGlyphDef
##### altGlyphItem
##### animate
##### animateColor
##### animateMotion
##### animateTransform
##### circle
signature["circle"] = ["cx", "cy", "r", "stroke", "fill"]
require["circle"] = ["cx", "cy", "r"]
defaults["circle"] = {"stroke": "black", "fill": "none"}
# transform_circle doesn't yet follow the rule given above: it handles translations and rotations, but not skews
# for that, we'd have to turn it into an ellipse (I suppose it's possible to change the tag inline)
def transform_circle(func, obj):
  x1, y1 = func(float(obj.cx), float(obj.cy))
  x2, y2 = func(float(obj.cx) + float(obj.r), float(obj.cy))
  obj.cx, obj.cy = x1, y1
  obj.r = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
def bbox_circle(obj):
  return BBox(obj.cx - obj.r, obj.cx + obj.r, obj.cy - obj.r, obj.cy + obj.r)

##### clipPath
##### color-profile
##### cursor
##### definition-src
##### defs
inline.append("defs")

##### desc
##### ellipse
##### feBlend
##### feColorMatrix
##### feComponentTransfer
##### feComposite
##### feConvolveMatrix
##### feDiffuseLighting
##### feDisplacementMap
##### feDistantLight
##### feFlood
##### feFuncA
##### feFuncB
##### feFuncG
##### feFuncR
##### feGaussianBlur
##### feImage
##### feMerge
##### feMergeNode
##### feMorphology
##### feOffset
##### fePointLight
##### feSpecularLighting
##### feSpotLight
##### feTile
##### feTurbulence
##### filter
##### font
##### font-face
##### font-face-format
##### font-face-name
##### font-face-src
##### font-face-uri
##### foreignObject
##### g
inline.append("g")
def transform_g(func, obj):
  for child in obj.children:
    child.transform(func)
def bbox_g(obj):
  output = BBox(None, None, None, None)
  for child in obj.children:
    output += child.bbox()
  return output

##### glyph
##### glyphRef
##### hkern
##### image
##### line
signature["line"] = ["x1", "y1", "x2", "y2", "stroke"]
require["line"] = ["x1", "y1", "x2", "y2"]
defaults["line"] = {"stroke": "black"}
def transform_line(func, obj):
  x1, y1 = func(float(obj.x1), float(obj.y1))
  x2, y2 = func(float(obj.x2), float(obj.y2))
  obj.x1, obj.y1 = x1, y1
  obj.x2, obj.y2 = x2, y2
def bbox_line(obj):
  return BBox(obj.x1, obj.x2, obj.y1, obj.y2)

##### linearGradient
##### marker
inline.append("marker")

##### mask
##### metadata
##### missing-glyph
##### mpath
##### path
signature["path"] = ["d", "stroke", "fill"]
require["path"] = []
defaults["path"] = {"d": [], "stroke": "black", "fill": "none"}
def transform_path(func, obj):
  obj.d = pathdata.transform(func, pathdata.parse(obj.d))
def bbox_path(obj):
  return pathdata.bbox(pathdata.parse(obj.d))
  
##### pattern
##### polygon
##### polyline
##### radialGradient
##### rect
signature["rect"] = ["x", "y", "width", "height", "stroke", "fill"]
require["rect"] = ["x", "y", "width", "height"]
defaults["rect"] = {"stroke": "black", "fill": "none"}
def transform_rect(func, obj):
  x1, y1 = func(float(obj.x), float(obj.y))
  x2, y2 = func(float(obj.x) + float(obj.width), float(obj.y) + float(obj.height))
  obj.x, obj.y = x1, y1
  obj.width, obj.height = x2 - x1, y2 - y1
def bbox_rect(obj):
  return BBox(obj.x, obj.x + obj.width, obj.y, obj.y + obj.height)

##### script
##### set
##### stop
##### style
##### svg
signature["svg"] = ["width", "height", "viewBox"]
defaults["svg"] = {"width": 400, "height": 400, "viewBox": (0, 0, 100, 100),
                   "style": {"stroke-width": "0.5pt", "font-size": "4px", "text-anchor": "middle"},
                   "font-family": ["Helvetica", "Arial", "FreeSans", "Sans", "sans", "sans-serif"],
                   "xmlns": "http://www.w3.org/2000/svg", "xmlns:xlink": "http://www.w3.org/1999/xlink", "version":"1.1",
                   }
def transform_svg(func, obj):
  for child in obj.children:
    child.transform(func)
def bbox_svg(obj):
  output = BBox(None, None, None, None)
  for child in obj.children:
    output += child.bbox()
  return output

##### switch
##### symbol
inline.append("symbol")

##### text
signature["text"] = ["x", "y", "stroke", "fill"]
require["text"] = ["x", "y"]
defaults["text"] = {"stroke": "none", "fill": "black"}
def transform_text(func, obj):
  obj.x, obj.y = func(obj.x, obj.y)
  for child in obj.children:
    if callable(getattr(child, "transform", None)):
      child.transform(func)
def bbox_text(obj):
  output = BBox(obj.x, obj.x, obj.y, obj.y) # how to calculate text size???
  for child in obj.children:
    if callable(getattr(child, "bbox", None)):
      output += child.bbox()
  return output

##### textPath
##### title
##### tref
##### tspan
inline.append("tspan")
def transform_tspan(func, obj):
  for child in obj.children:
    if callable(getattr(child, "transform", None)):
      child.transform(func)
def bbox_text(obj):
  output = BBox(obj.x, obj.x, obj.y, obj.y) # how to calculate text size???
  for child in obj.children:
    if callable(getattr(child, "bbox", None)):
      output += child.bbox()
  return output

##### use
signature["use"] = ["x", "y", "xlink:href"]
require["use"] = ["x", "y", "xlink:href"]
def transform_use(func, obj):
  obj.x, obj.y = func(float(obj.x), float(obj.y))
def bbox_use(obj):
  return BBox(obj.x, obj.x, obj.y, obj.y)

##### view
##### vkern

##############################################################################

class BBox:
  def __init__(self, xmin, xmax, ymin, ymax):
    self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax

  def __repr__(self):
    return "<BBox xmin=%g xmax=%g ymin=%g ymax=%g>" % (self.xmin, self.xmax, self.ymin, self.ymax)

  def insert(self, x, y):
    if self.xmin == None or x < self.xmin: self.xmin = x
    if self.ymin == None or y < self.ymin: self.ymin = y
    if self.xmax == None or x > self.xmax: self.xmax = x
    if self.ymax == None or y > self.ymax: self.ymax = y

  def __add__(self, other):
    output = BBox(self.xmin, self.xmax, self.ymin, self.ymax)
    output += other
    return output

  def __iadd__(self, other):
    if self.xmin is None: self.xmin = other.xmin
    elif other.xmin is None: pass
    else: self.xmin = min(self.xmin, other.xmin)

    if self.xmax is None: self.xmax = other.xmax
    elif other.xmax is None: pass
    else: self.xmax = max(self.xmax, other.xmax)

    if self.ymin is None: self.ymin = other.ymin
    elif other.ymin is None: pass
    else: self.ymin = min(self.ymin, other.ymin)

    if self.ymax is None: self.ymax = other.ymax
    elif other.ymax is None: pass
    else: self.ymax = max(self.ymax, other.ymax)

    return self

  def __eq__(self, other):
    return self.xmin == other.xmin and self.xmax == other.xmax and self.ymin == other.ymin and self.ymax == other.ymax

  def __ne__(self, other): return not (self == other)


