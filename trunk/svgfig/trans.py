import svg, math, copy

epsilon = 1e-5

def transform(expr, obj):
  """Return a copy of obj with transformation expr applied."""
  obj = copy.deepcopy(obj)
  obj.transform(expr)
  return obj

def transformation_angle(expr, x, y, scale=1.):
  func = svg.cannonical_transformation(expr)
  eps = epsilon
  if scale != 0.: eps *= scale

  xprime, yprime = func(x + eps, y)
  x, y = func(x, y)

  delx, dely = xprime - x, yprime - y
  return math.atan2(dely, delx)

def transformation_jacobian(expr, x, y, scale=1.):
  func = svg.cannonical_transformation(expr)
  eps = epsilon
  if scale != 0.: eps *= scale

  X0, Y0 = func(x, y)
  xhatx, xhaty = func(x + eps, y)
  yhatx, yhaty = func(x, y + eps)

  return (1.*(xhatx - X0)/eps, 1.*(xhaty - Y0)/eps), (1.*(yhatx - X0)/eps, 1.*(yhaty - Y0)/eps)

##############################################################################

class Hold(svg.SVG):
  """Holds SVG objects for special transformation handling."""

  def __init__(self, *args, **kwds):
    self.tag = None
    self.attrib = {}
    self.children = list(args)

  def __repr__(self):
    if len(self.children) == 1: return "<Hold (1 child)>"
    else: return "<Hold (%d children)>" % len(self.children)

  def evaluate(self):
    for child in self.children: child.evaluate()

  def svg(self):
    output = svg.SVG("g", **self.attrib)
    for child in self.children: output.append(copy.deepcopy(child))
    return output

  def __eq__(self, other):
    if id(self) == id(other): return True
    return self.__class__ == other.__class__ and self.tag == other.tag and self.children == other.children and self.attrib == other.attrib

  def __deepcopy__(self, memo={}):
    result = self.__class__(*copy.deepcopy(self.children), **copy.deepcopy(self.attrib))
    memo[id(self)] = result
    return result

  def __getattr__(self, name): return self.__dict__[name]
  def __setattr__(self, name, value): self.__dict__[name] = value

##############################################################################

class Delay(Hold):
  """Delay SVG objects and accumulates transformations to
apply to them without applying them right away.  Transformations are
applied (a) when evaluate() is called, (b) to a copy when svg() is
called, and (c) to a copy when drawn as XML."""

  def __init__(self, *args, **kwds):
    Hold.__init__(self, *args, **kwds)
    self.trans = []

  def __repr__(self):
    ren = "ren"
    if len(self.children) == 1: ren = ""
    return "<Delay (%d child%s) (%d trans)>" % (len(self.children), ren, len(self.trans))

  def transform(self, expr):
    """Store a transformation for later."""
    self.trans.append(svg.cannonical_transformation(expr))

  def bbox(self): return self.svg().bbox()

  def evaluate(self):
    """Apply all transformations."""
    for t in self.trans:
      for child in self.children:
        child.transform(t)
    self.trans = []
    Hold.evaluate(self)

  def svg(self):
    """Return a copy of SVG with transformations applied."""
    output = Hold.svg(self)
    for t in self.trans: output.transform(t)
    return output

  def __eq__(self, other):
    return Hold.__eq__(self, other) and self.trans == other.trans

  def __deepcopy__(self, memo={}):
    result = Hold.__deepcopy__(self, memo)
    result.trans = copy.copy(self.trans)
    return result

##############################################################################

class Freeze(Hold):
  """Freeze holds an SVG object and ignores all attempts to transform it."""
  def __repr__(self):
    if len(self.children) == 1: return "<Freeze (1 child)>"
    else: return "<Freeze (%d children)>" % len(self.children)

  def transform(self, expr): pass

##############################################################################

class Pin(Hold):
  """Pin holds an SVG object and applies transformations to only one
point, such that the drawing is never distorted, only moved.  The
drawing rotates if rotate=True."""
  x = 0.
  y = 0.
  rotate = False

  def __init__(self, *args, **kwds):
    for var in "x", "y", "rotate":
      if var in kwds:
        self.__dict__[var] = kwds[var]
        del kwds[var]
    Hold.__init__(self, *args, **kwds)

  def __repr__(self):
    rotate = ""
    if self.rotate: rotate = "and rotate "
    ren = "ren"
    if len(self.children) == 1: ren = ""

    return "<Pin %sat %g %g (%d child%s)>" % (rotate, self.x, self.y, len(self.children), ren)

  def transform(self, expr):
    """Transform the pin position, moving (and rotating) the drawing (if rotate=True)."""
    func = svg.cannonical_transformation(expr)

    oldx, oldy = self.x, self.y
    self.x, self.y = func(self.x, self.y)

    if self.rotate:
      shiftx, shifty = func(oldx + epsilon, oldy)
      angle = math.atan2(shifty, shiftx)
      trans = lambda x, y: (self.x + math.cos(angle)*(x - oldx) - math.sin(angle)*(y - oldy),
                            self.y + math.sin(angle)*(x - oldx) + math.cos(angle)*(y - oldy))

    else:
      trans = lambda x, y: (x + self.x - oldx, y + self.y - oldy)

    for child in self.children:
      child.transform(trans)

  def __eq__(self, other):
    return Hold.__eq__(self, other) and self.x == other.x and self.y == other.y and self.rotate == other.rotate

  def __deepcopy__(self, memo={}):
    result = Hold.__deepcopy__(self, memo)
    result.x, result.y, result.rotate = self.x, self.y, self.rotate
    return result

##############################################################################

def window(xmin, xmax, ymin, ymax, x=0, y=0, width=100, height=100, xlogbase=None, ylogbase=None, minusInfinityX=-1000, minusInfinityY=-1000, flipx=False, flipy=False):
  """Returns a coordinate transformation from
      (xmin, ymin), (xmax, ymax)
to
      (x, y), (x + width, y + height)

xlogbase, ylogbase                if a number, transform logarithmically with given base
minusInfinityX, minusInfinityY    what to return if log(0) or log(negative) is attempted
flipx, flipy                      if True, reverse the direction of x or y"""

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

  def maybelog(t, it1, it2, ot1, ot2, logbase, minusInfinity):
    if t <= 0.: return minusInfinity
    else:
      return ot1 + 1.*(math.log(t, logbase) - math.log(it1, logbase))/(math.log(it2, logbase) - math.log(it1, logbase)) * (ot2 - ot1)

  xlogstr, ylogstr = "", ""

  if xlogbase == None:
    xfunc = lambda x: ox1 + 1.*(x - ix1)/(ix2 - ix1) * (ox2 - ox1)
  else:
    xfunc = lambda x: maybelog(x, ix1, ix2, ox1, ox2, xlogbase, minusInfinityX)
    xlogstr = " xlog=%g" % xlogbase

  if ylogbase == None:
    yfunc = lambda y: oy1 + 1.*(y - iy1)/(iy2 - iy1) * (oy2 - oy1)
  else:
    yfunc = lambda y: maybelog(y, iy1, iy2, oy1, oy2, ylogbase, minusInfinityY)
    ylogstr = " ylog=%g" % ylogbase

  output = lambda x, y: (xfunc(x), yfunc(y))

  output.func_name = "(%g, %g), (%g, %g) -> (%g, %g), (%g, %g)%s%s" % (ix1, ix2, iy1, iy2, ox1, ox2, oy1, oy2, xlogstr, ylogstr)

  output.xmin, output.xmax, output.ymin, output.ymax = xmin, xmax, ymin, ymax
  output.x, output.y, output.width, output.height = x, y, width, height
  output.xlogbase, output.ylogbase, output.minusInfinityX, output.minusInfinityY = xlogbase, ylogbase, minusInfinityX, minusInfinityY
  output.flipx, output.flipy = flipx, flipy
  return output

##############################################################################

def rotation(angle, cx=0, cy=0):
  """Creates and returns a coordinate transformation which rotates
  around (cx,cy) by "angle" radians."""
  output = lambda x, y: (cx + math.cos(angle)*(x - cx) - math.sin(angle)*(y - cy), cy + math.sin(angle)*(x - cx) + math.cos(angle)*(y - cy))
  output.angle = angle
  output.cx = cx
  output.cy = cy
  return output

##############################################################################

