# Latest source #

[Source tree](http://svgfig.googlecode.com/svn/trunk/)

After releasing SVGFig, we noticed that the structure could be improved, and the benefits that could be gained outweighed the loss of backward compatibility for scripts.  However, I know that it is very important to be able to re-run old scripts, so we split the source tree into two branches, [svgfig](http://code.google.com/p/svgfig/source/browse/trunk/svgfig/) for new developments and [svgfig-1.x](http://code.google.com/p/svgfig/source/browse/trunk/svgfig-1.x) for bug-fixes to the old structure.

I've just prepared the a new 2.x release, called [2.0.0alpha2](http://svgfig.googlecode.com/files/svgfig-2.0.0alpha2.tgz) to make it absolutely clear that it is neither complete nor guaranteed to be bug-free (but better than alpha1).  However, if you're curious and/or adventurous, [take a look](Version2Announcement.md) and let me know what you think.  If you have opinions about how it should look or work in the end, now would be an excellent time to join the development team, all you need is a [Google/GMail account](https://www.google.com/accounts/NewAccount) (and [send me an e-mail](mailto:jpivarski@gmail.com)).

The existing wiki documentation refers to 1.x behavior, which is different than the planned behavior for 2.x.  New wiki pages will be made for 2.x (starting with "V2" and having label "Version2", rather than "Version1").

If you find issues in 1.x that you think might be bugs, please inform me through the [Issues tab](http://code.google.com/p/svgfig/issues/list).

# Fixed Releases #

[Click here](http://code.google.com/p/svgfig/downloads/list) for a searchable list of all downloads.

## svgfig-1.1.6 ##

[svgfig-1.1.6.tgz](http://svgfig.googlecode.com/files/svgfig-1.1.6.tgz) [svgfig-1.1.6.zip](http://svgfig.googlecode.com/files/svgfig-1.1.6.zip)

  * Fixed two typos and a division-by-zero.

## svgfig-1.1.5 ##

[svgfig-1.1.5.tgz](http://svgfig.googlecode.com/files/svgfig-1.1.5.tgz) [svgfig-1.1.5.zip](http://svgfig.googlecode.com/files/svgfig-1.1.5.zip)

  * [Fixed issue 1](http://code.google.com/p/svgfig/issues/detail?id=1) ("svgfig.Text() renders list representation of characters instead of string")

## svgfig-1.1.4 ##

[svgfig-1.1.4.tgz](http://svgfig.googlecode.com/files/svgfig-1.1.4.tgz) [svgfig-1.1.4.zip](http://svgfig.googlecode.com/files/svgfig-1.1.4.zip)

  * Fixed [load](Defload.md) so that it works on Windows
  * Prepended globals with underscores so they are not loaded by `import *`
  * General code clean-up

## svgfig-1.1.3 ##

[svgfig-1.1.3.tgz](http://svgfig.googlecode.com/files/svgfig-1.1.3.tgz)

  * more minor bugs that turned up as Jim Belk learned the system
  * now SVG attributes can be lists and dictionaries: `svg["style"]["stroke-linewidth"] = 1` etc

## svgfig-1.1.2 ##

[svgfig-1.1.2.tgz](http://svgfig.googlecode.com/files/svgfig-1.1.2.tgz)

  * minor bugs that I discovered and fixed as I wrote the first two examples in the [Example Gallery](ExampleGallery.md)
  * these will probably keep coming as I make more examples...

## svgfig-1.1.1 ##

[svgfig-1.1.1.tgz](http://svgfig.googlecode.com/files/svgfig-1.1.1.tgz)

  * minor bugs that I discovered and fixed as I wrote the [Introduction](Introduction.md).

## svgfig-1.1.0 ##

[svgfig-1.1.0.tgz](http://svgfig.googlecode.com/files/svgfig-1.1.0.tgz)

  * added arrows to [Line](ClassLine.md) and [LineGlobal](ClassLineGlobal.md)
  * added Python documentation strings to everything (copied from [Reference](Reference.md)).

## svgfig-1.0.0 ##

[svgfig-1.0.0.tgz](http://svgfig.googlecode.com/files/svgfig-1.0.0.tgz)

  * first release