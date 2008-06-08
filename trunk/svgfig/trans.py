import math, cmath, copy

def transform(expr, obj):
  """Return a copy of obj with transformation expr applied."""
  obj = copy.deepcopy(obj)
  obj.transform(expr)
  return obj

##############################################################################

class Hold:
  """Holds an SVG object for special transformation handling."""

  def __init__(self, hold):
    self.__dict__["hold"] = hold

  def __repr__(self): return "<Hold %s>" % self.hold

  def evaluate(self): self.hold.evaluate()

  def __getattr__(self, name): return self.hold.__getattr__(name)

  def __setattr__(self, name, value):
    if name in self.__dict__:
      self.__dict__[name] = value
    else:
      self.hold.__setattr__(name, value)

  def append(self, other): self.hold.append(other)
  def prepend(self, other): self.hold.prepend(other)
  def extend(self, other): self.hold.extend(other)
  def insert(self, i, other): self.hold.insert(i, other)
  def remove(self, other): self.hold.remove(other)
  def __len__(self): return len(self.hold.children)
  def __add__(self, other): return self.hold + other
  def __iadd__(self, other): self.hold += other
  def __mul__(self, other): return self.hold * other
  def __rmul__(self, other): return self * other
  def __imul__(self, other): self.hold *= other
  def count(self, *args, **kwds): return self.hold.count(*args, **kwds)
  def index(self, *args, **kwds): return self.hold.index(*args, **kwds)
  def pop(self, *args, **kwds): return self.hold.pop(*args, **kwds)
  def reverse(self, *args, **kwds): return self.hold.reverse(*args, **kwds)
  def clear(self, *args, **kwds): return self.hold.clear(*args, **kwds)
  def update(self, other): return self.hold.update(other)
  def __contains__(self, other): return other in self.hold
  def fromkeys(self, *args, **kwds): return self.hold.fromkeys(*args, **kwds)
  def has_key(self, *args, **kwds): return self.hold.has_key(*args, **kwds)
  def items(self, *args, **kwds): return self.hold.items(*args, **kwds)
  def keys(self, *args, **kwds): return self.hold.keys(*args, **kwds)
  def values(self, *args, **kwds): return self.hold.values(*args, **kwds)
  def get(self, *args, **kwds): return self.hold.get(*args, **kwds)
  def setdefault(self, *args, **kwds): return self.hold.setdefault(*args, **kwds)
  def iteritems(self, *args, **kwds): return self.hold.iteritems(*args, **kwds)
  def iterkeys(self, *args, **kwds): return self.hold.iterkeys(*args, **kwds)
  def itervalues(self, *args, **kwds): return self.hold.itervalues(*args, **kwds)
  def pop(self, *args, **kwds): return self.hold.pop(*args, **kwds)
  def popitem(self, *args, **kwds): return self.hold.popitem(*args, **kwds)
  def copy(self): return self.hold.copy(*args, **kwds)
  def deepcopy(self): return self.hold.deepcopy(*args, **kwds)
  def __getitem__(self, treeindex): return self.hold[treeindex]
  def __setitem__(self, treeindex, value): self.hold[treeindex] = value
  def __delitem__(self, treeindex): del self.hold[treeindex]
  def __eq__(self, other):
    if id(self) == id(other): return True
    return isinstance(other, Hold) and self.hold == other.hold
  def __ne__(self, other): return not (self == other)
  def walk(self, *args, **kwds): return self.hold.walk(*args, **kwds)
  def tree(self, *args, **kwds): return self.hold.tree(*args, **kwds)
  def xml(self, *args, **kwds): return self.hold.xml(*args, **kwds)
  def save(self, *args, **kwds): return self.hold.save(*args, **kwds)
  def inkview(self, *args, **kwds): return self.hold.inkview(*args, **kwds)
  def inkscape(self, *args, **kwds): return self.hold.inkscape(*args, **kwds)
  def firefox(self, *args, **kwds): return self.hold.firefox(*args, **kwds)

##############################################################################

class Delay(Hold):
  """Delay holds an SVG object and accumulates transformations to
apply to it without applying them right away.  Transformations are
applied (a) when evaluate() is called, (b) to a copy when svg() is
called, and (c) to a copy when drawn as XML.

Arguments: Delay(svg)

Members: hold, transformations"""

  def __init__(self, svg):
    Hold.__init__(self, svg)
    self.__dict__["transformations"] = []

  def __repr__(self):
    s = "s"
    if len(self.transformations) == 1: s = ""
    return "<Delay %s (%d transformation%s)>" % (self.hold, len(self.transformations), s)

  def transform(self, expr):
    """Store a transformation for later."""
    self.transformations.append(cannonical_transformation(expr))

  def evaluate(self):
    """Apply all transformations."""
    for t in self.transformations: self.hold.transform(t)
    self.__dict__["transformations"] = []
    self.hold.evaluate()

  def svg(self):
    """Return a copy of SVG with transformations applied."""
    output = copy.deepcopy(self.hold)
    for t in self.transformations: output.transform(t)
    return output

  def __eq__(self, other):
    if id(self) == id(other): return True
    return isinstance(other, Delay) and self.hold == other.hold and self.transformations == other.transformations

  def __deepcopy__(self, memo={}):
    result = self.__class__(copy.deepcopy(self.hold))
    result.__dict__["transformations"] = copy.copy(self.transformations)
    memo[id(self)] = result
    return result

##############################################################################

class Freeze(Hold):
  """Freeze holds an SVG object and ignores all attempts to transform it.

Arguments: Freeze(svg)

Members: svg"""
  def __init__(self, svg): self.__dict__["hold"] = svg

  def __repr__(self): return "<Freeze %s>" % self.hold

  def transform(self, expr): pass

  def svg(self): return self.hold

  def __eq__(self, other):
    if id(self) == id(other): return True
    return isinstance(other, Freeze) and self.hold == other.hold

##############################################################################

class Pin(Hold):
  """Pin holds an SVG object and applies transformations to only one
point, such that the drawing is never distorted, only moved.  The
drawing rotates if rotate=True.

Arguments: Pin(x, y, svg, rotate=False)

Members: x, y, svg, rotate"""

  epsilon = 1e-3

  def __init__(self, x, y, svg, rotate=False):
    self.__dict__["x"] = x
    self.__dict__["y"] = y
    self.__dict__["hold"] = svg
    self.__dict__["rotate"] = rotate

  def __repr__(self):
    rotate = ""
    if self.rotate: rotate = "and rotate "

    return "<Pin %sat (%g %g) %s>" % (rotate, self.x, self.y, self.hold)

  def transform(self, expr):
    """Transform the pin position, moving (and rotating) the drawing (if rotate=True)."""
    func = cannonical_transformation(expr)

    oldx, oldy = self.x, self.y
    self.__dict__["x"], self.__dict__["y"] = func(self.x, self.y)

    if self.rotate:
      scale = abs(oldx)
      if scale == 0.: scale = 1.
      shiftx, shifty = func(oldx + scale*self.epsilon, oldy)
      angle = math.atan2(shifty, shiftx)

      self.hold.transform(lambda x, y: (self.x + math.cos(angle)*(x - oldx) - math.sin(angle)*(y - oldy),
                                        self.y + math.sin(angle)*(x - oldx) + math.cos(angle)*(y - oldy)))

    else:
      self.hold.transform(lambda x, y: (x + self.x - oldx, y + self.y - oldy))

  def svg(self): return self.hold

  def __eq__(self, other):
    if id(self) == id(other): return True
    return isinstance(other, Pin) and self.x == other.x and self.y == other.y and self.hold == other.hold and self.rotate == other.rotate

##############################################################################

def cannonical_transformation(expr):
  """Put transformation function into cannonical form (function of two variables -> 2-tuple)"""

  if expr is None:
    return lambda x, y: (x, y)

  elif callable(expr):

    # 2 real -> 2 real
    if expr.func_code.co_argcount == 2:
      return expr

    # complex -> complex
    elif expr.func_code.co_argcount == 1:
      split = lambda z: (z.real, z.imag)
      output = lambda x, y: split(expr(complex(x, y)))
      output.func_name = expr.func_name
      return output

    else:
      raise TypeError, "Must be a 2 -> 2 real function or a complex -> complex function"

  else:
    compiled = compile(expr, expr, "eval")

    # 2 real -> 2 real
    if "x" in compiled.co_names and "y" in compiled.co_names:
      output = lambda x, y: eval(compiled, math.__dict__, {"x": x, "y": y})
      output.func_name = "x, y -> %s" % expr
      return output

    # complex -> complex
    elif "z" in compiled.co_names:
      split = lambda z: (z.real, z.imag)
      output = lambda x, y: split(eval(compiled, cmath.__dict__, {"z": complex(x, y)}))
      output.func_name = "z -> %s" % expr
      return output

    else:
      raise TypeError, "Transformation string '%s' must contain real 'x' and 'y' or complex 'z'" % expr

##############################################################################

def window(xmin, xmax, ymin, ymax, x=0, y=0, width=100, height=100, xlogbase=None, ylogbase=None, minusInfinity=-1000, flipx=False, flipy=False):
  """Returns a coordinate transformation from
      (xmin, ymin), (xmax, ymax)
to
      (x, y), (x + width, y + height)

xlogbase, ylogbase      if a number, transform logarithmically with given base
minusInfinity           what to return if log(0) or log(negative) is attempted
flipx, flipy            if True, reverse the direction of x or y"""

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
    yfunc = lambda y: maybelog(y, iy1, iy2, oy1, oy2, ylogbase)
    ylogstr = " ylog=%g" % ylogbase

  output = lambda x, y: (xfunc(x), yfunc(y))

  output.func_name = "(%g, %g), (%g, %g) -> (%g, %g), (%g, %g)%s%s" % (ix1, ix2, iy1, iy2, ox1, ox2, oy1, oy2, xlogstr, ylogstr)
  return output

##############################################################################

def rotation(angle, cx=0, cy=0):
  """Creates and returns a coordinate transformation which rotates
  around (cx,cy) by "angle" radians."""
  return lambda x, y: (cx + math.cos(angle)*(x - cx) - math.sin(angle)*(y - cy), cy + math.sin(angle)*(x - cx) + math.cos(angle)*(y - cy))
