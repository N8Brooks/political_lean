# -*- coding: utf-8 -*-
"""
Created on Fri Dec 20 16:11:49 2019

@author: Nate
"""

import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from tqdm import tqdm
from langdetect import detect
import swifter
from sklearn.utils import shuffle

# read in data and drop duplicate content
R = pd.read_csv('R.csv', index_col='Unnamed: 0').drop_duplicates(subset='content')
RC = pd.read_csv('RC.csv', index_col='Unnamed: 0').drop_duplicates(subset='content')
C = pd.read_csv('C.csv', index_col='Unnamed: 0').drop_duplicates(subset='content')
LC = pd.read_csv('LC.csv', index_col='Unnamed: 0').drop_duplicates(subset='content')
L = pd.read_csv('L.csv', index_col='Unnamed: 0').drop_duplicates(subset='content')

# exception safe function for language detection
def try_me(text):
    try:
        return detect(text)
    except:
        print(text)
        return 'xx'

# remove non english articles
pbar = tqdm(total=5)
R = R[R['content'].swifter.allow_dask_on_strings().apply(try_me) == 'en']
pbar.update(1)
RC = RC[RC['content'].swifter.allow_dask_on_strings().apply(try_me) == 'en']
pbar.update(1)
C = C[C['content'].swifter.allow_dask_on_strings().apply(try_me) == 'en']
pbar.update(1)
LC = LC[LC['content'].swifter.allow_dask_on_strings().apply(try_me) == 'en']
pbar.update(1)
L = L[L['content'].swifter.allow_dask_on_strings().apply(try_me) == 'en']
pbar.update(1)
pbar.close()

"""
# character length 'len' and word length 'count' analysis
R['len'] = R['content'].apply(len)
RC['len'] = RC['content'].apply(len)
C['len'] = C['content'].apply(len)
LC['len'] = LC['content'].apply(len)
L['len'] = L['content'].apply(len)
R['count'] = R['content'].apply(lambda x: len(x.split(' ')))
RC['count'] = RC['content'].apply(lambda x: len(x.split(' ')))
C['count'] = C['content'].apply(lambda x: len(x.split(' ')))
L['count'] = L['content'].apply(lambda x: len(x.split(' ')))
LC['count'] = LC['content'].apply(lambda x: len(x.split(' ')))
"""

# shuffle
L = shuffle(L)
LC = shuffle(LC)
C = shuffle(C)
RC = shuffle(RC)
R = shuffle(R)

# add labels
L['label'] = 'L'
LC['label'] = 'LC'
C['label'] = 'C'
RC['label'] = 'RC'
R['label'] = 'R'

# under sampling
low = min(map(len, [R, RC, C, LC, L]))
R = R[:low]
RC = RC[:low]
C = C[:low]
LC = LC[:low]
L = L[:low]

size = 344
# train and test datasets
train = pd.DataFrame()
test = pd.DataFrame()
for data in [L, LC, C, RC, R]:
    train = train.append(data[-size:], ignore_index=True)
    test = test.append(data[:-size], ignore_index=True)











