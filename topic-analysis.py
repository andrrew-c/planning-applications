import os
import pickle

from tqdm import tqdm

import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation as lda

folder = 'data'
prefix = 'data'


def duplicated_varnames(df):
    """Return a dict of all variable names that 
    are duplicated in a given dataframe.

    Source: https://stackoverflow.com/questions/26226343/pandas-concat-yields-valueerror-plan-shapes-are-not-aligned
    """
    repeat_dict = {}
    var_list = list(df) # list of varnames as strings
    for varname in var_list:
        # make a list of all instances of that varname
        test_list = [v for v in var_list if v == varname] 
        # if more than one instance, report duplications in repeat_dict
        if len(test_list) > 1: 
            repeat_dict[varname] = len(test_list)
    return repeat_dict

def resolve_dupvarnames(df):

    # Cols -> list
    cols = df.columns.to_list()

    # Get repeated col name
    repeats = duplicated_varnames(df)

    if len(repeats) == 0:
        return cols
    else:
        
        # Iterate through each repeated key
        for k in repeats.keys():
            
            # Get indices of repeats
            repeatIdx = [i for i in range(len(cols)) if cols[i] == k]
            

        # Init suffix to 1
        suf = 1
        
        # Rename the 2nd, 3rd,+ with 2, 3, etc. (keep the original name
        for i in repeatIdx[1:]:
            suf+=1
            #print(i, cols[i])
            origName = cols[i]
            newName = '{}_{}'.format(origName, suf)
            cols[i] = newName

        
        return cols
        

    

def combineDFs():

    # Get all files in folder
    listall = os.listdir(folder)

    # Get all files which match prefix
    files = [f for f in listall if f[:len(prefix)]==prefix]
    print("There were {:,} files but we only want {:,}".format(len(listall), len(files)))

    # Init list of dfs
    alldfs = []

    # For each file in list
    for fi in tqdm(files):
        
        path = '{}/{}'.format(folder, fi)
        # Get next df
        with open(path, 'rb') as f:
            df = pickle.load(f)

            # Resolve any duplicate names
            df.columns = resolve_dupvarnames(df)
            
            #repeats = duplicated_varnames(df)
##            if len(repeats) > 0:
##                print("Repeats in {}.\n\n{}".format(f, repeats))

            # Add name of source file
            df.insert(0, 'source', fi)

        # Add to list of DFs
        alldfs.append(df)

    

    # Concat into final df
    finaldf = pd.concat(alldfs, sort=False).reset_index()

    # Drop old index
    finaldf = finaldf.drop(columns='index')

    # Return result
    return finaldf

def topWords(model, vect, numtop):

    # Feature names
    names = np.array(vect.get_feature_names())

    # List of tuples
    topwords = []
    
    for t in range(model.n_components):

        # Get model
        topic = model.components_[t, :]

        # Get top indices
        idx = np.argsort(topic)

        # Reverse list
        idx = idx[::-1][:numtop]

        # feats
        feats = names[idx]

        # Scores
        scores = topic[idx]

        topwords.append((feats, scores))
        #print(feats, scores)
    return topwords

        

        

if __name__ == '__main__':

    # Read in and combine all DFs
    df = combineDFs()
    
    # Initialise vectorizer for text
    vect = TfidfVectorizer(stop_words='english', max_df=0.9, ngram_range=(2,2))

    # Get X
    X = vect.fit_transform(df.Proposal)

    # Initialise LDA
    topic_model = lda(random_state=0)
    print("Initialised lda model")

    # Fit model
    print("Fitting lda model to X")
    topic_model.fit(X)

    # Normalise model
    norm_topic_model = topic_model.components_ / topic_model.components_.sum(axis=1)[:, np.newaxis]

    # Get top words from each topic
    topwords = topWords(topic_model, vect, 10)
