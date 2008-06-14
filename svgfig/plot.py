import defaults, svg, glyphs, trans, curve

class Fig(trans.Delay):
  xmin = None
  xmax = None
  ymin = None
  ymax = None
  x = 10.
  y = 10.
  width = 80.
  height = 80.
  clip = False

  def __init__(self, *args, **kwds):
    trans.Delay.__init__(self, *args, **kwds)

    for var in "x", "y", "width", "height", "clip", "xmin", "xmax", "ymin", "ymax":
      if var in kwds:
        self.__dict__[var] = kwds[var]
        del kwds[var]

    if len(kwds) > 0:
      raise TypeError, "Unrecognized keywords " + ", ".join(map(lambda word: "\"%s\"" % word, kwds.keys()))

  def __repr__(self):
    ren = "ren"
    if len(self.children) == 1: ren = ""
    clip = ""
    if self.clip: clip = " clip"
    return "<Fig (%d child%s) xmin=%s xmax=%s ymin=%s ymax=%s%s>" % (len(self.children), ren, self.xmin, self.xmax, self.ymin, self.ymax, clip)

  def bbox(self): return defaults.BBox(self.x, self.x + self.width, self.y, self.y + self.height)

  def fit(self):
    bbox = defaults.BBox(None, None, None, None)
    for child in self.children:
      bbox += child.bbox()

    if self.xmin is not None: bbox.xmin = self.xmin
    if self.xmax is not None: bbox.xmax = self.xmax
    if self.ymin is not None: bbox.ymin = self.ymin
    if self.ymax is not None: bbox.ymax = self.ymax

    self.trans = [trans.window(bbox.xmin, bbox.xmax, bbox.ymin, bbox.ymax,
                               x=self.x, y=self.y, width=self.width, height=self.height,
                               minusInfinity=(self.x - 10.*self.width), flipy=True)]
    
  def svg(self):
    if self.trans == [] or \
           self.xmin != self.trans[0].xmin or self.xmax != self.trans[0].xmax or self.ymin != self.trans[0].ymin or self.ymax != self.trans[0].ymax or \
           self.x != self.trans[0].x or self.y != self.trans[0].y or self.width != self.trans[0].width or self.height != self.trans[0].height:

      if self.xmin is not None and self.xmax is not None and \
         self.ymin is not None and self.ymax is not None:
        self.trans = [trans.window(self.xmin, self.xmax, self.ymin, self.ymax,
                                   x=self.x, y=self.y, width=self.width, height=self.height,
                                   minusInfinity=(self.x - 10.*self.width), flipy=True)]
      else:
        self.fit()

    output = trans.Delay.svg(self)

    if self.clip:
      clipPath = svg.SVG("clipPath", id=svg.newid("clip-"))(svg.SVG("rect", self.x, self.y, self.width, self.height))
      output["clip-path"] = "url(#%s)" % clipPath["id"]
      return svg.SVG("g", clipPath, output)      

    return output
