#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 10:04:35 2020

@author: nathan
"""

import pymongo
import time
import sys
import re
import requests
import tldextract
import pandas as pd
import datetime as dt
import multiprocessing as mp
from newspaper import build
from langdetect import detect
from tqdm import tqdm
from random import uniform, randrange

wayback_wait = 4.
process_count = 12

min_date = dt.datetime(2010, 1, 1)
max_date = dt.datetime(2020, 1, 14)
delta = dt.timedelta(days = 1)

def download(url, wait):
    # connect to db
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['outlet_data']
    
    # memoize downloaded and parsed articles
    memo = {x['_id'] for x in mydb[url].find()}
    
    # the domain of the url
    domain = tldextract.extract(url).domain
    
    cur_date = min_date
    
    # loop through dates
    while cur_date <= max_date:
        # date string and datetime of current date
        tmp_date = cur_date.strftime("%Y%m%d")
        
        # try to find next wayback snapshot
        try:
            # see if date is available
            response = requests.get(('https://archive.org/wayback/available?ur'
                f'l={url}&timestamp={tmp_date}'))
            if response.status_code == 503 or response.status_code == 429:
                time.sleep(randrange(30, 300))
                continue
            
            # set available snapshot date
            snap_date = dt.datetime.strptime(response.json()[('archived_snapsh'
                'ots')]['closest']['timestamp'][:8], "%Y%m%d")
    
            # update cur_date based on availability
            if snap_date < cur_date:
                cur_date += (cur_date - snap_date)
                continue
            elif snap_date > cur_date:
                cur_date = snap_date
            
            # what url to check
            check = response.json()['archived_snapshots']['closest']['url']
            
            # ruh roh
            if 'archive' not in check:
                print(check)
                check = f'http://web.archive.org/web{check}'
            
            # wait patiently for archive
            while wait.value > time.time():
                time.sleep(uniform(0.37, 3.14))
            wait.value = time.time() + wayback_wait
            
            # build paper
            paper = build(check, memoize_articles = False, fetch_images =False,
                          follow_meta_refresh =False, keep_article_html = True)
        except:
            cur_date += delta
            continue
        
        # where to store the articles
        articles = list()
        
        for a in paper.articles:
            try:
                # replace with original url's articles
                a.url = a.url[-a.url[::-1].index('ptth')-4:]
                
                # skip if article has already been processed
                if a.url in memo:
                    continue
                memo.add(a.url)
                
                # skip if it is not from source url
                if domain != tldextract.extract(a.url).domain:
                    continue
                
                # download and parse
                a.download()
                a.parse()
                
                # skip if it is not english
                if detect(a.text) != 'en':
                    continue
                
                # add article as record
                articles.append({'content':re.sub('\s+',' ',a.text),
                                 '_id':a.url, 'date':cur_date})
            except:
                continue
        
        # stop if it got no articles
        if not articles:
            cur_date += delta
            continue
    
        # add to db
        mydb[url].insert_many(articles, ordered=False)
        
        # update cur_date
        cur_date += delta
    
if __name__ == '__main__':
    sites = pd.read_csv('outlet_bias.csv', index_col='Unnamed: 0')
    sites = sites[sites['bias'] == sys.argv[1]]
    
    wait = mp.Manager().Value('f', time.time())
    
    # with pool call each site
    with mp.Pool(process_count) as p:
        results={url:p.apply_async(download, (url,wait,)) for url in sites.url}
        
        # sites that are being run or have yet to run
        incomplete = list(results)
        
        # tqdm progress bar
        pbar = tqdm(total=len(results))
        
        # update tqdm progress bar
        while incomplete:
            incomp_index = list()
            
            for i, x in enumerate(incomplete):
                if results[x].ready():
                    results[x].get()
                    pbar.set_description(x)
                    pbar.update()
                else:
                    incomp_index.append(i)
            
            pbar.refresh()
            incomplete = [incomplete[i] for i in incomp_index]
            time.sleep(1)
        
        # close pool
        p.close()
        p.join()
    
    # close tqdm progress bar
    pbar.close()