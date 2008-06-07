import math, os, re, platform
import pathdata

# default values, may be modified at runtime by importing

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

# inline and signature are mutually exclusive (inline wins if there's a conflict, but that's poor design)
inline = []
signature = {}

# require items and defaults keys are mutually exclusive and partition the signature
require = {}
defaults = {}

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
def transform_circle(func, svg):
  x1, y1 = func(float(svg.cx), float(svg.cy))
  x2, y2 = func(float(svg.cx) + float(svg.r), float(svg.cy))
  svg.cx, svg.cy = x1, y1
  svg.r = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

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
def transform_g(func, svg):
  for child in svg.children:
    child.transform(func)

##### glyph
##### glyphRef
##### hkern
##### image
##### line
signature["line"] = ["x1", "y1", "x2", "y2", "stroke"]
require["line"] = ["x1", "y1", "x2", "y2"]
defaults["line"] = {"stroke": "black"}
def transform_line(func, svg):
  x1, y1 = func(float(svg.x1), float(svg.y1))
  x2, y2 = func(float(svg.x2), float(svg.y2))
  svg.x1, svg.y1 = x1, y1
  svg.x2, svg.y2 = x2, y2

##### linearGradient
##### marker
inline.append("marker")
def transform_marker(func, svg):
  for child in svg.children:
    child.transform(func)

##### mask
##### metadata
##### missing-glyph
##### mpath
##### path
signature["path"] = ["d", "stroke", "fill"]
require["path"] = []
defaults["path"] = {"d": [], "stroke": "black", "fill": "none"}
def transform_path(func, svg):
  svg.d = pathdata.transform(func, pathdata.parse(svg.d))
  
##### pattern
##### polygon
##### polyline
##### radialGradient
##### rect
signature["rect"] = ["x", "y", "width", "height", "stroke", "fill"]
require["rect"] = ["x", "y", "width", "height"]
defaults["rect"] = {"stroke": "black", "fill": "none"}
def transform_rect(func, svg):
  x1, y1 = func(float(svg.x), float(svg.y))
  x2, y2 = func(float(svg.x) + float(svg.width), float(svg.y) + float(svg.height))
  svg.x, svg.y = x1, y1
  svg.width, svg.height = x2 - x1, y2 - y1

##### script
##### set
##### stop
##### style
##### svg
signature["svg"] = ["width", "height", "viewBox"]
defaults["svg"] = {"width": 400, "height": 400, "viewBox": (0, 0, 100, 100),
                   "style": {"stroke-width":"0.5pt", "text-anchor":"middle"},
                   "font-family": ["Helvetica", "Arial", "FreeSans", "Sans", "sans", "sans-serif"],
                   "xmlns": "http://www.w3.org/2000/svg", "xmlns:xlink": "http://www.w3.org/1999/xlink", "version":"1.1",
                   }
def transform_svg(func, svg):
  for child in svg.children:
    child.transform(func)

##### switch
##### symbol
inline.append("symbol")
def transform_symbol(func, svg):
  for child in svg.children:
    child.transform(func)

##### text
signature["text"] = ["x", "y", "stroke", "fill"]
require["text"] = ["x", "y"]
defaults["text"] = {"stroke": "none", "fill": "black"}
def transform_text(func, svg):
  svg.x, svg.y = func(svg.x, svg.y)
  for child in svg.children:
    child.transform(func)

##### textPath
##### title
##### tref
##### tspan
inline.append("tspan")
def transform_tspan(func, svg):
  for child in svg.children:
    child.transform(func)

##### use
signature["use"] = ["x", "y", "xlink:href"]
require["use"] = ["x", "y", "xlink:href"]
def transform_use(func, svg):
  svg.x, svg.y = func(float(svg.x), float(svg.y))

##### view
##### vkern
