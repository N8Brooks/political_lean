#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 22:52:09 2020

@author: nathan
"""

from datetime import date, timedelta
from tqdm import tqdm
from newspaper import build
from langdetect import detect
from random import uniform
import pandas as pd
import multiprocessing as mp
import re
import time

process_count = 24
archive_max = 8

min_date = date(2010, 1, 1)
max_date = date(2020, 1, 9)
delta = timedelta(days = 1)

# exception safe function for language detection
def try_me(text):
    try:
        return detect(text)
    except:
        return 'xx'

def source_scrape(url):
    # janky method to not redo stuff done
    # helpful when you have to restart this script
    try:
        pd.read_csv(f'./sources/{url}.csv')
        return
    except:
        pass
    
    # df to hold articles
    df = list()
    # current date
    cur_date = min_date
    
    # loop through dates
    while cur_date <= max_date:
        # date string
        tmp_date = cur_date.strftime("%Y%m%d")
        
        try:
            # try to find articles on wayback machine
            check = f'https://web.archive.org/web/{tmp_date}/https://{url}'
            paper = build(check, memoize_articles = False, fetch_images =False,
                          follow_meta_refresh = True, keep_article_html = True)
        
        except Exception as e:
            #print(e)
            #print(f'Skipped site: {url} at {cur_date}')
            cur_date += delta
            continue
        
        for a in paper.articles:
            try:
                # replace with original url's articles
                a.url = a.url[-a.url[::-1].index('ptth')-4:]
                
                # skip if it is an archive blog or something link
                if any(x in a.url for x in ['archive.org', 'twitter.com', 
                                            'facebook.com', 'flipboard.com']):
                    continue
                
                # download and parse
                a.download()
                a.parse()
                
                # add article as record
                df.append({'content':re.sub('\s+', ' ', a.text),
                           'url':a.url, 'date':pd.Timestamp(cur_date)})
            
            except Exception as e:
                pass
                #print(e)
                #print(f'Skipped article: {url} at {cur_date}')
        
        # update cur_date
        cur_date += delta
    
    # no articles found
    if not df:
        #print(f'No articles found for {url}')
        return
        
    # drop duplicates
    df = pd.DataFrame(df)
    df = df.drop_duplicates(subset='content')
        
    # remove non-english articles
    df = df[df.content.apply(try_me) == 'en']
    
    # save as csv
    df.to_csv(f'./sources/{url}.csv')

if __name__ == '__main__':
    # site url, bias of site
    sites = pd.read_csv('outlet_bias.csv', index_col='Unnamed: 0')
    
    # tqdm progress bar
    pbar = tqdm(total=len(sites))
    
    # with pool call each site
    with mp.Pool(process_count) as p:
        results = {url:p.apply_async(source_scrape, (url,))\
                   for url in sites.url.tolist()}
        
        # sites that are being run or have yet to run
        incomplete = sites.url.tolist()
        
        # update tqdm progress bar
        while incomplete:
            incomp_index = list()
            
            for i, x in enumerate(incomplete):
                try:
                    if results[x].successful(): pass
                    pbar.update()
                except ValueError:
                    incomp_index.append(i)
            
            pbar.refresh()
            incomplete = [incomplete[i] for i in incomp_index]
            time.sleep(1)
        
        # close pool
        p.close()
        p.join()
    
    # close tqdm progress bar
    pbar.close()
    
    
    
    
    
    
    