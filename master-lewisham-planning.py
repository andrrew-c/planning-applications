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
import lewisham_functions as lf

import functions as mf

import json


# Open file and read in any parameters
with open('.data/params.txt', 'rt') as f: params = json.loads(f.read())


## Base URL used for planning applications
urlbase = params['urlbase']

def getArgs(args):

    """ Return dictionary of arguments passed
        '-p': STRING - postcode
    """

    argsDict = {'urlbase':urlbase}
    

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
    return argsDict
            

    
if __name__== '__main__':

    print(sys.argv)
    args = getArgs(sys.argv)
    lf.mainLoop(args)


    
