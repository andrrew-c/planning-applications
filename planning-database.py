import pdb

import sqlite3
import os, sys
import pickle

from tqdm import tqdm

## Database name
dbname = 'plan-applications.db'

# Data path
datapath = '.data'

def getFileNames(prefix):

    """ Returns list of files that match prefix"""

    # List files in directory    
    ldir = os.listdir()

    # Files that have prefix
    files = [f for f in ldir if f[:len(prefix)]==prefix]

    return files

def getAllColumns(files):

    """ Loop through files and get all column names """

    cols = []

    # Loop through each file
    for file in tqdm(files, desc="Processing file"):

        # Create dataframe
        with open(file, 'rb') as f: df = pickle.load(f)

        # List of new cols
        newCols = df.columns.to_list()
        
        cols.extend(newCols)

        # Make list unique
        cols = list(set(cols))
        
    return cols


def createTables(con, cols):

    """ With dataframe and db connection - create tables, if not already existing"""

    # SQL statement to create tables   
    sql = """ CREATE TABLE IF NOT EXISTS applications (
                {} STRING
                )
                


                
            """.format(' STRING,\n'.join(cols))
    #print(sql)

    # Execute SQL
    c = con.cursor().execute(sql)
    con.commit()

def dumpDuplicates(df):

    """ Output duplicate IDs to text file"""
    
    # Check for duplicate reference numbers
    dup = df[df.duplicates('Reference')].copy()

    # If there's at least one duplicate
    if dup.shape[0] >0:

        # Output with index to existing file
        dup.to_csv(dupfile, mode='a', header=False)
        

def updateDB(con, df):


    """ Update SQLITE database.
        Single dataframe
        For each application in dataframe, check whether the reference is in the applications table.
        If not, insert the row into the table.
    """

    c = con.cursor()

    sqls = []
    
    # Drop duplicate rows (entire duplicates: OK to drop)
    dfc = df.drop_duplicates().copy()
    #dumpDuplicates(dfc)

    # Get columns
    cols = df.columns
 
    for i in tqdm(range(dfc.shape[0])):

        #print(i)
        # Single reference
        ref = dfc.iloc[i].Reference

        # SQL to check whether reference is already in table
        sql = """SELECT reference
                FROM applications
                WHERE reference = "{}"
                GROUP BY reference""".format(ref)

        # Execute and return
        c.execute(sql)
        res = c.fetchall()

        # No match found, continue
        if len(res) == 0:

            # Update DB
            sql = """
                        INSERT INTO applications ({})
                        VALUES ({})
                        
                        
                    """.format(', '.join(cols), (', '.join('"' + str(item).replace('"',"'") + '"\n' for item in dfc.iloc[i])))

            c.execute(sql)

    # Commit changes
    con.commit()
            
            
        
            
if __name__ == "__main__":

    os.chdir(datapath)
    
    # Get files in folder
    files = getFileNames('data')

    # Get columns for all files
    cols = getAllColumns(files)

    ## Connect to DB
    con = sqlite3.connect(dbname)

    # Create tables
    createTables(con, cols)

    # Update DB with all files
    for file in tqdm(files, desc="Update DB"):
        with open(file, 'rb') as f: df = pickle.load(f)
        
        # Update DB
        updateDB(con, df)
        
    print("Close connection to", dbname)
    con.close()
