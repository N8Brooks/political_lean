# -*- coding: utf-8 -*-
"""
Created on Mon Dec 23 10:25:15 2019

@author: Nate
"""

import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from tqdm import tqdm
from langdetect import detect
import swifter
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

# read in data and drop duplicate content
df = pd.read_csv('article_data.csv', index_col='Unnamed: 0')
df = df.drop_duplicates(subset='content')

def time_me(date):
    try:
        return pd.Timestamp(date).year == 2019
    except:
        return True

# exception safe function for language detection
def try_me(text):
    try:
        return detect(text)
    except:
        return 'xx'

# remove non english articles
#df['lang'] = df['content'].swifter.allow_dask_on_strings().apply(try_me)
df = df[df['content'].swifter.allow_dask_on_strings().apply(try_me) == 'en']

# under sampling
g = df.groupby('label')
df = g.apply(lambda x: x.sample(g.size().min())).reset_index(drop=True)

# split into train and test datasets, shuffled, equal label amounts
train,test=train_test_split(df,test_size=27045,shuffle=True,stratify=df.label)

