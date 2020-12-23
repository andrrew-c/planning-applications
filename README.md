# planning-applications

 Scraping and analysis of planning data using local authority portals
 
# Requirements
selenium - currently using Chrome drive

beautiful soup (bs4)

# Getting Started

The file **master-planning-wrapper** is used to get key parameters and kick of the main loop. 

The main loop is in the module planning_functions.py

## .data 

All outputs will be written to a folder in the main directory called .data

The .data folder should hold a text file called 

### .data/params.txt

params.txt is in a json format to read into a python dictionary by the module **master-planning-wrapper**.

Read in by the function getArgs.

Format

{"urlbase":string}

### urlbase: string value of URL for main planning portal page

## master-planning-wrapper

Loads major parameters and kicks of main loop.

## planning-functions

Key functions used by scraper

## planning-database

Python module to create a SQLite3 database and update it. 

