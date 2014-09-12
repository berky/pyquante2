"""\
 basis sets loader for use with PyQuante

 This program is part of the PyQuante quantum chemistry program suite.
"""

import os
from pyparsing import *

from pyquante2.geo import elements

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
coeffs = OneOrMore(floatNumber)('coeffs')
# Not Implemented
associatedECR = Keyword("ASSOCIATED_ECP") + QuotedString('"')

def parseOrbital(s, l, t):
    if t['orbital'] == 'SP':
        yield t['element'], ('S', zip(t['coeffs'][0::3], t['coeffs'][1::3]))
        yield t['element'], ('P', zip(t['coeffs'][0::3], t['coeffs'][2::3]))
    else:
        yield (t['element'], (t['orbital'], zip(t['coeffs'][0::2], t['coeffs'][1::2])))

def parseElement(s, l, t):
    symbol = t['orbitals'][0][0]
    return (numberedElement[symbol], [orbital[1] for orbital in t['orbitals']])

orbital = elementSymbol + orbitalSymbol + coeffs
orbital.setParseAction(parseOrbital)

element = beginElement + label + angularPart + OneOrMore(orbital)('orbitals') + endElement
element.setParseAction(parseElement)

parser = OneOrMore(element) + Optional(associatedECR).suppress()
parser.ignore(comment)

class load_basis(dict):
    def __getitem__(self, key):
        if key not in not_implemented_basis:
            dir = os.path.dirname(__file__)
            filename = os.path.join(dir, 'libraries', key)
            basis = parser.parseFile(filename, parseAll=True)
            return {e:c for e,c in basis}

basis = load_basis()

not_implemented_basis = ['ano-rcc', 'aug-cc-pv5z-pp', 'aug-cc-pvdz-pp', 'aug-cc-pvqz-pp', 'aug-cc-pvtz-pp',
                         'cc-pv5z-pp', 'cc-pvdz-pp', 'cc-pvqz-pp', 'cc-pvtz-pp', 'cc-pwcv5z-pp', 'cc-pwcvdz-pp',
                         'cc-pwcvqz-pp', 'cc-pwcvtz-pp', 'crenbl_ecp', 'crenbs_ecp', 'def2-ecp', 'dhf-ecp',
                         'dhf-qzvp', 'dhf-qzvpp', 'dhf-svp', 'dhf-tzvp', 'dhf-tzvpp', 'hay-wadt_mb_n+1_ecp',
                         'hay_wadt_n-1_ecp', 'hay-wadt_vdz_n+1_ecp', 'lanl2dz_ecp', 'qmmm_zhang_3-21g_ecp',
                         'qmmm_zhang_6-31gs_ecp', 'sarc-dkh', 'sarc-zora', 'sbkjc_ecp', 'sdb_rlc_ecp',
                         'stuttgart-koeln_mcdhf_rsc_ecp', 'stuttgart_rlc_ecp', 'stuttgart_rsc_1997_ecp',
                         'stuttgart_rsc_ano_ecp', 'stuttgart_rsc_ecp', 'ugbs', 'valgrind-python.supp']
