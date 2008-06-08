import math, cmath, copy
import _curve, svg, trans, pathdata

def cannonical_parametric(expr):
  """Put parametric expression into cannonical form (function of one variable -> 2-tuple)"""

  if callable(expr):

    # 1 real -> 2 real
    if expr.func_code.co_argcount == 1:
      return expr

    else:
      raise TypeError, "Must be a 1 -> 2 real function"

  else:
    compiled = compile(expr, expr, "eval")

    # 1 real -> 2 real
    if "t" in compiled.co_names:
      output = lambda t: eval(compiled, math.__dict__, {"t": t})
      output.func_name = "t -> %s" % expr
      return output

    # 1 real -> 1 real
    elif "x" in compiled.co_names:
      output = lambda t: (t, eval(compiled, math.__dict__, {"x": t}))
      output.func_name = "x -> %s" % expr
      return output

    # real (a complex number restricted to the real axis) -> complex
    elif "z" in compiled.co_names:
      split = lambda z: (z.real, z.imag)
      output = lambda z: split(eval(compiled, cmath.__dict__, {"z": z}))
      output.func_name = "z -> %s" % expr
      return output

    else:
      raise TypeError, "Parametric string '%s' must contain real 't', 'x', or 'z'" % expr

##############################################################################

class Curve:
  attrib = {"stroke": "black", "fill": "none"}
  smooth = True
  random_sampling = True
  random_seed = 12345
  recursion_limit = 15
  linearity_limit = 0.05
  discontinuity_limit = 5.

  def __init__(self, expr, low, high, **kwds):
    self.f, self.low, self.high = cannonical_parametric(expr), low, high

    for var in "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit":
      if var in kwds:
        exec("self.%s = %s" % (var, kwds[var]))
        del kwds[var]

    self.attrib = dict(self.__class__.attrib)
    self.attrib.update(kwds)
    
    self.transformations = []

  def __repr__(self):
    specials = []
    for var in "attrib", "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit":
      if eval("self.%s" % var) != eval("self.__class__.%s" % var):
        specials.append("%s=%s" % (var, eval("self.%s" % var)))
    specials = " ".join(specials)
    if specials != "": specials = " " + specials

    transformations = ""
    if len(self.transformations) == 1: transformations = " (1 transformation)"
    if len(self.transformations) > 1: transformations = " (%d transformations)" % len(self.transformations)

    return "<Curve %s from %g to %g%s%s>" % (self.f, self.low, self.high, specials, transformations)

  def transform(self, expr): self.transformations.append(trans.cannonical_transformation(expr))

  def d(self):
    data = _curve.curve(self.f, self.transformations, self.low, self.high,
                        self.random_sampling, self.random_seed, self.recursion_limit, self.linearity_limit, self.discontinuity_limit)

    svgdata = []
    begin, end = 0, 0
    for d in data:
      end += 1
      if d == None:
        segment = data[begin:end-1]
        begin = end

        if len(segment) == 1:
          pass
        elif self.smooth:
          svgdata.extend(pathdata.smooth(segment))
        else:
          svgdata.extend(pathdata.poly(segment))

    segment = data[begin:end]
    if len(segment) == 1:
      pass
    elif self.smooth:
      svgdata.extend(pathdata.smooth(segment))
    else:
      svgdata.extend(pathdata.poly(segment))

    return svgdata

  def svg(self):
    return svg.SVG("path", self.d(), **self.attrib)

  def __getitem__(self, name): return self.attrib[name]
  def __setitem__(self, name, value): self.attrib[name] = value
  def __delitem__(self, name): del self.attrib[name]

  def __eq__(self, other):
    """x == y iff x represents the same Curve as y."""
    if id(self) == id(other): return True
    if not isinstance(other, Curve): return False
    for var in "f", "low", "high", "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit", "transformations":
      if eval("self.%s" % var) != eval("other.%s" % var): return False
    return True

  def __ne__(self, other):
    """x != y iff x does not represent the same Curve as y."""
    return not (self == other)
  
  def __deepcopy__(self, memo={}):
    kwds = dict(self.attrib)
    for var in "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit":
      kwds[var] = eval("self.%s" % var)
    result = self.__class__(self.f, self.low, self.high, **kwds)
    memo[id(self)] = result
    return result
