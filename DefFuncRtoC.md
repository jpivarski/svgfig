_(This page applies only to the 1.x branch of SVGFig.)_

# funcRtoC #

Converts a "z(t)" string to a function acceptable for
[Curve](ClassCurve.md).  Use this to draw on the Argand plane.

## Arguments ##

**funcRtoC(expr, var, globals, locals)**

| expr | _**required**_ | string in the form "z(t)" |
|:-----|:---------------|:--------------------------|
| var | _default_="t" | name of the independent variable |
| globals | _default_=None | dict of global variables used in the expression; you may want to use Python's builtin `globals()` |
| locals | _default_=None | dict of local variables |

All symbols from Python's [cmath library](http://docs.python.org/lib/module-cmath.html)
are in scope, so you can say things like "cos(t)".

Example use of globals.
```
>>> funcRtoC("c*t", globals={"c": 1+1j})
```

This does the same thing.
```
>>> c = 1+1j
>>> funcRtoC("c*t", globals=globals())
```