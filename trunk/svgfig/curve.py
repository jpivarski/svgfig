import math, cmath, copy
import _curve, svg, trans, pathdata, glyphs

##############################################################################

class Curve:
  attrib = {"stroke": "black", "fill": "none"}
  smooth = False
  marks = {}
  random_sampling = True
  random_seed = 12345
  recursion_limit = 15
  linearity_limit = 0.05
  discontinuity_limit = 5.
  text_offsetx = 0.
  text_offsety = -2.5
  text_attrib = {}

  def __init__(self, expr, low, high, **kwds):
    self.f, self.low, self.high = cannonical_parametric(expr), low, high

    for var in "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit", "text_offsetx", "text_offsety":
      if var in kwds:
        exec("self.%s = %s" % (var, kwds[var]))
        del kwds[var]

    self.marks = copy.deepcopy(self.marks)
    if "marks" in kwds:
      self.marks.update(kwds["marks"])
      del kwds["marks"]

    self.text_attrib = copy.deepcopy(self.text_attrib)
    if "text_attrib" in kwds:
      self.text_attrib.update(kwds["text_attrib"])
      del kwds["text_attrib"]

    # need to set "stroke" attribute before adding ticks and arrows
    self.attrib = copy.deepcopy(self.__class__.attrib)
    if "stroke" in kwds:
      self.attrib["stroke"] = kwds["stroke"]
      del kwds["stroke"]

    if "ticks" in kwds:
      ticks = kwds["ticks"]
      del kwds["ticks"]

      if isinstance(ticks, dict):
        for t, mark in ticks.items(): self.tick(t, mark)
      else:
        for t in ticks: self.tick(t, unicode_number(t, scale=(self.high - self.low)))
          
    if "farrow" in kwds:
      self.farrow(kwds["farrow"])
      del kwds["farrow"]

    if "barrow" in kwds:
      self.barrow(kwds["barrow"])
      del kwds["barrow"]

    # now add the rest of the attributes
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
    lentransformations = len(self.transformations)
    if lentransformations == 1: transformations = " (1 transformation)"
    elif lentransformations > 1: transformations = " (%d transformations)" % lentransformations

    marks = ""
    lenmarks = len(self.marks)
    if lenmarks == 1: marks = " (1 mark)"
    elif lenmarks > 1: marks = " (%d marks)" % lenmarks

    return "<Curve %s from %g to %g%s%s%s>" % (self.f, self.low, self.high, specials, transformations, marks)

  def transform(self, expr): self.transformations.append(trans.cannonical_transformation(expr))

  def __call__(self, t, transformed=True):
    x, y = self.f(t)
    if transformed:
      for transformation in self.transformations:
        x, y = transformation(x, y)
    return x, y

  def angle(self, t, transformed=True):
    x, y = self(t, transformed)

    tprime = t + trans.epsilon * abs(self.high - self.low)
    xprime, yprime = self(tprime, transformed)

    delx, dely = xprime - x, yprime - y
    return math.atan2(dely, delx)

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
    if self.marks == {}:
      return svg.SVG("path", self.d(), **self.attrib)
    else:
      output = svg.SVG("g", svg.SVG("path", self.d(), **self.attrib))

      tolerance = 2. * trans.epsilon * abs(self.high - self.low)

      items = self.marks.items()
      items.sort()
      for t, mark in items:
        if self.low - tolerance < t < self.high + tolerance:
          X, Y = self(t, transformed=True)
          angle = self.angle(t, transformed=True)

          if isinstance(mark, basestring):
            text_attrib = {"transform": "translate(%g, %g) rotate(%g)" %
                           (X + self.text_offsetx*math.cos(angle) - self.text_offsety*math.sin(angle),
                            Y + self.text_offsetx*math.sin(angle) + self.text_offsety*math.cos(angle), 180./math.pi*angle),
                           "text-anchor": "middle"}
            text_attrib.update(self.text_attrib)
            mark = svg.SVG("text", 0., 0., **text_attrib)(mark)

          else:
            mark = trans.transform(lambda x, y: (X + math.cos(angle)*x - math.sin(angle)*y,
                                                 Y + math.sin(angle)*x + math.cos(angle)*y), mark)
          output.append(mark)

      return output

  def __getitem__(self, name): return self.attrib[name]
  def __setitem__(self, name, value): self.attrib[name] = value
  def __delitem__(self, name): del self.attrib[name]

  def __eq__(self, other):
    if id(self) == id(other): return True
    if not isinstance(other, Curve): return False
    for var in "f", "low", "high", "smooth", "marks", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit", "transformations":
      if eval("self.%s" % var) != eval("other.%s" % var): return False
    return True
  def __ne__(self, other): return not (self == other)
  
  def __deepcopy__(self, memo={}):
    kwds = copy.deepcopy(self.attrib)
    for var in "smooth", "marks", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit":
      kwds[var] = eval("self.%s" % var)
    result = self.__class__(self.f, self.low, self.high, **kwds)
    memo[id(self)] = result
    return result

  def drop(self, t, tolerance=None):
    if tolerance is None: tolerance = trans.epsilon * abs(self.high - self.low)

    for pos in self.marks.keys():
      if abs(pos - t) < tolerance:
        del self.marks[pos]

  def wipe(self, low, high):
    for pos in self.marks.keys():
      if low <= pos < high:
        del self.marks[pos]

  def add(self, t, mark, angle=0., dx=0., dy=0., replace=False):
    if not isinstance(mark, basestring):
      # always copies mark (through transformation), before adding it
      # so that the behavior is predictable (always copy rather than only sometimes)
      # (strings are always constants)
      mark = trans.transform(lambda x, y: (dx + math.cos(angle)*x - math.sin(angle)*y,
                                           dy + math.sin(angle)*x + math.cos(angle)*y), mark)

    # floating point keys are hard to reproduce, so in the interest of
    # predictable behavior, don't allow collisions by default
    if not replace and t in self.marks: raise KeyError, "Position %g is already occupied (set replace=True to replace it)"

    self.marks[t] = mark

  ### convenience functions for adding forward and backward arrows
  def farrow(self, mark=True):
    if mark is False or mark is None:
      if self.high in self.marks:
        del self.marks[self.high]
    elif mark is True:
      self.add(self.high, glyphs.arrowhead, angle=0., dx=0., dy=0., replace=True)
      self.marks[self.high]["fill"] = self["stroke"]
    else:
      self.add(self.high, mark, angle=0., dx=0., dy=0., replace=True)
      self.marks[self.high]["fill"] = self["stroke"]

  def barrow(self, mark=True):
    if mark is False or mark is None:
      if self.low in self.marks:
        del self.marks[self.low]
    elif mark is True:
      self.add(self.low, glyphs.arrowhead, angle=math.pi, dx=0., dy=0., replace=True)
      self.marks[self.low]["fill"] = self["stroke"]
    else:
      self.add(self.low, mark, angle=math.pi, dx=0., dy=0., replace=True)
      self.marks[self.low]["fill"] = self["stroke"]

  def tick(self, t, mark=None):
    if mark is None:
      self.add(t, glyphs.tick)
      self.marks[t]["stroke"] = self["stroke"]
    elif isinstance(mark, basestring):
      self.add(t, glyphs.tick)
      self.marks[t]["stroke"] = self["stroke"]
      self.add(t + trans.epsilon * abs(self.high - self.low), mark)
    else:
      self.add(t, mark)
      self.marks[t]["stroke"] = self["stroke"]

  def minitick(self, t): self.tick(t, glyphs.minitick)

##############################################################################

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

def format_number(x, format="%g", scale=1.):
  eps = trans.epsilon * abs(scale)
  if abs(x) < eps: return "0"
  return format % x

def unicode_number(x, scale=1.):
  """Converts numbers to a Unicode string, taking advantage of special
Unicode characters to make nice minus signs and scientific notation."""
  output = format_number(x, u"%g", scale)

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

##############################################################################




















# def compute_ticks(self, N, format):
#   """Return less than -N or exactly N optimal linear ticks.

#   Normally only used internally.
#   """
#   if self.low >= self.high: raise ValueError, "low must be less than high"
#   if N == 1: raise ValueError, "N can be 0 or >1 to specify the exact number of ticks or negative to specify a maximum"

#   eps = _epsilon * (self.high - self.low)

#   if N >= 0:
#     output = {}
#     x = self.low
#     for i in xrange(N):
#       if format == unumber and abs(x) < eps: label = u"0"
#       else: label = format(x)
#       output[x] = label
#       x += (self.high - self.low)/(N-1.)
#     return output

#   N = -N

#   counter = 0
#   granularity = 10**math.ceil(math.log10(max(abs(self.low), abs(self.high))))
#   lowN = math.ceil(1.*self.low / granularity)
#   highN = math.floor(1.*self.high / granularity)

#   while (lowN > highN):
#     countermod3 = counter % 3
#     if countermod3 == 0: granularity *= 0.5
#     elif countermod3 == 1: granularity *= 0.4
#     else: granularity *= 0.5
#     counter += 1
#     lowN = math.ceil(1.*self.low / granularity)
#     highN = math.floor(1.*self.high / granularity)

#   last_granularity = granularity
#   last_trial = None

#   while True:
#     trial = {}
#     for n in range(int(lowN), int(highN)+1):
#       x = n * granularity
#       if format == unumber and abs(x) < eps: label = u"0"
#       else: label = format(x)
#       trial[x] = label

#     if int(highN)+1 - int(lowN) >= N:
#       if last_trial == None:
#         v1, v2 = self.low, self.high
#         return {v1: format(v1), v2: format(v2)}
#       else:
#         low_in_ticks, high_in_ticks = False, False
#         for t in last_trial.keys():
#           if 1.*abs(t - self.low)/last_granularity < _epsilon: low_in_ticks = True
#           if 1.*abs(t - self.high)/last_granularity < _epsilon: high_in_ticks = True

#         lowN = 1.*self.low / last_granularity
#         highN = 1.*self.high / last_granularity
#         if abs(lowN - round(lowN)) < _epsilon and not low_in_ticks:
#           last_trial[self.low] = format(self.low)
#         if abs(highN - round(highN)) < _epsilon and not high_in_ticks:
#           last_trial[self.high] = format(self.high)
#         return last_trial

#     last_granularity = granularity
#     last_trial = trial

#     countermod3 = counter % 3
#     if countermod3 == 0: granularity *= 0.5
#     elif countermod3 == 1: granularity *= 0.4
#     else: granularity *= 0.5
#     counter += 1
#     lowN = math.ceil(1.*self.low / granularity)
#     highN = math.floor(1.*self.high / granularity)

# def regular_miniticks(self, N):
#   """Return exactly N linear ticks.

#   Normally only used internally.
#   """
#   output = []
#   x = self.low
#   for i in xrange(N):
#     output.append(x)
#     x += (self.high - self.low)/(N-1.)
#   return output

# def compute_miniticks(self, original_ticks):
#   """Return optimal linear miniticks, given a set of ticks.

#   Normally only used internally.
#   """
#   if len(original_ticks) < 2: original_ticks = ticks(self.low, self.high)
#   original_ticks = original_ticks.keys()
#   original_ticks.sort()

#   if self.low > original_ticks[0] + _epsilon or self.high < original_ticks[-1] - _epsilon:
#     raise ValueError, "original_ticks {%g...%g} extend beyond [%g, %g]" % (original_ticks[0], original_ticks[-1], self.low, self.high)

#   granularities = []
#   for i in range(len(original_ticks)-1):
#     granularities.append(original_ticks[i+1] - original_ticks[i])
#   spacing = 10**(math.ceil(math.log10(min(granularities)) - 1))

#   output = []
#   x = original_ticks[0] - math.ceil(1.*(original_ticks[0] - self.low) / spacing) * spacing

#   while x <= self.high:
#     if x >= self.low:
#       already_in_ticks = False
#       for t in original_ticks:
#         if abs(x-t) < _epsilon * (self.high - self.low): already_in_ticks = True
#       if not already_in_ticks: output.append(x)
#     x += spacing
#   return output

# def compute_logticks(self, base, N, format):
#   """Return less than -N or exactly N optimal logarithmic ticks.

#   Normally only used internally.
#   """
#   if self.low >= self.high: raise ValueError, "low must be less than high"
#   if N == 1: raise ValueError, "N can be 0 or >1 to specify the exact number of ticks or negative to specify a maximum"

#   eps = _epsilon * (self.high - self.low)

#   if N >= 0:
#     output = {}
#     x = self.low
#     for i in xrange(N):
#       if format == unumber and abs(x) < eps: label = u"0"
#       else: label = format(x)
#       output[x] = label
#       x += (self.high - self.low)/(N-1.)
#     return output

#   N = -N

#   lowN = math.floor(math.log(self.low, base))
#   highN = math.ceil(math.log(self.high, base))
#   output = {}
#   for n in range(int(lowN), int(highN)+1):
#     x = base**n
#     label = format(x)
#     if self.low <= x <= self.high: output[x] = label

#   for i in range(1, len(output)):
#     keys = output.keys()
#     keys.sort()
#     keys = keys[::i]
#     values = map(lambda k: output[k], keys)
#     if len(values) <= N:
#       for k in output.keys():
#         if k not in keys:
#           output[k] = ""
#       break

#   if len(output) <= 2:
#     output2 = self.compute_ticks(N=-int(math.ceil(N/2.)), format=format)
#     lowest = min(output2)

#     for k in output:
#       if k < lowest: output2[k] = output[k]
#     output = output2

#   return output

# def compute_logminiticks(self, base):
#   """Return optimal logarithmic miniticks, given a set of ticks.

#   Normally only used internally.
#   """
#   if self.low >= self.high: raise ValueError, "low must be less than high"

#   lowN = math.floor(math.log(self.low, base))
#   highN = math.ceil(math.log(self.high, base))
#   output = []
#   num_ticks = 0
#   for n in range(int(lowN), int(highN)+1):
#     x = base**n
#     if self.low <= x <= self.high: num_ticks += 1
#     for m in range(2, int(math.ceil(base))):
#       minix = m * x
#       if self.low <= minix <= self.high: output.append(minix)

#   if num_ticks <= 2: return []
#   else: return output
