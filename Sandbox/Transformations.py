import math

if 'reversed' not in __builtins__.__dict__:   # reversed() was new in Python 2.4
    def reversed(data):
        for index in range(len(data)-1, -1, -1):
            yield data[index]

def simplify(x):
    """Convert a float to an int, if possible."""
    if x // 1 == x:
        return int(x)
    else:
        return float(x)

class _readonly:
    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise AttributeError, "cannot set read-only attribute '%s'" % name
        else:
            raise AttributeError, "'%s' object has no attribute '%s'" \
                                  % (self.__class__.__name__, name)

class Matrix(_readonly, tuple):
    """Matrix(a,b,c,d,e,f) or Matrix(tuple)"""

    def __new__(cls, *args):
        if len(args) == 6:
            return tuple.__new__(cls, args)
        elif len(args) == 1 and isinstance(args[0], tuple):
            return Matrix(*args[0])
        else:
            raise TypeError, 'Invalid arguments to Matrix(): %s' % repr(args)

    a = property(lambda self: self[0])
    b = property(lambda self: self[1])
    c = property(lambda self: self[2])
    d = property(lambda self: self[3])
    e = property(lambda self: self[4])
    f = property(lambda self: self[5])

    def __call__(self, *args):
        """M(x,y) or M((x,y)): applies the matrix M to the point (x,y)"""
        if len(args) == 1:
            args = args[0]
        if len(args) != 2:
            raise TypeError, 'Invalid arguments to Matrix object.'
        return (self[0]*args[0] + self[2]*args[1] + self[4],
                self[1]*args[0] + self[3]*args[1] + self[5])

    def __repr__(self):
        return "Matrix(%s, %s, %s, %s, %s, %s)" \
              % (simplify(self[0]), simplify(self[1]), simplify(self[2]),
                 simplify(self[3]), simplify(self[4]), simplify(self[5]))

    def __str__(self):
        return "matrix(%s, %s, %s, %s, %s, %s)" \
              % (simplify(self[0]), simplify(self[1]), simplify(self[2]),
                 simplify(self[3]), simplify(self[4]), simplify(self[5]))

    def __mul__(self, other):
        """Return the product (composition) of two matrices."""
        if not isinstance(other, Matrix):
            return NotImplemented
        if self == Identity:
            return other
        elif other == Identity:
            return self
        else:
            return Matrix(self[0]*other[0] + self[2]*other[1],
                          self[1]*other[0] + self[3]*other[1],
                          self[0]*other[2] + self[2]*other[3],
                          self[1]*other[2] + self[3]*other[3],
                          self[0]*other[4] + self[2]*other[5] + self[4],
                          self[1]*other[4] + self[3]*other[5] + self[5])

    def inverse(self):
        """Return the inverse of a matrix."""
        det = float(self[0]*self[3] - self[1]*self[2])
        if det == 0:
            raise ZeroDivisionError, 'Matrix is not invertible.'
        return Matrix(self[3]/det, -self[1]/det, -self[2]/det, self[0]/det,
                      self[2]*self[5] - self[3]*self[4],
                      self[1]*self[4] - self[0]*self[5])

    def simplify(self):
        """Convert the Matrix to a Translate, Scale, Rotate, SkewX, or SkewY."""
        if self[:4] == (1,0,0,1):
            return Translate(self[4], self[5])
        elif self[1] == self[2] == self[4] == self[5] == 0:
            return Scale(self[0], self[3])
        elif self[0]*self[2]+self[1]*self[3] == 0 \
             and self[0]**2+self[1]**2 == self[2]**2+self[3]**2 == 1:
            return Rotate(math.degrees(math.atan2(self[1], self[0])),
                          (self[4]+self[5]*self[2]/(1-self[0]))/2.,
                          (self[5]+self[4]*self[1]/(1-self[3]))/2.)
        elif self[1] == self[4] == self[5] == 0 and self[0] == self[3] == 1:
            return SkewX(math.degrees(math.atan(self[2])))
        elif self[2] == self[4] == self[5] == 0 and self[0] == self[3] == 1:
            return SkewY(math.degrees(math.atan(self[1])))
        else:
            return self


Identity = Matrix(1,0,0,1,0,0)


class Translate(Matrix):
    """Translate(tx, ty=0)"""

    def __new__(cls, tx, ty = 0):
        return Matrix.__new__(cls, 1, 0, 0, 1, simplify(tx), simplify(ty))

    tx = property(lambda self: self[4])
    ty = property(lambda self: self[5])

    def __repr__(self):
        if self.ty == 0:
            return "Translate(%s)" % self.tx
        else:
            return "Translate(%s, %s)" % (self.tx, self.ty)

    def __str__(self):
        if self.ty == 0:
            return "translate(%s)" % self.tx
        else:
            return "translate(%s, %s)" % (self.tx, self.ty)

    def __mul__(self, other):
        if isinstance(other, Translate):
            return Translate(self.tx + other.tx, self.ty + other.ty)
        else:
            return Matrix.__mul__(self, other)

    def inverse(self):
        return Translate(-self.tx, -self.ty)


class Scale(Matrix):
    """Scale(sx[,sy])"""

    def __new__(cls, sx, sy = None):
        if sy is None:
            sy = sx
        return Matrix.__new__(cls, simplify(sx), 0, 0, simplify(sy), 0, 0)

    sx = property(lambda self: self[0])
    sy = property(lambda self: self[3])

    def __repr__(self):
        if self.sx == self.sy:
            return "Scale(%s)" % self.sx
        else:
            return "Scale(%s, %s)" % (self.sx, self.sy)

    def __mul__(self, other):
        if isinstance(other, Scale):
            return Scale(self.sx * other.sx, self.sy * other.sy)
        else:
            return Matrix.__mul__(self, other)

    def __str__(self):
        if self.sx == self.sy:
            return "scale(%s)" % self.sx
        else:
            return "scale(%s, %s)" % (self.sx, self.sy)

    def inverse(self):
        """Return the inverse Scale."""
        return Scale(1./self.sx, 1./self.sy)


flipX = Scale(-1, 1)
flipY = Scale(1, -1)


class Rotate(Matrix):
    """Rotate(angle, cx=0, cy=0)"""

    def __new__(cls, angle, cx=0, cy=0):
        c = math.cos(math.radians(angle))
        s = math.sin(math.radians(angle))
        self = Matrix.__new__(cls, simplify(c), simplify(s), simplify(-s),
                              simplify(c), simplify(cx*(1-c)+cy*s),
                              simplify(-cx*s+cy*(1-c)))
        self.__dict__['angle'] = angle
        return self

    cx = property(lambda self: simplify((self[4]+self[5]*self[2]/(1-self[0]))/2.))
    cy = property(lambda self: simplify((self[5]+self[4]*self[1]/(1-self[3]))/2.))

    def __mul__(self, other):
        if isinstance(other, Rotate):
            if self.angle == 0:
                return other
            if other.angle == 0:
                return self
            if self.cx == other.cx and self.cy == other.cy:
                return Rotate(self.angle + other.angle, self.cx, self.cy)
            else:
                continue
        else:
            return Matrix.__mul__(self, other)

    def __repr__(self):
        if self[4] == self[5] == 0:
            return "Rotate(%s)" % self.angle
        else:
            return "Rotate(%s, %s, %s)" % (self.angle, self.cx, self.cy)

    def __str__(self):
        if self[4] == self[5] == 0:
            return "rotate(%s)" % simplify(float(self.angle))
        else:
            return "rotate(%s, %s, %s)" \
                   % (simplify(float(self.angle), self.cx, self.cy))

    def inverse(self):
        """Return the inverse Rotation."""
        return Rotate(-self.angle, self.cx, self.cy)


class SkewX(Matrix):
    """SkewX(angle)"""

    def __new__(cls, angle):
        t = simplify(math.tan(math.radians(angle)))
        self = Matrix.__new__(cls, 1, 0, t, 1, 0, 0)
        self.__dict__['angle'] = angle
        return self

    def __repr__(self):
        return "SkewX(%s)" % self.angle

    def __str__(self):
        return "skewX(%s)" % simplify(float(self.angle))

    def __mul__(self, other):
        if isinstance(other, SkewX):
            return SkewX(self.angle + other.angle)
        else:
            return Matrix.__mul__(self, other)

    def inverse(self):
        """Return the inverse SkewX."""
        return SkewX(-self.angle)


class SkewY(Matrix):
    """SkewY(angle)"""

    def __new__(cls, angle):
        t = simplify(math.tan(math.radians(angle)))
        self = Matrix.__new__(cls, 1, t, 0, 1, 0, 0)
        self.__dict__['angle'] = angle
        return self

    def __repr__(self):
        return "SkewY(%s)" % self.angle

    def __str__(self):
        return "skewY(%s)" % simplify(float(self.angle))

    def __mul__(self, other):
        if isinstance(other, SkewY):
            return SkewY(self.angle + other.angle)
        else:
            return Matrix.__mul__(self, other)

    def inverse(self):
        """Return the inverse SkewY."""
        return SkewY(-self.angle)


class TransformList(_readonly, list):
    """TransformList(*args) or TransformList(list) or TransformList(string)

    A list of coordinate transformations. Use as data for the transform attribute.

    Note:  The transformation defined by a TransformList is the matrix product of
    its items.  Because matrices compose from right to left, the transformations
    are applied in order from last to first.
    """
    def __init__(self, *args):
        if len(args) > 1:
            list.__init__(self, args)
        elif isinstance(args[0], (list,tuple)):
            list.__init__(self, args[0])
        elif isinstance(args[0], basestring):
            list.__init__(self, TransformList.parse(args[0]))
        else:
            raise TypeError, 'Invalid argument to TransformList(): %s' % args[0]

    def consolidate(self):
        """Multiply the matrices in the list and return the result"""
        output = Identity
        for M in self:
            output *= M
        return output

    def inverse(self):
        """Invert the transformations and reverse their order."""
        return TransformList([M.inverse() for M in reversed(self)])

    def __call__(self, *args):
        """T(x,y) or T((x,y)): applies the TransformList T to the point (x,y)"""
        if len(args) == 1:
            args = args[0]
        if len(args) != 2:
            raise TypeError, 'Invalid arguments to Matrix object.'
        for M in reversed(self):
            args = M(args)
        return args

    def __repr__(self):
        return "TransformList(%s)" % list(self)

    def __str__(self):
        return ' '.join([str(M) for M in self])

    # The next function requres the Parser class from Parser.py
    def parse(string):
        """Convert an SVG string to a TransformList."""
        p = Parser(string)
        output = []
        p.parse_whitespace()
        transform_args = {'matrix': [6], 'translate': [1,2], 'scale': [1,2],
                          'rotate': [1, 3], 'skewX': [1], 'skewY': [1]}
        transform_commands = {'matrix': 'Matrix', 'translate': 'Translate',
                             'scale': 'Scale', 'rotate': 'Rotate',
                             'skewX': 'SkewX', 'skewY': 'SkewY'}
        while p:
            transform = p.parse_word()
            p.parse_whitespace()
            if transform not in transform_commands:
                raise TypeError, 'Invalid transform command: %s' % transform
            if p.pop() != '(':
                raise SyntaxError, 'Invalid transform syntax'
            args = []
            num = p.parse_number()
            while num is not None:
                args.append(num)
                p.parse_comma()
                num = p.parse_number()
            if len(args) not in transform_args[transform]:
                raise TypeError, 'Invalid arguments to %s: %s' % (transform, args)
            output.append(eval(transform_commands[transform] + str(tuple(args))))
            if p.pop() != ')':
                raise SyntaxError, 'Invalid transform syntax'
            p.parse_comma()
        return output
    parse = staticmethod(parse)
