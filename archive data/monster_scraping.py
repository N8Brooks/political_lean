# -*- coding: utf-8 -*-
"""
Iterates year downloading specified outlet's data to dataframe
Saves dataframe for every year
Note: newspaper MUST be modified to not cache articles!
"""

from datetime import date, timedelta
from tqdm import tqdm
import newspaper
import pandas as pd
import multiprocessing as mp
import re

# parse sources data and return list of dictionary results
def parse(url, bias, date, paper):
    # parse articles
    try:
        paper.parse_articles()
    
    except Exception as e:
        print(e)
        print('Skipped parsing site: ' + str(url))
        return list()
    
    # appending data to list
    records = list()
    for article in paper.articles:
        try:
            records.append({'content':re.sub('\s+', ' ', article.text),
                          'published':str(article.publish_date),
                          'scraped':date,
                          'authors':article.authors,
                          'url':article.url,
                          'source':url,
                          'title':article.title,
                          'label':bias})
    
        except Exception as e:
            print(e)
            print('Skipped: ' + str(article.url))
    
    # return list of records
    return records

if __name__ == '__main__':
    
    # sites df shows which sites to target
    sites = pd.read_csv('outlet_bias.csv', index_col='Unnamed: 0')
    
    # date information
    cur_date = date.today()
    end_date = date(2011, 12, 31)
    delta = timedelta(days=1)
    save_name = cur_date.year()
    
    # fresh df for start
    df = pd.DataFrame()
    
    # loop through dates
    pbar = tqdm(total=(cur_date - end_date).days)
    while cur_date > end_date:
        # date string
        tmp_date = cur_date.strftime("%Y%m%d")
        
        # save dfs as yearly chunks
        if save_name != cur_date.year():
            df.to_csv(f'{save_name}.csv')
            df = pd.DataFrame()
            save_name = cur_date.year()
        
        # build archive links serially
        papers, info = list(), list()
        for url, bias in zip(sites.url, sites.bias):
            try:
                check = f'https://web.archive.org/web/{tmp_date}/https://{url}'
                paper = newspaper.build(check, follow_meta_refresh = True,
                    memoize_articles=False, fetch_images=False,
                    keep_article_html=False)
                
                # replace archived articles with source's articles
                for a in paper.articles:
                    a.url = a.url[-a.url[::-1].index('ptth')-4:]
                
                # add to list
                papers.append(paper)
                info.append((url, bias))
            
            except Exception as e:
                pbar.write(str(e))
                pbar.write('Skipped site: ' + str(url))
        
        # download in parallel
        newspaper.news_pool.set(papers, threads_per_source = 1)
        newspaper.news_pool.join()
        
        # parse in apply async pool
        with mp.Pool(24) as p:
            results = [p.apply_async(parse, (url, bias, cur_date, paper,)) for\
                (url, bias), paper in zip(info, papers)]
            p.close()
            p.join()
        
        # add data to dataframe
        for res in results:
            df = df.append(pd.DataFrame(res.get()), ignore_index=True)
            df = df.drop_duplicates(subset='content')
        
        # update pbar
        pbar.update(delta.days)
    
    # save final year's df
    df.to_csv(f'{save_name}.csv')
        
        
        
        
        
        
        
        
        
        