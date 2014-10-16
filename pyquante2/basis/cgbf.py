"""\
 cgbf.py Perform basic operations over contracted gaussian basis
  functions. Uses the functions in pgbf.py.

 References:
  OHT = K. O-ohata, H. Taketa, S. Huzinaga. J. Phys. Soc. Jap. 21, 2306 (1966).
  THO = Taketa, Huzinaga, O-ohata, J. Phys. Soc. Jap. 21,2313 (1966).

 This program is part of the PyQuante quantum chemistry program suite.
"""

import numpy as np
import array


class cgbf(object):

    """
    Class for a contracted Gaussian basis function.
    >>> s = cgbf(exps=[1], coefs=[1])
    >>> print(s)
    cgbf((0.0, 0.0, 0.0), (0, 0, 0), [1.0], [1.0000000000000002])
    >>> np.isclose(s(0, 0, 0), 0.712705)
    True
    """

    contracted = True

    def __init__(self, origin=(0, 0, 0), powers=(0, 0, 0), exps=[], coefs=[]):
        assert len(origin) == 3
        assert len(powers) == 3
        self.origin = np.asarray(origin, 'd')
        self.powers = powers

        self.pgbfs = []
        self.coefs = array.array('d')
        self.pnorms = array.array('d')
        self.pexps = array.array('d')

        for expn, coef in zip(exps, coefs):
            self.add_pgbf(expn, coef, False)

        if self.pgbfs:
            self.normalize

        return

    def __getitem__(self, item):
        return list(zip(self.coefs, self.pgbfs)).__getitem__(item)

    def __call__(self, *args, **kwargs):
        return sum(c * p(*args, **kwargs) for c, p in self)

    def __repr__(self):
        return 'cgbf({}, {}, {}, {})'.format(tuple(self.origin),
                                             self.powers,
                                             list(self.pexps),
                                             list(self.coefs))

    def mesh(self, xyzs):
        '''Evaluate basis function on a mesh of points *xyz*.'''
        return sum(c * p.mesh(xyzs) for c, p in self)

    def cne_list(self):
        '''Return a tuple of coefficients, normalization constants, and
        exponents of the primitives.
        '''
        return self.coefs, self.pnorms, self.pexps

    def add_pgbf(self, expn, coef, renormalize=True):
        '''Add a primitive gaussian basis function to this contracted
        Gaussian basis function.
        '''
        from pyints.basis.pgbf import pgbf

        self.pgbfs.append(pgbf(expn, self.origin, self.powers))
        self.coefs.append(coef)

        if renormalize:
            self.normalize()

        p = self.pgbfs[-1]
        self.pnorms.append(p.norm)
        self.pexps.append(p.exponent)

        return

    def normalize(self):
        from pyquante2.ints.one import S
        from numpy import sqrt
        Saa = S(self, self)
        Saa_sqrt = sqrt(Saa)
        for i in range(len(self.coefs)):
            self.coefs[i] /= Saa_sqrt
        # Is this the right way to do this, or should I have
        # a separate normalization constant?
        return

if __name__ == '__main__':
    import doctest
    doctest.testmod()
