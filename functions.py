
def initbrowser(url=None, hidebrowser=False):

    """
        Initialises browser to scrape web data
        returns object browser (driver) - selenium object.

        Only needs to be run once per session.#

        url: url to load up
        hidebrowser: Minimise browser if True

        Dependencies: Will require selenium to control a browser.
            This has been developed bsaed on Chrome.  Not sure if other browsers will work (they should!)

        Suggested improvements:
            - Ability for python to pick up an existing session

        Author: Andrew Craik
        Date:   2017/2018?
    """

    ## Import os, system
    import os
    import sys

     
    #############################################
    ## Import selenium
    #############################################import time
    
    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys

    ## Chrome options
    ## Source: https://stackoverflow.com/questions/43149534/selenium-webdriver-how-to-download-a-pdf-file-with-python

    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', {
        #"download.default_directory": r"C:/Users/andre/Desktop", #Change default directory for downloads
        "download.prompt_for_download": False, #To auto download the file
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
        })

    ###############################################
    ## Linux 
    ###############################################
    
    ## If running on linux open up pyvirtualdisplay to open browser
    if sys.platform == 'linux':

        from pyvirtualdisplay import Display

        driver_path = r'/home/public/python/chrome/chromedriver'
        print("NOTE: Driver path for chrome set as '{}'\nThis is hard-coded in '{}'".format(driver_path, os.path.abspath(__file__)))
    
        
        
        disp_size = (1024, 768)
        display = Display(visible=0, size=disp_size)
        display.start()
        
        browser = webdriver.Chrome(driver_path, chrome_options=options)
        
    
    ## Else, on windows - specify path
    else:
        #browser_path = "C:\\Program Files\\Python36\\selenium\\webdriver\\chrome\\chromedriver.exe"
        browser_path = os.environ['CHROME_DRIVER']
        sys.path.append(os.environ['CHROME_DRIVER'])
        print("Opening browser with URL", url)
        browser = webdriver.Chrome(os.environ['CHROME_DRIVER'], chrome_options=options)
        
    


    ##  hide browser
    if hidebrowser: 
        print("Hiding browser - current position (before moving)\n", browser.get_window_position())
        browser.set_window_position(0,10000)
    
    ## Get browser to webpage
    if url != None:
        browser.get(url)
    return browser
