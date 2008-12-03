
##
## linked boxes
##
##  i added that to svgfig - so i can make linked elements
##  its only quick hack.
##
##class Link:
##  """link elements to a url. local or http one
##
##      url                    text/Unicode string
##      attribute=value pairs  keyword list  SVG attributes
##  """
##
##  defaults = {"fill":"black", "font-size":4}
##
##  def __repr__(self):
##    return "<link %s with attributes %s>" % (repr(self.url), self.attr)
##
##  def __init__(self, url, **attr):
##    self.url = str(url)
##    attr['xlink:href'] = str(url)
##    self.attr = dict(self.defaults)
##    self.attr.update(attr)
##
##  def SVG(self, trans=None):
##    """Apply the transformation "trans" and return an SVG object."""
##
##    return SVG("a", **self.attr)


from svgfig import *

svg = canvas_outline(viewBox="0 0 200 100",width=800, height=400 )
svg.append(SVG('g',id="Bookmarks", fill="white",x=0,y=0,width=1000, height=1000))

def makeLinkBox(myurl, x, y, width, height, color):
    url = Link(url= myurl, xlink__type="simple").SVG()
    box = Rect(x, y, width+x, height+y, fill=color, fill_opacity=0.7, id=myurl).SVG()
    text = Text(x = (x+width/2), y = (y+height/1.5), d=myurl).SVG()
    url.append(box)
    url.append(text)
    svg.append(url)

makeLinkBox('http://google.com', 10, 10, 40, 15, 'blue')
makeLinkBox('http://code.google.com/p/svgfig', 50, 50, 60, 20, 'green')
makeLinkBox('http://proclos.com', 120, 70, 40, 15, 'yellow')
makeLinkBox('http://python.org', 90, 5, 70, 15, 'pink')


print svg.xml()
svg.firefox()
