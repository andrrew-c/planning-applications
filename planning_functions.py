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
datafolder = '.data'

def makeSearch(postcode, browser):

    """ Take postcode and search for it using the browser"""
    
    ## With browser object make search
    searchbox = browser.find_element_by_id('simpleSearchString')

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
    
    fname = ".data/links_{}_{}.p".format(postcode, datetime.today().strftime('%Y%m%d'))

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
        
        os.chdir('.data')
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
    
    fname = ".data/data_{}_{}.p".format(postcode, datetime.today().strftime('%Y%m%d'))
    
    if os.path.exists(fname):
        print("File '{}' already exists'")
    else:

        with open(fname, 'wb') as f: pickle.dump(df, f)    


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


    # Extract arguments from arguments dictionary
    postcode = args['postcode']
    urlbase= args['urlbase']
    
    ## Init browser object on planning page
    browser = initbrowser(urlbase)

    ## With browser object make search
    makeSearch(postcode, browser)

    # If there's at least one result for this postcode
    if not hasAResult(browser):
        print("Postcode '{}' has no results".format(postcode))
        input("Press enter to exit.")
        return 0
    
    # Boolean - did the search return multiple results or a single application
    searchResults = hasMultipleResults(browser)

    # If search results
    if searchResults:

        # Update results page to show 100/page
        makeResults100(browser)

        # Create dictionary of number of results
        resultPages = getResultNumber(browser, searchResults)

        # If user specified to NOT load links
        if not bloadLinks:
            # Get Links for apps: Iterate through all search pages and get links
            hrefs = getSearchResults(browser, searchResults, resultPages)

            ## Save links to pickled object
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

    # Close browser
    browser.close()
        

