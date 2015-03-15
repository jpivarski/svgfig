_(This page applies only to the 1.x branch of SVGFig.)_

# How to install #

  1. Download the latest version of SVGFig from the [Downloads tab](http://code.google.com/p/svgfig/downloads/list).
  1. Unpack the archive (your browser might do this automatically).  In Unix/Linux, the command is
```
tar -xzvf svgfig-x.y.z.tgz
```
  1. Run the installer script, =setup.py=, with Python.
```
cd svgfig/
python setup.py install
```
  1. To install in your home directory (e.g. if you don't have superuser privileges)
```
python setup.py install --home=~
```
  1. Now you should be able to load the svgfig library in Python:
```
Python 2.4.3 (#2, Oct  6 2006, 07:52:30) 
[GCC 4.0.3 (Ubuntu 4.0.3-1ubuntu5)] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import svgfig
```

## Known problems (and solutions) ##

None yet.