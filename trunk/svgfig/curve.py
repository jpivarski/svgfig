import math, cmath, copy, re
import svg, trans, pathdata, glyphs

##############################################################################

class Curve(svg.SVG):
  attrib = {"stroke": "black", "fill": "none"}
  smooth = False
  marks = []
  random_sampling = True
  random_seed = 12345
  recursion_limit = 15
  linearity_limit = 0.05
  discontinuity_limit = 5.
  text_offsetx = 0.
  text_offsety = -2.5
  text_attrib = {}

  def __init__(self, expr, low, high, **kwds):
    self.tag = None
    self.children = []
    self.trans = []

    self.f, self.low, self.high = svg.cannonical_parametric(expr), low, high

    for var in "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit", "text_offsetx", "text_offsety":
      if var in kwds:
        exec("self.%s = kwds[\"%s\"]" % (var, var))
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
      if kwds["farrow"] is True:
        self.add(self.high, glyphs.farrowhead)
        self.marks[-1][1]["fill"] = self["stroke"]
      else:
        self.add(self.high, kwds["farrow"])
        self.marks[-1][1]["fill"] = self["stroke"]
      del kwds["farrow"]

    if "barrow" in kwds:
      if kwds["barrow"] is True:
        self.add(self.low, glyphs.barrowhead)
        self.marks[-1][1]["fill"] = self["stroke"]
      else:
        self.add(self.low, kwds["barrow"])
        self.marks[-1][1]["fill"] = self["stroke"]
      del kwds["barrow"]

    # now add the rest of the attributes
    self.attrib.update(kwds)

  def __getattr__(self, name): return self.__dict__[name]
  def __setattr__(self, name, value): self.__dict__[name] = value

  def __repr__(self):
    specials = []
    for var in "attrib", "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit":
      if eval("self.%s" % var) != eval("self.__class__.%s" % var):
        specials.append("%s=%s" % (var, eval("self.%s" % var)))
    specials = " ".join(specials)
    if specials != "": specials = " " + specials

    trans = ""
    lentrans = len(self.trans)
    if lentrans > 0: trans = " (%d trans)" % lentrans

    marks = ""
    lenmarks = len(self.marks)
    if lenmarks == 1: marks = " (1 mark)"
    elif lenmarks > 1: marks = " (%d marks)" % lenmarks

    return "<Curve %s from %g to %g%s%s%s>" % (self.f, self.low, self.high, specials, trans, marks)

  def transform(self, expr): self.trans.append(svg.cannonical_transformation(expr))

  def __call__(self, t, transformed=True):
    x, y = self.f(t)
    if transformed:
      for trans in self.trans:
        x, y = trans(x, y)
    return x, y

  def angle(self, t, transformed=True):
    x, y = self(t, transformed)

    tprime = t + trans.epsilon * abs(self.high - self.low)
    xprime, yprime = self(tprime, transformed)

    delx, dely = xprime - x, yprime - y
    return math.atan2(dely, delx)

  def d(self):
    import _curve
    data = _curve.curve(self.f, self.trans, self.low, self.high,
                        self.random_sampling, self.random_seed, self.recursion_limit, self.linearity_limit, self.discontinuity_limit)

    segments = []
    last_d = None
    for d in data:
      if d is not None:
        if last_d is None: segments.append([])
        segments[-1].append(d)
      last_d = d

    output = []
    if self.smooth:
      for seg in segments:
        output.extend(pathdata.smooth(seg))
    else:
      for seg in segments:
        output.extend(pathdata.poly(seg))

    return output

  def svg(self):
    if self.marks == []:
      return svg.SVG("path", self.d(), **self.attrib)
    else:
      output = svg.SVG("g", svg.SVG("path", self.d(), **self.attrib))

      lowX, lowY = self(self.low)
      highX, highY = self(self.high)

      items = copy.copy(self.marks)
      items.sort()
      for item in items:
        if isinstance(item, (int, long, float)):
          t, mark = item, glyphs.tick
        else:
          t, mark = item # marks should be (pos, mark) pairs or just pos

        X, Y = self(t)
        if self.low <= t <= self.high or \
           math.sqrt((X - lowX)**2 + (Y - lowY)**2) < trans.epsilon or \
           math.sqrt((X - highX)**2 + (Y - highY)**2) < trans.epsilon:

          angle = self.angle(t)

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

  def bbox(self): return self.svg().bbox()

  def __eq__(self, other):
    if id(self) == id(other): return True
    if not isinstance(other, Curve): return False
    for var in "f", "low", "high", "attrib", "smooth", "marks", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit", "text_offsetx", "text_offsety", "text_attrib", "trans":
      if eval("self.%s" % var) != eval("other.%s" % var): return False
    return True
  
  def __deepcopy__(self, memo={}):
    result = self.__class__(self.f, self.low, self.high)
    for var in "smooth", "random_sampling", "random_seed", "recursion_limit", "linearity_limit", "discontinuity_limit", "text_offsetx", "text_offsety":
      result.__dict__[var] = eval("self.%s" % var)
    for var in "attrib", "marks", "text_attrib":
      result.__dict__[var] = copy.deepcopy(eval("self.%s" % var))
    result.trans = copy.copy(self.trans)

    memo[id(self)] = result
    return result

  def _matches(self, matching, mark):
    if matching is None: return True

    try:
      if isinstance(mark, matching): return True
    except TypeError: pass
    
    if isinstance(mark, svg.SVG) and isinstance(matching, basestring):
      if re.search(matching, mark.tag): return True
      if "repr" in mark.__dict__ and re.search(matching, mark.repr): return True

    if isinstance(matching, basestring) and isinstance(mark, basestring):
      if re.search(matching, mark): return True

    return matching == mark

  def wipe(self, low=None, high=None, matching=None):
    if low is None: low = self.low
    if high is None: high = self.high

    newmarks = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if self._matches(matching, item):
          if not low <= item <= high: newmarks.append(item)
        else:
          newmarks.append(item)

      else:
        pos, mark = item # marks should be (pos, mark) pairs or just pos
        if self._matches(matching, mark):
          if not low <= pos <= high: newmarks.append(item)
        else:
          newmarks.append(item)

    self.marks = newmarks

  def keep(self, low=None, high=None, matching=None):
    if low is None: low = self.low
    if high is None: high = self.high

    newmarks = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if self._matches(matching, item):
          if low <= item <= high: newmarks.append(item)

      else:
        pos, mark = item # marks should be (pos, mark) pairs or just pos
        if self._matches(matching, mark):
          if low <= pos <= high: newmarks.append(item)

    self.marks = newmarks

  def drop(self, t, tolerance=None, matching=None):
    if tolerance is None: tolerance = trans.epsilon * abs(self.high - self.low)
    self.wipe(t - tolerance, t + tolerance, matching=matching)

  def clean(self, keep="arrowhead", drop="tick", clearance=1.):
    hold = {}
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if self._matches(keep, item):
          hold[item] = None

      else:
        pos, mark = item # marks should be (pos, mark) pairs or just pos
        if self._matches(keep, mark):
          hold[pos] = mark
    
    newmarks = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        pos, mark = item, None
      else:
        pos, mark = item

      okay = True
      if self._matches(drop, mark):
        for kpos, kmark in hold.items():
          x1, y1 = self(pos)
          x2, y2 = self(kpos)
          if math.sqrt((x1 - x2)**2 + (y1 - y2)**2) < clearance: okay = False

      if okay: newmarks.append(item)

    for kpos, kmark in hold.items():
      if kmark is None:
        newmarks.append(kpos)
      else:
        newmarks.append((kpos, kmark))

    self.marks = newmarks

  def add(self, t, mark, angle=0., dx=0., dy=0.):
    if not isinstance(mark, basestring):
      mark = trans.transform(lambda x, y: (dx + math.cos(angle)*x - math.sin(angle)*y,
                                           dy + math.sin(angle)*x + math.cos(angle)*y), mark)
    self.marks.append((t, mark))

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

  def closest(self, t, tolerance=None, matching=None):
    if tolerance is None: tolerance = trans.epsilon * abs(self.high - self.low)

    candidates = []
    for item in self.marks:
      if isinstance(item, (int, long, float)):
        if self._matches(matching, item) and abs(t - item) < tolerance:
          candidates.append(item)
      else:
        pos, mark = item
        if self._matches(matching, mark) and abs(t - pos) < tolerance:
          candidates.append(item)

    def closecmp(a, b):
      if isinstance(a, (int, long, float)):
        posa, marka = a, None
      else:
        posa, marka = a # marks should be (pos, mark) pairs or just pos
      if isinstance(b, (int, long, float)):
        posb, markb = b, None
      else:
        posb, markb = b # marks should be (pos, mark) pairs or just pos
      return cmp(abs(posa - t), abs(posb - t))

    candidates.sort(closecmp)
    return candidates

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

def ticks(low, high, maximum=None, exactly=None, format=unicode_number):
  if exactly is not None:
    output = []
    t = low
    for i in xrange(exactly):
      output.append((t, glyphs.tick))
      output.append((t, format(t, scale=abs(high - low))))
      t += (high - low)/(exactly - 1.)
    return output

  if maximum is None: maximum = 10

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
        return [(v1, format(v1, scale=abs(high - low))), (v2, format(v2, scale=abs(high - low)))]

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
          output.append((t, format(t, scale=abs(high - low))))
        for t in trial:
          if t not in last_trial:
            output.append((t, glyphs.minitick))
        return output

    last_granularity = granularity
    last_trial = trial

    counter, granularity, low, high, lowN, highN = \
             subdivide(counter, granularity, low, high, lowN, highN)

def logticks(low, high, base=10., maximum=None, format=unicode_number):
  if maximum is None: maximum = 10

  lowN = math.floor(math.log(low, base))
  highN = math.ceil(math.log(high, base))

  trial = []
  for n in range(int(lowN), int(highN)+1):
    trial.append(base**n)

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
    output2 = ticks(low, high, maximum=maximum, format=format)

    lowest = min(output2)
    for t, mark in output:
      if t < lowest: output2.append((t, mark))

    return output2

  for n in range(int(lowN), int(highN)+1):
    t = base**n
    for m in range(2, int(math.ceil(base))):
      output.append((m * t, glyphs.minitick))
        
  return output
