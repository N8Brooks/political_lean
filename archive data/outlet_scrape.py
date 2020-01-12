#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Driver code will get the table from the bias_list values, add the key as a 
label, parse the urls from the table, and save to disk as outlet_bias.csv
"""

import requests
import pandas as pd
import re

# dictionary with key of bias and value of site list url
bias_list = {'L':'https://mediabiasfactcheck.com/left/',
              'LC':'https://mediabiasfactcheck.com/leftcenter/',
              'C':'https://mediabiasfactcheck.com/center/',
              'RC':'https://mediabiasfactcheck.com/right-center/',
              'R':'https://mediabiasfactcheck.com/right/'}

def remove_scheme(url):
    """
    Args:
        url (str): url which may or may not contain scheme or ending slash
    Returns:
        str: url without scheme and without ending slash
    """
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    url = url.rstrip('/')
    return url

def grab_table(url):
    """
    Args:
        url (str): mediabiasfactcheck url which should have table of sites
    Returns:
        pandas.core.frame.DataFrame: dataframe with parsed urls from site table
    """
    # get table from url
    html = requests.get(url).content
    df = pd.read_html(html)[0].rename(columns={0: 'url'})
    
    # remove ad spots
    df = df[~df.url.str.contains('adsbygoogle', regex=False)]
    # must contain parenthesis
    df = df[df.url.str.contains('(', regex=False)]
    # get items between parenthesis
    df.url = df.url.apply(lambda s: re.findall('\((.*?)\)', s)[-1])
    # url must contain a dot
    df = df[df.url.str.contains('.', regex=False)]
    # remove scheme
    df.url = df.url.apply(remove_scheme)

    return df

if __name__ == '__main__':
    # dataframe of news outlets and biases
    df = pd.DataFrame()
    
    # add all sites and biases to df
    for bias, url in bias_list.items():
        tmp = grab_table(url)
        tmp['bias'] = bias
        df = df.append(tmp)
    
    # reset the index
    df = df.reset_index(drop=True)
    
    # save to disk
    df.to_csv('outlet_bias.csv')
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    