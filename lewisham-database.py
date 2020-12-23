import sqlite3
import os, sys
import pickle

from tqdm import tqdm

## Database name
dbname = 'lew-apps.db'

# Data path
datapath = '.data'

# Database path
dbpath = os.path.join(datapath, dbname)

# File holding duplicates
dupname = 'duplicates.csv'
dupfile = os.path.join(datapath, dupname)

# Postcode for df
postcode = 'SE264'
date = '20201206'
dataobj = '{path}/data_{pc}_{dt}.p'.format(path=datapath, pc=postcode, dt=date)


def connectDB(dbname):
    """ Returns connection object"""
    return sqlite3.connect(dbpath)
    

def createTables(con, df):

    """ With dataframe and db connection - create tables, if not already existing"""
   
    # Get columns from dataframe
    cols = df.columns
    
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

    # Get df for specific postcode
    print("Open connection to", dbpath)
    with open(dataobj, 'rb') as f: df = pickle.load(f)

    ## Connect to DB
    con = sqlite3.connect(dbpath)

    # Create tables
    createTables(con, df)

    # Update DB
    updateDB(con, df)
    
    print("Close connection to", dbpath)
    con.close()

