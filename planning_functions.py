import os
import re
from datetime import datetime
import time

import pandas as pd
import pickle

from functions import initbrowser

# Progress bars
from tqdm import tqdm 

# Beautiful Soup
from bs4 import BeautifulSoup as bs

## Num pages
rgx_showing = re.compile("(?<=-)[0-9]+")
rgx_results = re.compile("(?<=of )[0-9]+")

import pdb

datafolder = 'data'


pcsearchfile = '{}/postcodes-searched.txt'.format(datafolder)



def getArgs(params, args):

    """ Return dictionary of arguments passed

        args - List of options
            -b: Mandatory - borough
            -p: Optional - postcode to search, if not provided, will ask for it
            
        '-b': STRING - brough name, e.g. Southwark, Bromley, Lewisham
        '-p': STRING - postcode
        {'urlbase':url, 'postcode':postcode}
    """

    # Init dictionary
    argsDict = {}

    # Init postcode to null string
    postcode = ''

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

        # Postcode argument found
        if args[i] == '-p' and len(args) >= i+1:
            bPostcode = True
            if args[i+1] != None:
                
                argsDict.update({'postcode':args[i+1]})


    # Default - one loop
    numIters = 1
    # Get number of iterations
    for i in range(len(args)):

        if args[i] == '--num' and len(args) >= i+1:
            numIters = int(args[i+1])

    # Update dictionary
    argsDict.update({'borough':borough, 'postcode':postcode.upper(), 'numIters':numIters})

    # Return output of function
    return argsDict

def makeSearch(postcode, browser):

    """ Take postcode and search for it using the browser"""
    
    ## With browser object make search
    searchbox = browser.find_element_by_id('simpleSearchString')

    searchbox.clear()
    ## Send postcode to box
    searchbox.send_keys(postcode)

    ## Submit
    submit_button = browser.find_element_by_xpath("//input[@type='submit'][@class='button primary']")
    
    ## Click it!
    submit_button.click()


def hasMultipleResults(browser):
    checkstring = "Application Summary"
    
    # If we have a single match (i.e. no page of results)
    if browser.page_source.find(checkstring) != -1:
        return False
    
    # Else, we have multiple results
    else:
        return True
    
def makeResults100(browser):
    
    """ Change results page to show 100 per page """

    numresults = browser.find_element_by_xpath("//select[@id='resultsPerPage']")
    numresults.send_keys('100')
    browser.find_element_by_xpath("//input[@type='submit']").click()

def getResultNumber(browser, searchResults):

    import pdb
    
    """ Return a dictionary: the total number of results and the number of results/page """
 
    if searchResults:
        
        # Are all results on one page?
        text_results = browser.find_elements_by_xpath("//span[@class='showing']")
        if len(text_results) == 0:
            # Need to find element which holds list
            current_results = len(browser.find_elements_by_xpath("//li[@class='searchresult']"))
            num_results = current_results
            
            print("Currently showing all results of {:,}".format(current_results))
            print("There are {:,} results in total".format(num_results))
                
            
        

        # Results are over at least 2 pages
        else:

            ## How many results?
            text_results = browser.find_element_by_xpath("//span[@class='showing']").text
            #print(text_results)
            current_results = int(rgx_showing.findall(text_results)[0])
            num_results = int(rgx_results.findall(text_results)[0])

            print("Currently showing up to {}".format(current_results))
            print("There are {:,} results in total".format(num_results))
    # Else, single result
    else:
        current_results = 1
        num_results = 1
        
    return {'num_results':num_results, 'current_results':current_results}
    
    
    
def getSearchResults(browser, searchResults, resultPages):
    """ Returns a list of hrefs """
    
    hrefs = []
    
    current_results = resultPages['current_results'] 
    num_results = resultPages['num_results']
    
    if searchResults:
        
        ## First page
        links = browser.find_elements_by_xpath("//li[@class='searchresult']")
        hrefs = [l.find_element_by_tag_name('a').get_attribute('href') for l in links]
        # print(len(links))
        # print(len(hrefs))
        #links[0].find_element_by_tag_name('a').get_attribute('href')

        # Init keepGoing flag
        keepGoing = True if current_results < num_results else False
        
        #print("Keep going = {}".format(keepGoing))
        while keepGoing==True:    

            #print(current_results)
            ## Find 'next' button
            nbutton = browser.find_element_by_xpath("//a[@class='next']")
            nbutton.click()
            links = browser.find_elements_by_xpath("//li[@class='searchresult']")
            hrefs.extend([l.find_element_by_tag_name('a').get_attribute('href') for l in links])
            #print("Sleep 1 seconds")
            time.sleep(1)


            ## Find results and update
            text_results = browser.find_element_by_xpath("//span[@class='showing']").text
            current_results = int(rgx_showing.findall(text_results)[0])
            keepGoing = True if current_results < num_results else False
            #print("Keepgoing updated to {}".format(keepGoing))

        # How many links have we got?
        print("Extracted {:,} links".format(len(hrefs)))
        return hrefs
    
def saveLinks(hrefs, postcode):

    """ With a list of hrefs, let's save as pickled object"""

    # Out postcode
    outPC = postcode.replace(' ', '_')
    if postcode.find(' ') == -1:
        outPC = outPC + '_'
        
    
    fname = "{}/links_{}_{}.p".format(datafolder, outPC, datetime.today().strftime('%Y%m%d'))

    # Does a file with a similar name already exist?
    if hrefs==None:
        print("No hrefs provided")
        return None
   

    if not os.path.isfile(fname):
        with open(fname, 'wb') as f: pickle.dump(hrefs, f)
    else:
        print("File '{}' already exists.".format(fname))
        #with open(fname, 'rb') as f: hrefs = pickle.load(f)
        
def loadLinks(postcode):

    
    # RegEx to find a file with name
    rgx_fname = re.compile("links_{pc}_[0-9]{{8}}.p".format(pc=postcode))
    
    fname = "{}/links_{}_{}.p".format(datafolder, postcode, datetime.today().strftime('%Y%m%d'))
    
    # If file doesn't exist
    if not os.path.exists(fname):

        print(rgx_fname)
        
        os.chdir(datafolder)
        files =os.listdir()
        fileMatches = [f for f in files if rgx_fname.match(f)]
        os.chdir('..')
        #print(len(files))

        # If there's at least one match that isn't today
        if fileMatches != []:
            # Get latest file
            fname = '{}/{}'.format(datafolder, fileMatches[-1])
        else:
            print("No hrefs file with today's date or another exists")
            return None
            
   
    # ask user if they want to open any file
    ck = input("Do you want to open {}?\n".format(fname))

    # If yes open
    if ck.upper() == 'Y':
        with open(fname, 'rb') as f: hrefs = pickle.load(f)
        print("Loaded hrefs with {:,} entries".format(len(hrefs)))
        return hrefs
    else:
        return None
    
def GetTableFromPage(browser, transp=True):
    
    """ Assumes a live browser object (selenium)
        returns a table extracted from the HTML
    """
    
    # Init table
    table = None
    
    # Let's load a table into a pd dataframe
    html = browser.page_source
    soup = bs(html, 'html.parser')
    div = soup.find('table')
    if div !=None:
        table = pd.read_html(str(div))[0]
        #table.iloc[:,0]
        #table.columns = table.iloc[:,0]
        #table.drop(index=0, inplace=True)
        if transp:
            table = table.transpose() 
        table.columns =table.iloc[0,:]
        table.drop(index=0, inplace=True)
    return table

def tabletoDF(browser, tabs, app=None):

    """ Get table from page (selenium browser) and transform it into a dataframe"""

    ## Initiliase table
    table = GetTableFromPage(browser)
    
    ## Save URL
    table.url = app

    ## Iterate over remaining tab names
    for t in tabs[1:]:

        #print(t)
        xp = "//span[contains(text(), '{}')]".format(t)

        btn = browser.find_element_by_xpath(xp)
        tabLink = btn.find_element_by_xpath('./..').get_attribute('href')
        browser.get(tabLink)
        newTable = GetTableFromPage(browser)

        if str(type(newTable)) == "<class 'pandas.core.frame.DataFrame'>":
            ## Update column names if already in table
            newColumns = ['{}_{}'.format(t.replace(' ', '_'), c) if c in table.columns else c for c in newTable.columns]
            newTable.columns = newColumns

            table = table.merge(newTable, 'outer', left_index=True, right_index=True)
            

    # Remove all spaces from col names
    newColumns = [col.replace(' ', '_') for col in table.columns]
    table.columns = newColumns

    return table

    

def getDetailsMultiplePages(browser, links, singlePage=False):
    
    """
        Loops over multiple pages to get information from the links
    """
    
    tabs = "Summary,Further Information,Contacts,Important Dates".split(',')
    
    ## Initialise dataframe
    df = pd.DataFrame()

    if singlePage:

        df = tabletoDF(browser, tabs)

    else:
        i = 0
        for link in tqdm(links):
            i += 1

            # Load up application
            app = link
            
            try:
                browser.get(app)

                t1 = tabletoDF(browser, tabs, app)
                ## If df hasn't been updated yet
                if df.shape[0] == 0:
                    df = t1.copy()
                else:

                    ## Add on row
                    df = df.append(t1, sort=False)

                time.sleep(1)
            except: 
                pass
            
        
    return df
            
def saveApplicationInfo(df, postcode):
    
    """ Save the application information that has been scraped by getDetailsMultiplePages """

    # Out postcode
    outPC = postcode.replace(' ', '_')
    if postcode.find(' ') == -1:
        outPC = outPC + '_'
        
    fname = "{}/data_{}_{}.p".format(datafolder, outPC, datetime.today().strftime('%Y%m%d'))
    
    if os.path.exists(fname):
        print("File '{}' already exists'")
    else:

        with open(fname, 'wb') as f: pickle.dump(df, f)    

def updatePostcodeLog(postcode, borough):

    with open(pcsearchfile, 'at') as f: f.write('{},{}\n'.format(postcode,borough))
    
def hasAResult(browser):

    """ Returns True is there's at least one application for the searched for postcode
        browser - selenium browser object
    """
    els = browser.find_elements_by_xpath("//li[contains(text(), 'No results found.')]")
    if len(els) >0 :
        return False
    else:
        return True

def mainLoop(args, bloadLinks=False):

    """
        Run main program for getting planning application data.

        args - DICT
        bloadLinks - BOOLEAN


        -- Steps --
        - Get information fromm args DICT
            Get url for borough portal and get borough name

        - Initialise browser for scraping

        - postcode - get next postcode in loop (based on result of a function

        - Make a search for this postcode and check whether there are any results

        - Check if the results are all on one page, or across multiple

        - 
    """


    # Extract arguments from arguments dictionary
    urlbase = args['urlbase']

    # Borough
    borough = args['borough']
    
    ## Init browser object on planning page
    browser = initbrowser(urlbase)

    # Get a postcode
    postcode = getNextPostcode(browser, borough)

    ## With browser object make search
    makeSearch(postcode, browser)

    # If there's at least one result for this postcode
    if not hasAResult(browser):
        print("Postcode '{}' has no results".format(postcode))
        input("Press enter to exit.")
        return 0
    
    # Boolean - did the search return multiple results or a single application
    searchResults = hasMultipleResults(browser)
    print("Searchresults - has multi")

    # If search results
    if searchResults:

        print("Had search results")

        # Update results page to show 100/page
        makeResults100(browser)

        # Create dictionary of number of results
        resultPages = getResultNumber(browser, searchResults)

        # If user specified to NOT load links
        if not bloadLinks:
            # Get Links for apps: Iterate through all search pages and get links
            hrefs = getSearchResults(browser, searchResults, resultPages)

            # Save links to pickled object
            saveLinks(hrefs, postcode) #os.path.abspath(os.curdir)

        # User thinks pickled object already exists
        else:

            print("Let's load up links")
            hrefs = loadLinks(postcode)
            

        # With links, create dataframe
        if hrefs != None:
            df = getDetailsMultiplePages(browser, hrefs)
            
        else:
            print("Error - no hrefs loaded up")
          

    ## Else, there's only one application for the given postcode
    else:

        df = getDetailsMultiplePages(browser, None, True)
      
    print("df shape =", df.shape)
        
    # Save application data
    saveApplicationInfo(df, postcode)

    # Add postcode information to log
    updatePostcodeLog(postcode, borough)
    
    # Close browser
    browser.close()
        

def getPostcodes(borough):

    """ Return dataframe read in from csv of postcodes
        borough - STRING - name of borough to match .csv in data folder
    """

    pcfile = '{}/postcodes-{}.csv'.format(datafolder, borough.lower())
    with open(pcfile) as f: df = pd.read_csv(f)
    return df

def processPostcodes(df):

    """ Produce possible postcode combinations.
        For each postcode combination, we want to try the top-most level (least detail)

        For example,
            (1) Most detailed: SE17 2HA
            (2) Less detail:   SE17 2H
            (3) Less detail:   SE17 2
            (4) Least detail:  SE17
    """

    # Exctract postcodes
    pcodes = df.Postcode.copy()
    p1 = pd.concat([pcodes, pcodes.str.split().map(lambda x:x[0])], axis=1)
    p2 = pd.concat([p1, pcodes.str.split().map(lambda x:"{} {}".format(x[0], x[1][0]))], axis=1)
    p3 = pd.concat([p2, pcodes.str.split().map(lambda x:"{} {}".format(x[0], x[1][:2]))], axis=1)

    
    ## Rename columns
    p3.columns = "postcode1,postcode2,postcode3,postcode4".split(',')
    #print(p3.columns)
    p3 = p3[list(p3.columns[1:]) + [p3.columns[0]]].copy()
    p3.columns = "postcode1,postcode2,postcode3,postcode4".split(',')

    return p3


def processPostcodesD(df):

    """ Return a nested python dictionary of postcodes

        Dataframe in format
        
        postcode1    postcode2    postcod3    postcode4
        SE1 0AA      SE1          SE1 0       SE1 0A
        SE1 0AB      .
        .
        .
        .


        Function returns a nested dictionary
        'SE1': {'SE10
    """
    
    ### Init dictionary (postcode dictionary)
    pdict = {}

    # For each high level postcode (e.g. SE17)
    for pc in df.postcode1.unique():
        
        # init sub dictionary
        sdict = {}

        # For each level down (e.g. SE171, SE172, ...)
        subs = df[df.postcode1==pc].postcode1.unique()
        for spc in subs:

            ssdict = {}

            # Get list of unique, most-detailed, postcodes
            subs2 = list(df[df.postcode2==spc].postcode3.unique())

            for sspc in subs2:
                subs3 = list(df[df.postcode3==sspc].postcode4.unique())
                
                # sub-ditionary updated
                ssdict.update({sspc:subs3})
            sdict.update({spc:ssdict})

        # For this postcode2 (e.g. SE17) update dictionary
        pdict.update({pc:sdict})


    return pdict


def getPostCodeDict(borough):


    """ Return dictionary of dictionaries of postcodes given a borough """

    postCodes2 = None
    
    if borough != '':
        
        # Postcode to search (dataframe, original data)
        postcodes_ = getPostcodes(borough)

        # Processed postcodes (dataframe)
        postCodes = processPostcodes(postcodes_)

        # Nested dictionary
        postCodes2 = processPostcodesD(postCodes)

    return postCodes2


def invalidPostcode(browser):
    
    """ Return True if the current search criteria fails due to having too many results
        browser: selenium browser object after a search has been made
    """
    
    # Browser element
    el = browser.find_elements_by_xpath("//li[contains(text(), 'No results found.')]")
    if len(el) > 0:
        return True
    else:
        return False


def tooManyResult(browser):
    
    """ Return True if the current search criteria fails due to having too many results
        browser: selenium browser object after a search has been made
    """
    
    # Browser element
    el = browser.find_elements_by_xpath("//li[contains(text(), 'Too many results found. Please enter some more parameters.')]")
    if len(el) > 0:
        return True
    else:
        return False

    
def findHighestPostcode(browser, urlbase, df):

    """ Go through dictionary of dictionaries to find highest postcode level"""

    # List of highest level of postcodes
    results = []

    i = 0

    if type(dct) == dict:
        
        for k in tqdm(dct):

            i += 1

            print("k = ", k, "i = ", i)

            # Make search with postcode
            makeSearch(k, browser)

            # If postcode is invalid
            if invalidPostcode(browser):
                #print("Ignore where postcode = ", k)
                continue

            # The part of the postcode we've used has worked - this will be saved
            if not tooManyResult(browser):
                print("Result worked for {}".format(k))
                results.append(k)

                print("Browser to get urlbase", urlbase)
                # Bring browser back to search page
                browser.get(urlbase)
            elif type(dct[k]) == dict:
                print("Going down another level... k = ", k)
                results.append(findHighestPostcode(browser, dct[k], urlbase))
                print("Results = ", results)
            elif type(dct[k]) == list:
                print("List of postcodes = ", dct[k])
                return dct[k]
            
        return results

def pcLogHeader():

    # Make file
    with open(pcsearchfile, 'wt') as f: f.write('postcode,borough,check\n')

def pcHasBeenSearched(pc):

    """ Return True if postcode has been searched"""
    
    # If 'searched' log doesn't exist
    if not os.path.isfile(pcsearchfile):
        pcLogHeader()
            
    else:
        # Get searched postcodes
        pcdf = pd.read_csv(pcsearchfile)

        if pcdf[pcdf.postcode==pc].shape[0] >0:
            return True
        else:
            return False
        
def updatePCLog(tipo, pc, borough):

    # If file doesn't exist
    if not os.path.isfile(pcsearchfile):
        # Make file
        pcLogHeader()
        
    if tipo=='invalid':
        strng = 'invalid postcode'
    elif tipo=='toomany':
        strng = 'too many results'

    # Write out to log
    with open(pcsearchfile, 'at') as f: f.write("{},{},{}\n".format(pc, borough, strng))
        
def getNextPostcode(browser, borough):

    """ Finds postcode to search on: Returns a string of postcode with space in middle (if applicable)
        With a browser object find which postcode we can use """
    
    # Load in standard .csv of postcodes
    df1 = getPostcodes(borough)

    # Process postcodes into SE1, SE1 0, SE1 0A, ....
    df2 = processPostcodes(df1)

    # Nested dictionary
    #pcdict = processPostcodesD(df2)

    pclist = df2.postcode1.unique().tolist()

    # Load in processed postcodes
    procList = pd.read_csv(pcsearchfile).postcode.to_list()

    # For each 'main' postcode (e.g. SE1) in the dataframe
    for pc in pclist:

        # If postcode has been searched
        if pcHasBeenSearched(pc):

            # go to next pc in pclist
            continue

        # Else, postcode has not been searched - keep going down
        else:

            # Subset the main df
            dfsubset = df2[df2.postcode1==pc]

            # Iterate through each row
            for r in range(dfsubset.shape[0]):

                # Init skip to false
                skip = False

                # Get row - pd.series
                row = dfsubset.iloc[r]

                # Check whether we should skip this section of postcodes
                for sr in row:
                    
                    if sr in procList:
                        skip = True
                        break

                if skip:
                    continue
                
                # Try main key (pc)
                # Make search with postcode
                makeSearch(pc, browser)

                # If postcode is invalid
                if invalidPostcode(browser):
                    #print("Ignore where postcode = ", k)#
                    updatePCLog('invalid', pc, borough)
                    continue
            
                # The part of the postcode we've used has worked - this will be saved
                if not tooManyResult(browser):
                    print("Result worked for {}".format(pc))
                    return pc
                else:
                    

                    ## POSTCODE 2
                    pc = row.postcode2

                    if pcHasBeenSearched(pc):
                        continue
                    else:
                        
                        # Make search with postcode
                        makeSearch(pc, browser)

                        # If postcode is invalid
                        if invalidPostcode(browser):
                            #print("Ignore where postcode = ", k)
                            #updatePCLog('invalid', pc, borough)
                            continue

                        
                        # The part of the postcode we've used has worked - this will be saved
                        if not tooManyResult(browser):
                            print("Result worked for {}".format(pc))
                            return pc
                        
                            
                        
                        ## POSTCODE 3
                        pc = row.postcode3

                        if pcHasBeenSearched(pc):
                            break
                        else:

                            # Make search with postcode
                            makeSearch(pc, browser)

                            # If postcode is invalid
                            if invalidPostcode(browser):
                                #print("Ignore where postcode = ", k)
                                #updatePCLog('invalid', pc, borough)
                                continue

                            
                            # The part of the postcode we've used has worked - this will be saved
                            if not tooManyResult(browser):
                                print("Result worked for {}".format(pc))
                                return pc
                            else:
                                pass #updatePCLog('toomany', pc, borough)

                            ## POSTCODE 4
                            pc = row.postcode4

                            if pcHasBeenSearched(pc):
                                break
                            else:

                                # Make search with postcode
                                makeSearch(pc, browser)

                                # If postcode is invalid
                                if invalidPostcode(browser):
                                    #print("Ignore where postcode = ", k)
                                    #updatePCLog('invalid', pc, borough)
                                    continue

                                
                                # The part of the postcode we've used has worked - this will be saved
                                if not tooManyResult(browser):
                                    print("Result worked for {}".format(pc))
                                    return pc
                                else:

                                    pass #updatePCLog('toomany', pc, borough)
                                



   
        

