# should be compatible with Python 2.3 and higher (and tested with 2.4.3)

import re, codecs, os, platform, copy, itertools, tempfile
import defaults, trans

saved = []

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
    self.__dict__["attrib"] = dict(defaults.defaults.get(tag, {}))
    self.__dict__["children"] = []

    signature = defaults.signature.get(tag)
    if tag in defaults.inline:
      self.children.extend(signature_attrib)

    elif signature is not None:

      if len(signature_attrib) > len(signature):
        raise TypeError, "Tag '%s' expects no more than %d non-keyword attributes (saw %d)" % (tag, len(signature), len(signature_attrib))

      for name, value in zip(signature, signature_attrib):
        self.attrib[name] = value

    elif len(signature_attrib) > 0:
      raise TypeError, "Tag '%s' expects 0 non-keyword attributes (saw %d)" % (tag, len(signature_attrib))

    for name, value in more_attrib.items():
      processed_name = self._preprocess_attribname(name)
      if processed_name != name:
        del more_attrib[name]
        more_attrib[processed_name] = value

    self.attrib.update(more_attrib)

    require = defaults.require.get(tag)
    if require is not None:
      for name in require:
        if name not in self.attrib:
          raise TypeError, "Tag '%s' requires a '%s' attribute" % (tag, name)

  def __call__(self, *children):
    """Extends the list of children and returns self (for inline construction of trees)."""
    self.children.extend(children)
    return self

  def transform(self, expr):
    transform_function = defaults.__dict__.get("transform_%s" % self.tag)
    if transform_function is not None:
      transform_function(trans.cannonical_transformation(expr), self)

  def bbox(self):
    bbox_function = defaults.__dict__.get("bbox_%s" % self.tag)
    if bbox_function is not None:
      return bbox_function(self)
    else:
      return trans.BBox(None, None, None, None)

  def evaluate(self):
    for child in self.children:
      if isinstance(child, (SVG, trans.Hold)):
        child.evaluate()
        
  def svg(self):
    newchildren = []
    for i, child in enumerate(self.children):
      doit = False
      try:
        child.svg
        doit = True
      except AttributeError: pass
      if doit:
        if callable(child.svg): newchildren.append(child.svg())
        else: newchildren.append(child.svg)
      else:
        newchildren.append(copy.deepcopy(child))

    return SVG(self.tag, **self.attrib)(*newchildren)

  ### signature attributes are accessible as member data
  def __getattr__(self, name):
    signature = defaults.signature.get(self.tag)
    if signature is not None and name in signature:
      return self.attrib[name]
    else:
      raise AttributeError, "SVG tag '%s' has no signature attrib '%s' (access others with brackets)" % (self.tag, name)

  def __setattr__(self, name, value):
    if name in self.__dict__ or name == "repr":
      self.__dict__[name] = value

    else:
      signature = defaults.signature.get(self.tag)
      if signature is not None and name in signature:
        self.attrib[name] = value
      else:
        raise AttributeError, "SVG tag '%s' has no signature attrib '%s' (access others with brackets)" % (self.tag, name)

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
    output = copy.deepcopy(self)
    output += other
    return output

  def __iadd__(self, other):
    self.children.append(other)
    return self

  def __mul__(self, other):
    output = copy.deepcopy(self)
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
  def copy(self): return copy.copy(self)
  def deepcopy(self): return copy.deepcopy(self)
  ###

  def __repr__(self):
    if "repr" in self.__dict__: return self.repr

    output = ["%s" % self.tag]

    remaining = copy.copy(self.attrib)  # shallow copy

    value = remaining.pop("id", None)
    if value is not None:
      output.append("id='%s'" % value)

    # special handling of a text child: print it out and truncate if it's too long
    if self.tag in ("text", "tspan") and len(self.children) == 1 and isinstance(self.children[0], basestring):
      value = re.sub("\n", "\\\\n", self.children[0])
      if len(value) > 13:
        repr_value = "'%s...'" % value[0:10]
      else:
        repr_value = "'%s'" % value
      output.append(repr_value)

    if self.tag in defaults.signature:
      for name in defaults.signature[self.tag]:
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
            repr_value = "%s" % str(value)

          # normal handling
          else:
            repr_value = repr(value)

          output.append("%s=%s" % (name, repr_value))

        # if the signature item is not present, don't print it
        except KeyError:
          pass

    lenchildren = len(self.children)
    if lenchildren == 1:
      # special handling of a text child: already printed
      if self.tag in ("text", "tspan") and isinstance(self.children[0], basestring):
        pass
      else:
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
    if isinstance(obj, trans.Hold): obj = obj.hold

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
    if isinstance(obj, trans.Hold): obj = obj.hold

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
    if isinstance(obj, trans.Hold): obj = obj.hold

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

    def __init__(self, svg, treeindex, depth_limit, attrib, attrib_first):
      self.current = svg
      self.treeindex = treeindex
      self.shown = False
      self.depth_limit = depth_limit
      self.attrib = attrib
      self.attrib_first = attrib_first

    def __iter__(self): return self

    def make_children_iterators(self):
      doit = False
      try:
        self.current.children
        doit = True
      except AttributeError: pass
      if doit:
        for i, s in enumerate(self.current.children):
          self.iterators.append(self.__class__(s, self.treeindex + (i,), self.depth_limit, self.attrib, self.attrib_first))

    def make_attrib_iterators(self):
      doit = False
      try:
        self.current.attrib
        doit = True
      except AttributeError: pass
      if doit:
        items = self.current.attrib.items()
        items.sort()
        for k, s in items:
          self.iterators.append(self.__class__(s, self.treeindex + (k,), self.depth_limit, self.attrib, self.attrib_first))

    def next(self):
      if not self.shown:
        self.shown = True
        if self.treeindex != ():
          return self.treeindex, self.current

      if isinstance(self.current, trans.Hold): self.current = self.current.hold

      if self.depth_limit is not None and len(self.treeindex) >= self.depth_limit: raise StopIteration

      if "iterators" not in self.__dict__:
        self.iterators = []

        if self.attrib and self.attrib_first: self.make_attrib_iterators()
        self.make_children_iterators()
        if self.attrib and not self.attrib_first: self.make_attrib_iterators()

        self.iterators = itertools.chain(*self.iterators)

      return self.iterators.next()
  ### end nested class

  def walk(self, depth_limit=None, attrib=False, attrib_first=False):
    """Returns a depth-first generator over the SVG.  If depth_limit
    is a number, stop recursion at that depth.  If attrib=True, show
    attributes as well as elements."""
    return self._SVGDepthIterator(self, (), depth_limit, attrib, attrib_first)

  def tree(self, depth_limit=None, attrib=False, attrib_first=False, index_width=20, showtop=True, asstring=False):
    if showtop:
      output = [("%s %s" % (("%%-%ds" % index_width) % repr(None), repr(self)))]
    else:
      output = []

    for treeindex, element in self.walk(depth_limit, attrib, attrib_first):
      if isinstance(element, basestring):
        if len(element) > 13:
          repr_element = "'%s...'" % element[0:10]
        else:
          repr_element = "'%s'" % element
      else:
        repr_element = repr(element)

      output.append(("%s %s%s" % (("%%-%ds" % index_width) % repr(list(treeindex)), ". . " * len(treeindex), repr_element)))

    if asstring: return "\n".join(output)
    else: print "\n".join(output)

  def xml(self, indent=u"    ", newl=u"\n"):
    """Get an XML representation of the SVG that can be saved/rendered.

    indent      string used for indenting
    newl        string used for newlines
    """

    # how to convert different attribute types into XML
    def attribstr(tag, name, value):
      if isinstance(value, basestring):
        return value

      elif isinstance(value, (int, long, float)):
        return repr(value)  # more precise

      elif isinstance(value, (list, tuple)) and tag == "path" and name == "d":
        def numbertostr(x):
          if isinstance(x, (int, long, float)): return repr(x)  # more precise
          else: return x

        line = []
        lastcommand = None
        for datum in value:
          if not isinstance(datum, (list, tuple)):
            raise TypeError, "Pathdata elements must be lists/tuples"

          command = datum[0]
          args = map(numbertostr, datum[1:])

          if lastcommand == command:
            line.append(u" ")
            line.append(u" ".join(args))
            lastcommand = command
          else:
            line.append(command)
            line.append(u" ".join(args))

          lastcommand = command

        return u"".join(line)

      elif isinstance(value, (list, tuple)):
        line = []
        for v in value:
          line.append(attribstr(tag, name, v))
        return u", ".join(line)

      elif isinstance(value, dict):
        line = []
        for n, v in value.items():
          line.append(u"%s:%s" % (n, attribstr(tag, name, v)))
        return u"; ".join(line)

      else:
        return unicode(value)

    # recursive function for writing XML
    def subxml(sub, depth=0):
      doit = False
      try:
        sub.svg
        doit = True
      except AttributeError: pass
      if doit:
        sub = sub.svg() # if sub is a dynamic object that needs to be evaluated, now is the time to do it

      if isinstance(sub, basestring):
        return [sub]

      elif isinstance(sub, SVG) and not sub.__class__ == SVG:
        return [u"%s%s" % (indent * depth, sub.xml())]

      elif isinstance(sub, SVG):
        line = [indent * depth, u"<", sub.tag, u" "]
        remaining = copy.copy(sub.attrib)  # shallow copy

        try:
          line.append(u"id=\"%s\" " % remaining.pop("id"))
        except KeyError: pass

        signature = defaults.signature.get(sub.tag)
        if signature is not None:
          for name in signature:
            try:
              line.append(u"%s=\"%s\" " % (name, attribstr(sub.tag, name, remaining.pop(name))))
            except KeyError: pass

        for name, value in remaining.items():
          line.append(u"%s=\"%s\" " % (name, attribstr(sub.tag, name, value)))

        if len(sub.children) == 0:
          line.append(u"/>")
          return [u"".join(line)]

        else:
          line.append(u">")

          if sub.tag in ("text", "tspan"):
            for i in sub.children:
              line.extend(subxml(i, 0))
            line.append(u"</%s>" % (sub.tag))
            return [u"".join(line)]

          else:
            lines = [u"".join(line)]
            for i in sub.children:
              lines.extend(subxml(i, depth+1))
            lines.append(u"%s</%s>" % (indent * depth, sub.tag))
            return lines

      else:
        raise TypeError, "SVG contains an unrecognized object: %s" % type(sub)

    # the actual xml() function is rather short
    if self.tag != "svg": svg = SVG("svg")(self)
    else: svg = self
    output = [defaults.xml_header] + subxml(svg) + [u""]
    return unicode(newl.join(output))

  def view(self):
    import _viewer
    _viewer.str(self.xml())

  def _expand_fileName(self, fileName):
    if re.search("windows", platform.system(), re.I) and not os.path.isabs(fileName):
      fileName = defaults.directory + os.sep + fileName
    return fileName

  def save(self, fileName, encoding="utf-8", compresslevel=None):
    """Save to a file for viewing.

    fileName                                If the extension is ".svgz" or ".gz", the output will be gzipped
    encoding        default="utf-8"         file encoding ("utf-8" is Unicode mostly-readable as ASCII)
    compresslevel   default=None            if a number, the output will be gzipped with that
                                            compression level (1-9, 1 being fastest and 9 most
                                            thorough)
    """
    fileName = self._expand_fileName(fileName)

    if compresslevel is not None or re.search("\.svgz$", fileName, re.I) or re.search("\.gz$", fileName, re.I):
      import gzip
      if compresslevel is None:
        f = gzip.GzipFile(fileName, "w")
      else:
        f = gzip.GzipFile(fileName, "w", compresslevel)

      f = codecs.EncodedFile(f, "utf-16", encoding)
      f.write(self.xml())
      f.close()

    else:
      f = codecs.open(fileName, "w", encoding=encoding)
      f.write(self.xml())
      f.close()

    saved.append(fileName)

  def _write_tempfile(self, fileName=None, encoding="utf-8"):
    if fileName is None:
      fd, fileName = tempfile.mkstemp(".svg", "svgfig-")
      os.close(fd)
    else:
      fileName = self._expand_fileName(fileName)

    self.save(fileName, encoding)
    return fileName
    
  def inkview(self, fileName=None, encoding="utf-8"):
    """View in "inkview", assuming that program is available on your system.

    fileName        default=None            if None, generate a temporary file
    encoding        default="utf-8"         file encoding ("utf-8" is Unicode mostly-readable as ASCII)
    """
    fileName = self._write_tempfile(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "inkview", ("inkview", fileName))
    saved.append(fileName)

  def inkscape(self, fileName=None, encoding="utf-8"):
    """View in "inkscape", assuming that program is available on your system.

    fileName        default=None            if None, generate a temporary file
    encoding        default="utf-8"         file encoding ("utf-8" is Unicode mostly-readable as ASCII)
    """
    fileName = self._write_tempfile(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "inkscape", ("inkscape", fileName))
    saved.append(fileName)

  def firefox(self, fileName=None, encoding="utf-8"):
    """View in "firefox", assuming that program is available on your system.

    fileName        default=None            if None, generate a temporary file
    encoding        default="utf-8"         file encoding ("utf-8" is Unicode mostly-readable as ASCII)
    """
    fileName = self._write_tempfile(fileName, encoding)
    os.spawnvp(os.P_NOWAIT, "firefox", ("firefox", fileName))
    saved.append(fileName)

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

  >>> load("template.svg").tree()
  None                 <svg width=u'400' height=u'400' viewBox=u'0, 0, 100, 100' (2 children) (5 other attributes)>
  [0]                  . . <rect x=u'0' y=u'0' width=u'100' height=u'100' stroke=u'none' fill=u'yellow'>
  [1]                  . . <REPLACEME>

  >>> template("template.svg", SVG("circle", 50, 50, 30)).tree()
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
        if not isinstance(ch, basestring) or self.all_whitespace.match(ch) is None:
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

##############################################################################

# This rgb function could be a lot better... something to think about...
def rgb(r, g, b, maximum=1.):
  """Create an SVG color string "#xxyyzz" from r, g, and b.

r,g,b = 0 is black and r,g,b = maximum is white.
  """
  return "#%02x%02x%02x" % (max(0, min(r*255./maximum, 255)), max(0, min(g*255./maximum, 255)), max(0, min(b*255./maximum, 255)))

