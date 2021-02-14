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

datafolder = 'data'
secsSleep = 1

# Open file and read in any parameters
with open('{}/params.txt'.format(datafolder), 'rt') as f: params = json.loads(f.read())
        
if __name__== '__main__':

    # If user has not provided any other arguments
    if len(sys.argv) == 1:

        # Ask user for a borough name
        userLA = input("Please enter borough name: ")

        # Update 'args' list
        args  = pf.getArgs(params, '-b {}'.format(userLA).split())
        
    # Else, user has provided some arguments
    elif len(sys.argv) > 1:

        print(sys.argv)
        args = pf.getArgs(params, sys.argv)

    # With a borough, get a postcode to search
    if args['postcode'] == '':

        # Nested dictionary of postcodes
        pcdict = pf.getPostCodeDict(args['borough'])


    while args['numIters'] > 0:
        
        # Kick off the main loop
        pf.mainLoop(args)

        print("Time sleep {} seconds".format(secsSleep))
        time.sleep(secsSleep)
        # Reduce number of iterations by one
        args['numIters'] -= 1

        

    


    
#with open('data/data_BR3_20201224.p', 'rb') as f: df = pickle.load(f)
#print(df.Address.iloc[0])
