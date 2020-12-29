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

# Open file and read in any parameters
with open('{}/params.txt'.format(datafolder), 'rt') as f: params = json.loads(f.read())
    
            
    
if __name__== '__main__':

    print(sys.argv)
    args = pf.getArgs(sys.argv)
    pf.mainLoop(args)


    
