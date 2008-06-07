import math, cmath, copy

##############################################################################

def transform(expr, obj):
  obj = copy.deepcopy(obj)
  obj.transform(expr)
  return obj

class Pin:
  epsilon = 1e-3

  def __init__(self, x, y, svg, rotate=False):
    self.x, self.y = x, y
    self.svg = svg
    self.rotate = rotate

  def __repr__(self):
    rotate = ""
    if self.rotate: rotate = "and rotate "

    return "<Pin %s%s at (%g %g)>" % (rotate, self.svg, self.x, self.y)

  def transform(self, expr):
    func = cannonical(expr)

    oldx, oldy = self.x, self.y
    self.x, self.y = func(self.x, self.y)

    if self.rotate:
      scale = abs(oldx)
      if scale == 0.: scale = 1.
      shiftx, shifty = func(oldx + scale*self.epsilon, oldy)
      angle = math.atan2(shifty, shiftx)

      self.svg.transform(lambda x, y: (self.x + math.cos(angle)*(x - oldx) - math.sin(angle)*(y - oldy),
                                       self.y + math.sin(angle)*(x - oldx) + math.cos(angle)*(y - oldy)))

    else:
      self.svg.transform(lambda x, y: (x + self.x - oldx, y + self.y - oldy))

  def __getitem__(self, treeindex): return self.svg[treeindex]
  def __setitem__(self, treeindex, value): self.svg[treeindex] = value
  def __delitem__(self, treeindex): del self.svg[treeindex]
  def __eq__(self, other):
    """x == y iff x represents the same Pin as y."""
    if id(self) == id(other): return True
    return isinstance(other, Pin) and self.x == other.x and self.y == other.y and self.svg == other.svg and self.rotate == other.rotate
  def __ne__(self, other):
    """x != y iff x does not represent the same Pin as y."""
    return not (self == other)

##############################################################################

def cannonical(expr):
  """Put into cannonical form (function of two variables -> 2-tuple)"""

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
  """Creates and returns a coordinate transformation (a function that
  accepts two arguments and returns two values) that transforms from
      (xmin, ymin), (xmax, ymax)
  to
      (x, y), (x + width, y + height).

  xlogbase, ylogbase    default=None, None     if a number, transform
                                               logarithmically with given base
  minusInfinity         default=-1000          what to return if
                                               log(0 or negative) is attempted
  flipx                 default=False          if true, reverse the direction of x
  flipy                 default=False          if true, reverse the direction of y
  """

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
