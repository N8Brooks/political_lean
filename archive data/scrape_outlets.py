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
import tldextract
import re
import time
import pymongo
import sys

process_count = 8

min_date = date(2010, 1, 1)
max_date = date(2020, 1, 12)
delta = timedelta(days = 1)

def try_me(text):
    """
    Parameters:
        text (str): an article's content
    Returns:
        str: the language of the article or xx if it wasn't able to parse
    """
    try:
        return detect(text)
    except:
        return 'xx'

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
    df = pd.DataFrame(columns=['content', '_id', 'date'])
    
    # loop through dates
    while cur_date <= max_date:
        # date string
        tmp_date = cur_date.strftime("%Y%m%d")
        
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
                
                # add article as record
                df.loc[df.shape[0]] = [re.sub('\s+',' ',a.text),a.url,cur_date]
            
            except:
                continue
        
        # update cur_date
        cur_date += delta
    
    # remove non-english articles
    df = df[df['content'].apply(try_me) == 'en']

    # stop if it got no articles
    if not len(df):
        return

    # convert dates to datetimes    
    df.date = df.date.apply(lambda x: pd.Timestamp(x).to_pydatetime())
    
    # add to db
    outlet.insert_many(df.to_dict('records'), ordered=False)

if __name__ == '__main__':
    # site url, bias of site based on argv[1]
    sites = pd.read_csv('outlet_bias.csv', index_col='Unnamed: 0')
    sites = sites[sites.bias == str(sys.argv[1])]
    
    # tqdm progress bar
    pbar = tqdm(total=len(sites))
    
    # with pool call each site
    with mp.Pool(process_count) as p:
        results = dict()
        for url in sites.url:
            results[url] = p.apply_async(source_scrape, (url,))
        
        # sites that are being run or have yet to run
        incomplete = sites.url.tolist()
        
        # update tqdm progress bar
        while incomplete:
            incomp_index = list()
            
            for i, x in enumerate(incomplete):
                try:
                    if results[x].successful():
                        pass
                    else:
                        results[x].get()
                    pbar.update()
                    # del results[x] - are async_results gc-ed? idk ...
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
    
    
    
    
    
    
    