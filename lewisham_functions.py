import os 
import re
from datetime import datetime
import time

import pickle

## Num pages
rgx_showing = re.compile("(?<=-)[0-9]+")
rgx_results = re.compile("(?<=of )[0-9]+")


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
    
    """ Return a dictionary: the total number of results and the number of results/page """
    
 
    if searchResults:

        ## How many results?
        text_results = browser.find_element_by_xpath("//span[@class='showing']").text
        #print(text_results)
        current_results = int(rgx_showing.findall(text_results)[0])
        num_results = int(rgx_results.findall(text_results)[0])

        print("Currently showing up to {}".format(current_results))
        print("There are {:,} results in total".format(num_results))
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
    
    fname = "links_{}_{}.p".format(postcode, datetime.today().strftime('%Y%m%d'))

    # Does a file with a similar name already exist?
    if hrefs==None:
        print("No hrefs provided")
        return None
   

    if not os.path.isfile(fname):
        with open(fname, 'wb') as f: pickle.dump(hrefs, f)
    else:
        print("File '{} already exists.".format(fname))
        #with open(fname, 'rb') as f: hrefs = pickle.load(f)
        
def loadLinks(postcode):
    
    # RegEx to find a file with name
    rgx_fname = re.compile("links_{pc}_[0-9]{{8}}.p".format(pc=postcode))
    
    fname = "links_{}_{}.p".format(postcode, datetime.today().strftime('%Y%m%d'))

    if not os.path.exists(fname):

        print(rgx_fname)
        files =os.listdir()
        fileMatches = [f for f in files if rgx_fname.match(f)]
        #print(len(files))

        # If there's at least one match that isn't today
        if fileMatches != []:
            # Get latest file
            fname = fileMatches[-1]
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
        