# compatible with Python 2.3 and higher

import re, codecs, os, platform, copy, itertools, tempfile

_epsilon = 1e-5

defaults = { \
  "svg": {"width": 400, "height": 400, "viewBox": (0, 0, 100, 100), \
          "style": {"stroke":"black", "fill":"none", "stroke-width":"0.5pt", "stroke-linejoin":"round", "text-anchor":"middle"}, \
          "font-family": ["Helvetica", "Arial", "FreeSans", "Sans", "sans", "sans-serif"], \
          "xmlns": "http://www.w3.org/2000/svg", "xmlns:xlink": "http://www.w3.org/1999/xlink", "version":"1.1", \
          }, \
  "text": {"stroke": "none", "fill": "black"}, \
  }

# _svg_inline and _svg_signature.keys() are mutually exclusive

_svg_inline = ["g", "text", "tspan", "symbol", "marker"]

_svg_signature = { \
  "svg": ["width", "height", "viewBox"], \
  "path": ["d", "stroke", "fill"], \
  "line": ["x1", "y1", "x2", "y2", "stroke"], \
  "rect": ["x", "y", "width", "height", "stroke", "fill"], \
  "circle": ["cx", "cy", "r", "stroke", "fill"], \
  }

_xml_header = """\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
"""

if re.search("windows", platform.system(), re.I):
  try:
    import _winreg
    _default_directory = _winreg.QueryValueEx(_winreg.OpenKey(_winreg.HKEY_CURRENT_USER, \
                       r"Software\Microsoft\Windows\Current Version\Explorer\Shell Folders"), "Desktop")[0]
  except:
    _default_directory = os.path.expanduser("~") + os.sep + "Desktop"

##############################################################################

def rgb(r, g, b, maximum=1.):
  """Create an SVG color string "#xxyyzz" from r, g, and b.

  r,g,b = 0 is black and r,g,b = maximum is white.
  """
  return "#%02x%02x%02x" % (max(0, min(r*255./maximum, 255)), max(0, min(g*255./maximum, 255)), max(0, min(b*255./maximum, 255)))

##############################################################################

class SVG:
  def _preprocess_attribname(self, name):
    name_colon = re.sub("__", ":", name)
    if name_colon != name: name = name_colon

    name_dash = re.sub("_", "-", name)
    if name_dash != name: name = name_dash

    return name

  def __init__(self, tag, *signature_attrib, **more_attrib):
    self.__dict__["tag"] = tag
    self.__dict__["attrib"] = defaults.get(tag, {})
    self.__dict__["children"] = []

    signature = _svg_signature.get(tag)
    if signature != None:

      if len(signature_attrib) > len(signature):
        raise TypeError, "Tag '%s' expects no more than %d non-keyword attributes (saw %d)" % (tag, len(signature), len(signature_attrib))

      for name, value in zip(signature, signature_attrib):
        self.attrib[name] = value

    elif tag in _svg_inline:
      self.children.extend(signature_attrib)

    elif len(signature_attrib) > 0:
      raise TypeError, "Tag '%s' expects 0 non-keyword attributes (saw %d)" % (tag, len(signature_attrib))

    for name, value in more_attrib.items():
      processed_name = self._preprocess_attribname(name)
      if processed_name != name:
        del more_attrib[name]
        more_attrib[processed_name] = value

    self.attrib.update(more_attrib)

  def __call__(self, *children):
    """Extends the list of children and returns self (for inline construction of trees)."""
    self.children.extend(children)
    return self

  ### act like a list
  def append(self, other):
    """Appends to the list of children (drawn last, may overlap
    other primatives)."""
    self.children.append(other)

  def prepend(self, other):
    """Prepends to the list of children (drawn first, might be
    overlapped by other primatives)."""
    self.children[0:0] = [other]

  def extend(self, other):
    """Extends list of children by a list or another SVG group."""
    if isinstance(other, SVG):
      self.children.extend(other.children)
    elif isinstance(other, basestring):
      self.children.append(other)
    else:
      self.children.extend(other)

  def insert(self, i, other):
    """Insert item at index i."""
    self.children.insert(i, other)

  def remove(self, other):
    self.children.remove(other)

  def __len__(self): return len(self.children)

  def __add__(self, other):
    output = self.deepcopy()
    output += other
    return output

  def __iadd__(self, other):
    self.children.append(other)
    return self

  def __mul__(self, other):
    output = self.deepcopy()
    output *= other
    return output

  def __rmul__(self, other):
    return self * other

  def __imul__(self, other):
    self.children *= other
    return self

  def count(self, *args, **kwds): return self.children.count(*args, **kwds)
  def index(self, *args, **kwds): return self.children.index(*args, **kwds)
  def pop(self, *args, **kwds): return self.children.pop(*args, **kwds)
  def reverse(self, *args, **kwds): return self.children.reverse(*args, **kwds)
  ###
  ### act like a dict
  def clear(self, *args, **kwds):
    self.children = []
    self.attrib.clear(*args, **kwds)

  def update(self, other):
    if isinstance(other, SVG):
      self.attrib.update(other.attrib)
    else:
      self.attrib.update(other)

  def __contains__(self, other):
    return other in self.attrib or other in self.children

  def fromkeys(self, *args, **kwds): return self.attrib.fromkeys(*args, **kwds)
  def copy(self, *args, **kwds): return copy.copy(self, *args, **kwds)
  def deepcopy(self, *args, **kwds): return copy.deepcopy(self, *args, **kwds)
  def has_key(self, *args, **kwds): return self.attrib.has_key(*args, **kwds)
  def items(self, *args, **kwds): return self.attrib.items(*args, **kwds)
  def keys(self, *args, **kwds): return self.attrib.keys(*args, **kwds)
  def values(self, *args, **kwds): return self.attrib.values(*args, **kwds)
  def get(self, *args, **kwds): return self.attrib.get(*args, **kwds)
  def setdefault(self, *args, **kwds): return self.attrib.setdefault(*args, **kwds)
  def iteritems(self, *args, **kwds): return self.attrib.iteritems(*args, **kwds)
  def iterkeys(self, *args, **kwds): return self.attrib.iterkeys(*args, **kwds)
  def itervalues(self, *args, **kwds): return self.attrib.itervalues(*args, **kwds)
  def pop(self, *args, **kwds): return self.attrib.pop(*args, **kwds)
  def popitem(self, *args, **kwds): return self.attrib.popitem(*args, **kwds)
  ###

  def __repr__(self):
    output = ["%s" % self.tag]

    remaining = copy.copy(self.attrib)  # shallow copy

    value = remaining.pop("id", None)
    if value != None:
      output.append("id='%s'" % value)

    if self.tag in _svg_signature:
      for name in _svg_signature[self.tag]:
        try:
          value = remaining.pop(name)

          # special handling of path data: truncate it if it's too long
          if name == "d":
            if isinstance(value, basestring):
              value = re.sub("\n", "\\\\n", value)
              if len(value) > 13:
                repr_value = "'%s...'" % value[0:10]
              else:
                repr_value = "'%s'" % value

            elif isinstance(value, (list, tuple)):
              if len(value) > 3:
                repr_value = repr(value[0:3])
                repr_value = "%s, ...%s" % (repr_value[0:-1], repr_value[-1])
              else:
                repr_value = repr(value)

            else:
              repr_value = repr(value)

          # special handling of floats: use __str__ instead of __repr__
          elif isinstance(value, float):
            repr_value = "'%s'" % str(value)

          # normal handling
          else:
            repr_value = repr(value)

          output.append("%s=%s" % (name, repr_value))

        # if the signature item is not present, don't print it
        except KeyError:
          pass

    lenchildren = len(self.children)
    if lenchildren == 1:
      output.append("(1 child)")
    elif lenchildren > 1:
      output.append("(%d children)" % lenchildren)

    lenremaining = len(remaining)
    if lenremaining == 1:
      output.append("(1 other attribute)")
    elif lenremaining > 1:
      output.append("(%d other attributes)" % lenremaining)

    return "<%s>" % " ".join(output)

  def __getitem__(self, treeindex):
    """Index is a list that descends tree, returning a child if
    it ends with a number and an attribute if it ends with a string."""
    obj = self
    if isinstance(treeindex, (list, tuple)):
      for i in treeindex[:-1]: obj = obj[i]
      treeindex = treeindex[-1]

    if isinstance(treeindex, (int, long, slice)):
      return obj.children[treeindex]
    elif isinstance(treeindex, basestring):
      return obj.attrib[treeindex]
    else:
      raise IndexError, "treeindex must be an index, a string, or a list/tuple"

  def __setitem__(self, treeindex, value):
    """Index is a list that descends tree, returning a child if
    it ends with a number and an attribute if it ends with a string."""
    obj = self
    if isinstance(treeindex, (list, tuple)):
      for i in treeindex[:-1]: obj = obj[i]
      treeindex = treeindex[-1]

    if isinstance(treeindex, (int, long, slice)):
      obj.children[treeindex] = value
    elif isinstance(treeindex, basestring):
      obj.attrib[treeindex] = value
    else:
      raise IndexError, "treeindex must be an index, a string, or a list/tuple"

  def __delitem__(self, treeindex):
    """Index is a list that descends tree, returning a child if
    it ends with a number and an attribute if it ends with a string."""
    obj = self
    if isinstance(treeindex, (list, tuple)):
      for i in treeindex[:-1]: obj = obj[i]
      treeindex = treeindex[-1]

    if isinstance(treeindex, (int, long, slice)):
      del obj.children[treeindex]
    elif isinstance(treeindex, basestring):
      del obj.attrib[treeindex]
    else:
      raise IndexError, "treeindex must be an index, a string, or a list/tuple"

  def __eq__(self, other):
    """x == y iff x represents the same SVG as y."""
    if id(self) == id(other): return True
    return isinstance(other, SVG) and self.tag == other.tag and self.children == other.children and self.attrib == other.attrib

  def __ne__(self, other):
    """x != y iff x does not represent the same SVG as y."""
    return not (self == other)

  ### nested class
  class _SVGDepthIterator:
    """Manages SVG iteration."""

    def __init__(self, svg, treeindex, depth_limit, attrib):
      self.svg = svg
      self.treeindex = treeindex
      self.shown = False
      self.depth_limit = depth_limit
      self.attrib = attrib

    def __iter__(self): return self

    def next(self):
      if not self.shown:
        self.shown = True
        if self.treeindex != ():
          return self.treeindex, self.svg

      if not isinstance(self.svg, SVG): raise StopIteration
      if self.depth_limit != None and len(self.treeindex) >= self.depth_limit: raise StopIteration

      if "iterators" not in self.__dict__:
        self.iterators = []
        for i, s in enumerate(self.svg.children):
          self.iterators.append(self.__class__(s, self.treeindex + (i,), self.depth_limit, self.attrib))
        if self.attrib:
          for k, s in self.svg.attrib.items():
            self.iterators.append(self.__class__(s, self.treeindex + (k,), self.depth_limit, self.attrib))
        self.iterators = itertools.chain(*self.iterators)

      return self.iterators.next()
  ### end nested class

  def walk(self, depth_limit=None, attrib=False):
    """Returns a depth-first generator over the SVG.  If depth_limit
    is a number, stop recursion at that depth.  If attrib=True, show
    attributes as well as elements."""
    return self._SVGDepthIterator(self, (), depth_limit, attrib)

  def view(self, depth_limit=None, attrib=False, width=20, string=False):
    output = [("%s %s" % (("%%-%ds" % width) % repr(None), repr(self)))]

    for treeindex, element in self.walk(depth_limit, attrib):
      if isinstance(element, basestring):
        if len(element) > 13:
          repr_element = "'%s...'" % element[0:10]
        else:
          repr_element = "'%s'" % element
      else:
        repr_element = repr(element)

      output.append(("%s %s%s" % (("%%-%ds" % width) % repr(list(treeindex)), ". . " * len(treeindex), repr_element)))

    if string: return "\n".join(output)
    else: print "\n".join(output)

  def xml(self, indent="    ", newl="\n"):
    """Get an XML representation of the SVG that can be saved/rendered.

    indent      string used for indenting
    newl        string used for newlines
    """

    # how to convert different attribute types into XML
    def attribstr(value):
      if isinstance(value, basestring):
        return value

      elif isinstance(value, (int, long, float)):
        return repr(value)  # more precise

      elif isinstance(value, (list, tuple)):
        line = []
        for v in value:
          line.append(attribstr(v))
        return ", ".join(line)

      elif isinstance(value, dict):
        line = []
        for n, v in value.items():
          line.append("%s:%s" % (n, attribstr(v)))
        return "; ".join(line)

      else:
        return str(value)

    # recursive function for writing XML
    def subxml(sub, depth=0):
      if isinstance(sub, basestring):
        return [sub]

      elif isinstance(sub, SVG) and not sub.__class__ == SVG:
        return ["%s%s" % (indent * depth, sub.xml())]

      elif isinstance(sub, SVG):
        line = [indent * depth, "<", sub.tag, " "]
        remaining = copy.copy(sub.attrib)  # shallow copy

        try:
          line.append("id=%s " % remaining.pop("id"))
        except KeyError: pass

        signature = _svg_signature.get(sub.tag)
        if signature != None:
          for name in signature:
            try:
              line.append("%s=\"%s\" " % (name, attribstr(remaining.pop(name))))
            except KeyError: pass

        for name, value in remaining.items():
          line.append("%s=\"%s\" " % (name, attribstr(value)))

        if len(sub.children) == 0:
          line.append("/>")
          return ["".join(line)]

        else:
          line.append(">")

          if sub.tag in ("text", "tspan"):
            for i in sub.children:
              line.extend(subxml(i, 0))
            line.append("</%s>" % (sub.tag))
            return ["".join(line)]

          else:
            lines = ["".join(line)]
            for i in sub.children:
              lines.extend(subxml(i, depth+1))
            lines.append("%s</%s>" % (indent * depth, sub.tag))
            return lines

      else:
        raise TypeError, "SVG contains an unrecognized object: %s" % type(sub)

    # the actual xml() function is rather short
    if self.tag != "svg": svg = SVG("svg")(self)
    else: svg = self
    output = [_xml_header] + subxml(svg) + [""]
    return newl.join(output)

  def _expand_fileName(self, fileName):
    if re.search("windows", platform.system(), re.I) and not os.path.isabs(fileName):
      fileName = _default_directory + os.sep + fileName
    return fileName

  def save(self, fileName, encoding="utf-8", compresslevel=None):
    """Save to a file for viewing.

    fileName                                If the extension is ".svgz" or ".gz", the output will be gzipped
    encoding        default="utf-8"         file encoding (default is Unicode)
    compresslevel   default=None            if a number, the output will be gzipped with that
                                            compression level (1-9, 1 being fastest and 9 most
                                            thorough)
    """
    fileName = self._expand_fileName(fileName)

    if compresslevel != None or re.search("\.svgz$", fileName, re.I) or re.search("\.gz$", fileName, re.I):
      import gzip
      if compresslevel == None:
        f = gzip.GzipFile(fileName, "w")
      else:
        f = gzip.GzipFile(fileName, "w", compresslevel)

      f = codecs.EncodedFile(f, "utf-8", encoding)
      f.write(self.xml())
      f.close()

    else:
      f = codecs.open(fileName, "w", encoding=encoding)
      f.write(self.xml())
      f.close()

    return fileName

  def _write_tempfile(self, fileName=None, encoding="utf-8"):
    if fileName == None:
      fd, fileName = tempfile.mkstemp(".svg", "svgfig-")
      os.write(fd, self.xml())
      os.close(fd)
    else:
      fileName = self._expand_fileName(fileName)
      self.save(fileName, encoding)
    return fileName
    
  def inkview(self, fileName=None, encoding="utf-8"):
    """View in "inkview", assuming that program is available on your system.

    fileName        default=None            if None, generate a temporary file
    encoding        default="utf-8"         file encoding (default is Unicode)
    """
    fileName = self._write_tempfile(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "inkview", ("inkview", fileName))
    return fileName

  def inkscape(self, fileName=None, encoding="utf-8"):
    """View in "inkscape", assuming that program is available on your system.

    fileName        default=None            if None, generate a temporary file
    encoding        default="utf-8"         file encoding (default is Unicode)
    """
    fileName = self._write_tempfile(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "inkscape", ("inkscape", fileName))
    return fileName

  def firefox(self, fileName=None, encoding="utf-8"):
    """View in "firefox", assuming that program is available on your system.

    fileName        default=None            if None, generate a temporary file
    encoding        default="utf-8"         file encoding (default is Unicode)
    """
    fileName = self._write_tempfile(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "firefox", ("firefox", fileName))
    return fileName

##############################################################################

class Instruction(SVG):
  def __init__(self, tag, text):
    self.__dict__["tag"] = tag
    self.__dict__["attrib"] = {}
    self.__dict__["children"] = []
    self.__dict__["text"] = text

  def xml(self): return "<?%s %s?>" % (self.tag, self.text)

  def __repr__(self):
    value = re.sub("\n", "\\\\n", self.text)
    if len(value) > 23:
      return "<?%s %s...?>" % (self.tag, value[0:20])
    else:
      return "<?%s %s?>" % (self.tag, value)

class Comment(SVG):
  def __init__(self, text):
    if text.find("--") != -1:
      raise ValueError, "SVG comments must not include '--'"
    self.__dict__["tag"] = "comment"
    self.__dict__["attrib"] = {}
    self.__dict__["children"] = []
    self.__dict__["text"] = text
  
  def __eq__(self, other): return SVG.__eq__(self, other) and self.text == other.text

  def xml(self): return "<!-- %s -->" % self.text

  def __repr__(self):
    value = re.sub("\n", "\\\\n", self.text)
    if len(value) > 23:
      return "<!-- %s... -->" % value[0:20]
    else:
      return "<!-- %s -->" % value

class CDATA(SVG):
  def __init__(self, text):
    if text.find("]]>") != -1:
      raise ValueError, "CDATA must not include ']]>'"
    self.__dict__["tag"] = "CDATA"
    self.__dict__["attrib"] = {}
    self.__dict__["children"] = []
    self.__dict__["text"] = text
  
  def __eq__(self, other): return SVG.__eq__(self, other) and self.text == other.text

  def xml(self): return "<![CDATA[%s]]>" % self.text

  def __repr__(self):
    value = re.sub("\n", "\\\\n", self.text)
    if len(value) > 23:
      return "<![CDATA[%s...]]>" % value[0:20]
    else:
      return "<![CDATA[%s]]>" % value

##############################################################################

def template(fileName, svg, replaceme="REPLACEME"):
  """Loads an SVG image from a file, replacing instances of
  <REPLACEME /> with a given svg object.

  fileName         required                name of the template SVG
  svg              required                SVG object for replacement
  replaceme        default="REPLACEME"     fake SVG element to be replaced by the given object

  >>> load("template.svg").view()
  None                 <svg width=u'400' height=u'400' viewBox=u'0, 0, 100, 100' (2 children) (5 other attributes)>
  [0]                  . . <rect x=u'0' y=u'0' width=u'100' height=u'100' stroke=u'none' fill=u'yellow'>
  [1]                  . . <REPLACEME>

  >>> template("template.svg", SVG("circle", 50, 50, 30)).view()
  None                 <svg width=u'400' height=u'400' viewBox=u'0, 0, 100, 100' (2 children) (5 other attributes)>
  [0]                  . . <rect x=u'0' y=u'0' width=u'100' height=u'100' stroke=u'none' fill=u'yellow'>
  [1]                  . . <circle cx=50 cy=50 r=30>
  """
  output = load(fileName)
  for treeindex, i in output.walk():
    if isinstance(i, SVG) and i.tag == replaceme:
      output[treeindex] = svg
  return output

def load(fileName):
  """Loads an SVG image from a file."""
  if re.search("\.svgz$", fileName, re.I) or re.search("\.gz$", fileName, re.I):
    import gzip
    f = gzip.GzipFile(fileName)
  else:
    f = file(fileName)
  return load_stream(f)

def load_stream(stream):
  """Loads an SVG image from a stream (can be a string or a file object)."""

  from xml.sax import handler, make_parser
  from xml.sax.handler import feature_namespaces, feature_external_ges, feature_external_pes

  # With a little thought, this could be streamlined.  In its current
  # state, it works (with processing instructions, comments, and CDATA).
  class ContentHandler(handler.ContentHandler):
    def __init__(self):
      self.stack = []
      self.output = None
      self.all_whitespace = re.compile("^\s*$")
      self.CDATA = False

    def startElement(self, tag, attrib):
      s = SVG(tag)
      s.attrib = dict(attrib.items())
      if len(self.stack) > 0:
        last = self.stack[-1]
        last.children.append(s)
      self.stack.append(s)

    def characters(self, ch):
      if self.CDATA:
        last = self.stack[-1]
        last.text += ch

      else:
        if not isinstance(ch, basestring) or self.all_whitespace.match(ch) == None:
          if len(self.stack) > 0:
            last = self.stack[-1]
            if len(last.children) > 0 and isinstance(last.children[-1], basestring):
              last.children[-1] = last.children[-1] + "\n" + ch
            else:
              last.children.append(ch)

    def endElement(self, tag):
      if len(self.stack) > 0:
        last = self.stack[-1]
      self.output = self.stack.pop()

    # If a processing instruction is outside the main <svg> tag, it will be lost.
    def processingInstruction(self, target, data):
      s = Instruction(target, data)
      if len(self.stack) > 0:
        last = self.stack[-1]
        last.children.append(s)
      self.output = s

    def comment(self, comment):
      s = Comment(re.sub("(^ | $)", "", comment))
      if len(self.stack) > 0:
        last = self.stack[-1]
        last.children.append(s)
      self.output = s

    def startCDATA(self):
      s = CDATA("")
      if len(self.stack) > 0:
        last = self.stack[-1]
        last.children.append(s)
      self.stack.append(s)
      self.CDATA = True

    def endCDATA(self):
      if len(self.stack) > 0:
        last = self.stack[-1]
      self.output = self.stack.pop()
      self.CDATA = False

    def startDTD(self, name, public_id, system_id): pass
    def endDTD(self): pass
    def startEntity(self, name): pass
    def endEntity(self, name): pass

  ch = ContentHandler()
  parser = make_parser()
  parser.setContentHandler(ch)
  parser.setProperty(handler.property_lexical_handler, ch)
  parser.setFeature(feature_namespaces, 0)
  parser.setFeature(feature_external_ges, 0)
  parser.parse(stream)
  return ch.output
