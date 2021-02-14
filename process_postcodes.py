import requests

from bs4 import BeautifulSoup as bs
import os, sys
import re

from tqdm import tqdm
from datetime import datetime
import time

import pandas as pd
import csv

import pickle

# My functions
import planning_functions as pf
import master_planning_wrapper as mpw

import functions as mf

import json


datafolder = 'data'

# Open file and read in any parameters
with open('{}/params.txt'.format(datafolder), 'rt') as f: params = json.loads(f.read())
    
valFile = '{}/valid_searches_{}.csv'

if __name__ == '__main__':

    args = pf.getArgs(params, sys.argv, ignorePostcode=True)

    # Postcode to search (dataframe, original data)
    postcodes = pf.getPostcodes(args['borough'])

    # Processed postcodes (dataframe)
    procCodes = pf.processPostcodes(postcodes)

    # Nested dictionary
    pCodes2 = pf.processPostcodesD(procCodes)

    ## Init browser object on planning page
    browser = mf.initbrowser(args['urlbase'])

    # Valid searches for postcodes
    valSearches = pf.findHighestPostcode(browser, pCodes2, args['urlbase'])


    # List to dataframe, then dataframe to csv
    df = pd.DataFrame(data=valSearches, columns=['postcodes'])
    df.to_csv(valFile.format(datafolder, args['borough'].lower()), index=False)
        
    
