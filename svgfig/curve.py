import math, cmath, copy
import svg, trans, pathdata, glyphs

##############################################################################

class Curve:
  attrib = {"stroke": "black", "fill": "none"}
  smooth = False
  marks = []
  random_sampling = True
  random_seed = 12345
  recursion_limit = 50
  linearity_limit = 0.05
  discontinuity_limit = 1.
  text_offsetx = 0.
  text_offsety = -2.5
  text_attrib = {}

  def __init__(self, expr, low, high, **kwds):
    self.f, self.low, self.high = cannonical_parametric(expr), low, high

    for var in "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit", "text_offsetx", "text_offsety":
      if var in kwds:
        exec("self.%s = %s" % (var, kwds[var]))
        del kwds[var]
    
    if "marks" in kwds:
      self.marks = copy.deepcopy(kwds["marks"])
      del kwds["marks"]
    else:
      self.marks = copy.deepcopy(self.marks)      

    self.text_attrib = copy.deepcopy(self.text_attrib)
    if "text_attrib" in kwds:
      self.text_attrib.update(kwds["text_attrib"])
      del kwds["text_attrib"]

    # need to set "stroke" attribute before adding ticks and arrows
    self.attrib = copy.deepcopy(self.__class__.attrib)
    if "stroke" in kwds:
      self.attrib["stroke"] = kwds["stroke"]
      del kwds["stroke"]
          
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
    import _curve
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
    if self.marks == []:
      return svg.SVG("path", self.d(), **self.attrib)
    else:
      output = svg.SVG("g", svg.SVG("path", self.d(), **self.attrib))

      tolerance = 2. * trans.epsilon * abs(self.high - self.low)

      items = copy.copy(self.marks)
      items.sort()
      for item in items:
        if isinstance(item, (int, long, float)):
          t, mark = item, glyphs.tick
        else:
          t, mark = item # marks should be (pos, mark) pairs or just pos

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
    newmarks = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if abs(item - t) > tolerance:
          newmarks.append(item)
      else:
        pos, mark = item # marks should be (pos, mark) pairs or just pos
        if abs(pos - t) > tolerance:
          newmarks.append(item)
    self.marks = newmarks

  def wipe(self, low, high):
    newmarks = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if not low <= item < high:
          newmarks.append(item)
      else:
        pos, mark = item # marks should be (pos, mark) pairs or just pos
        if not low <= pos < high:
          newmarks.append(item)
    self.marks = newmarks

  def keep(self, low, high):
    newmarks = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if low <= item < high:
          newmarks.append(item)
      else:
        pos, mark = item # marks should be (pos, mark) pairs or just pos
        if low <= pos < high:
          newmarks.append(item)
    self.marks = newmarks

  def add(self, t, mark, angle=0., dx=0., dy=0.):
    if not isinstance(mark, basestring):
      mark = trans.transform(lambda x, y: (dx + math.cos(angle)*x - math.sin(angle)*y,
                                           dy + math.sin(angle)*x + math.cos(angle)*y), mark)
    self.marks.append((t, mark))

  def _markorder(self, a, b):
    if isinstance(a, (int, long, float)):
      posa, marka = a, None
    else:
      posa, marka = a # marks should be (pos, mark) pairs or just pos
    if isinstance(b, (int, long, float)):
      posb, markb = b, None
    else:
      posb, markb = b # marks should be (pos, mark) pairs or just pos

    if marka is None and markb is not None: return 1
    if marka is not None and markb is None: return -1
    return cmp(posa, posb)

  def sort(self, order=None):
    if order is None: order = lambda a, b: self._markorder(a, b)
    self.marks.sort(order)

  def mark(self, t, tolerance=None):
    if tolerance is None: tolerance = trans.epsilon * abs(self.high - self.low)

    candidates = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if abs(item - t) < tolerance:
          candidates.append(item)
      else:
        pos, mark = item # marks should be (pos, mark) pairs or just pos
        if abs(pos - t) < tolerance:
          candidates.append(item)

    candidates.sort(lambda a, b: self._markorder(a, b))
    try:
      return candidates[0][1]
    except:
      return None

  ### convenience functions for adding forward and backward arrows
  def farrow(self, mark=True):
    self.drop(self.high)
    if mark is False or mark is None: pass
    elif mark is True:
      self.add(self.high, glyphs.farrowhead)
      self.marks[-1][1]["fill"] = self["stroke"]
    else:
      self.add(self.high, mark)
      self.marks[-1][1]["fill"] = self["stroke"]

  def barrow(self, mark=True):
    self.drop(self.low)
    if mark is False or mark is None: pass
    elif mark is True:
      self.add(self.low, glyphs.barrowhead)
      self.marks[-1][1]["fill"] = self["stroke"]
    else:
      self.add(self.low, mark, angle=math.pi)
      self.marks[-1][1]["fill"] = self["stroke"]

  def tick(self, t, mark=None):
    if mark is None:
      self.add(t, glyphs.tick)
      self.marks[-1][1]["stroke"] = self["stroke"]
    elif isinstance(mark, basestring):
      self.add(t, glyphs.tick)
      self.marks[-1][1]["stroke"] = self["stroke"]
      self.add(t, mark)
    else:
      self.add(t, mark)
      self.marks[-1][1]["stroke"] = self["stroke"]

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
      output = lambda t: eval(compiled, math.__dict__, {"t": float(t)})
      output.func_name = "t -> %s" % expr
      return output

    # 1 real -> 1 real
    elif "x" in compiled.co_names:
      output = lambda t: (t, eval(compiled, math.__dict__, {"x": float(t)}))
      output.func_name = "x -> %s" % expr
      return output

    # real (a complex number restricted to the real axis) -> complex
    elif "z" in compiled.co_names:
      split = lambda z: (z.real, z.imag)
      output = lambda z: split(eval(compiled, cmath.__dict__, {"z": complex(z)}))
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

def ticks(low, high, maximum=None, exactly=None, format=unicode_number, tolerance=None):
  if exactly is not None:
    output = []
    t = low
    for i in xrange(exactly):
      output.append((t, glyphs.tick))
      output.append((t, format(t)))
      t += (high - low)/(exactly - 1.)
    return output

  if maximum is None: maximum = 10
  if tolerance is None: tolerance = trans.epsilon * abs(high - low)

  counter = 0
  granularity = 10**math.ceil(math.log10(max(abs(low), abs(high))))
  lowN = math.ceil(1.*low / granularity)
  highN = math.floor(1.*high / granularity)

  def subdivide(counter, granularity, low, high, lowN, highN):
    countermod3 = counter % 3
    if countermod3 == 0: granularity *= 0.5
    elif countermod3 == 1: granularity *= 0.4
    elif countermod3 == 2: granularity *= 0.5
    counter += 1
    lowN = math.ceil(1.*low / granularity)
    highN = math.floor(1.*high / granularity)
    return counter, granularity, low, high, lowN, highN
    
  while lowN > highN:
    counter, granularity, low, high, lowN, highN = \
             subdivide(counter, granularity, low, high, lowN, highN)

  last_granularity = granularity
  last_trial = None

  while True:
    trial = []
    for n in range(int(lowN), int(highN)+1):
      t = n * granularity
      trial.append(t)

    if len(trial) > maximum:
      if last_trial is None:
        v1, v2 = low, high
        return [(v1, format(v1)), (v2, format(v2))]

      else:
        if counter % 3 == 2:
          counter, granularity, low, high, lowN, highN = \
                   subdivide(counter, granularity, low, high, lowN, highN)
        trial = []
        for n in range(int(lowN), int(highN)+1):
          t = n * granularity
          trial.append(t)

        output = []
        for t in last_trial:
          output.append((t, glyphs.tick))
          output.append((t, format(t)))
        for t in trial:
          if t not in last_trial:
            output.append((t, glyphs.minitick))
        return output

    last_granularity = granularity
    last_trial = trial

    counter, granularity, low, high, lowN, highN = \
             subdivide(counter, granularity, low, high, lowN, highN)

def logticks(low, high, base=10., maximum=None, format=unicode_number, tolerance=None):
  if maximum is None: maximum = 10
  if tolerance is None: tolerance = trans.epsilon * abs(high - low)

  lowN = math.floor(math.log(low, base))
  highN = math.ceil(math.log(high, base))

  trial = []
  for n in range(int(lowN), int(highN)+1):
    t = base**n
    if low - tolerance <= t < high + tolerance:
      trial.append(t)

  output = []

  # don't need every decade if the ticks cover too many
  for i in range(1, len(trial)):
    subtrial = trial[::i]
    if len(subtrial) <= maximum:
      for t in trial:
        output.append((t, glyphs.tick))
        if t in subtrial:
          output.append((t, format(t)))
      break

  if len(trial) <= 2:
    output2 = ticks(low, high, maximum=maximum, format=format, tolerance=tolerance)

    lowest = min(output2)
    for t, mark in output:
      if t < lowest: output2.append((t, mark))

    return output2

  return output

# def compute_logticks(self, base, N, format):
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
