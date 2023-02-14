'''
About  : Implements the DeeParser class which performs parsing of the source
         data. Instantiated from the DeeController class.
Version: 1 (14-Feb-2023)
Author : Kevin Morley
'''

# ------------------------------------------------------------------------------

import const                # KPM
import logging
import re
import reference as ref     # KPM

from datetime import datetime

# ------------------------------------------------------------------------------

log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Class which performs parsing of HTML input pages.

class DeeParser:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self):
        '''
        Params: N/A
        Return: N/A
        '''
        self.unknown_locs = {}   # dict of unknown locations
        self.unknown_specs = {}  # dict of unknown species
        # Instantiate reference objects for subsequent lookups.
        self.birdlist = ref.BirdList()
        self.gridrefs = ref.GridRefs()

    # --------------------------------------------------------------------------
    # Parse date at start of line for Type 2 pages - e.g.
    # '|August 31, 2008:|3 Wheatear on rocks at|Dove Point, Meols|, \n  morning'

    def date_start_line(self, l, yr):
        '''
        Params: l (string) - line to be parsed
                yr (int) - year associated with page being parsed
        Return: (tuple: datetime, int) - (date parsed from line, index of next 
                character following date) - else (None, -1) if no date
        '''
        if l.count('|') >= 2:
            i = l.index('|')
            j = l.index('|', i+1)
            dts = l[i+1:j]
            dts = re.sub('[,|:]', '', dts)
            # Check whether year is already present in string
            has_year = re.findall('.*([1-3][0-9]{3})', dts)
            if len(has_year) == 0:
                dts = '{} {}'.format(dts, yr)
            dto = self.parse_date(dts)
        else:
            dto = None
            j = -1
        return dto, j

    # ------------------------------------------------------------------------------
    # Factory method to create and reurn an observation dictionary.

    def make_ob(self, src, dto, rec, abund='', name='', sci='', loc='', com='',
                sex='', stat='ok', statnote=''):
        '''
        Params: src (string) - observation source filename/URL
                dto (datetime) - date of observation
                rec (string) - full record from which observation is parsed
                abund (string) - abundance - e.g. '5', 'c250', '10-12000'
                name (string) - common name of bird
                sci (string) - scientific name of bird
                loc (string) - textual description of location
                com (string) - comment parsed from record
                sex (string) - sex/stage parsed from record
                stat (string) - status of parsing
                statnote (string) - note to accompany stats
        Return: (dict) - dictionary representing a single sighting
        '''
        sex = sex if len(sex) > 0 else 'Not recorded'
        ob = {const.E_SOURCE: src,
            const.E_RECORD: rec,
            const.E_STATUS: stat,
            const.E_STATUSNOTE: statnote,
            const.E_NAME: name,
            const.E_SCIENTIFIC: sci,
            const.E_DATE: dto,
            const.E_LOCATION: loc,
            const.E_GRIDREF: '',
            const.E_ABUNDANCE: abund,
            const.E_SEX: sex,
            const.E_RECTYPE: 'Sighting',
            const.E_OBSERVER: 'Anon at Dee Estuary Bird Sightings',
            const.E_DETERMINER: 'Anon at Dee Estuary Bird Sightings',
            const.E_COMMENTS: (f'Retrieved from www.deeestuary.co.uk. {com}')
            }
        return ob

    # ------------------------------------------------------------------------------
    # Parse a string representation of a date into a datetime object.
    # This approach runs more quickly than quicker than using:
    #   from dateparser.search import search_dates
    
    def parse_date(self, dts):
        '''
        Params: dts (string) - date to be parsed
        Return: (datetime) - datetime object parsed from dts, else None
        '''
        # Define acceptable date formats.
        date_format_options = ['%B %d %Y',   # 'February 10 2008'
                               '%b %d %Y']   # 'Feb 10 2008'
        if dts is None:
            return None
        dto = None
        for f in date_format_options:
            try:
                dto = datetime.strptime(dts, f)
                break
            except ValueError:
                continue

        return dto

    # --------------------------------------------------------------------------
    # Parse an observation record into individual sightings. e.g.
    '''
    '4 Short-eared Owl, 1 Eider \n  (drake), 25 Brent Geese, 2 Peregrine, 
    2 Merlin and 2 Stonechat (pair) \n  -|Heswall Marsh, Riverbank Road|, at \n
     high tide, started in a heavy snow storm and finished off in brilliant \n 
     sunshine!|53 Brent Geese (pale-bellied), 9,000 Dunlin, 250 Grey Plover, 35
     \n  Sanderling and 1,400 Knot -|West Kirby|Shore.|6 Goldeneye, 
     11 Red-breasted Merganser and 1 Shag -|West Kirby Marine Lake.
     |1 Hen Harrier (ringtail), 1 \n   
     Short-eared Owl, 2 Merlin, 50 Pink-footed Geese and 1 Stonechat (f) -
     |Parkgate Marsh|, unlike Heswall the \n          
     tide was a long way out here!|3 Spotted Redshank, 300 Wigeon and 
     50 Pink-footed Geese -|Inner Marsh Farm|and nearby fields.
     |Birdwatching Events for Dee and Mersey areas 
     (Birdwatchers Diary 2006)|now available on this website.'
    '''
    def parse_observations(self, fn, dto, txt_obs):
        '''
        Params: fn (string) - filename/URL associated with page being parsed
                dto (datetime) - date object associated with page being parsed
                txt_obs (string) - text record to be parsed
        Return: (list of dicts) - list of parsed sightings
        '''
        char_to_replace = {'!': '.',
                           '\n': '',
                           '\r': '',
                           ',': '',
                           '.|.|': '.|'   # double stop chars
                          }

        obs = []
        '''
        if '1 Alpine Swift - Barnston by Fox & Hounds pub' in txt_obs:
            print('*** Breakpoint')
        '''
        # Remove extraneous characters
        cleaned = txt_obs
        for key, value in char_to_replace.items():
            cleaned = cleaned.replace(key, value)
        cleaned = ' '.join(cleaned.split())
        # Split into individual records based upon full stop chars '.'
        records = re.findall('\.'.join(['[^.]+']), cleaned)
        for record in records:
            sections = re.findall('\|'.join(['[^|]+']), record)
            if len(sections) > 1:
                try:
                    s_s = sections[0]                               # species
                    s_l = sections[1]                               # location
                    s_c = sections[2] if len(sections)>2 else ''    # comment
                    # Parse individual sightings from single record
                    recs = self.parse_record(s_s)
                    # Check whether the location section has further sightings
                    recs_l = self.parse_record(s_l)
                    if len(recs_l) > 0:
                        recs += recs_l
                        s_l = s_c
                        s_c = sections[3] if len(sections) > 3 else ''
                    # Check whether the comment section has further sightings
                    com = ''
                    if len(s_c) > 0:
                        recs_c = self.parse_record(s_c)
                        if len(recs_c) > 0:
                            recs += recs_c
                        else:
                            com = s_c.strip().capitalize()
                    # Create observation records from sighting
                    for rec in recs:
                        r_abund = rec[0].strip('- ')    # abundance
                        r_spec = rec[1].strip('- ')     # species
                        r_sex = rec[2].strip('- ')      # sex/stage
                        # Identify most likely species
                        species, exact_species = self.birdlist.get_species(
                                                                    r_spec)
                        if species is not None:
                            spec_name = species[const.B_COMMON]
                            spec_sci = species[const.B_SCIENTIFIC]
                        else:
                            # Failed to find a good species match
                            spec_name = const.UNKNOWN_SPEC
                            spec_sci = const.UNKNOWN_SPEC
                            # Update count of unmatched terms
                            if r_spec not in self.unknown_specs:
                                self.unknown_specs[r_spec] = 1
                            else:
                                self.unknown_specs[r_spec] += 1
                        # Create new observation record
                        ob = self.make_ob(src=fn, dto=dto, rec=record, 
                                          abund=r_abund, sex=r_sex,
                                            name=spec_name,
                                            sci=spec_sci,
                                            loc=s_l)
                        ob[const.E_COMMENTS] += com
                        # Identify most likely grid reference
                        grid, exact_grid = self.gridrefs.get_gridref(ob[const.E_LOCATION])
                        if grid is not None:
                            grid_ref = grid[const.G_GRIDREF]
                            grid_desc = grid[const.G_LOCDESC]
                        else:
                            # Failed to find a good location match
                            grid_ref = const.UNKNOWN_LOC
                            grid_desc = const.UNKNOWN_LOC
                            # Update count of unmatched terms
                            if ob[const.E_LOCATION] not in self.unknown_locs:
                                self.unknown_locs[ob[const.E_LOCATION]] = 1
                            else:
                                self.unknown_locs[ob[const.E_LOCATION]] += 1
                            
                        ob[const.E_GRIDREF] = grid_ref
                        # Update status warnings if not exact matches
                        if not exact_species and not exact_grid:
                            ob[const.E_STATUS] = 'check species & gridref'
                            ob[const.E_STATUSNOTE] = f'[{rec[1]}] / [{grid_desc}]'
                        elif not exact_species:
                            ob[const.E_STATUS] = 'check species'
                            ob[const.E_STATUSNOTE] = rec[1]
                        elif not exact_grid:
                            ob[const.E_STATUS] = 'check gridref'
                            ob[const.E_STATUSNOTE] = ob[const.E_LOCATION]

                        obs.append(ob)
                except Exception as ex:
                    log.error(ex)
                    ob = self.make_ob(src=fn, dto=dto, rec=record,
                                stat='error', statnote=sections[0])
                    obs.append(ob)
            else:
                ob = self.make_ob(src=fn, dto=dto, rec=record,
                            stat='format', statnote=sections[0])
                obs.append(ob)

        return obs

    # --------------------------------------------------------------------------
    # Parse a single sighting record from an observation. e.g
    '''
    4 Short-eared Owl 1 Eider (drake) 25 Brent Geese 2 Peregrine 2 Merlin and
      2 Stonechat (pair) -
    '''
    def parse_record(self, rec):
        '''
        Params: rec (string) - record to be parsed
        Return: (list of tuples: string, string, string) 
                (abundance, species, stage) e.g.
         [('4', 'Short-eared Owl', ''), ('1', 'Eider', 'Male')...]
        '''
        obs = []
        r2 = rec.replace(' and ', ' ')
        r = r2.replace('.', '')
        # Extract abundance
        pattern = r'c?\d[0-9\-+/ ]*'
        num = re.findall(pattern, r)
        # Extract descriptions
        des = re.split(pattern, r)
        if len(num) != len(des)-1:
            log.error('Record parse error: {rec}')
            return []
        # Process each pair of number and description
        for i in range(len(num)):
            stage = ''
            spec = des[i+1].strip('- ')
            spec = re.sub(r'[()]', '', spec)
            # Parse spec into separate words and check against sex/stage terms
            words = spec.split()
            for word in words:
                wl = word.lower()
                # Is this a stage term?
                wt = [w for w in const.STAGE_TERMS if w[0] == wl]
                if len(wt) > 0:
                    stage += wt[0][1] if len(stage) == 0 else f' {wt[0][1]}'
                    spec = spec.replace(word, '')
                else:
                    # Is this a sex term?
                    wt = [w for w in const.SEX_TERMS if w[0] == wl]
                    if len(wt) > 0:
                        stage += wt[0][1] if len(stage) == 0 else f' {wt[0][1]}'
                        spec = spec.replace(word, '')
                    else:
                        # Is this a quantity term?
                        wt = [w for w in const.QUANTITY_TERMS if w[0] == wl]
                        if len(wt) > 0:
                            stage += wt[0][1] if len(stage) == 0 else f' {wt[0][1]}'
                            spec = spec.replace(word, '')
                                    
            ob = (num[i].strip(), spec.strip(), stage)
            # ob = (num[i].strip(), des[i+1].strip('- '))
            obs.append(ob)

        return obs

    # --------------------------------------------------------------------------
    # Parse a single page. Determine what type of page it is, then call relevant
    # method.

    def read_page(self, fn, soup):
        '''
        Params: fn (string) - filename associated with contents of soup object
                soup (BeautifulSoup) - populated BS with HTML to parse
        Return: (list of dicts) - sightings parsed from soup object
        '''
        log.info(f'Page: {fn}')
        # Get year from page
        txt = soup.get_text()
        i = txt.find('Archived')
        j = txt.find('.', i)
        nums = re.findall(r'\d+', txt[i:j])
        # Handle 2-digit dates e.g. '09' rather than '2009'
        yr_txt = nums[0] if len(nums[0]) == 4 else '20'+nums[0]
        yr = int(yr_txt)
        log.info(f'Year: {yr}')
        # Determine which page formatting has been used - i.e. table or block
        obs_all = self.read_page_type_1(fn, soup, yr)
        if len(obs_all) == 0:
            obs_all = self.read_page_type_2(fn, soup, yr)
        if len(obs_all) > 0:
            log.info(f'Start: {obs_all[-1][const.E_DATE].strftime("%d-%b-%Y")}' 
                    f' End: {obs_all[0][const.E_DATE].strftime("%d-%b-%Y")}')
        log.info(f'No. of records: {len(obs_all)}')

        return obs_all

    # --------------------------------------------------------------------------
    # Parse a Type 1 page. Type 1 consists of a two-column table, with dates in
    # first columns and records in the second.

    def read_page_type_1(self, fn, soup, yr):
        '''
        Params: fn (string) - filename associated with contents of soup object
                soup (BeautifulSoup) - populated BS with HTML to parse
                yr (int) - year associated with contents of soup object
        Return: (list of dicts) - sightings parsed from soup object, else empty 
                list if error
        '''
        obs_all = []
        trs = soup.find_all('tr')
        # Check whether this is a Type 1 page
        if len(trs) == 0:
            log.debug(f'Not Type 1: {fn}')
            return []
        for count, row in enumerate(trs):
            # TODO: confirm skipping to row 7 doesn't exclude any observations
            if (count < 7) or (count > len(trs)-2):
                continue
            cells = row.find_all('td')
            # Skip any blank rows
            if len(cells) != 2:
                continue
            html_date = cells[0]
            html_obs = cells[1]
            txt_date = ' '.join(html_date.get_text().strip().split())
            log.debug(f'{yr} - {txt_date}')
            dts = '{} {}'.format(txt_date, yr)
            dto = self.parse_date(dts)
            if dto is None:
                continue
            if html_obs.find(string=re.compile('![^\\n]')) is not None:
                for m in html_obs.find_all(string=re.compile('![^\\n]')):
                    t = str(m).replace('!', '')
                    m.replace_with(t)
            txt_obs = html_obs.get_text('|', strip=True)
            obs = self.parse_observations(fn, dto, txt_obs)
            obs_all += obs

        return obs_all

    # --------------------------------------------------------------------------
    # Parse a Type 2 page. Type 2 consists of a single block of text with dates
    # inline with records.

    def read_page_type_2(self, fn, soup, yr):
        '''
        Params: fn (string) - filename associated with contents of soup object
                soup (BeautifulSoup) - populated BS with HTML to parse
                yr (int) - year associated with contents of soup object
        Return: (list of dicts) - sightings parsed from soup object, else empty
                list if error
        '''
        obs_all = []
        # Format data for subsequent processing
        txt = soup.get_text('|', strip=True)
        if soup.find(string=re.compile('![^\\n]')) is not None:
            for m in soup.find_all(string=re.compile('![^\\n]')):
                t = str(m).replace('!', '')
                m.replace_with(t)
        lines = re.findall('\.'.join(['[^.]+']), txt)
        # Find start of data
        ixs = [i for i, s in enumerate(lines) if 'Click here to see list of' in s]
        # Check that page is of the correct type
        if len(ixs) != 1:
            log.debug(f'Not Type 2 (no "Click here to see list of"): {fn}')
            return []
        i = ixs[0]
        # Skip to first line with date
        while i < len(lines)-2:
            i += 1
            dto, j = self.date_start_line(lines[i], yr)
            if dto is not None:
                break
        # Check that we've found the start of the data
        if dto is None:
            log.error(f'Failed to find first date: {fn}')
            return []
        # Process remainder of first line
        txt_obs = lines[i][j:].strip('|')
        log.debug(dto)
        # Process the subsequent lines
        while i < len(lines)-2:
            obs = self.parse_observations(fn, dto, txt_obs)
            obs_all += obs
            i += 1
            # Check whether next line start with date
            dto_new, j = self.date_start_line(lines[i], yr)
            if dto_new is None:
                txt_obs = lines[i].strip('|')
            else:
                dto = dto_new
                log.debug(dto)
                txt_obs = lines[i][j:].strip('|')

        return obs_all

# ------------------------------------------------------------------------------
# Test
# ------------------------------------------------------------------------------
# Run module-specific tests.

def do_test():
    '''
    Params: N/A
    Return: (bool) Returns True if tests succesful, else False
    '''
    from bs4 import BeautifulSoup
    
    log.info('-'*25)
    log.info('Beginning test of DeeParser...')
    fn = 'TMP\\2006_03.html'
    dp = DeeParser()
    with open(fn, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    obs = dp.read_page(fn, soup)
    # TODO: Perform checks on parsed data
    log.info('Finished test')
    return True

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
            format='[%(module)s]-[%(funcName)s]-[%(levelname)s] - %(message)s')
    do_test()

# ------------------------------------------------------------------------------
       
'''
End
'''