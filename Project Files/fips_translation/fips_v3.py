import os
import json
import requests
from bs4 import BeautifulSoup as bs


def scrape_codes():
    """
    Scrapes FIPS codes from the USDA site and returns them in a set of dictionaries.
    Each state is assigned it's own dictionary, with the county name in uppercase and the FIPS code of said county used as key value pairs respectively.
    """
    page = requests.get('https://www.nrcs.usda.gov/wps/portal/nrcs/detail/national/home/?cid=nrcs143_013697')
    page.raise_for_status()

    #use bs to parse the webpage, drills down to the data we want
    content = bs(page.content, 'html.parser').find(class_='data').find_all('tr')
    
    #splits raw text and stores each state county code row in a list
    store = [line.get_text() for line in content]
    store = [item.strip().split('\n') for item in store]

    #removes index row
    store.pop(0)

    states = set()
    corpus = dict()
    for i in store:
        #adds the state associated with that code to the states set. It is a set, so duplicates are ignored
        #results in a set of all state abbreviation
        states.add(i[2])
    
    #this loop aims to build a dict of dicts. each state abbreviation is a key and stores a dict of the county name-code pairs
    for i in states:
        county_set = []
        for line in store:
            if line[2] == i:
                county_set.append([''.join(line[1].split()).upper(),line[0]])
        corpus[i] = {r[0]:r[1] for r in county_set}

    return corpus


def load_statedict():
    #Loads a dict of state name-abbreviation pairs
    with open('fips_translation/statedict.json', 'r') as f:
        dict = json.load(f)
    return dict


class FIPS_Translator():
    """
    Main container class for the translation methods.
    Does all scraping and loads the neccisary dicts to memory on creation so that the website does not have to be scraped for every user input, only once during startup.
    """
    def __init__(self):
        """
        loads state and county translation dicts
        """
        self.corpus = scrape_codes()
        self.statedict = load_statedict()

    def state_to_abr(self, state:str):
        """
        converts state names to it's 2 letter abbreviation
        """
        state = ''.join(state.split()).upper()
        return self.statedict[state]

    def encode(self, state:str, county:str):
        """
        encodes state-county pairs into a FIPS code
        """
        state = ''.join(state.split()).upper()
        county = ''.join(county.split()).upper()

        if len(state) > 2:
            state = self.state_to_abr(state.upper())
        
        try:
            return self.corpus[state][county]
        except KeyError:
            return None

    def encode_many(self, datalist:list):
        """
        Takes in a list of [state, county] pairs and appends the list with a 3rd column containing the FIPS codes
        ensure state is coded using its 2 letter postal abbreviation.
        """
        for i in datalist:
            code = self.encode(datalist[0], datalist[1])
            i.append(code)
        return datalist

