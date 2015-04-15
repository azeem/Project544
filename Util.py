from bs4 import BeautifulSoup

def stripTags(html):
    return BeautifulSoup(html).getText()
