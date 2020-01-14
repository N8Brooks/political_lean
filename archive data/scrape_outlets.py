#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Driver code calls source scrape for every url in outlet_bias.csv. Uses wayback
machine to get all articles historically. Does not do a unique article twice.
Makes sure the article is written in english. Replaces all whitespace with a
single space. 
"""

from datetime import date, timedelta
from tqdm import tqdm
from newspaper import build
from langdetect import detect
import pandas as pd
import multiprocessing as mp
import datetime
import tldextract
import re
import time
import pymongo

process_count = 72

min_date = date(2010, 1, 1)
max_date = date(2020, 1, 13)
delta = timedelta(days = 1)

def source_scrape(url):
    """
    Parameters:
        url (str): a url to get the articles for every date between min and max
            and add them to the database. 
    """
    
    # connect to db
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient['outlet_data']
    outlet = mydb[url]
    
    # memoize downloaded and parsed articles
    memo = {x['_id'] for x in outlet.find()}
    
    # get start date (start where you left off, otherwise start at min_date)
    try:
        cur_date = max(x['date'] for x in outlet.find()).date()
    except:
        cur_date = min_date
    
    # the domain of the url
    domain = tldextract.extract(url).domain
    
    # where to store the articles
    articles = list()
    
    # loop through dates
    while cur_date <= max_date:
        # date string
        tmp_date = cur_date.strftime("%Y%m%d")
        cur_datetime = datetime.datetime.combine(cur_date, datetime.time.min)
        
        try:
            # try to find articles on wayback machine
            check = f'https://web.archive.org/web/{tmp_date}/https://{url}'
            paper = build(check, memoize_articles = False, fetch_images =False,
                          follow_meta_refresh = True, keep_article_html = True)
        
        except:
            cur_date += delta
            continue
        
        for a in paper.articles:
            try:
                # replace with original url's articles
                a.url = a.url[-a.url[::-1].index('ptth')-4:]
                
                # skip if article has already been processed - collisions okay
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
                                 '_id':a.url, 'date':cur_datetime})
            
            except:
                continue
        
        # update cur_date
        cur_date += delta

    # stop if it got no articles
    if not articles:
        return

    # add to db
    outlet.insert_many(articles, ordered=False)

if __name__ == '__main__':
    # site url, bias of site based on argv[1]
    sites = pd.read_csv('outlet_bias.csv', index_col='Unnamed: 0')
    
    # tqdm progress bar
    pbar = tqdm(total=len(sites))
    
    # with pool call each site
    with mp.Pool(process_count) as p:
        results={url:p.apply_async(source_scrape, (url,)) for url in sites.url}
        
        # sites that are being run or have yet to run
        incomplete = sites.url.tolist()
        
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
    
    
    
    
    
    
    