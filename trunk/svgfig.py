# svgfig.py copyright (C) 2008 Jim Pivarski <jpivarski@gmail.com>
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# 
# Full licence is in the file COPYING and at http://www.gnu.org/copyleft/gpl.html

import re, codecs, os, copy, itertools, math, cmath, random, sys, copy
epsilon = 1e-5

hacks = {}
hacks["inkscape-text-vertical-shift"] = None

def rgb(r, g, b, maximum=1.):
  return "#%02x%02x%02x" % (max(0, min(r*255./maximum, 255)), max(0, min(g*255./maximum, 255)), max(0, min(b*255./maximum, 255)))

class SVG:
  def __init__(self, *t_sub, **attr):
    if len(t_sub) == 0: raise TypeError, "SVG element must have a t (SVG type)"

    # first argument is t (SVG type)
    self.t = t_sub[0]
    # the rest are sub-elements
    self.sub = list(t_sub[1:])

    # keyword arguments are attributes
    # need to preprocess to handle differences between SVG and Python syntax
    for name in attr.keys():
      name_colon = re.sub("__", ":", name)
      if name_colon != name:
        attr[name_colon] = attr[name]
        del attr[name]
        name = name_colon

      name_dash = re.sub("_", "-", name)
      if name_dash != name:
        attr[name_dash] = attr[name]
        del attr[name]
        name = name_dash

    self.attr = attr

  def __getitem__(self, ti):
    obj = self
    if isinstance(ti, (list, tuple)):
      for i in ti[:-1]: obj = obj[i]
      ti = ti[-1]

    if isinstance(ti, (int, long, slice)): return obj.sub[ti]
    else: return obj.attr[ti]

  def __setitem__(self, ti, value):
    obj = self
    if isinstance(ti, (list, tuple)):
      for i in ti[:-1]: obj = obj[i]
      ti = ti[-1]

    if isinstance(ti, (int, long, slice)): obj.sub[ti] = value
    else: obj.attr[ti] = value

  def __delitem__(self, ti):
    obj = self
    if isinstance(ti, (list, tuple)):
      for i in ti[:-1]: obj = obj[i]
      ti = ti[-1]

    if isinstance(ti, (int, long, slice)): del obj.sub[ti]
    else: del obj.attr[ti]

  def __contains__(self, value):
    return value in self.attr

  def __eq__(self, other):
    if id(self) == id(other): return True
    return isinstance(other, SVG) and self.t == other.t and self.sub == other.sub and self.attr == other.attr

  def __ne__(self, other):
    return not (self == other)

  def append(self, x): self.sub.append(x)

  def prepend(self, x): self.sub[0:0] = [x]

  def extend(self, x): self.sub.extend(x)

  def clone(self, shallow=False):
    if shallow:
      return copy.copy(self)
    else:
      return copy.deepcopy(self)

  ### nested class
  class SVGDepthIterator:
    def __init__(self, svg, ti, depth_limit):
      self.svg = svg
      self.ti = ti
      self.shown = False
      self.depth_limit = depth_limit

    def __iter__(self): return self

    def next(self):
      if not self.shown:
        self.shown = True
        if self.ti != ():
          return self.ti, self.svg

      if not isinstance(self.svg, SVG): raise StopIteration
      if self.depth_limit != None and len(self.ti) >= self.depth_limit: raise StopIteration

      if "iterators" not in self.__dict__:
        self.iterators = []
        for i, s in enumerate(self.svg.sub):
          self.iterators.append(self.__class__(s, self.ti + (i,), self.depth_limit))
        for k, s in self.svg.attr.items():
          self.iterators.append(self.__class__(s, self.ti + (k,), self.depth_limit))
        self.iterators = itertools.chain(*self.iterators)

      return self.iterators.next()
  ### end nested class

  def depth_first(self, depth_limit=None):
    return self.SVGDepthIterator(self, (), depth_limit)

  def breadth_first(self, depth_limit=None):
    raise NotImplementedError, "Got an algorithm for breadth-first searching a tree without effectively copying the tree?"

  def __iter__(self): return self.depth_first()

  def items(self, sub=True, attr=True, text=True):
    output = []
    for ti, s in self:
      show = False
      if isinstance(ti[-1], (int, long)):
        if isinstance(s, basestring): show = text
        else: show = sub
      else: show = attr

      if show: output.append((ti, s))
    return output

  def keys(self, sub=True, attr=True, text=True): return [ti for ti, s in self.items(sub, attr, text)]

  def values(self, sub=True, attr=True, text=True): return [s for ti, s in self.items(sub, attr, text)]

  def __repr__(self): return self.xml(depth_limit=0)

  def __str__(self): return self.tree(sub=True, attr=False, text=False)

  def tree(self, depth_limit=None, sub=True, attr=True, text=True, tree_width=20, obj_width=80):
    output = []

    line = "%s %s" % (("%%-%ds" % tree_width) % repr(None), ("%%-%ds" % obj_width) % (repr(self))[0:obj_width])
    output.append(line)

    for ti, s in self.depth_first(depth_limit):
      show = False
      if isinstance(ti[-1], (int, long)):
        if isinstance(s, basestring): show = text
        else: show = sub
      else: show = attr

      if show:
        line = "%s %s" % (("%%-%ds" % tree_width) % repr(list(ti)), ("%%-%ds" % obj_width) % ("    "*len(ti) + repr(s))[0:obj_width])
        output.append(line)

    return "\n".join(output)

  def xml(self, indent="    ", newl="\n", depth_limit=None, depth=0):
    attrstr = []
    for n, v in self.attr.items(): attrstr.append(" %s=%s" % (n, repr(v)))
    attrstr = "".join(attrstr)

    if len(self.sub) == 0: return "%s<%s%s />" % (indent * depth, self.t, attrstr)

    if depth_limit == None or depth_limit > depth:
      substr = []
      for s in self.sub:
        if isinstance(s, SVG):
          substr.append(s.xml(indent, newl, depth_limit, depth + 1) + newl)
        elif isinstance(s, str):
          substr.append("%s%s%s" % (indent * (depth + 1), s, newl))
        else:
          substr.append("%s%s%s" % (indent * (depth + 1), repr(s), newl))
      substr = "".join(substr)

      return "%s<%s%s>%s%s%s</%s>" % (indent * depth, self.t, attrstr, newl, substr, indent * depth, self.t)

    else:
      return "%s<%s (%d sub)%s />" % (indent * depth, self.t, len(self.sub), attrstr)

  def standalone_xml(self, indent="    ", newl="\n"):
    if self.t == "svg": top = self
    else: top = canvas(self)
    return "<?xml version=\"1.0\" standalone=\"no\"?>\n<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n\n"+("".join(top.__standalone_xml(indent, newl)))

  def __standalone_xml(self, indent, newl):
    output = [u"<%s" % self.t]

    for n, v in self.attr.items(): output.append(u" %s=\"%s\"" % (n, v))

    if len(self.sub) == 0:
      output.append(u" />%s%s" % (newl, newl))
      return output

    elif self.t == "text" or self.t == "tspan" or self.t == "style":
      output.append(u">")

    else:
      output.append(u">%s%s" % (newl, newl))

    for s in self.sub:
      if isinstance(s, SVG): output.extend(s.__standalone_xml(indent, newl))
      else: output.append(unicode(s))

    if self.t == "tspan": output.append(u"</%s>" % self.t)
    else: output.append(u"</%s>%s%s" % (self.t, newl, newl))

    return output

  def save(self, fileName="tmp.svg", encoding="utf-8", compresslevel=None):
    if compresslevel != None or re.search("\.svgz$", fileName, re.I) or re.search("\.gz$", fileName, re.I):
      import gzip
      if compresslevel == None:
        f = gzip.GzipFile(fileName, "w")
      else:
        f = gzip.GzipFile(fileName, "w", compresslevel)

      f = codecs.EncodedFile(f, "utf-8", encoding)
      f.write(self.standalone_xml())
      f.close()

    else:
      f = codecs.open(fileName, "w", encoding=encoding)
      f.write(self.standalone_xml())
      f.close()

  def inkview(self, fileName="tmp.svg", encoding="utf-8"):
    self.save(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "inkview", ("inkview", fileName))

  def inkscape(self, fileName="tmp.svg", encoding="utf-8"):
    self.save(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "inkscape", ("inkscape", fileName))

  def firefox(self, fileName="tmp.svg", encoding="utf-8"):
    self.save(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "firefox", ("firefox", fileName))

######################################################################

def canvas(*sub, **attr):
  defaults = {"width": "400px", "height": "400px", "viewBox": "0 0 100 100", \
              "xmlns": "http://www.w3.org/2000/svg", "xmlns:xlink": "http://www.w3.org/1999/xlink", "version":"1.1", \
              "style": "stroke:black; fill:none; stroke-width:0.5pt; stroke-linejoin:round; text-anchor:middle", \
              "font-family": "Helvetica,Arial,FreeSans,Sans,sans,sans-serif", \
              }
  defaults.update(attr)
  attr = defaults

  if sub == None or sub == ():
    return SVG("svg", **attr)
  else:
    return SVG("svg", *sub, **attr)

def canvas_outline(*sub, **attr):
  svg = canvas(*sub, **attr)
  match = re.match("[, \t]*([0-9e.+\-]+)[, \t]+([0-9e.+\-]+)[, \t]+([0-9e.+\-]+)[, \t]+([0-9e.+\-]+)[, \t]*", svg["viewBox"])
  if match == None: raise ValueError, "canvas viewBox is incorrectly formatted"
  x, y, width, height = [float(x) for x in match.groups()]
  svg.prepend(SVG("rect", x=x, y=y, width=width, height=height, stroke="none", fill="cornsilk"))
  svg.append(SVG("rect", x=x, y=y, width=width, height=height, stroke="black", fill="none"))
  return svg

def template(fileName, svg, replaceme="REPLACEME"):
  output = load(fileName)
  for ti, s in output:
    if isinstance(s, SVG) and s.t == replaceme:
      output[ti] = svg
  return output

######################################################################

def load(fileName=None): return load_stream(file(fileName))

def load_stream(stream):
  from xml.sax import saxutils, make_parser
  from xml.sax.handler import feature_namespaces, feature_external_ges, feature_external_pes

  class ContentHandler(saxutils.DefaultHandler):
    def __init__(self):
      self.stack = []
      self.output = None
      self.all_whitespace = re.compile("^\s*$")

    def startElement(self, name, attr):
      s = SVG(name)
      s.attr = dict(attr.items())
      if len(self.stack) > 0:
        last = self.stack[-1]
        last.sub.append(s)
      self.stack.append(s)

    def characters(self, ch):
      if not isinstance(ch, basestring) or self.all_whitespace.match(ch) == None:
        if len(self.stack) > 0:
          last = self.stack[-1]
          if len(last.sub) > 0 and isinstance(last.sub[-1], basestring):
            last.sub[-1] = last.sub[-1] + "\n" + ch
          else:
            last.sub.append(ch)

    def endElement(self, name):
      if len(self.stack) > 0:
        last = self.stack[-1]
        if isinstance(last, SVG) and last.t == "style" and "type" in last.attr and last.attr["type"] == "text/css" and len(last.sub) == 1 and isinstance(last.sub[0], basestring):
          last.sub[0] = "<![CDATA[\n" + last.sub[0] + "]]>"

      self.output = self.stack.pop()

  ch = ContentHandler()
  parser = make_parser()
  parser.setContentHandler(ch)
  parser.setFeature(feature_namespaces, 0)
  parser.setFeature(feature_external_ges, 0)
  parser.parse(stream)
  return ch.output

######################################################################

def totrans(expr, vars=("x", "y"), globals=None, locals=None):
  if callable(expr):
    if expr.func_code.co_argcount == 2:
      return expr

    elif expr.func_code.co_argcount == 1:
      split = lambda z: (z.real, z.imag)
      output = lambda x, y: split(func(x + y*1j))
      output.func_name = func.func_name
      return output

    else:
      raise TypeError, "must be a function of 2 or 1 variables"

  if len(vars) == 2:
    g = math.__dict__
    if globals != None: g.update(globals)
    output = eval("lambda %s, %s: (%s)" % (vars[0], vars[1], expr), g, locals)
    output.func_name = "%s,%s -> %s" % (vars[0], vars[1], expr)
    return output

  elif len(vars) == 1:
    g = cmath.__dict__
    if globals != None: g.update(globals)
    output = eval("lambda %s: (%s)" % (vars[0], expr), g, locals)
    split = lambda z: (z.real, z.imag)
    output2 = lambda x, y: split(output(x + y*1j))
    output2.func_name = "%s -> %s" % (vars[0], expr)
    return output2

  else:
    raise TypeError, "vars must have 2 or 1 elements"

def window(xmin, xmax, ymin, ymax, x=0, y=0, width=100, height=100, xlogbase=None, ylogbase=None, minusInfinity=-1000, flipx=False, flipy=True):
  if flipx:
    ox1 = x + width
    ox2 = x
  else:
    ox1 = x
    ox2 = x + width
  if flipy:
    oy1 = y + height
    oy2 = y
  else:
    oy1 = y
    oy2 = y + height
  ix1 = xmin
  iy1 = ymin
  ix2 = xmax
  iy2 = ymax
  
  if xlogbase != None and (ix1 <= 0. or ix2 <= 0.): raise ValueError, "x range incompatible with log scaling: (%g, %g)" % (ix1, ix2)

  if ylogbase != None and (iy1 <= 0. or iy2 <= 0.): raise ValueError, "y range incompatible with log scaling: (%g, %g)" % (iy1, iy2)

  def maybelog(t, it1, it2, ot1, ot2, logbase):
    if t <= 0.: return minusInfinity
    else:
      return ot1 + 1.*(math.log(t, logbase) - math.log(it1, logbase))/(math.log(it2, logbase) - math.log(it1, logbase)) * (ot2 - ot1)

  xlogstr, ylogstr = "", ""

  if xlogbase == None:
    xfunc = lambda x: ox1 + 1.*(x - ix1)/(ix2 - ix1) * (ox2 - ox1)
  else:
    xfunc = lambda x: maybelog(x, ix1, ix2, ox1, ox2, xlogbase)
    xlogstr = " xlog=%g" % xlogbase

  if ylogbase == None:
    yfunc = lambda y: oy1 + 1.*(y - iy1)/(iy2 - iy1) * (oy2 - oy1)
  else:
    yfunc = lambda y: maybelog(y, ylogbase)
    ylogstr = " ylog=%g" % ylogbase

  output = lambda x, y: (xfunc(x), yfunc(y))

  output.func_name = "(%g, %g), (%g, %g) -> (%g, %g), (%g, %g)%s%s" % (ix1, ix2, iy1, iy2, ox1, ox2, oy1, oy2, xlogstr, ylogstr)
  return output

def rotate(angle, cx=0, cy=0):
  angle *= math.pi/180.
  return lambda x, y: (cx + math.cos(angle)*(x - cx) - math.sin(angle)*(y - cy), cy + math.sin(angle)*(x - cx) + math.cos(angle)*(y - cy))

class Fig:
  def __repr__(self):
    if self.trans == None:
      return "<Fig (%d items)>" % len(self.d)
    else:
      return "<Fig (%d items) %s>" % (len(self.d), self.trans.func_name)

  def __init__(self, *d, **kwds):
    self.d = list(d)
    defaults = {"trans":None}
    defaults.update(kwds)
    kwds = defaults

    self.trans = kwds["trans"]; del kwds["trans"]
    if len(kwds) != 0:
      raise TypeError, "Fig() got unexpected keyword arguments %s" % kwds.keys()

  def SVG(self, trans=None):
    if trans == None: trans = self.trans
    if isinstance(trans, basestring): trans = totrans(trans)

    output = SVG("g")
    for s in self.d:
      if isinstance(s, SVG):
        output.append(s)

      elif isinstance(s, Fig):
        strans = s.trans
        if isinstance(strans, basestring): strans = totrans(strans)

        if trans == None: subtrans = strans
        elif strans == None: subtrans = trans
        else: subtrans = lambda x,y: trans(*strans(x, y))

        output.sub += s.SVG(subtrans).sub

      elif s == None: pass

      else:
        output.append(s.SVG(trans))

    return output

class Plot:
  def __repr__(self):
    if self.trans == None:
      return "<Plot (%d items)>" % len(self.d)
    else:
      return "<Plot (%d items) %s>" % (len(self.d), self.trans.func_name)

  def __init__(self, xmin, xmax, ymin, ymax, *d, **kwds):
    self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
    self.d = list(d)
    defaults = {"trans":None, "x":5, "y":5, "width":90, "height":90, "flipx":False, "flipy":True, "minusInfinity":-1000, \
                "atx":0, "xticks":-10, "xminiticks":True, "xlabels":True, "xlogbase":None, \
                "aty":0, "yticks":-10, "yminiticks":True, "ylabels":True, "ylogbase":None, \
                "arrows":None, "text_attr":{}, "axis_attr":{}}
    defaults.update(kwds)
    kwds = defaults

    self.trans = kwds["trans"]; del kwds["trans"]
    self.x = kwds["x"]; del kwds["x"]
    self.y = kwds["y"]; del kwds["y"]
    self.width = kwds["width"]; del kwds["width"]
    self.height = kwds["height"]; del kwds["height"]
    self.flipx = kwds["flipx"]; del kwds["flipx"]
    self.flipy = kwds["flipy"]; del kwds["flipy"]
    self.minusInfinity = kwds["minusInfinity"]; del kwds["minusInfinity"]
    self.atx = kwds["atx"]; del kwds["atx"]
    self.xticks = kwds["xticks"]; del kwds["xticks"]
    self.xminiticks = kwds["xminiticks"]; del kwds["xminiticks"]
    self.xlabels = kwds["xlabels"]; del kwds["xlabels"]
    self.xlogbase = kwds["xlogbase"]; del kwds["xlogbase"]
    self.aty = kwds["aty"]; del kwds["aty"]
    self.yticks = kwds["yticks"]; del kwds["yticks"]
    self.yminiticks = kwds["yminiticks"]; del kwds["yminiticks"]
    self.ylabels = kwds["ylabels"]; del kwds["ylabels"]
    self.ylogbase = kwds["ylogbase"]; del kwds["ylogbase"]
    self.arrows = kwds["arrows"]; del kwds["arrows"]
    self.text_attr = kwds["text_attr"]; del kwds["text_attr"]
    self.axis_attr = kwds["axis_attr"]; del kwds["axis_attr"]
    if len(kwds) != 0:
      raise TypeError, "Plot() got unexpected keyword arguments %s" % kwds.keys()

  def SVG(self, trans=None):
    if trans == None: trans = self.trans
    if isinstance(trans, basestring): trans = totrans(trans)

    self.last_window = window(self.xmin, self.xmax, self.ymin, self.ymax, x=self.x, y=self.y, width=self.width, height=self.height, \
                              xlogbase=self.xlogbase, ylogbase=self.ylogbase, minusInfinity=self.minusInfinity, flipx=self.flipx, flipy=self.flipy)

    d = [Axes(self.xmin, self.xmax, self.ymin, self.ymax, self.atx, self.aty, \
              self.xticks, self.xminiticks, self.xlabels, self.xlogbase, \
              self.yticks, self.yminiticks, self.ylabels, self.ylogbase, \
              self.arrows, self.text_attr, **self.axis_attr)] \
        + self.d

    return Fig(Fig(*d, **{"trans":trans})).SVG(self.last_window)
    
class Frame:
  text_defaults = {"stroke":"none", "fill":"black", "font-size":5}
  axis_defaults = {}

  tick_length = 1.5
  minitick_length = 0.75
  text_xaxis_offset = 1.
  text_yaxis_offset = 2.
  text_xtitle_offset = 6.
  text_ytitle_offset = 12.

  def __repr__(self):
    return "<Frame (%d items)>" % len(self.d)

  def __init__(self, xmin, xmax, ymin, ymax, *d, **kwds):
    self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
    self.d = list(d)
    defaults = {"x":20, "y":5, "width":75, "height":80, "flipx":False, "flipy":True, "minusInfinity":-1000, \
                "xtitle":None, "xticks":-10, "xminiticks":True, "xlabels":True, "x2labels":None, "xlogbase":None, \
                "ytitle":None, "yticks":-10, "yminiticks":True, "ylabels":True, "y2labels":None, "ylogbase":None, \
                "text_attr":{}, "axis_attr":{}}
    defaults.update(kwds)
    kwds = defaults

    self.x = kwds["x"]; del kwds["x"]
    self.y = kwds["y"]; del kwds["y"]
    self.width = kwds["width"]; del kwds["width"]
    self.height = kwds["height"]; del kwds["height"]
    self.flipx = kwds["flipx"]; del kwds["flipx"]
    self.flipy = kwds["flipy"]; del kwds["flipy"]
    self.minusInfinity = kwds["minusInfinity"]; del kwds["minusInfinity"]
    self.xtitle = kwds["xtitle"]; del kwds["xtitle"]
    self.xticks = kwds["xticks"]; del kwds["xticks"]
    self.xminiticks = kwds["xminiticks"]; del kwds["xminiticks"]
    self.xlabels = kwds["xlabels"]; del kwds["xlabels"]
    self.x2labels = kwds["x2labels"]; del kwds["x2labels"]
    self.xlogbase = kwds["xlogbase"]; del kwds["xlogbase"]
    self.ytitle = kwds["ytitle"]; del kwds["ytitle"]
    self.yticks = kwds["yticks"]; del kwds["yticks"]
    self.yminiticks = kwds["yminiticks"]; del kwds["yminiticks"]
    self.ylabels = kwds["ylabels"]; del kwds["ylabels"]
    self.y2labels = kwds["y2labels"]; del kwds["y2labels"]
    self.ylogbase = kwds["ylogbase"]; del kwds["ylogbase"]

    self.text_attr = dict(self.text_defaults)
    self.text_attr.update(kwds["text_attr"]); del kwds["text_attr"]

    self.axis_attr = dict(self.axis_defaults)
    self.axis_attr.update(kwds["axis_attr"]); del kwds["axis_attr"]

    if len(kwds) != 0:
      raise TypeError, "Frame() got unexpected keyword arguments %s" % kwds.keys()

  def SVG(self):
    self.last_window = window(self.xmin, self.xmax, self.ymin, self.ymax, x=self.x, y=self.y, width=self.width, height=self.height, \
                              xlogbase=self.xlogbase, ylogbase=self.ylogbase, minusInfinity=self.minusInfinity, flipx=self.flipx, flipy=self.flipy)

    left = YAxis(self.ymin, self.ymax, self.xmin, self.yticks, self.yminiticks, self.ylabels, self.ylogbase, None, None, None, self.text_attr, **self.axis_attr)
    right = YAxis(self.ymin, self.ymax, self.xmax, self.yticks, self.yminiticks, self.y2labels, self.ylogbase, None, None, None, self.text_attr, **self.axis_attr)
    bottom = XAxis(self.xmin, self.xmax, self.ymin, self.xticks, self.xminiticks, self.xlabels, self.xlogbase, None, None, None, self.text_attr, **self.axis_attr)
    top = XAxis(self.xmin, self.xmax, self.ymax, self.xticks, self.xminiticks, self.x2labels, self.xlogbase, None, None, None, self.text_attr, **self.axis_attr)

    left.tick_start = -self.tick_length
    left.tick_end = 0
    left.minitick_start = -self.minitick_length
    left.minitick_end = 0.
    left.text_start = self.text_yaxis_offset

    right.tick_start = 0.
    right.tick_end = self.tick_length
    right.minitick_start = 0.
    right.minitick_end = self.minitick_length
    right.text_start = -self.text_yaxis_offset
    right.text_attr["text-anchor"] = "start"

    bottom.tick_start = 0.
    bottom.tick_end = self.tick_length
    bottom.minitick_start = 0.
    bottom.minitick_end = self.minitick_length
    bottom.text_start = -self.text_xaxis_offset

    top.tick_start = -self.tick_length
    top.tick_end = 0.
    top.minitick_start = -self.minitick_length
    top.minitick_end = 0.
    top.text_start = self.text_xaxis_offset
    top.text_attr["dominant-baseline"] = "text-after-edge"

    output = Fig(*self.d).SVG(self.last_window)
    output.prepend(left.SVG(self.last_window))
    output.prepend(bottom.SVG(self.last_window))
    output.prepend(right.SVG(self.last_window))
    output.prepend(top.SVG(self.last_window))

    if self.xtitle != None:
      output.append(SVG("text", self.xtitle, transform="translate(%g, %g)" % ((self.x + self.width/2.), (self.y + self.height + self.text_xtitle_offset)), dominant_baseline="text-before-edge", **self.text_attr))
    if self.ytitle != None:
      output.append(SVG("text", self.ytitle, transform="translate(%g, %g) rotate(-90)" % ((self.x - self.text_ytitle_offset), (self.y + self.height/2.)), **self.text_attr))
    return output
    
######################################################################

def pathtoPath(svg):
  if not isinstance(svg, SVG) or svg.t != "path":
    raise TypeError, "Only SVG <path /> objects can be converted into Paths"
  attr = svg.attr
  d = attr["d"]
  del attr["d"]
  return Path(d, **attr)

class Path:
  defaults = {}

  def __repr__(self):
    return "<Path (%d nodes) %s>" % (len(self.d), self.attr)

  def __init__(self, d, **attr):
    if isinstance(d, basestring): self.d = self.parse(d)
    else: self.d = d

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def parse_whitespace(self, index, pathdata):
    while index < len(pathdata) and pathdata[index] in (" ", "\t", "\r", "\n"): index += 1
    return index, pathdata

  def parse_command(self, index, pathdata):
    index, pathdata = self.parse_whitespace(index, pathdata)

    if index >= len(pathdata): return None, index, pathdata
    command = pathdata[index]
    if "A" <= command <= "Z" or "a" <= command <= "z":
      index += 1
      return command, index, pathdata
    else: 
      return None, index, pathdata

  def parse_number(self, index, pathdata):
    index, pathdata = self.parse_whitespace(index, pathdata)

    if index >= len(pathdata): return None, index, pathdata
    first_digit = pathdata[index]

    if "0" <= first_digit <= "9" or first_digit in ("-", "+", "."):
      start = index
      while index < len(pathdata) and ("0" <= pathdata[index] <= "9" or pathdata[index] in ("-", "+", ".", "e", "E")):
        index += 1
      end = index

      index = end
      return float(pathdata[start:end]), index, pathdata
    else: 
      return None, index, pathdata

  def parse_boolean(self, index, pathdata):
    index, pathdata = self.parse_whitespace(index, pathdata)

    if index >= len(pathdata): return None, index, pathdata
    first_digit = pathdata[index]

    if first_digit in ("0", "1"):
      index += 1
      return int(first_digit), index, pathdata
    else:
      return None, index, pathdata

  def parse(self, pathdata):
    output = []
    index = 0
    while True:
      command, index, pathdata = self.parse_command(index, pathdata)
      index, pathdata = self.parse_whitespace(index, pathdata)

      if command == None and index == len(pathdata): break  # this is the normal way out of the loop
      if command in ("Z", "z"):
        output.append((command,))

      ######################
      elif command in ("H", "h", "V", "v"):
        errstring = "Path command \"%s\" requires a number at index %d" % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        if num1 == None: raise ValueError, errstring

        while num1 != None:
          output.append((command, num1))
          num1, index, pathdata = self.parse_number(index, pathdata)

      ######################
      elif command in ("M", "m", "L", "l", "T", "t"):
        errstring = "Path command \"%s\" requires an x,y pair at index %d" % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)

        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None: raise ValueError, errstring
          output.append((command, num1, num2, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)

      ######################
      elif command in ("S", "s", "Q", "q"):
        errstring = "Path command \"%s\" requires a cx,cy,x,y quadruplet at index %d" % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)
        num3, index, pathdata = self.parse_number(index, pathdata)
        num4, index, pathdata = self.parse_number(index, pathdata)

        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None or num3 == None or num4 == None: raise ValueError, errstring
          output.append((command, num1, num2, False, num3, num4, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)
          num3, index, pathdata = self.parse_number(index, pathdata)
          num4, index, pathdata = self.parse_number(index, pathdata)
          
      ######################
      elif command in ("C", "c"):
        errstring = "Path command \"%s\" requires a c1x,c1y,c2x,c2y,x,y sextuplet at index %d" % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)
        num3, index, pathdata = self.parse_number(index, pathdata)
        num4, index, pathdata = self.parse_number(index, pathdata)
        num5, index, pathdata = self.parse_number(index, pathdata)
        num6, index, pathdata = self.parse_number(index, pathdata)
        
        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None or num3 == None or num4 == None or num5 == None or num6 == None: raise ValueError, errstring

          output.append((command, num1, num2, False, num3, num4, False, num5, num6, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)
          num3, index, pathdata = self.parse_number(index, pathdata)
          num4, index, pathdata = self.parse_number(index, pathdata)
          num5, index, pathdata = self.parse_number(index, pathdata)
          num6, index, pathdata = self.parse_number(index, pathdata)

      ######################
      elif command in ("A", "a"):
        errstring = "Path command \"%s\" requires a rx,ry,angle,large-arc-flag,sweep-flag,x,y septuplet at index %d" % (command, index)
        num1, index, pathdata = self.parse_number(index, pathdata)
        num2, index, pathdata = self.parse_number(index, pathdata)
        num3, index, pathdata = self.parse_number(index, pathdata)
        num4, index, pathdata = self.parse_boolean(index, pathdata)
        num5, index, pathdata = self.parse_boolean(index, pathdata)
        num6, index, pathdata = self.parse_number(index, pathdata)
        num7, index, pathdata = self.parse_number(index, pathdata)

        if num1 == None: raise ValueError, errstring

        while num1 != None:
          if num2 == None or num3 == None or num4 == None or num5 == None or num6 == None or num7 == None: raise ValueError, errstring

          output.append((command, num1, num2, False, num3, num4, num5, num6, num7, False))

          num1, index, pathdata = self.parse_number(index, pathdata)
          num2, index, pathdata = self.parse_number(index, pathdata)
          num3, index, pathdata = self.parse_number(index, pathdata)
          num4, index, pathdata = self.parse_boolean(index, pathdata)
          num5, index, pathdata = self.parse_boolean(index, pathdata)
          num6, index, pathdata = self.parse_number(index, pathdata)
          num7, index, pathdata = self.parse_number(index, pathdata)

    return output

  def SVG(self, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans)

    x, y, X, Y = None, None, None, None
    output = []
    for datum in self.d:
      if not isinstance(datum, (tuple, list)):
        raise TypeError, "pathdata elements must be tuples/lists"

      command = datum[0]

      ######################
      if command in ("Z", "z"):
        x, y, X, Y = None, None, None, None
        output.append("Z")

      ######################
      elif command in ("H", "h", "V", "v"):
        command, num1 = datum

        if command == "H" or (command == "h" and x == None): x = num1
        elif command == "h": x += num1
        elif command == "V" or (command == "v" and y == None): y = num1
        elif command == "v": y += num1

        if trans == None: X, Y = x, y
        else: X, Y = trans(x, y)

        output.append("L%g %g" % (X, Y))
        
      ######################
      elif command in ("M", "m", "L", "l", "T", "t"):
        command, num1, num2, isglobal12 = datum

        if trans == None or isglobal12:
          if command.isupper() or X == None or Y == None:
            X, Y = num1, num2
          else:
            X += num1
            Y += num2
          x, y = X, Y

        else:
          if command.isupper() or x == None or y == None:
            x, y = num1, num2
          else:
            x += num1
            y += num2
          X, Y = trans(x, y)

        COMMAND = command.capitalize()
        output.append("%s%g %g" % (COMMAND, X, Y))

      ######################
      elif command in ("S", "s", "Q", "q"):
        command, num1, num2, isglobal12, num3, num4, isglobal34 = datum

        if trans == None or isglobal12:
          if command.isupper() or X == None or Y == None:
            CX, CY = num1, num2
          else:
            CX = X + num1
            CY = Y + num2

        else:
          if command.isupper() or x == None or y == None:
            cx, cy = num1, num2
          else:
            cx = x + num1
            cy = y + num2
          CX, CY = trans(cx, cy)

        if trans == None or isglobal34:
          if command.isupper() or X == None or Y == None:
            X, Y = num3, num4
          else:
            X += num3
            Y += num4
          x, y = X, Y

        else:
          if command.isupper() or x == None or y == None:
            x, y = num3, num4
          else:
            x += num3
            y += num4
          X, Y = trans(x, y)

        COMMAND = command.capitalize()
        output.append("%s%g %g %g %g" % (COMMAND, CX, CY, X, Y))

      ######################
      elif command in ("C", "c"):
        command, num1, num2, isglobal12, num3, num4, isglobal34, num5, num6, isglobal56 = datum

        if trans == None or isglobal12:
          if command.isupper() or X == None or Y == None:
            C1X, C1Y = num1, num2
          else:
            C1X = X + num1
            C1Y = Y + num2

        else:
          if command.isupper() or x == None or y == None:
            c1x, c1y = num1, num2
          else:
            c1x = x + num1
            c1y = y + num2
          C1X, C1Y = trans(c1x, c1y)

        if trans == None or isglobal34:
          if command.isupper() or X == None or Y == None:
            C2X, C2Y = num3, num4
          else:
            C2X = X + num3
            C2Y = Y + num4

        else:
          if command.isupper() or x == None or y == None:
            c2x, c2y = num3, num4
          else:
            c2x = x + num3
            c2y = y + num4
          C2X, C2Y = trans(c2x, c2y)

        if trans == None or isglobal56:
          if command.isupper() or X == None or Y == None:
            X, Y = num5, num6
          else:
            X += num5
            Y += num6
          x, y = X, Y

        else:
          if command.isupper() or x == None or y == None:
            x, y = num5, num6
          else:
            x += num5
            y += num6
          X, Y = trans(x, y)

        COMMAND = command.capitalize()
        output.append("%s%g %g %g %g %g %g" % (COMMAND, C1X, C1Y, C2X, C2Y, X, Y))

      ######################
      elif command in ("A", "a"):
        command, num1, num2, isglobal12, angle, large_arc_flag, sweep_flag, num3, num4, isglobal34 = datum

        oldx, oldy = x, y
        OLDX, OLDY = X, Y

        if trans == None or isglobal34:
          if command.isupper() or X == None or Y == None:
            X, Y = num3, num4
          else:
            X += num3
            Y += num4
          x, y = X, Y

        else:
          if command.isupper() or x == None or y == None:
            x, y = num3, num4
          else:
            x += num3
            y += num4
          X, Y = trans(x, y)
        
        if x != None and y != None:
          centerx, centery = (x + oldx)/2., (y + oldy)/2.
        CENTERX, CENTERY = (X + OLDX)/2., (Y + OLDY)/2.

        if trans == None or isglobal12:
          RX = CENTERX + num1
          RY = CENTERY + num2

        else:
          rx = centerx + num1
          ry = centery + num2
          RX, RY = trans(rx, ry)

        COMMAND = command.capitalize()
        output.append("%s%g %g %g %d %d %g %g" % (COMMAND, RX - CENTERX, RY - CENTERY, angle, large_arc_flag, sweep_flag, X, Y))

      elif command in (",", "."):
        command, num1, num2, isglobal12, angle, num3, num4, isglobal34 = datum
        if trans == None or isglobal34:
          if command == "." or X == None or Y == None:
            X, Y = num3, num4
          else:
            X += num3
            Y += num4
            x, y = None, None

        else:
          if command == "." or x == None or y == None:
            x, y = num3, num4
          else:
            x += num3
            y += num4
          X, Y = trans(x, y)

        if trans == None or isglobal12:
          RX = X + num1
          RY = Y + num2

        else:
          rx = x + num1
          ry = y + num2
          RX, RY = trans(rx, ry)

        RX, RY = RX - X, RY - Y

        X1, Y1 = X + RX * math.cos(angle*math.pi/180.), Y + RX * math.sin(angle*math.pi/180.)
        X2, Y2 = X + RY * math.sin(angle*math.pi/180.), Y - RY * math.cos(angle*math.pi/180.)
        X3, Y3 = X - RX * math.cos(angle*math.pi/180.), Y - RX * math.sin(angle*math.pi/180.)
        X4, Y4 = X - RY * math.sin(angle*math.pi/180.), Y + RY * math.cos(angle*math.pi/180.)

        output.append("M%g %gA%g %g %g 0 0 %g %gA%g %g %g 0 0 %g %gA%g %g %g 0 0 %g %gA%g %g %g 0 0 %g %g" \
                      % (X1, Y1, RX, RY, angle, X2, Y2, RX, RY, angle, X3, Y3, RX, RY, angle, X4, Y4, RX, RY, angle, X1, Y1))

    return SVG("path", d="".join(output), **self.attr)

######################################################################

def funcRtoC(expr, var="t", globals=None, locals=None):
  g = cmath.__dict__
  if globals != None: g.update(globals)
  output = eval("lambda %s: (%s)" % (var, expr), g, locals)
  split = lambda z: (z.real, z.imag)
  output2 = lambda t: split(output(t))
  output2.func_name = "%s -> %s" % (var, expr)
  return output2

def funcRtoR2(expr, var="t", globals=None, locals=None):
  g = math.__dict__
  if globals != None: g.update(globals)
  output = eval("lambda %s: (%s)" % (var, expr), g, locals)
  output.func_name = "%s -> %s" % (var, expr)
  return output

def funcRtoR(expr, var="x", globals=None, locals=None):
  g = math.__dict__
  if globals != None: g.update(globals)
  output = eval("lambda %s: (%s, %s)" % (var, var, expr), g, locals)
  output.func_name = "%s -> %s" % (var, expr)
  return output

class Curve:
  defaults = {}
  random_sampling = True
  recursion_limit = 15
  linearity_limit = 0.05
  discontinuity_limit = 5.

  def __repr__(self):
    return "<Curve %s [%s, %s] %s>" % (self.f, self.low, self.high, self.attr)

  def __init__(self, f, low, high, loop=False, **attr):
    self.f = f
    self.low = low
    self.high = high
    self.loop = loop

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  ### nested class Sample
  class Sample:
    def __repr__(self):
      t, x, y, X, Y = self.t, self.x, self.y, self.X, self.Y
      if t != None: t = "%g" % t
      if x != None: x = "%g" % x
      if y != None: y = "%g" % y
      if X != None: X = "%g" % X
      if Y != None: Y = "%g" % Y
      return "<Curve.Sample t=%s x=%s y=%s X=%s Y=%s>" % (t, x, y, X, Y)

    def __init__(self, t): self.t = t

    def link(self, left, right): self.left, self.right = left, right

    def evaluate(self, f, trans):
      self.x, self.y = f(self.t)
      if trans == None:
        self.X, self.Y = self.x, self.y
      else:
        self.X, self.Y = trans(self.x, self.y)
  ### end Sample

  ### nested class Samples
  class Samples:
    def __repr__(self): return "<Curve.Samples (%d samples)>" % len(self)

    def __init__(self, left, right): self.left, self.right = left, right

    def __len__(self):
      count = 0
      current = self.left
      while current != None:
        count += 1
        current = current.right
      return count

    def __iter__(self):
      self.current = self.left
      return self

    def next(self):
      current = self.current
      if current == None: raise StopIteration
      self.current = self.current.right
      return current
  ### end nested class

  def sample(self, trans=None):
    oldrecursionlimit = sys.getrecursionlimit()
    sys.setrecursionlimit(self.recursion_limit + 100)
    try:
      # the best way to keep all the information while sampling is to make a linked list
      if not (self.low < self.high): raise ValueError, "low must be less than high"
      low, high = self.Sample(float(self.low)), self.Sample(float(self.high))
      low.link(None, high)
      high.link(low, None)

      low.evaluate(self.f, trans)
      high.evaluate(self.f, trans)

      # adaptive sampling between the low and high points
      self.subsample(low, high, 0, trans)

      # Prune excess points where the curve is nearly linear
      left = low
      while left.right != None:
        # increment mid and right
        mid = left.right
        right = mid.right
        if right != None and left.X != None and left.Y != None and mid.X != None and mid.Y != None and right.X != None and right.Y != None:
          numer = left.X*(right.Y - mid.Y) + mid.X*(left.Y - right.Y) + right.X*(mid.Y - left.Y)
          denom = math.sqrt((left.X - right.X)**2 + (left.Y - right.Y)**2)
          if denom != 0. and abs(numer/denom) < self.linearity_limit:
            # drop mid (the garbage collector will get it)
            left.right = right
            right.left = left
          else:
            # increment left
            left = left.right
        else:
          left = left.right

      self.last_samples = self.Samples(low, high)

    finally:
      sys.setrecursionlimit(oldrecursionlimit)

  def subsample(self, left, right, depth, trans=None):
    if self.random_sampling:
      mid = self.Sample(left.t + random.uniform(0.3, 0.7) * (right.t - left.t))
    else:
      mid = self.Sample(left.t + 0.5 * (right.t - left.t))

    left.right = mid
    right.left = mid
    mid.link(left, right)
    mid.evaluate(self.f, trans)

    # calculate the distance of closest approach of mid to the line between left and right
    numer = left.X*(right.Y - mid.Y) + mid.X*(left.Y - right.Y) + right.X*(mid.Y - left.Y)
    denom = math.sqrt((left.X - right.X)**2 + (left.Y - right.Y)**2)

    # if we haven't sampled enough or left fails to be close enough to right, or mid fails to be linear enough...
    if depth < 3 or (denom == 0 and left.t != right.t) or denom > self.discontinuity_limit or (denom != 0. and abs(numer/denom) > self.linearity_limit):

      # and we haven't sampled too many points
      if depth < self.recursion_limit:
        self.subsample(left, mid, depth+1, trans)
        self.subsample(mid, right, depth+1, trans)

      else:
        # We've sampled many points and yet it's still not a small linear gap.
        # Break the line: it's a discontinuity
        mid.y = mid.Y = None

  def SVG(self, trans=None):
    return self.Path(trans).SVG()

  def Path(self, trans=None, local=False):
    if isinstance(trans, basestring): trans = totrans(trans)
    if isinstance(self.f, basestring): self.f = funcRtoR2(self.f)

    self.sample(trans)

    output = []
    for s in self.last_samples:
      if s.X != None and s.Y != None:
        if s.left == None or s.left.Y == None:
          command = "M"
        else:
          command = "L"

        if local: output.append((command, s.x, s.y, False))
        else: output.append((command, s.X, s.Y, True))

    if self.loop: output.append(("Z",))
    return Path(output, **self.attr)

######################################################################

class Poly:
  defaults = {}

  def __repr__(self):
    return "<Poly (%d nodes) mode=%s loop=%s %s>" % (len(self.d), self.mode, repr(self.loop), self.attr)

  def __init__(self, d, mode="L", loop=False, **attr):
    self.d = d
    self.mode = mode
    self.loop = loop

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    return self.Path(trans).SVG()

  def Path(self, trans=None, local=False):
    if isinstance(trans, basestring): trans = totrans(trans)

    if self.mode[0] == "L" or self.mode[0] == "l": mode = "L"
    elif self.mode[0] == "B" or self.mode[0] == "b": mode = "B"
    elif self.mode[0] == "V" or self.mode[0] == "v": mode = "V"
    elif self.mode[0] == "F" or self.mode[0] == "f": mode = "F"
    elif self.mode[0] == "S" or self.mode[0] == "s":
      mode = "S"

      vx, vy = [0.]*len(self.d), [0.]*len(self.d)
      for i in xrange(len(self.d)):
        inext = (i+1) % len(self.d)
        iprev = (i-1) % len(self.d)

        vx[i] = (self.d[inext][0] - self.d[iprev][0])/2.
        vy[i] = (self.d[inext][1] - self.d[iprev][1])/2.
        if not self.loop and (i == 0 or i == len(self.d)-1):
          vx[i], vy[i] = 0., 0.

    else:
      raise ValueError, "mode must be \"lines\", \"bezier\", \"velocity\", \"foreback\", \"smooth\", or an abbreviation"

    d = []
    indexes = range(len(self.d))
    if self.loop and len(self.d) > 0: indexes.append(0)

    for i in indexes:
      inext = (i+1) % len(self.d)
      iprev = (i-1) % len(self.d)

      x, y = self.d[i][0], self.d[i][1]

      if trans == None: X, Y = x, y
      else: X, Y = trans(x, y)

      if d == []:
        if local: d.append(("M", x, y, False))
        else: d.append(("M", X, Y, True))

      elif mode == "L":
        if local: d.append(("L", x, y, False))
        else: d.append(("L", X, Y, True))

      elif mode == "B":
        c1x, c1y = self.d[i][2], self.d[i][3]
        if trans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = trans(c1x, c1y)

        c2x, c2y = self.d[i][4], self.d[i][5]
        if trans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = trans(c2x, c2y)

        if local: d.append(("C", c1x, c1y, False, c2x, c2y, False, x, y, False))
        else: d.append(("C", C1X, C1Y, True, C2X, C2Y, True, X, Y, True))

      elif mode == "V":
        c1x, c1y = self.d[iprev][2]/3. + self.d[iprev][0], self.d[iprev][3]/3. + self.d[iprev][1]
        c2x, c2y = self.d[i][2]/-3. + x, self.d[i][3]/-3. + y

        if trans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = trans(c1x, c1y)
        if trans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = trans(c2x, c2y)

        if local: d.append(("C", c1x, c1y, False, c2x, c2y, False, x, y, False))
        else: d.append(("C", C1X, C1Y, True, C2X, C2Y, True, X, Y, True))

      elif mode == "F":
        c1x, c1y = self.d[iprev][4]/3. + self.d[iprev][0], self.d[iprev][5]/3. + self.d[iprev][1]
        c2x, c2y = self.d[i][2]/-3. + x, self.d[i][3]/-3. + y

        if trans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = trans(c1x, c1y)
        if trans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = trans(c2x, c2y)

        if local: d.append(("C", c1x, c1y, False, c2x, c2y, False, x, y, False))
        else: d.append(("C", C1X, C1Y, True, C2X, C2Y, True, X, Y, True))

      elif mode == "S":
        c1x, c1y = vx[iprev]/3. + self.d[iprev][0], vy[iprev]/3. + self.d[iprev][1]
        c2x, c2y = vx[i]/-3. + x, vy[i]/-3. + y

        if trans == None: C1X, C1Y = c1x, c1y
        else: C1X, C1Y = trans(c1x, c1y)
        if trans == None: C2X, C2Y = c2x, c2y
        else: C2X, C2Y = trans(c2x, c2y)

        if local: d.append(("C", c1x, c1y, False, c2x, c2y, False, x, y, False))
        else: d.append(("C", C1X, C1Y, True, C2X, C2Y, True, X, Y, True))

    if self.loop and len(self.d) > 0: d.append(("Z",))

    return Path(d, **self.attr)

######################################################################

class Text:
  defaults = {"stroke":"none", "fill":"black", "font-size":5}

  def __repr__(self):
    return "<Text %s at (%g, %g) %s>" % (repr(self.d), self.x, self.y, self.attr)

  def __init__(self, x, y, d, **attr):
    self.x = x
    self.y = y
    self.d = d
    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans)

    X, Y = self.x, self.y
    if trans != None: X, Y = trans(X, Y)
    return SVG("text", self.d, x=X, y=Y, **self.attr)

class TextGlobal:
  defaults = {"stroke":"none", "fill":"black", "font-size":5}

  def __repr__(self):
    return "<TextGlobal %s at (%s, %s) %s>" % (repr(self.d), str(self.x), str(self.y), self.attr)

  def __init__(self, x, y, d, **attr):
    self.x = x
    self.y = y
    self.d = d
    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    return SVG("text", self.d, x=self.x, y=self.y, **self.attr)

######################################################################

symbol_templates = {"dot": SVG("symbol", SVG("circle", cx=0, cy=0, r=1, stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                    "box": SVG("symbol", SVG("rect", x1=-1, y1=-1, x2=1, y2=1, stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                    "uptri": SVG("symbol", SVG("path", d="M -1 0.866 L 1 0.866 L 0 -0.866 Z", stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                    "downtri": SVG("symbol", SVG("path", d="M -1 -0.866 L 1 -0.866 L 0 0.866 Z", stroke="none", fill="black"), viewBox="0 0 1 1", overflow="visible"), \
                    }

def make_symbol(id, shape="dot", **attr):
  output = copy.deepcopy(symbol_templates[shape])
  for i in output.sub: i.attr.update(attr)
  output["id"] = id
  return output

class Dots:
  defaults = {}

  def __repr__(self):
    return "<Dots (%d nodes) %s>" % (len(self.d), self.attr)

  def __init__(self, d, symbol="Untitled", width=1., height=1., **attr):
    self.d = d
    self.width = width
    self.height = height

    self.attr = dict(self.defaults)
    self.attr.update(attr)

    if isinstance(symbol, SVG): self.symbol = symbol
    else: self.symbol = make_symbol(symbol)

  def SVG(self, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans)

    output = SVG("g", SVG("defs", self.symbol))
    id = "#%s" % self.symbol["id"]

    for p in self.d:
      x, y = p[0], p[1]

      if trans == None: X, Y = x, y
      else: X, Y = trans(x, y)

      item = SVG("use", x=X, y=Y, xlink__href=id)
      if self.width != None: item["width"] = self.width
      if self.height != None: item["height"] = self.height
      output.append(item)
      
    return output

######################################################################

marker_templates = {"arrow_start": SVG("marker", SVG("path", d="M 9 3.6 L 10.5 0 L 0 3.6 L 10.5 7.2 L 9 3.6 Z"), viewBox="0 0 10.5 7.2", refX="9", refY="3.6", markerWidth="10.5", markerHeight="7.2", markerUnits="strokeWidth", orient="auto", stroke="none", fill="black"), \
                    "arrow_end": SVG("marker", SVG("path", d="M 1.5 3.6 L 0 0 L 10.5 3.6 L 0 7.2 L 1.5 3.6 Z"), viewBox="0 0 10.5 7.2", refX="1.5", refY="3.6", markerWidth="10.5", markerHeight="7.2", markerUnits="strokeWidth", orient="auto", stroke="none", fill="black"), \
                    }

def make_marker(id, shape, **attr):
  output = copy.deepcopy(marker_templates[shape])
  for i in output.sub: i.attr.update(attr)
  output["id"] = id
  return output

class Line(Curve):
  defaults = {}

  def __repr__(self):
    return "<Line (%g, %g) to (%g, %g) %s>" % (self.x1, self.y1, self.x2, self.y2, self.attr)

  def __init__(self, x1, y1, x2, y2, **attr):
    self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    return self.Path(trans).SVG()

  def Path(self, trans=None, local=False):
    self.f = lambda t: (self.x1 + t*(self.x2 - self.x1), self.y1 + t*(self.y2 - self.y1))
    self.low = 0.
    self.high = 1.
    self.loop = False

    if trans == None:
      return Path([("M", self.x1, self.y1, not local), ("L", self.x2, self.y2, not local)], **self.attr)
    else:
      return Curve.Path(self, trans, local)

class LineGlobal:
  defaults = {}

  def __repr__(self):
    local1, local2 = "", ""
    if self.local1: local1 = "L"
    if self.local2: local2 = "L"

    return "<LineGlobal %s(%s, %s) to %s(%s, %s) %s>" % (local1, str(self.x1), str(self.y1), local2, str(self.x2), str(self.y2), self.attr)

  def __init__(self, x1, y1, x2, y2, local1=False, local2=False, **attr):
    self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
    self.local1 = local1
    self.local2 = local2

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans)

    X1, Y1, X2, Y2 = self.x1, self.y1, self.x2, self.y2

    if self.local1: X1, Y1 = trans(X1, Y1)
    if self.local2: X2, Y2 = trans(X2, Y2)

    return SVG("path", d="M%s %s L%s %s" % (X1, Y1, X2, Y2), **self.attr)

class VLine(Line):
  defaults = {}

  def __repr__(self):
    return "<VLine (%g, %g) at x=%s %s>" % (self.y1, self.y2, self.x, self.attr)

  def __init__(self, y1, y2, x, **attr):
    self.x = x
    self.attr = dict(self.defaults)
    self.attr.update(attr)
    Line.__init__(self, x, y1, x, y2, **self.attr)

  def SVG(self, trans=None):
    self.x1 = self.x
    self.x2 = self.x
    return Line.SVG(self, trans)

class HLine(Line):
  defaults = {}

  def __repr__(self):
    return "<HLine (%g, %g) at y=%s %s>" % (self.x1, self.x2, self.y, self.attr)

  def __init__(self, x1, x2, y, **attr):
    self.y = y
    self.attr = dict(self.defaults)
    self.attr.update(attr)
    Line.__init__(self, x1, y, x2, y, **self.attr)

  def SVG(self, trans=None):
    self.y1 = self.y
    self.y2 = self.y
    return Line.SVG(self, trans)

######################################################################

class Rect(Curve):
  defaults = {}

  def __repr__(self):
    return "<Rect (%g, %g), (%g, %g) %s>" % (self.x1, self.y1, self.x2, self.y2, self.attr)

  def __init__(self, x1, y1, x2, y2, **attr):
    self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    return self.Path(trans).SVG()

  def Path(self, trans=None, local=False):
    if trans == None:
      return Path([("M", self.x1, self.y1, not local), ("L", self.x2, self.y1, not local), ("L", self.x2, self.y2, not local), ("L", self.x1, self.y2, not local), ("Z",)], **self.attr)

    else:
      self.low = 0.
      self.high = 1.
      self.loop = True

      self.f = lambda t: (self.x1 + t*(self.x2 - self.x1), self.y1)
      d1 = Curve.Path(self, trans, local).d

      self.f = lambda t: (self.x2, self.y1 + t*(self.y2 - self.y1))
      d2 = Curve.Path(self, trans, local).d
      del d2[0]

      self.f = lambda t: (self.x2 + t*(self.x1 - self.x2), self.y2)
      d3 = Curve.Path(self, trans, local).d
      del d3[0]

      self.f = lambda t: (self.x1, self.y2 + t*(self.y1 - self.y2))
      d4 = Curve.Path(self, trans, local).d
      del d4[0]

      return Path(d=(d1 + d2 + d3 + d4 + [("Z",)]), **self.attr)

######################################################################

class Ellipse(Curve):
  defaults = {}

  def __repr__(self):
    return "<Ellipse (%g, %g) a=(%g, %g), b=%g %s>" % (self.x, self.y, self.ax, self.ay, self.b, self.attr)

  def __init__(self, x, y, ax, ay, b, **attr):
    self.x, self.y, self.ax, self.ay, self.b = x, y, ax, ay, b

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    return self.Path(trans).SVG()

  def Path(self, trans=None, local=False):
    angle = math.atan2(self.ay, self.ax) + math.pi/2.
    bx = self.b * math.cos(angle)
    by = self.b * math.sin(angle)

    self.f = lambda t: (self.x + self.ax*math.cos(t) + bx*math.sin(t), self.y + self.ay*math.cos(t) + by*math.sin(t))
    self.low = -math.pi
    self.high = math.pi
    self.loop = True
    return Curve.Path(self, trans, local)

######################################################################

def unumber(x):
  output = u"%g" % x

  if output[0] == u"-":
    output = u"\u2013" + output[1:]

  index = output.find(u"e")
  if index != -1:
    uniout = unicode(output[:index]) + u"\u00d710"
    saw_nonzero = False
    for n in output[index+1:]:
      if n == u"+": pass # uniout += u"\u207a"
      elif n == u"-": uniout += u"\u207b"
      elif n == u"0":
        if saw_nonzero: uniout += u"\u2070"
      elif n == u"1":
        saw_nonzero = True
        uniout += u"\u00b9"
      elif n == u"2":
        saw_nonzero = True
        uniout += u"\u00b2"
      elif n == u"3":
        saw_nonzero = True
        uniout += u"\u00b3"
      elif u"4" <= n <= u"9":
        saw_nonzero = True
        if saw_nonzero: uniout += eval("u\"\\u%x\"" % (0x2070 + ord(n) - ord(u"0")))
      else: uniout += n

    if uniout[:2] == u"1\u00d7": uniout = uniout[2:]
    return uniout

  return output

class Ticks:
  defaults = {"stroke-width":"0.25pt"}
  text_defaults = {"stroke":"none", "fill":"black", "font-size":5}
  tick_start = -1.5
  tick_end = 1.5
  minitick_start = -0.75
  minitick_end = 0.75
  text_start = 2.5
  text_angle = 0.

  def __repr__(self):
    return "<Ticks %s from %s to %s ticks=%s labels=%s %s>" % (self.f, self.low, self.high, str(self.ticks), str(self.labels), self.attr)

  def __init__(self, f, low, high, ticks=-10, miniticks=True, labels=True, logbase=None, arrow_start=None, arrow_end=None, text_attr={}, **attr):
    self.f = f
    self.low = low
    self.high = high
    self.ticks = ticks
    self.miniticks = miniticks
    self.labels = labels
    self.logbase = logbase
    self.arrow_start = arrow_start
    self.arrow_end = arrow_end

    self.attr = dict(self.defaults)
    self.attr.update(attr)

    self.text_attr = dict(self.text_defaults)
    self.text_attr.update(text_attr)

  def orient_tickmark(self, t, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans)
    if trans == None:
      f = self.f
    else:
      f = lambda t: trans(*self.f(t))

    eps = epsilon * abs(self.high - self.low)

    X, Y = f(t)
    Xprime, Yprime = f(t + eps)
    xhatx, xhaty = (Xprime - X)/eps, (Yprime - Y)/eps

    norm = math.sqrt(xhatx**2 + xhaty**2)
    xhatx, xhaty = xhatx/norm, xhaty/norm

    angle = math.atan2(xhaty, xhatx) + math.pi/2.
    yhatx, yhaty = math.cos(angle), math.sin(angle)

    return (X, Y), (xhatx, xhaty), (yhatx, yhaty), angle

  def SVG(self, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans)

    self.last_ticks, self.last_miniticks = self.interpret()
    tickmarks = Path([], **self.attr)
    minitickmarks = Path([], **self.attr)
    output = SVG("g")

    if (self.arrow_start != False and self.arrow_start != None) or (self.arrow_end != False and self.arrow_end != None):
      defs = SVG("defs")

      if self.arrow_start != False and self.arrow_start != None:
        if not isinstance(self.arrow_start, basestring):
          raise TypeError, "arrow_start must be False/None or an id string for the new marker"
        defs.append(make_marker(self.arrow_start, "arrow_start"))

      if self.arrow_end != False and self.arrow_end != None:
        if not isinstance(self.arrow_end, basestring):
          raise TypeError, "arrow_end must be False/None or an id string for the new marker"
        defs.append(make_marker(self.arrow_end, "arrow_end"))

      output.append(defs)

    eps = epsilon * (self.high - self.low)

    for t, label in self.last_ticks.items():
      (X, Y), (xhatx, xhaty), (yhatx, yhaty), angle = self.orient_tickmark(t, trans)
      
      if (not self.arrow_start or abs(t - self.low) > eps) and (not self.arrow_end or abs(t - self.high) > eps):
        tickmarks.d.append(("M", X - yhatx*self.tick_start, Y - yhaty*self.tick_start, True))
        tickmarks.d.append(("L", X - yhatx*self.tick_end, Y - yhaty*self.tick_end, True))

      angle = (angle - math.pi/2.)*180./math.pi + self.text_angle

      ########### a HACK! ############ (to be removed when Inkscape handles baselines)
      if hacks["inkscape-text-vertical-shift"]:
        if self.text_start > 0:
          X += math.cos(angle*math.pi/180. + math.pi/2.) * 2.
          Y += math.sin(angle*math.pi/180. + math.pi/2.) * 2.
        else:
          X += math.cos(angle*math.pi/180. + math.pi/2.) * 2. * 2.5
          Y += math.sin(angle*math.pi/180. + math.pi/2.) * 2. * 2.5
      ########### end hack ###########

      output.append(SVG("text", label, transform="translate(%g, %g) rotate(%g)" % \
                        (X - yhatx*self.text_start, Y - yhaty*self.text_start, angle), **self.text_attr))

    for t in self.last_miniticks:
      skip = False
      for tt in self.last_ticks.keys():
        if abs(t - tt) < eps:
          skip = True
          break
      if not skip:
        (X, Y), (xhatx, xhaty), (yhatx, yhaty), angle = self.orient_tickmark(t, trans)

      if (not self.arrow_start or abs(t - self.low) > eps) and (not self.arrow_end or abs(t - self.high) > eps):
        minitickmarks.d.append(("M", X - yhatx*self.minitick_start, Y - yhaty*self.minitick_start, True))
        minitickmarks.d.append(("L", X - yhatx*self.minitick_end, Y - yhaty*self.minitick_end, True))

    output.prepend(tickmarks.SVG(trans))
    output.prepend(minitickmarks.SVG(trans))
    return output

  def interpret(self):
    if self.labels == None or self.labels == False:
      format = lambda x: ""

    elif self.labels == True:
      format = unumber

    elif isinstance(self.labels, basestring):
      format = lambda x: (self.labels % x)

    elif callable(self.labels):
      format = self.labels

    else: raise TypeError, "labels must be None/False, True, a format string, or a number->string function"

    # Now for the ticks
    ticks = self.ticks

    # Case 1: ticks is None/False
    if ticks == None or ticks == False: return {}, []

    # Case 2: ticks is the number of desired ticks
    elif isinstance(ticks, (int, long)):
      if ticks == True: ticks = -10

      if self.logbase == None:
        ticks = self.compute_ticks(ticks, format)
      else:
        ticks = self.compute_logticks(self.logbase, ticks, format)

      # Now for the miniticks
      if self.miniticks == True:
        if self.logbase == None:
          return ticks, self.compute_miniticks(ticks)
        else:
          return ticks, self.compute_logminiticks(self.logbase)

      elif isinstance(self.miniticks, (int, long)):
        return ticks, self.regular_miniticks(self.miniticks)

      elif getattr(self.miniticks, "__iter__", False):
        return ticks, self.miniticks

      elif self.miniticks == False or self.miniticks == None:
        return ticks, []

      else:
        raise TypeError, "miniticks must be None/False, True, a number of desired miniticks, or a list of numbers"
        
    # Cases 3 & 4: ticks is iterable
    elif getattr(ticks, "__iter__", False):

      # Case 3: ticks is some kind of list
      if not isinstance(ticks, dict):
        output = {}
        eps = epsilon * (self.high - self.low)
        for x in ticks:
          if format == unumber and abs(x) < eps:
            output[x] = u"0"
          else:
            output[x] = format(x)
        ticks = output

      # Case 4: ticks is a dict
      else: pass

      # Now for the miniticks
      if self.miniticks == True:
        if self.logbase == None:
          return ticks, self.compute_miniticks(ticks)
        else:
          return ticks, self.compute_logminiticks(self.logbase)

      elif isinstance(self.miniticks, (int, long)):
        return ticks, self.regular_miniticks(self.miniticks)

      elif getattr(self.miniticks, "__iter__", False):
        return ticks, self.miniticks

      elif self.miniticks == False or self.miniticks == None:
        return ticks, []

      else:
        raise TypeError, "miniticks must be None/False, True, a number of desired miniticks, or a list of numbers"
        
    else:
      raise TypeError, "ticks must be None/False, a number of desired ticks, a list of numbers, or a dictionary of explicit markers"

  def compute_ticks(self, N, format):
    if self.low >= self.high: raise ValueError, "low must be less than high"
    if N == 1: raise ValueError, "N can be 0 or >1 to specify the exact number of ticks or negative to specify a maximum"

    eps = epsilon * (self.high - self.low)

    if N >= 0:
      output = {}
      x = self.low
      for i in xrange(N):
        if format == unumber and abs(x) < eps: label = u"0"
        else: label = format(x)
        output[x] = label
        x += (self.high - self.low)/(N-1.)
      return output

    N = -N

    counter = 0
    granularity = 10**math.ceil(math.log10(max(abs(self.low), abs(self.high))))
    lowN = math.ceil(1.*self.low / granularity)
    highN = math.floor(1.*self.high / granularity)

    while (lowN > highN):
      countermod3 = counter % 3
      if countermod3 == 0: granularity *= 0.5
      elif countermod3 == 1: granularity *= 0.4
      else: granularity *= 0.5
      counter += 1
      lowN = math.ceil(1.*self.low / granularity)
      highN = math.floor(1.*self.high / granularity)

    last_granularity = granularity
    last_trial = None

    while True:
      trial = {}
      for n in range(int(lowN), int(highN)+1):
        x = n * granularity
        if format == unumber and abs(x) < eps: label = u"0"
        else: label = format(x)
        trial[x] = label

      if int(highN)+1 - int(lowN) >= N:
        if last_trial == None:
          v1, v2 = self.low, self.high
          return {v1: format(v1), v2: format(v2)}
        else:
          low_in_ticks, high_in_ticks = False, False
          for t in last_trial.keys():
            if 1.*abs(t - self.low)/last_granularity < epsilon: low_in_ticks = True
            if 1.*abs(t - self.high)/last_granularity < epsilon: high_in_ticks = True

          lowN = 1.*self.low / last_granularity
          highN = 1.*self.high / last_granularity
          if abs(lowN - round(lowN)) < epsilon and not low_in_ticks:
            last_trial[self.low] = format(self.low)
          if abs(highN - round(highN)) < epsilon and not high_in_ticks:
            last_trial[self.high] = format(self.high)
          return last_trial

      last_granularity = granularity
      last_trial = trial

      countermod3 = counter % 3
      if countermod3 == 0: granularity *= 0.5
      elif countermod3 == 1: granularity *= 0.4
      else: granularity *= 0.5
      counter += 1
      lowN = math.ceil(1.*self.low / granularity)
      highN = math.floor(1.*self.high / granularity)

  def regular_miniticks(self, N):
    output = []
    x = self.low
    for i in xrange(N):
      output.append(x)
      x += (self.high - self.low)/(N-1.)
    return output

  def compute_miniticks(self, original_ticks):
    if len(original_ticks) < 2: original_ticks = ticks(self.low, self.high)
    original_ticks = original_ticks.keys()
    original_ticks.sort()

    if self.low > original_ticks[0] + epsilon or self.high < original_ticks[-1] - epsilon:
      raise ValueError, "original_ticks {%g...%g} extend beyond [%g, %g]" % (original_ticks[0], original_ticks[-1], self.low, self.high)

    granularities = []
    for i in range(len(original_ticks)-1):
      granularities.append(original_ticks[i+1] - original_ticks[i])
    spacing = 10**(math.ceil(math.log10(min(granularities)) - 1))

    output = []
    x = original_ticks[0] - math.ceil(1.*(original_ticks[0] - self.low) / spacing) * spacing

    while x <= self.high:
      if x >= self.low:
        already_in_ticks = False
        for t in original_ticks:
          if abs(x-t) < epsilon * (self.high - self.low): already_in_ticks = True
        if not already_in_ticks: output.append(x)
      x += spacing
    return output

  def compute_logticks(self, base, N, format):
    if self.low >= self.high: raise ValueError, "low must be less than high"
    if N == 1: raise ValueError, "N can be 0 or >1 to specify the exact number of ticks or negative to specify a maximum"

    eps = epsilon * (self.high - self.low)

    if N >= 0:
      output = {}
      x = self.low
      for i in xrange(N):
        if format == unumber and abs(x) < eps: label = u"0"
        else: label = format(x)
        output[x] = label
        x += (self.high - self.low)/(N-1.)
      return output

    N = -N

    lowN = math.floor(math.log(self.low, base))
    highN = math.ceil(math.log(self.high, base))
    output = {}
    for n in range(int(lowN), int(highN)+1):
      x = base**n
      label = format(x)
      if self.low <= x <= self.high: output[x] = label

    for i in range(1, len(output)):
      keys = output.keys()
      keys.sort()
      keys = keys[::i]
      values = map(lambda k: output[k], keys)
      if len(values) <= N:
        for k in output.keys():
          if k not in keys:
            output[k] = ""
        break

    if len(output) <= 2:
      output2 = compute_ticks(N=-int(math.ceil(N/2.)), format=format)
      lowest = min(output2)

      for k in output:
        if k < lowest: output2[k] = output[k]
      output = output2

    return output

  def compute_logminiticks(self, base):
    if self.low >= self.high: raise ValueError, "low must be less than high"

    lowN = math.floor(math.log(self.low, base))
    highN = math.ceil(math.log(self.high, base))
    output = []
    num_ticks = 0
    for n in range(int(lowN), int(highN)+1):
      x = base**n
      if self.low <= x <= self.high: num_ticks += 1
      for m in range(2, int(math.ceil(base))):
        minix = m * x
        if self.low <= minix <= self.high: output.append(minix)

    if num_ticks <= 2: return []
    else: return output

######################################################################

class CurveAxis(Curve, Ticks):
  defaults = {"stroke-width":"0.25pt"}
  text_defaults = {"stroke":"none", "fill":"black", "font-size":5}

  def __repr__(self):
    return "<CurveAxis %s [%s, %s] ticks=%s labels=%s %s>" % (self.f, self.low, self.high, str(self.ticks), str(self.labels), self.attr)

  def __init__(self, f, low, high, ticks=-10, miniticks=True, labels=True, logbase=None, arrow_start=None, arrow_end=None, text_attr={}, **attr):
    tattr = dict(self.text_defaults)
    tattr.update(text_attr)
    Curve.__init__(self, f, low, high)
    Ticks.__init__(self, f, low, high, ticks, miniticks, labels, logbase, arrow_start, arrow_end, tattr, **attr)

  def SVG(self, trans=None):
    func = Curve.SVG(self, trans)
    ticks = Ticks.SVG(self, trans) # returns a <g />

    if self.arrow_start != False and self.arrow_start != None:
      func.attr["marker-start"] = "url(#%s)" % self.arrow_start

    if self.arrow_end != False and self.arrow_end != None:
      func.attr["marker-end"] = "url(#%s)" % self.arrow_end

    ticks.append(func)
    return ticks

class LineAxis(Line, Ticks):
  defaults = {"stroke-width":"0.25pt"}
  text_defaults = {"stroke":"none", "fill":"black", "font-size":5}

  def __repr__(self):
    return "<LineAxis (%g, %g) to (%g, %g) ticks=%s labels=%s %s>" % (self.x1, self.y1, self.x2, self.y2, str(self.ticks), str(self.labels), self.attr)

  def __init__(self, x1, y1, x2, y2, start=0., end=1., ticks=-10, miniticks=True, labels=True, logbase=None, arrow_start=None, arrow_end=None, exclude=None, text_attr={}, **attr):
    self.start = start
    self.end = end
    self.exclude = exclude
    tattr = dict(self.text_defaults)
    tattr.update(text_attr)
    Line.__init__(self, x1, y1, x2, y2, **attr)
    Ticks.__init__(self, None, None, None, ticks, miniticks, labels, logbase, arrow_start, arrow_end, tattr, **attr)

  def interpret(self):
    if self.exclude != None and not (isinstance(self.exclude, (tuple, list)) and len(self.exclude) == 2 and \
                                     isinstance(self.exclude[0], (int, long, float)) and isinstance(self.exclude[1], (int, long, float))):
      raise TypeError, "exclude must either be None or (low, high)"

    ticks, miniticks = Ticks.interpret(self)
    if self.exclude == None: return ticks, miniticks

    ticks2 = {}
    for loc, label in ticks.items():
      if self.exclude[0] <= loc <= self.exclude[1]:
        ticks2[loc] = ""
      else:
        ticks2[loc] = label

    return ticks2, miniticks

  def SVG(self, trans=None):
    line = Line.SVG(self, trans) # must be evaluated first, to set self.f, self.low, self.high

    f01 = self.f
    self.f = lambda t: f01((t - self.start) / (self.end - self.start))
    self.low = self.start
    self.high = self.end

    if self.arrow_start != False and self.arrow_start != None:
      line.attr["marker-start"] = "url(#%s)" % self.arrow_start

    if self.arrow_end != False and self.arrow_end != None:
      line.attr["marker-end"] = "url(#%s)" % self.arrow_end

    ticks = Ticks.SVG(self, trans) # returns a <g />
    ticks.append(line)
    return ticks
  
class XAxis(LineAxis):
  defaults = {"stroke-width":"0.25pt"}
  text_defaults = {"stroke":"none", "fill":"black", "font-size":5, "dominant-baseline":"text-before-edge"}
  text_start = -1.
  text_angle = 0.

  def __repr__(self):
    return "<XAxis (%g, %g) at y=%g ticks=%s labels=%s %s>" % (self.xmin, self.xmax, self.aty, str(self.ticks), str(self.labels), self.attr)

  def __init__(self, xmin, xmax, aty=0, ticks=-10, miniticks=True, labels=True, logbase=None, arrow_start=None, arrow_end=None, exclude=None, text_attr={}, **attr):
    self.aty = aty
    tattr = dict(self.text_defaults)
    tattr.update(text_attr)
    LineAxis.__init__(self, xmin, aty, xmax, aty, xmin, xmax, ticks, miniticks, labels, logbase, arrow_start, arrow_end, exclude, tattr, **attr)

  def SVG(self, trans=None):
    self.y1 = self.aty
    self.y2 = self.aty
    return LineAxis.SVG(self, trans)

class YAxis(LineAxis):
  defaults = {"stroke-width":"0.25pt"}
  text_defaults = {"stroke":"none", "fill":"black", "font-size":5, "text-anchor":"end", "dominant-baseline":"middle"}
  text_start = 2.5
  text_angle = 90.

  def __repr__(self):
    return "<YAxis (%g, %g) at x=%g ticks=%s labels=%s %s>" % (self.ymin, self.ymax, self.atx, str(self.ticks), str(self.labels), self.attr)

  def __init__(self, ymin, ymax, atx=0, ticks=-10, miniticks=True, labels=True, logbase=None, arrow_start=None, arrow_end=None, exclude=None, text_attr={}, **attr):
    self.atx = atx
    tattr = dict(self.text_defaults)
    tattr.update(text_attr)
    LineAxis.__init__(self, atx, ymin, atx, ymax, ymin, ymax, ticks, miniticks, labels, logbase, arrow_start, arrow_end, exclude, tattr, **attr)

  def SVG(self, trans=None):
    self.x1 = self.atx
    self.x2 = self.atx
    return LineAxis.SVG(self, trans)

class Axes:
  defaults = {"stroke-width":"0.25pt"}
  text_defaults = {"stroke":"none", "fill":"black", "font-size":5}

  def __repr__(self):
    return "<Axes x=(%g, %g) y=(%g, %g) at (%g, %g) %s>" % (self.xmin, self.xmax, self.ymin, self.ymax, self.atx, self.aty, self.attr)

  def __init__(self, xmin, xmax, ymin, ymax, atx=0, aty=0, xticks=-10, xminiticks=True, xlabels=True, xlogbase=None, yticks=-10, yminiticks=True, ylabels=True, ylogbase=None, arrows=None, text_attr={}, **attr):
    self.xmin, self.xmax = xmin, xmax
    self.ymin, self.ymax = ymin, ymax
    self.atx, self.aty = atx, aty
    self.xticks, self.xminiticks, self.xlabels, self.xlogbase = xticks, xminiticks, xlabels, xlogbase
    self.yticks, self.yminiticks, self.ylabels, self.ylogbase = yticks, yminiticks, ylabels, ylogbase
    self.arrows = arrows

    self.text_attr = dict(self.text_defaults)
    self.text_attr.update(text_attr)

    self.attr = dict(self.defaults)
    self.attr.update(attr)

  def SVG(self, trans=None):
    atx, aty = self.atx, self.aty
    if atx < self.xmin: atx = self.xmin
    if atx > self.xmax: atx = self.xmax
    if aty < self.ymin: aty = self.ymin
    if aty > self.ymax: aty = self.ymax

    xmargin = 0.1 * abs(self.ymin - self.ymax)
    xexclude = atx - xmargin, atx + xmargin
    
    ymargin = 0.1 * abs(self.xmin - self.xmax)
    yexclude = aty - ymargin, aty + ymargin

    if self.arrows != None and self.arrows != False:
      xarrow_start = self.arrows + ".xstart"
      xarrow_end = self.arrows + ".xend"
      yarrow_start = self.arrows + ".ystart"
      yarrow_end = self.arrows + ".yend"
    else:
      xarrow_start = xarrow_end = yarrow_start = yarrow_end = None

    xaxis = XAxis(self.xmin, self.xmax, aty, self.xticks, self.xminiticks, self.xlabels, self.xlogbase, xarrow_start, xarrow_end, exclude=xexclude, text_attr=self.text_attr, **self.attr).SVG(trans)
    yaxis = YAxis(self.ymin, self.ymax, atx, self.yticks, self.yminiticks, self.ylabels, self.ylogbase, yarrow_start, yarrow_end, exclude=yexclude, text_attr=self.text_attr, **self.attr).SVG(trans)
    return SVG("g", *(xaxis.sub + yaxis.sub))

######################################################################

class HGrid(Ticks):
  defaults = {"stroke-width":"0.25pt", "stroke":"gray"}
  mini_defaults = {"stroke-width":"0.25pt", "stroke":"lightgray", "stroke-dasharray":"1,1"}

  def __repr__(self):
    return "<HGrid x=(%g, %g) %g <= y <= %g ticks=%s miniticks=%s %s>" % (self.xmin, self.xmax, self.low, self.high, str(self.ticks), str(self.miniticks), self.attr)

  def __init__(self, xmin, xmax, low, high, ticks=-10, miniticks=False, logbase=None, mini_attr={}, **attr):
    self.xmin, self.xmax = xmin, xmax

    self.mini_attr = dict(self.mini_defaults)
    self.mini_attr.update(mini_attr)

    self.attr = dict(self.defaults)
    self.attr.update(attr)

    Ticks.__init__(self, None, low, high, ticks, miniticks, None, logbase)

  def SVG(self, trans=None):
    self.last_ticks, self.last_miniticks = Ticks.interpret(self)

    ticksd = []
    for t in self.last_ticks.keys():
      ticksd += Line(self.xmin, t, self.xmax, t).Path(trans).d

    miniticksd = []
    for t in self.last_miniticks:
      miniticksd += Line(self.xmin, t, self.xmax, t).Path(trans).d

    return SVG("g", Path(d=ticksd, **self.attr).SVG(), Path(d=miniticksd, **self.mini_attr).SVG())
    
class VGrid(Ticks):
  defaults = {"stroke-width":"0.25pt", "stroke":"gray"}
  mini_defaults = {"stroke-width":"0.25pt", "stroke":"lightgray", "stroke-dasharray":"1,1"}

  def __repr__(self):
    return "<VGrid y=(%g, %g) %g <= x <= %g ticks=%s miniticks=%s %s>" % (self.ymin, self.ymax, self.low, self.high, str(self.ticks), str(self.miniticks), self.attr)

  def __init__(self, ymin, ymax, low, high, ticks=-10, miniticks=False, logbase=None, mini_attr={}, **attr):
    self.ymin, self.ymax = ymin, ymax

    self.mini_attr = dict(self.mini_defaults)
    self.mini_attr.update(mini_attr)

    self.attr = dict(self.defaults)
    self.attr.update(attr)

    Ticks.__init__(self, None, low, high, ticks, miniticks, None, logbase)

  def SVG(self, trans=None):
    self.last_ticks, self.last_miniticks = Ticks.interpret(self)

    ticksd = []
    for t in self.last_ticks.keys():
      ticksd += Line(t, self.ymin, t, self.ymax).Path(trans).d

    miniticksd = []
    for t in self.last_miniticks:
      miniticksd += Line(t, self.ymin, t, self.ymax).Path(trans).d

    return SVG("g", Path(d=ticksd, **self.attr).SVG(), Path(d=miniticksd, **self.mini_attr).SVG())

class Grid(Ticks):
  defaults = {"stroke-width":"0.25pt", "stroke":"gray"}
  mini_defaults = {"stroke-width":"0.25pt", "stroke":"lightgray", "stroke-dasharray":"1,1"}

  def __repr__(self):
    return "<Grid x=(%g, %g) y=(%g, %g) ticks=%s miniticks=%s %s>" % (self.xmin, self.xmax, self.ymin, self.ymax, str(self.ticks), str(self.miniticks), self.attr)

  def __init__(self, xmin, xmax, ymin, ymax, ticks=-10, miniticks=False, logbase=None, mini_attr={}, **attr):
    self.xmin, self.xmax = xmin, xmax
    self.ymin, self.ymax = ymin, ymax

    self.mini_attr = dict(self.mini_defaults)
    self.mini_attr.update(mini_attr)

    self.attr = dict(self.defaults)
    self.attr.update(attr)

    Ticks.__init__(self, None, None, None, ticks, miniticks, None, logbase)

  def SVG(self, trans=None):
    self.low, self.high = self.xmin, self.xmax
    self.last_xticks, self.last_xminiticks = Ticks.interpret(self)
    self.low, self.high = self.ymin, self.ymax
    self.last_yticks, self.last_yminiticks = Ticks.interpret(self)

    ticksd = []
    for t in self.last_xticks.keys():
      ticksd += Line(t, self.ymin, t, self.ymax).Path(trans).d
    for t in self.last_yticks.keys():
      ticksd += Line(self.xmin, t, self.xmax, t).Path(trans).d

    miniticksd = []
    for t in self.last_xminiticks:
      miniticksd += Line(t, self.ymin, t, self.ymax).Path(trans).d
    for t in self.last_yminiticks:
      miniticksd += Line(self.xmin, t, self.xmax, t).Path(trans).d

    return SVG("g", Path(d=ticksd, **self.attr).SVG(), Path(d=miniticksd, **self.mini_attr).SVG())

######################################################################

class XErrorBars:
  defaults = {"stroke-width":"0.25pt"}

  def __repr__(self):
    return "<XErrorBars (%d nodes)>" % len(self.d)

  def __init__(self, d, **attr):
    self.d = d

    self.attr = dict(self.defaults)
    self.attr.update(attr)
    
  def SVG(self, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans) # only once

    output = SVG("g")
    for p in self.d:
      x, y = p[0], p[1]

      if len(p) == 3: bars = [x - p[2], x + p[2]]
      else: bars = [x + pi for pi in p[2:]]
      
      start, end = min(bars), max(bars)
      output.append(LineAxis(start, y, end, y, start, end, bars, False, False, **self.attr).SVG(trans))

    return output

class YErrorBars:
  defaults = {"stroke-width":"0.25pt"}

  def __repr__(self):
    return "<YErrorBars (%d nodes)>" % len(self.d)

  def __init__(self, d, **attr):
    self.d = d

    self.attr = dict(self.defaults)
    self.attr.update(attr)
    
  def SVG(self, trans=None):
    if isinstance(trans, basestring): trans = totrans(trans) # only once

    output = SVG("g")
    for p in self.d:
      x, y = p[0], p[1]

      if len(p) == 3: bars = [y - p[2], y + p[2]]
      else: bars = [y + pi for pi in p[2:]]
      
      start, end = min(bars), max(bars)
      output.append(LineAxis(x, start, x, end, start, end, bars, False, False, **self.attr).SVG(trans))

    return output
