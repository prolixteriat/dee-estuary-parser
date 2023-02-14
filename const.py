'''
About  : Define constants.
Version: 1 (14-Feb-2023)
Author : Kevin Morley
'''
# ------------------------------------------------------------------------------
# Source website URLs.
SITE_INDEX = 'http://www.deeestuary.co.uk/lsarch.htm'
SITE_ROOT = 'http://www.deeestuary.co.uk/'

# Sex/stage terms.
FEMALE = 'Female'       # Text to be written to Swift upload CSV
MALE = 'Male'           # Text to be written to Swift upload CSV
SEX_TERMS = [
    ('males', MALE),
    ('male', MALE),
    ('m', MALE),
    ('drakes', MALE),
    ('drake', MALE),
    ('females', FEMALE),
    ('female', FEMALE),
    ('f', FEMALE),
    ('ringtails', FEMALE),
    ('ringtail', FEMALE),
    ('ring-tails', FEMALE),
    ('ring-tail', FEMALE)
]

# Stage terms.
ADULT = 'Adult'         # Text to be written to Swift upload CSV
JUVENILE = 'Juvenile'   # Text to be written to Swift upload CSV
STAGE_TERMS = [
    ('adults', ADULT),
    ('adult', ADULT),
    ('ads', ADULT),
    ('ad', ADULT),
    ('chicks', JUVENILE),
    ('chick', JUVENILE),
    ('fledglings', JUVENILE),
    ('fledgling', JUVENILE),
    ('immature', JUVENILE),
    ('imm', JUVENILE),
    ('juveniles', JUVENILE),
    ('juvenile', JUVENILE),
    ('juvs', JUVENILE),
    ('juv', JUVENILE),
    ('sub-ad', JUVENILE),
    ('young', JUVENILE)
]

# Quantity terms.
QUANTITY_TERMS = [
    ('pair', 'Pair')
]

# Text for no-match conditions.
UNKNOWN_SPEC = 'UNKNOWN SPECIES'
UNKNOWN_LOC = 'UNKNOWN LOCATION'

# Export file column headers.
E_SOURCE = 'Source'
E_RECORD = 'Record'
E_STATUS = 'Status'
E_STATUSNOTE = 'Status Note'
E_SCIENTIFIC = 'Scientific'
E_NAME = 'Scientific or Common Name'
E_DATE = 'Date'
E_LOCATION = 'Location'
E_GRIDREF = 'Grid Reference'
E_ABUNDANCE = 'Abundance'
E_SEX = 'Sex/Stage'
E_RECTYPE = 'Record Type'
E_OBSERVER = 'Observer'
E_DETERMINER = 'Determiner'
E_COMMENTS = 'Comments'

# Grid reference import file column headers.
G_LOCDESC = 'Location description'
G_GRIDREF = 'Grid reference'
G_NOTES = 'Notes'

# Birdlist import file column headers.
B_COMMON = 'Common'
B_SCIENTIFIC = 'Scientific'
B_TYPE = 'Type'
B_ABUNDANCE = 'Abundance'
B_CATEGORY = 'Category'
B_ABBREVIATION = 'Abbreviation'

# ------------------------------------------------------------------------------
# Test
# ------------------------------------------------------------------------------
# Run module-specific tests.

def do_test():
    '''
    Params: N/A
    Return: (bool) Returns True if tests succesful, else False
    '''
    # TODO
    return True

# ------------------------------------------------------------------------------

if __name__ == '__main__':   
    do_test()

# ------------------------------------------------------------------------------
       
'''
End
'''