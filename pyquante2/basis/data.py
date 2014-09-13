"""\
 basis sets loader for use with PyQuante

 This program is part of the PyQuante quantum chemistry program suite.
"""

import os
from pyparsing import *

from pyquante2.geo import elements

elements.symbol = elements.symbol + ["Fr", "Ra", "Ac", "Th", "Pa", "U", "Np", "Pu", "Am", "Cm", "Bk",
                                     "Cf", "Es", "Fm", "Md", "No", "Lr", "Rf", "Db", "Sg", "Bh", "Hs",
                                     "Mt", "Uun", "Uuu", "Uub", "Uut", "Uuq", "Uup", "Uuh", "Uus"]
EOL = lineEnd.suppress()
comment = '#' + restOfLine
positiveInteger = Word(nums).setParseAction(lambda s,l,t: int(t[0]))
floatNumber = Regex(r'[-+]?\d+(\.\d*)?([eED]?[-+]\d+)?').setParseAction(lambda s,l,t: float(t[0].replace('D', 'E')))

beginElement = Keyword('basis').suppress()
endElement = Keyword('end').suppress()
numberedElement = {sym:num for num,sym in enumerate(elements.symbol)}
elementSymbol = oneOf(' '.join(elements.symbol))('element')
orbitalSymbol = oneOf("S P SP D F G H I K L M")('orbital')
angularPart = oneOf("CARTESIAN SPHERICAL")
label = QuotedString('"')
coeffs = Group(EOL + OneOrMore(floatNumber.setWhitespaceChars(" \t")))
# Not Implemented
associatedECR = Keyword("ASSOCIATED_ECP") + QuotedString('"')

def parseOrbital(s, l, t):
    if t['orbital'] == 'SP':
        yield (t['element'], ('S', [(c[0], c[1]) for c in t['coeffs']]))
        yield (t['element'], ('P', [(c[0], c[2]) for c in t['coeffs']]))
    else:
        for i in range(1, len(t['coeffs'][0])):
            yield (t['element'], (t['orbital'], [(c[0], c[i]) for c in t['coeffs']]))

def parseElement(s, l, t):
    symbol = t['orbitals'][0][0]
    return (numberedElement[symbol], [orbital[1] for orbital in t['orbitals']])

orbital = elementSymbol + orbitalSymbol + OneOrMore(coeffs)('coeffs')
orbital.setParseAction(parseOrbital)

element = beginElement + label + angularPart + OneOrMore(orbital)('orbitals') + endElement
element.setParseAction(parseElement)

basisParser = OneOrMore(element) + Optional(associatedECR).suppress()
basisParser.ignore(comment)

class load_basis(dict):
    def __getitem__(self, key):
        if key not in associated_ecp_basis + svp_svp_basis + qm_mm_methods_basis:
            dir = os.path.dirname(__file__)
            filename = os.path.join(dir, 'libraries', key)
            basis = basisParser.parseFile(filename, parseAll=True)
            return {e:c for e,c in basis}

basis = load_basis()

associated_ecp_basis = ['crenbl_ecp', 'crenbs_ecp', 'dhf-ecp', 'def2-ecp', 'hay_wadt_n-1_ecp', 'sdb_rlc_ecp', 'lanl2dz_ecp', 'sbkjc_ecp',
                        'stuttgart_rsc_ecp', 'stuttgart_rlc_ecp', 'stuttgart_rsc_1997_ecp', 'stuttgart-koeln_mcdhf_rsc_ecp']

svp_svp_basis = ['def2-svp', 'dhf-svp']

qm_mm_methods_basis = ['qmmm_zhang_3-21g_ecp', 'qmmm_zhang_6-31gs_ecp']

if __name__ == '__main__':
    flag = True
    for basis_file in sorted(os.listdir('libraries')):
        try:
            basis[basis_file]
        except Exception as e:
            flag = False
            print basis_file, "parser error", e
    if flag:
        print "all basises parsed OK"
