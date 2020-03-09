#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 15:53:19 2020

@author: nathan
"""

from newspaper import build
from langdetect import detect
from tqdm import tqdm
import pandas as pd
import multiprocessing as mp
import datetime
import tldextract
import re
import time
import pymongo

process_count = 16

def source_scrape(url):
    """
    Parameters:
        url (str): a url to get the articles for every date between min and max
            and add them to the database. 
    """
    
    # connect to db
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['outlet_data']
    
    # memoize downloaded and parsed articles
    memo = {x['_id'] for x in mydb[url].find()}
    
    # the domain of the url
    domain = tldextract.extract(url).domain
    
    # where to store the articles
    articles = list()
    
    # try to find articles
    try:
        paper = build(f'https://{url}', memoize_articles = False,
                      fetch_images = False, follow_meta_refresh = False, 
                      keep_article_html = True)
    except:
        return 0
    
    for a in paper.articles:
        try:
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
                             '_id':a.url, 'date':datetime.datetime.today()})
        
        except:
            continue

    # stop if it got no articles
    if not articles:
        return 0

    # add to db
    mydb[url].insert_many(articles, ordered=False)
    
    # force garbage collection to free up ram
    ret = len(articles)
    del articles, paper, memo
    
    return ret

if __name__ == '__main__':
    # site url, bias of site based on argv[1]
    sites = pd.read_csv('outlet_bias.csv', index_col='Unnamed: 0')
    
    # with pool call each site
    with mp.Pool(process_count) as p:
        results={url:p.apply_async(source_scrape, (url,)) for url in sites.url}
        
        # sites that are being run or have yet to run
        incomplete = list(results)
        
        # tqdm progress bar
        pbar = tqdm(total=len(results))
        
        total = 0
        
        # update tqdm progress bar
        while incomplete:
            incomp_index = list()
            
            for i, x in enumerate(incomplete):
                if results[x].ready():
                    total += results[x].get()
                    pbar.set_description(x)
                    pbar.update()
                    del results[x]
                else:
                    incomp_index.append(i)
            
            pbar.refresh()
            incomplete = [incomplete[i] for i in incomp_index]
            time.sleep(1)
        
        # close progress bar
        pbar.close()
        
        # close pool
        p.close()
        p.join()
        
    print(f'Found {total} articles.')