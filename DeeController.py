'''
About  : Main program file. See main() function.
         Crawls bird-sighting data published at the Dee Estuary Birding website:
         http://www.deeestuary.co.uk/lsarch.htm.
         Parses the data and publishes to CSV files in a format suitable for 
         upload to RECORD Swift:
         https://record-lrc.co.uk/swift/
Version: 1 (14-Feb-2023)
Author : Kevin Morley
Uses   :
  BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
'''

# ------------------------------------------------------------------------------

import const                        # KPM
import csv
import logging
import os
import re
import requests

from bs4 import BeautifulSoup
from DeeParser import DeeParser     # KPM

# ------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO, 
            format='[%(module)s]-[%(funcName)s]-[%(levelname)s] - %(message)s', 
            handlers= [
                logging.FileHandler('debug.log', mode='w'), 
                logging.StreamHandler()
            ])
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------

DEFAULT_OUTPUT_DIR = 'Data/'

# ------------------------------------------------------------------------------
# Class which orchestrates the data input, parsing and output processes.

class DeeController:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self):
        '''
        Params: N/A
        Return: N/A
        '''
        self.parser = DeeParser()
        self.output_dir = DEFAULT_OUTPUT_DIR

    # --------------------------------------------------------------------------
    # Get list of filenames in a target folder.

    def get_files(self, folder):
        '''
        Params: folder (string) - path to folder containing files to parse
        Return: (list of strings) - filenames to be parsed
        '''
        log.info(f'Reading filenames in folder: {folder}')
        files = []
        for filename in os.listdir(folder):
            f = os.path.join(folder, filename)
            if os.path.isfile(f):
                files.append(f)

        return files

    # --------------------------------------------------------------------------
    # Read HTML pages from file, parse contents and write to output files.

    def main_files(self):
        '''
        Params: N/A
        Return: N/A
        '''
        pages = self.get_files('HTML')
        # pages = self.get_files('TMP')

        # pages = []
        # pages.append('TMP\\l070808.htm.html')
        # pages.append('TMP\\l070809.htm.html')
        obs_all = []
        for count, page in enumerate(pages):
            log.info('-' * 60)
            log.info(f'Processing file {count+1} of {len(pages)}')
            obs = self.read_file(page)
            obs_all += obs
            self.write_file(page, obs)

        log.info('-' * 60)
        self.write_file('_Results_All_Files', obs_all, datename=False)
        self.write_unknowns()

    # --------------------------------------------------------------------------
    # Read HTML pages from URLs, parse contents and write to output files.

    def main_web(self):
        '''
        Params: N/A
        Return: N/A
        '''
        log.info(f'Reading index page: {const.SITE_INDEX}')
        page = requests.get(const.SITE_INDEX)
        if page.status_code != 200:
            log.error(f' *** Download error: {page.status_code}')
            return

        # Get list of pages to be processed
        soup = BeautifulSoup(page.content, 'html.parser')
        pages = []
        # pages.append('http://www.deeestuary.co.uk/l050608.htm')
        # pages.append('http://www.deeestuary.co.uk/l010221.htm')
        # '''
        for link in soup.find_all('a'):
            l = link.get('href')
            # Sightings pages all begin with 'l' (with one exception)
            if l is None or l[0].lower() != 'l' or l.lower() == 'lsight.htm':
                continue
            url = const.SITE_ROOT+l
            if url not in pages:
                pages.append(url)
        # '''
        # Process identified pages
        obs_all = []
        for count, page in enumerate(pages):
            log.info('-' * 60)
            log.info(f'Processing page {count+1} of {len(pages)}')
            obs = self.read_web(page)
            obs_all += obs
            self.write_file(page, obs)

        log.info('-' * 60)
        self.write_file('_Results_All_Web', obs_all, datename=False)
        self.write_unknowns()

    # --------------------------------------------------------------------------
    # Read an HTML page from file and return parsed contents.

    def read_file(self, fn):
        '''
        Params: fn (string) - name of file to parse
        Return: (list of dicts) - sightings parsed from 'fn'
        '''
        with open(fn, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        obs = self.parser.read_page(fn, soup)
        return obs

    # --------------------------------------------------------------------------
    # Read an HTML page from URL and return parsed contents.

    def read_web(self, fn):
        '''
        Params: fn (string) - name of URL to parse
        Return: (list of dicts) - sightings parsed from 'fn'
        '''
        page = requests.get(fn)
        soup = BeautifulSoup(page.content, 'html.parser',
                             from_encoding='Windows-1255')
        obs = self.parser.read_page(fn, soup)
        return obs

    # --------------------------------------------------------------------------
    # Write parsed results to output CSV file.

    def write_file(self, fn, obs, datename=True):
        '''
        Params: fn (string) - source filename
                obs (list of dicts) - parsed results to write to file
                datename (bool) - True = include source date in output filename
        Return: N/A
        '''
        # Generate filename
        if datename:
            # Include date name in filename
            fnp = re.split(r'/|\\', fn)
            d = obs[-1][const.E_DATE].strftime('%Y_%b')
            fn_csv = f'{self.output_dir}{d}_{fnp[-1]}.csv'
        else:
            fn_csv = f'{self.output_dir}{fn}.csv'
        log.info(f'Writing file: {fn_csv}')
        with open(fn_csv, 'w') as out_file:
            writer = csv.DictWriter(out_file, lineterminator='\r',
                                    quoting=csv.QUOTE_ALL,
                                    fieldnames=[const.E_SOURCE, 
                                                const.E_RECORD,
                                                const.E_STATUS,
                                                const.E_STATUSNOTE, 
                                                const.E_DATE,
                                                const.E_ABUNDANCE, 
                                                const.E_NAME,
                                                const.E_SCIENTIFIC,
                                                const.E_LOCATION, 
                                                const.E_GRIDREF,
                                                const.E_SEX, 
                                                const.E_RECTYPE,
                                                const.E_OBSERVER, 
                                                const.E_DETERMINER,
                                                const.E_COMMENTS])
            writer.writeheader()
            writer.writerows(obs)

    # --------------------------------------------------------------------------
    # Write unknown species and locations to separate files.

    def write_unknowns(self):
        '''
        Params: N/A
        Return: N/A
        '''
        fn = f'{self.output_dir}_Unknown_Locations.csv'
        log.info(f'Writing file: {fn}')
        with open(fn, 'w') as f:
            for k in sorted(self.parser.unknown_locs.keys()):
                f.write(f'"{k}",{self.parser.unknown_locs[k]}\n')

        fn = f'{self.output_dir}_Unknown_Species.csv'
        log.info(f'Writing file: {fn}')
        with open(fn, 'w') as f:
            for k in sorted(self.parser.unknown_specs.keys()):
                f.write(f'"{k}",{self.parser.unknown_specs[k]}\n')

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
# Main program entry point. Instantiate controller object and call methods.

def main():
    '''
    Params: N/A
    Return: N/A
    '''
    try:
        dc = DeeController()
        # Use main_files() method to import from downloaded HTML files
        # dc.main_files()
        # Use main_web() method to import directly from website
        dc.main_web()
    except Exception as ex:
        log.error(ex)

# ------------------------------------------------------------------------------
# Test
# ------------------------------------------------------------------------------
# Run module-specific tests.

def do_test():
    '''
    Params: N/A
    Return: (bool) Returns True if tests succesful, else False
    '''
    log.info('-'*25)
    log.info('Beginning test of DeeController...')
    dc = DeeController()
    dc.main_files()
    # TODO
    log.info('Finished test')
    return True

# ------------------------------------------------------------------------------

if __name__ == '__main__':
    main()

# ------------------------------------------------------------------------------
       
'''
End
'''