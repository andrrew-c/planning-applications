import requests

from bs4 import BeautifulSoup as bs
import os, sys
import re

from tqdm import tqdm
from datetime import datetime
import time

import pandas as pd

import pickle

# My functions
import planning_functions as pf

import functions as mf

import json


# Open file and read in any parameters
with open('.data/params.txt', 'rt') as f: params = json.loads(f.read())
    
def getArgs(args):

    """ Return dictionary of arguments passed

        '-b': STRING - brough name, e.g. Southwark, Bromley, Lewisham
        '-p': STRING - postcode
        {'urlbase':url, 'postcode':postcode}
    """

    # Init dictionary
    argsDict = {}

    # Extract borough from arguments
    try:
        borough = args[args.index('-b')+1]

        # Check that borough name doesn't start with '-' for another option
        if borough[0] == '-':
            return 0
    except ValueError:
        print("-b not in argumnets provided by user")
        return 0


    # URL for planning applications        
    urlbase = params[borough]['urlbase']
    argsDict.update({'urlbase':urlbase})
    
    # Get postcode
    bPostcode = False
    for i in range(len(args)):

        # Postcode argument
        if args[i] == '-p' and len(args) >= i+1:
            bPostcode = True
            if args[i+1] != None:
                
                argsDict.update({'postcode':args[i+1]})

    if not bPostcode:
        postcode = input("Please enter a postcode to search, e.g. SE154 for 'SE15 4' ")
        argsDict.update({'postcode':postcode.upper()})

    # Return output of function
    return argsDict
            

    
if __name__== '__main__':

    print(sys.argv)
    args = getArgs(sys.argv)
    pf.mainLoop(args)


    
