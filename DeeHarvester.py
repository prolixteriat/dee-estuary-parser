'''
About  : Copy the contents of the Dee Estuary website to local storage.
         http://www.deeestuary.co.uk/lsarch.htm.
         Sightings pages all begin with 'l' (with one exception).
Version: 1 (014-Feb-2023)
Author : Kevin Morley

Uses:
  BeautifulSoup: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
  pywebcopy    : https://github.com/rajatomar788/pywebcopy/
'''

# ------------------------------------------------------------------------------

import const                # KPM
import logging
import requests

from bs4 import BeautifulSoup
from pywebcopy import save_webpage

# ------------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO,
            format='[%(module)s]-[%(funcName)s]-[%(levelname)s] - %(message)s')
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------

DEFAULT_FOLDER = 'HTML/'        # default target folder name

# ------------------------------------------------------------------------------
# Class which copies Dee Estuary site.

class SiteHarvester:

    # --------------------------------------------------------------------------
    # Constructor.

    def __init__(self, name='DeeEstuary', index=const.SITE_INDEX, 
                 root=const.SITE_ROOT, folder=DEFAULT_FOLDER):
        '''
        Params: name (string)    - sub-folder to which files will be written
                index (string)   - full URL of page to be crawled
                root (string)    - URL root to be prefixed to identified links
                folder (string)  - target folder name
        Return: N/A
        '''
        self.folder = folder    # target folder name
        self.index = index      # full URL of page to be crawled
        self.name = name        # sub-folder to which files will be written
        self.root = root        # URL root to be prefixed to identified links 

    # --------------------------------------------------------------------------
    # Download a single web page.

    def download_page(self, page):
        '''
        Params: page (string) - page name without site prefix
        Return: N/A
        '''
        log.info(f'Downloading: {page}')
        url = self.root + page
        save_webpage(
            url=url,
            project_folder=self.folder,
            project_name=self.name,
            bypass_robots=True,
            debug=False,
            open_in_browser=False,
            delay=None,
            threaded=False,
        )

    # --------------------------------------------------------------------------
    # Download the full site - i.e. all qualifying links on the index page.

    def download_site(self):
        '''
        Params: N/A
        Return: (int) number of downloaded pages
        '''
        log.info('-' * 60)
        log.info(f'Reading index page: {self.index}')
        page = requests.get(self.index)
        if page.status_code != 200:
            log.error(f'Failed. HTTP error code: {page.status_code}')
            return 0

        log.info('Findings links in index page')
        soup = BeautifulSoup(page.content, 'html.parser')
        links = []
        a_tags = soup.find_all('a')
        for tag in a_tags:
            l = tag.get('href')
            # Sightings pages all begin with 'l' (with one exception)
            if l is None or l[0].lower() != 'l' or l.lower() == 'lsight.htm':
                continue
            # Ignore duplicate links
            if l not in links:
                links.append(l)
        
        log.info('Downloading identified pages')
        # Process identified pages
        for count, link in enumerate(links):
            log.info('-' * 60)
            log.info(f'Processing page {count+1} of {len(links)}')
            self.download_page(link)

        log.info('Finished')
        return len(links)

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
# Download site.

def main():
    '''
    Params: N/A
    Return: N/A
    '''
    sh = SiteHarvester()
    sh.download_site()

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
    main()

# ------------------------------------------------------------------------------
       
'''
End
'''