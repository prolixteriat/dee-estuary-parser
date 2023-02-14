'''
About  : Reference classes used for fuzzy lookups: BirdList, GridRefs
Version: 1 (14-Feb-2023)
Author : Kevin Morley
Uses   : 
  fuzzywuzzy: https://pypi.org/project/fuzzywuzzy/
'''

# ------------------------------------------------------------------------------

import const                    # KPM
import csv
import logging

from fuzzywuzzy import fuzz

# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------

DEFAULT_FN_BIRDLIST = 'Location/birdlist.csv'  # default filename for bird list
DEFAULT_FN_GRIDREFS = 'Location/gridrefs.csv'  # default filename for grid refs

# ------------------------------------------------------------------------------
# Class which finds defined species information from a textual description.

class BirdList:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self, filename=DEFAULT_FN_BIRDLIST):
        '''
        Params: filename (string) - name of input file
        Return: N/A
        '''
        self.filename = filename
        self.birds = []
        log.debug(f'Reading birdlist reference file: {filename}')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for dict in reader:
                self.birds.append(dict)

    # --------------------------------------------------------------------------
    # Perform a fuzzy search for the common name of a bird.

    def get_species(self, com):
        '''
        Params: com (string) - non-exact text representing common name
        Return: (tuple: dict, bool) - 
                    dict - matching entry from self.birds list, else None if
                           no good match
                    bool - True if exact match on commmon name, else False
        '''
        # Try initial simple match
        m = max(self.birds, key=lambda b: 
                fuzz.ratio(b[const.B_COMMON], com))
        exact = com.lower() == m[const.B_COMMON].lower()
        ratio = fuzz.ratio(m[const.B_COMMON], com)
        # Check whether we have a good match
        if not exact and ratio <= 85:
            # Try partial match
            m = max(self.birds, key=lambda b: 
                    fuzz.partial_ratio(b[const.B_COMMON], com))
            ratio = fuzz.partial_ratio(m[const.B_COMMON], com)
            # Check whether we have a good match now
            if ratio <=85:
                m = None
                # Try match with first two words
                spl = com.split()
                if len(spl) >= 2:
                    part = ' '.join(spl[:2]).lower()
                    m = max(self.birds, key=lambda b: fuzz.ratio(
                        b[const.B_COMMON], part))
                    ratio = fuzz.ratio(m[const.B_COMMON].lower(), part)
                    # Give up if not good match
                    if ratio < 82:
                        m = None
        
        return m, exact
        
# ------------------------------------------------------------------------------
# Class which finds grid references from textual descriptions of locations. 

class GridRefs:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self, filename=DEFAULT_FN_GRIDREFS):
        '''
        Params: filename (string) - name of input file
        Return: N/A
        '''
        self.filename = filename
        self.gridrefs = []
        log.debug(f'Reading gridrefs reference file: {filename}')
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for dict in reader:
                # Remove any leading/trailing spaces. Noticed in input file.
                dict[const.G_LOCDESC] = dict[const.G_LOCDESC].strip()
                dict[const.G_GRIDREF] = dict[const.G_GRIDREF].strip()
                dict[const.G_NOTES] = dict[const.G_NOTES].strip()
                self.gridrefs.append(dict)

    # --------------------------------------------------------------------------
    # Perform a fuzzy search for the grid reference of a location.

    def get_gridref(self, des):
        '''
        Params: des (string) - non-exact text representing location description
        Return: (tuple: dict, bool) - 
                    dict - matching entry from self.gridrefs list, else None if
                           no good match
                    bool - True if exact match on location description name, 
                           else False
        '''

        # Try simple match
        m = max(self.gridrefs, key=lambda l: fuzz.ratio(
                    l[const.G_LOCDESC], des))
        exact = des.lower() == m[const.G_LOCDESC].lower()
        ratio = fuzz.ratio(m[const.G_LOCDESC], des)
        # Check whether we have a good match
        if not exact and ratio <= 80:
            m = None
        return m, exact

# ------------------------------------------------------------------------------
# Test
# ------------------------------------------------------------------------------
# Run module-specific tests.

def do_test():
    '''
    Params: N/A
    Return: (bool) Returns True if tests succesful, else False
    '''
    t1= do_test_birdlist() 
    t2 =do_test_gridrefs()
    return t1 and t2

# ------------------------------------------------------------------------------

BL_TEST = [
    "(",
    "Brent geese",
    "Brent Geese",
    "Smew (redhead)",
    "Barnacle Geese",
    "Barnacle Goose in the fields",
    "Black-tailed Godwit many thousands of Knot which I didn't count",
    "Brambling at Gilroy Nature Park",
    "Brent geese",
    "Brent Geese flying from Bird Rock (Red Rocks) to Middle Hilbre",
    "Bullfinch at garden feeder next to",
    "Common Buzzard",
    "Common Snipe",
    "drakes)",
    "Dunlin heading past",
    "Eider (",
    "Goldeneye on flat calm sea off",
    "Goshawk over at",
    "Green-winged Teal (drake)",
    "Grey Partridge in field behind Old Baths car park",
    "Grey Partridge in field close to Old Baths car park",
    "Hen Harrier (ringtail)",
    "Hen Harrier (ring-tail)",
    "Little Egret late afternoon",
    "Little heard calling from behind the car park",
    "Marsh Harrier (",
    "Marsh Harrier (fem/imm) over",
    "Peregrine caused havoc",
    "Peregrine chasing Knot",
    "Peregrine seen from shore",
    "Pink-footed Geese",
    "Pink-footed Geese in the fields",
    "pm",
    "Red-breasted Merganser on the Marine Lake",
    "Richard's Pipit",
    "Richard's Pipit this morning",
    "singing Chiffchaff in the scrub behind beach",
    "Smew (redhead)",
    "st win male)",
    "Stonechat (f)",
    "Turnstone on lake wall",
    "Twite just south of",
]

def do_test_birdlist():
    log.info('-'*25)
    log.info('Beginning test of BirdList...')
    bl = BirdList()

    for b in BL_TEST:
        species, exact = bl.get_species(b)
        match = species[const.B_COMMON] if species is not None else '[NO MATCH]'
        print(f'"{b}","{match}",{exact}')
    log.info('Finished test')
    return True

# ------------------------------------------------------------------------------

GR_TEST = [
    "Burton Marsh",
    "West Kirby",
    "Riverbank Road Heswall",
    "Hilbre Island",
    "Hoylake Shore",
    "Little Eye",
    "Point of Ayr",
    "Decca Pools Burton Marsh",
    "Parkgate Marsh Old Baths",
    "Connah's Quay Reserve",
    "Leasowe Shore",
    "Thurstaston/Dungeon Wood",
    "Heswall",
    "Tansky Rocks/Caldy Shore",
    "Heswall Marsh Riverbank Road",
    "Roman Road Meols",
    "Bird Rock Red Rocks",
    "Caldy Shore",
    "Shotwick boating lake",
    "Moreton Shore",
    "Stapledon Wood"
]

def do_test_gridrefs():
    log.info('-'*25)
    log.info('Beginning test of GridRefs...')
    gr = GridRefs()
    
    for g in GR_TEST:
        ref, exact = gr.get_gridref(g)
        if ref is None:
            grid = '[NO MATCH]'
            locdesc = '[NO MATCH]'
        else:
            grid = ref[const.G_GRIDREF]
            locdesc = ref[const.G_LOCDESC]
        print(f'"{g}","{locdesc}",{grid},{exact}')
    log.info('Finished test')
    return True

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
            format='[%(module)s]-[%(funcName)s]-[%(levelname)s] - %(message)s')
    do_test()

# ------------------------------------------------------------------------------
       
'''
End
'''