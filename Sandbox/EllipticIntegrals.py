import math
pi = math.pi

# test complex.h with sqrt(-1-I) == 0.455 - 1.098I
# instead of the negative of that

def RC(a,b):
    """
    Compute Carlson's integral RC(a, b).

                1  /\oo       dx
    RC(a, b) =  -  |   -----------------
                2  |          1/2
                  \/0  (x + a)   (x + b)

    The parameters a and b may be complex numbers.
    """
    A, B = a, b
    for k in range(4):
        gms = 2*(A**0.5)*(B**0.5) + B
        A, B = (A+gms)/4, (B+gms)/4
    avg0, avg = (a + 2*b)/3., (A + 2*B)/3
    s = (b - avg0)/(avg * 4**4)
    return avg**-0.5 * (1 + s*s*(0.3 + s*(1/7. + s*
                                 (0.375 + s*(9/22. + s*(159/208. + s*9/8.))))))

def RF(a,b,c):
    """
    Compute Carlson's elliptic integral RF(a, b, c).

                   1  /\oo              dx
    RF(a, b, c) =  -  |   ------------------------------
                   2  |          1/2       1/2       1/2
                     \/0  (x + a)   (x + b)   (x + c)

    The parameters a, b, and c may be complex numbers.
    """
    A, B, C = a, b, c
    for k in range(5):
        gms = (A**0.5)*(B**0.5) + (A**0.5)*(C**0.5) + (B**0.5)*(C**0.5)
        A, B, C = (A+gms)/4, (B+gms)/4, (C+gms)/4
    avg0, avg = (a+b+c)/3., (A+B+C)/3
    X = (avg0 - a)/(avg * 4**5)
    Y = (avg0 - b)/(avg * 4**5)
    Z = -X - Y
    E2, E3 = X*Y - Z*Z, X*Y*Z
    return avg**-0.5 * (1. - E2/10. + E3/14. + E2*E2/24. - E2*E3*3./44.)

def RD(a,b,c):
    """
    Compute Carlson's elliptic integral RD(a, b, c).

                   3  /\oo              dx
    RD(a, b, c) =  -  |   ------------------------------
                   2  |          1/2       1/2       3/2
                     \/0  (x + a)   (x + b)   (x + c)

    The parameters a, b, and c may be complex numbers.
    """
    A, B, C = a, b, c
    sum = 0.0
    for k in range(5):
        gms = (A**0.5)*(B**0.5) + (A**0.5)*(C**0.5) + (B**0.5)*(C**0.5)
        sum += 1 / (4**k * C**0.5 * (C+gms))
        A, B, C = (A+gms)/4, (B+gms)/4, (C+gms)/4
    avg0, avg = (a+b+3*c)/5., (A+B+3*C)/5
    X = (avg0 - a)/(avg * 4**5)
    Y = (avg0 - b)/(avg * 4**5)
    Z = (-X-Y)/3
    E2, E3, E4, E5 = X*Y-6*Z*Z, (3*X*Y-8*Z*Z)*Z, 3*(X*Y-Z*Z)*Z*Z, X*Y*Z*Z*Z
    return 3*sum + avg**-1.5/4**5 * (1 + E2*(-3/14. + E2*9/88. - E3*9/52.)
                                       + E3/6. - E4*3/22. + E5*3/26.)

def RJ(a,b,c,d):
    """
    Compute Carlson's elliptic integral RJ(a, b, c, d).

                      3  /\oo                 dx
    RJ(a, b, c, d) =  -  |   -------------------------------------
                      2  |          1/2       1/2       1/2
                        \/0  (x + a)   (x + b)   (x + c)   (x + d)

    The parameters a, b, and c may be complex numbers.
    """
    A, B, C, D = a, b, c, d
    num = (d-a)*(d-b)*(d-c)
    sum = 0.0
    for k in range(5):
        gms = (A**0.5)*(B**0.5) + (A**0.5)*(C**0.5) + (B**0.5)*(C**0.5)
        den = (D**0.5 + A**0.5)*(D**0.5 + B**0.5)*(D**0.5 + C**0.5)
        sum += RC(1, 1 + num/(den*den*64**k)) / (den * 4**k)
        A, B, C, D = (A+gms)/4, (B+gms)/4, (C+gms)/4, (D+gms)/4
    avg0, avg = (a+b+c+2*d)/5., (A+B+C+2*D)/5
    X, Y, Z = (avg0-a)/(avg*4**5), (avg0-b)/(avg*4**5), (avg0-c)/(avg*4**5)
    P = (-X-Y-Z)/2
    E2, E5 = X*Y + X*Z + Y*Z - 3*P*P, X*Y*Z*P*P
    E3, E4 = X*Y*Z + 2*E2*P + 4*P*P*P, (2*X*Y*Z + E2*P + 3*P*P*P)*P
    return 6*sum + avg**-1.5/4**5 * (1 + E2*(-3/14. + E2*9/88. - E3*9/52.)
                                       + E3/6. - E4*3/22. + E5*3/26.)

def EllipticF(phi, m):
    """
    Compute Legendre's elliptic integral F(phi | m)


                  /\phi      dx
    F(phi | m) =  |    ---------------
                  |      _____________
                 \/0   \/1 - m sin^2 x

    The parameters phi and m must be real numbers.
    """
    if phi == 0:
        return 0
    if phi < 0 or phi > pi/2:
        return EllipticF(phi % (pi/2), m) + (phi // (pi/2))*EllipticF(pi/2, m)
    c = math.sin(phi)**-2
    return RF(c-1, c-m, c)


def EllipticE(phi, m):
    """
    Compute Legendre's elliptic integral E(phi | m)

                  /\phi  _____________
    E(phi | m) =  |    \/1 - m sin^2 x dx
                 \/0

    The parameters phi and m must be real numbers.
    """
    if phi == 0:
        return 0
    if phi < 0 or phi > pi/2:
        return EllipticE(phi % (pi/2), m) + (phi // (pi/2))*EllipticE(pi/2, m)
    c = math.sin(phi)**-2
    return RF(c-1, c-m, c) - (m/3.)*RD(c-1, c-m, c)


def EllipticPi(n, phi, m):
    """
    Compute Legendre's elliptic intgeral Pi(n ; phi | m)

                       /\phi              dx
    Pi(n ; phi | m) =  |    -------------------------------
                       |                      _____________
                      \/0   (1 - n sin^2 x) \/1 - m sin^2 x

    The parameters n, phi, and m must be real numbers.
    """
    if phi == 0:
        return 0
    if phi < 0 or phi > pi/2:
        return EllipticPi(n, phi%(pi/2), m) + (phi//(pi/2))*EllipticPi(n, pi/2, m)
    c = math.sin(phi)**-2
    return RF(c-1, c-m, c) - (n/3.)*RJ(c-1, c-m, c, c+n)


def EllipseLength(rx, ry, phi0, phi1):
    """
    Compute arclength along an ellipse.

    Ellipselength(rx, ry, phi1, phi2):
    Returns the arclength of (x, y) = (rx cos t, ry sin t) for phi1 <= t <= phi2.
    """
    m = (ry**2 - rx**2)/ry**2.
    return ry * (EllipticE(phi1, m) - EllipticE(phi0, m))


def InvEllipseLength(rx, ry, phi0, value):
    """
    Compute the value of phi1 for which EllipseLength(rx,ry,phi0,phi1) == value.
    """
    m = (ry**2 - rx**2)/ry**2.
    value = (value + EllipticE(phi0, m)) / ry
    complete = EllipticE(pi/2, m)
    intpart = value // complete
    value = value % complete
    guess = (value / complete)*(pi/2)   # linear approximation for initial guess
    for k in range(5):   # Newton's method
        guess = guess - ((EllipticE(guess, m) - value)
                           / (1 - m * math.sin(guess)**2)**0.5)
    return intpart + guess


def SqrtQuadratic(a, b, L, U):
    """
    Compute the integral of the square root of a quadratic polynomial.

                                     /\U   __________
    SqrtQuartic(a, b, c, d, L, U) =  |   \/(x+a)(x+b) dx
                                    \/L
    """
    Ua, Ub = (U+a)**0.5, (U+b)**0.5
    La, Lb = (L+a)**0.5, (L+b)**0.5
    V, W = (Ua*Lb + Ub*La)/(U-L), (Ua*Ub + La*Lb)/(U-L)
    A11, A31 = Ua*Ub - La*Lb, Ua**3*Ub - La**3*Lb
    return (U-L)/4 * (-RC(V**2,W**2)*(U-L) + A11) + A31/2


def QuadraticBezierLength(x0, y0, x1, y1, x2, y2, tmax=1):
    """
    BezierLength(x0, y0, x1, y1, x2, y2) -> float

    Return the length of the quadratic Bezier curve from (x0,y0) to (x2,y2)
    with control point (x1,y1).
    """
    p = [2*x2 - 4*x1 + 2*x0, 2*x1 - 2*x0]   # x-velocity (linear polynomial)
    q = [2*y2 - 4*y1 + 2*y0, 2*y1 - 2*y0]   # y-velocity (linear polynomial)
    if p[0] == q[0] == 0:       # if velocity is constant
        return (p[1]**2 + q[1]**2)**0.5
    # p^2+q^2 factors as (p + qj)(p - qj)
    r = (p[1] + q[1]*1j)/(p[0] + q[0]*1j)   # negative of complex root of p^2+q^2
    return (p[0]**2 + q[0]**2)**0.5 * abs(SqrtQuadratic(r,r.conjugate(),0,tmax))


def InvQuadraticBezierLength(x0, y0, x1, y1, x2, y2, value):
    """
    Returns the number t for which BezierLength(x0,y0,x1,y1,x2,y2,t)==value
    """
    p = [2*x2 - 4*x1 + 2*x0, 2*x1 - 2*x0]   # x-velocity (linear polynomial)
    q = [2*y2 - 4*y1 + 2*y0, 2*y1 - 2*y0]   # y-velocity (linear polynomial)
    if p[0] == q[0] == 0:       # if velocity is constant
        return value / (p[1]**2 + q[1]**2)**0.5
    # p^2+q^2 factors as (p + qj)(p - qj)
    r1 = (p[1] + q[1]*1j)/(p[0] + q[0]*1j)   # negative of complex root of p^2+q^2
    r2 = r1.conjugate()
    value /= (p[0]**2 + q[0]**2)**0.5
    # Newton's method
    total_length = abs(SqrtQuadratic(r1,r2,0,1))
    guess = value / total_length     # linear approximation
    for k in range(5):
        guess = guess - ( (abs(SqrtQuadratic(r1,r2,0,guess)) - value)
                          / abs(((guess+r1)*(guess+r2))**0.5)    )
    return guess


def SqrtQuartic(a, b, c, d, L, U):
    """
    Compute the integral of the square root of a quartic polynomial.

                                     /\U   ____________________
    SqrtQuartic(a, b, c, d, L, U) =  |   \/(x+a)(x+b)(x+c)(x+d) dx
                                    \/L
    """
    Ua, Ub, Uc, Ud = (U+a)**0.5, (U+b)**0.5, (U+c)**0.5, (U+d)**0.5
    La, Lb, Lc, Ld = (L+a)**0.5, (L+b)**0.5, (L+c)**0.5, (L+d)**0.5
    Uab = (Ua*Ub*Lc*Ld + La*Lb*Uc*Ud)/(U-L)
    Uac = (Ua*Lb*Uc*Ld + La*Ub*Lc*Ud)/(U-L)
    Uad = (Ua*Lb*Lc*Ud + La*Ub*Uc*Ld)/(U-L)
    W = Uab*Uab - (a-c)*(a-d)
    Q = W/((U+a)*(L+a))
    I1 = 2*RF(Uab*Uab, Uac*Uac, Uad*Uad)
    I2 = RD(Uab*Uab, Uac*Uac, Uad*Uad)*2*(a-b)*(a-c)/3. + 2*Ua*La/(Ud*Ld*Uad)
    I3 = -RJ(Uab*Uab, Uac*Uac, Uad*Uad, W)*2*(a-b)*(a-c)*(a-d)/3. + 2*RC(Q+1,Q)
    A1111 = Ua*Ub*Uc*Ud - La*Lb*Lc*Ld
    A111_1 = Ua*Ub*Uc/Ud - La*Lb*Lc/Ld
    A3111 = (Ua**3)*Ub*Uc*Ud - (La**3)*Lb*Lc*Ld
    return ( I3*(a-b-c+d)*((a-d)**2-(b-c)**2)/16.
            - (I2*(b-d)*(c-d)+2*A111_1)*((a-b-c+d)**2 + 2*((a-d)**2+(b-c)**2))/48.
            + I1*(4*(b-d)*(c-d)-3*(a-d)**2+3*(b-c)**2)*(a-b)*(a-c)/48.
            - A1111*(3*a-b-c-d)/12. + A3111/3. )


def BezierLength(x0, y0, x1, y1, x2, y2, x3, y3, tmax=1):
    """
    BezierLength(x0, y0, x1, y1, x2, y2, x3, y3, tmax=1) -> float

    Return the length of the cubic Bezier curve from (x0,y0) to (x3,y3) with
    control points at (x1,y1) and (x2,y2).
    """
    p = [3*x3-9*x2+9*x1-3*x0, 6*x2-12*x1+6*x0, 3*x1-3*x0]  # x-velocity polynomial
    q = [3*y3-9*y2+9*y1-3*y0, 6*y2-12*y1+6*y0, 3*y1-3*y0]  # y-velocity polynomial
    if p[0] == q[0] == 0:
        return QuadraticBezierLength(x0, y0, (3*x1-x0)/2., (3*y1-y0)/2., x3, y3)
    # p^2+q^2 factors as (p + qj)(p - qj)
    a, b, c = p[0]+q[0]*1j, p[1]+q[1]*1j, p[2]+q[2]*1j   # coefficients of p + jq
    disc = (b**2 - 4*a*c)**0.5
    r1, r2 = (b + disc)/(2*a), (b - disc)/(2*a)     # negative roots of p + jq
    return ((p[0]**2 + q[0]**2)**0.5
            * abs(SqrtQuartic(r1, r2, r1.conjugate(), r2.conjugate(), 0, tmax)))


def InvBezierLength(x0, y0, x1, y1, x2, y2, x3, y3, value):
    """
    Returns the number t for which BezierLength(x0,y0,x1,y1,x2,y2,x3,y3,t)==value
    """
    p = [3*x3-9*x2+9*x1-3*x0, 6*x2-12*x1+6*x0, 3*x1-3*x0]  # x-velocity polynomial
    q = [3*y3-9*y2+9*y1-3*y0, 6*y2-12*y1+6*y0, 3*y1-3*y0]  # y-velocity polynomial
    if p[0] == q[0] == 0:
        return InvQuadraticBezierLength(x0, y0, (3*x1-x0)/2., (3*y1-y0)/2.,
                                            x3, y3, value)
    # p^2+q^2 factors as (p + qj)(p - qj)
    a, b, c = p[0]+q[0]*1j, p[1]+q[1]*1j, p[2]+q[2]*1j   # coefficients of p + jq
    disc = (b**2 - 4*a*c)**0.5
    r1, r2 = (b + disc)/(2*a), (b - disc)/(2*a)     # roots of p + jq
    r3, r4 = r1.conjugate(), r2.conjugate()
    value /= (p[0]**2 + q[0]**2)**0.5
    # Newton's method
    total_length = abs(SqrtQuartic(r1,r2,r3,r4,0,1))
    guess = value / total_length     # linear approximation
    for k in range(5):
        guess = guess - ((abs(SqrtQuartic(r1,r2,r3,r4,0,guess))-value)
                         / abs(((guess+r1)*(guess+r2)*(guess+r3)*(guess+r4))**0.5))
    return guess


################################################################################


# The following function is for checking the above code.
# It computes the integral of (x+a)^(p1/2) * ... * (x+d)^(p4/2) from L to U.
# Consider removing from release versions.
def integral_check(a, b, c, d, L, U, p1, p2, p3, p4):
    p1,p2,p3,p4 = p1/2., p2/2., p3/2., p4/2.
    sum = 0.0
    delx = (U-L)/10000.
    for k in range(10000):
        l = L + k*delx
        r = l + delx
        m = (l+r)/2
        lvalue = (l+a)**p1 * (l+b)**p2 * (l+c)**p3 * (l+d)**p4
        rvalue = (r+a)**p1 * (r+b)**p2 * (r+c)**p3 * (r+d)**p4
        mvalue = (m+a)**p1 * (m+b)**p2 * (m+c)**p3 * (m+d)**p4
        sum += (delx/6)*(lvalue + 4*mvalue + rvalue)
    return sum
