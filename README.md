# DeeEstuary
Project to parse bird sighting data from http://www.deeestuary.co.uk/lsarch.htm site

## Overview
The code can parse pages directly from the the Dee Estuary web site or from downloaded HTML pages (see the 'HTML'folder for a copy of the downloaded pages).
Bird species and sightings locations which have been parsed from the web pages/files are matched against authoratative lists of accepted values. A fuzzy matching algorithm is used to suggest the closest match where an exact match cannot be found.
Synonym lists are used to substitute any non-standard sex/stage information with equivalent standard values - e.g. 'drake' and 'm' become 'Male'; 'ringtail' and 'f' become 'Female'; 'imm' and 'chick' become 'Juvenile'. See const.py for full list of synonyms.
A series of CSV files are produced by the app:
1. One results CSV file for every web page or file parsed.
2. A single summary results CSV which aggregates results form all pages parsed in a single run.
3. Two 'unknown' CSV files which list parsed bird species and sightings locations which were unable to be successfuly matched against authoratative referene files (see the 'Reference' folder.

The results CVS files include columns suitable for upload directly to Swift (https://record-lrc.co.uk/swift/). They also include troubleshoothing information to allow for manual inspection of results prior to upload.

## Folder Structure
**HTML** - contains a zipped copy of the in-scope HTML pages downloaded from the website.
**Reference** - contains the two CSV files used by the reference.py module for specieis and location matching purposes.
**Results_Processed** - contains a partial set of results which have been formatted within Excel.
**Results_Raw** - contains a zipped copy of the full set of results produced by DeeController.py.

## Code Structure
The code consists of three independent apps:
**DeeController** - coordinates the download, parsing, lookups and the output of results.
- DeeController.py
- DeeParser.py
- reference.py
- const.py

**DeeHarvester** - copies the relevant website HTML pages to local file storage.
- DeeHarvester.py
- const.py

**TestRunner** - coordinates execution of test functions across all in-scope module.
- TestRunner.py
- DeeHarvester.py
- DeeController.py
- DeeParser.py
- reference.py
- const.py

## Code Environment
All code is written in Python 3.10.5.
pipfile and pipefile.lock files are provided to facilitate tje download and installation of dependencies via the pipenv package manager: https://pipenv.pypa.io/en/latest/

