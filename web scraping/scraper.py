from urllib.request import urlopen
from bs4 import BeautifulSoup


class Article:
    def __init__(self, title=None, link=None):
        self.title = title
        self.link = link

    def title(self):
        return self.title

    def link(self):
        return self.link


def main():
    # You can assign articles to an Array based on URL into the arraylist[] or you can use on RSS feed (commented out
    # below)
    
    articlelist = []

    NEWS_URL = "https://news.google.com/rss/search?gl=US&hl=en-US&q=politics|nation&ceid=US:en"

    news(NEWS_URL, articlelist)

    printObject(articlelist)

    # articlelist.append(Article("Impeachment live updates: House Judiciary panel poised to debate articles of
    # impeachment against Trump tonight",
    # "https://www.washingtonpost.com/politics/trump-impeachment-live-updates/2019/12/11/a5b7a6be-1c03-11ea-b4c1
    # -fd0d91b60d9e_story.html"))

    printObject(articlelist)

    scrapeURL(articlelist)


def news(xml_news_url, articlelist):
    parse_xml_url = urlopen(xml_news_url)
    xml_page = parse_xml_url.read()
    parse_xml_url.close()

    soup_page = BeautifulSoup(xml_page, "xml")
    news_list = soup_page.findAll("item")

    for getfeed in news_list:
        articlelist.append(Article(getfeed.title.text, getfeed.link.text))
def printObject(articlelist):
    for Article in articlelist:
        print("\nImporting:")
        print(' %s' % Article.title)
        print(' %s' % Article.link)
    print("Importing Complete\n")


def scrapeURL(articlelist):
    count = 0
    filename = 'scrapedData'
    for Article in articlelist:
        count += 1
        url = Article.link
        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        f = open((filename + str(count) + '.txt'), 'w', encoding="utf-8")

        # now we start with the parsing of the website's content ****[WIP]****
        for p in soup.find_all('p'):
            text = p.text
            if text.isalpha:
                f.write(text + '\n')

        f.close()
        print("textfile " + str(count) + " complete\n")


if __name__ == '__main__':
    main()