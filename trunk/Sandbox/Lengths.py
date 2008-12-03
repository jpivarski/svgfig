def simplify(x):
    """Convert a float to an int, if possible."""
    if x // 1 == x:
        return int(x)
    else:
        return x

def _length_unit(name, magnitude):
    """Factory function for producing _Length classes"""
    class _Length(float):
        """
        Class for SVG lengths with units.  Possible units are:

        1px = 1 SVG user unit
        1pt = 1.25px
        1pc = 15px
        1mm = 3.543307px
        1cm = 35.43307px
        1in = 90px  (Note: Correspoding object is named "inch".)

        Objects named px, pt, pc, mm, cm, and inch are predefined.  You can create
        other length objects from these using multiplication:

        4 * pc -> SVG length object equal to "4pc"

        Length objects are immutable, and are essentially just floats that display
        diffetently.  You can convert a length object to a float using float():

        >>> float(4*pc)
        60.0

        The result is expressed in SVG user units.  You can convert to other units
        as follows:

        >>> pt(4*pc)                OR                   >>> (4*pc)/pt
        48pt                                             48.0

        Arithmetic operations performed on lengths may produce either a length or
        a float, according to the following rules:

        1. If L is a length, then so are +L, -L, and abs(L).

        2. If L and M are lengths with the same units, then L + M, L - M, and L % M
        are lengths of the same type.

        3. If L is a length and t is a number (int, long, or float), then t * L,
        L * t, and L / t are all lengths.

        4. Any other operation produces a float.

        Finally, be warned that lengths with different units are actually objects
        of different classes having the same name _Length.
        """
        __slots__ = []     # Objects of this class are entirely immutable
        def __pos__(self):
            return self
        def __neg__(self):
            return _Length(-float(self))
        def __abs__(self):
            return _Length(abs(float(self)))
        def __add__(self, other):
            if isinstance(other, _Length):
                return _Length(float(self) + float(other))
            else:
                return float(self) + other
        __radd__ = __add__
        def __sub__(self, other):
            if isinstance(other, _Length):
                return _Length(float(self) - float(other))
            else:
                return float(self) - other
        def __mul__(self, other):
            if type(other) in (int, long, float):
                return _Length(float(self) * other)
            else:
                return float(self) * float(other)
        __rmul__ = __mul__
        def __div__(self, other):
            if type(other) in (int, long, float):
                return _Length(float(self) / other)
            else:
                return float(self) / float(other)
        __truediv__ = __div__
        def __mod__(self, other):
            if isinstance(other, _Length):
                return _Length(float(self) % float(other))
            else:
                return float(self) % other
        def __divmod__(self, other):
            return (self // other, self % other)
        def __repr__(self):
            return "%s%s" % (simplify(float(self)/magnitude), name)
        __str__ = __repr__
        def __call__(self, other):
            return _Length(other)
    return _Length(magnitude)

px = _length_unit('px', 1)
pt = _length_unit('pt', 1.25)
pc = _length_unit('pc', 15)
mm = _length_unit('mm', 3.543307)
cm = _length_unit('cm', 35.43307)
inch = _length_unit('in', 90)        # Unfortunately, "in" is a Python keyword
