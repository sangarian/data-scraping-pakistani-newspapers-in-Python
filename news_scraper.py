import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import urllib.request, urllib.parse, urllib.error
import ssl
from urllib.request import Request, urlopen
import re

#BE SURE TO DOWNLOAD THE VERSION OF CROME WEBDRIVER THAT CORRESPONDS TO YOUR CURRECT CROME BROWSER. 
#TO SEE WHICH VERSION OF CROME YOU ARE USING CLICK ON THE THREE DOTS WIDGET IN THE TOP RIGHT CORNER OF YOUR BROWSER, SCROLL TO 'HELP" AND CLICK ON 'ABOUT GOOGLE CROME'.
#WEBDRIVER CAN BE DOWNLOADED HERE: https://sites.google.com/chromium.org/driver/downloads?authuser=0

query=input('Enter the word you wish to query: ')

url='https://www.dawn.com/search'

#block the notification pop up window
chrome_options = Options()
chrome_options.add_experimental_option("prefs", { "profile.default_content_setting_values.notifications": 1})
driver=webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(10)
#get the url
driver.get(url)
#click on the search bar
driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/form/div/input').click()
time.sleep(10)
#query the page and press enter
driver.find_element_by_xpath('/html/body/div[2]/div/div/div/div/form/div/input').send_keys(query+'\n')
time.sleep(5)
lst_dawn=list()
content=driver.find_elements_by_css_selector('.gsc-expansionArea')
print(content)

for link in content:
    fua=link.find_element_by_tag_name('a')
    lst_dawn.append(fua.get_attribute('href'))

#loop through multiple pages and fetch the Data
max_p=10
for i in range(1,max_p):
    time.sleep(10)
    pages=driver.find_elements_by_css_selector("div[class^='gsc-cursor-page']")
    driver.execute_script("(arguments[0]).click();", pages[i])
    time.sleep(3)
    con='cont'+str(i)
    con=driver.find_elements_by_css_selector('.gsc-webResult.gsc-result')
    for link in con:
        fua=link.find_element_by_tag_name('a')
        lst_dawn.append(fua.get_attribute('href'))
driver.quit()
print(lst_dawn)

#Loop through every link in the list and fetch the article Data
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

records_dawn= []
sum=0
for link in lst_dawn:
    #GET TITLE OF THE ARTCILE
    url=link
    req= Request(link,headers={'User-Agent': 'Mozilla/5.0'})
    link_r= urlopen(req, timeout=60, context=ctx).read()
    link_soup=BeautifulSoup(link_r,'html.parser')
    title=link_soup.find('title')
    title=str(title)
    quoted = re.compile('>([^>]*)</')
    for value in quoted.findall(title):
        title=value
        sum=sum+1
    print(title)
    print(url)
    print(sum)

    #GET THE DATE OF PUBLICATION
    try:
        dates=link_soup.select('span[class*="timestamp"]')
        datun=str(dates[3]).split()
        quoted = re.compile('"([^"]*)"')
        for value in quoted.findall(datun[3]):
            date_updated=value
            print(date_updated)
    except IndexError:
        dates=link_soup.select('span[class*="story__time"]')
        datun=str(dates).split()
        quoted = re.compile('="([^"]*)"')
        for value in quoted.findall(datun[9]):
            date_updated=value
            print(date_updated)

    #GET THE CONTENT OF THE Body
    link_soup.select('div[class*="story__content overflow-hidden"]')
    article_body=list()
    for cont in link_soup.find_all('p'):
        article_body.append(cont.string)
    records_dawn.append((url, title, date_updated,article_body))
    print('done')

    df = pd.DataFrame(records_dawn, columns=['url', 'title', 'date_updated', 'article_body'])
    df.to_csv('dawn_articles'+query+'.csv', index=False, encoding='utf-8')

 

#NOW LETS LOOK FOR ARTICLES PUBLISHED ON THE TOPIC OF INEREST IN ANOTHER NEWSPAPER (THE NATION)

url1='https://cse.google.com.pk/cse?cx=partner-pub-2495428981136420:9301056575&ie=UTF-8&q='+'query'+'&ref='
driver = webdriver.Chrome()
driver.get(url1)
content=driver.find_elements_by_css_selector('.gsc-table-result')
lst_nation=list()
for link in content:
    fua=link.find_element_by_tag_name('a')
    lst_nation.append(fua.get_attribute('href'))
print(lst_nation)

max_p=10
for i in range(1,max_p):
    pages=driver.find_elements_by_css_selector("div[class^='gsc-cursor-page']")
    driver.execute_script("(arguments[0]).click();", pages[i])
    time.sleep(3)
    con='cont'+str(i)
    con=driver.find_elements_by_css_selector('.gsc-table-result')
    for link in con:
        fua=link.find_element_by_tag_name('a')
        lst_nation.append(fua.get_attribute('href'))

print(lst_nation)
driver.quit()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

records_nation=[]
sum=0
for link in lst_nation:
    if link is None:
        continue
    else:
        #GET TITLE OF THE ARTCILE
        url=link
        req= Request(link,headers={'User-Agent': 'Mozilla/5.0'})
        link_r= urlopen(req, context=ctx).read()
        link_soup=BeautifulSoup(link_r,'html.parser')
        title=link_soup.find('h1')
        if title is None:
            continue
        else:
            title=title.get_text()
            sum=sum+1
            print(title)
            print(url)
            print(sum)

        #Get the Publication date
        try:
            date=link_soup.find('p',class_='meta-date')
            date_updated=date.get_text()
        except AttributeError:
            pass
        #Get the Body
        try:
            body=link_soup.find('div', class_='post-content')
            body_text=body.find('p')
            article_body=body_text.get_text()

            records_dawn.append((url, title, date_updated,article_body))
            print('done')
        except AttributeError:
            body=link_soup.find('div', class_='article-body')
            body_text=body.find('p')
            article_body=body_text.get_text()
            records_dawn.append((url, title, date_updated,article_body))
            print('done')
        df1 = pd.DataFrame(records_nation, columns=['url', 'title', 'date_updated', 'article_body'])
        df1.to_csv('nation_articles.csv', index=False, encoding='utf-8')
        print(df1)
   


#NOW LETS LOOK FOR ARTICLES PUBLISHED ON THE TOPIC OF INEREST IN ANOTHER NEWSPAPER (THE NEWS)


url2='https://www.thenews.com.pk/'

chrome_options = Options()
chrome_options.add_experimental_option("prefs", { "profile.default_content_setting_values.notifications": 1})
driver=webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(10)

driver.get(url2)
driver.find_element_by_xpath('//*[@id="search-label"]').click()
driver.find_element_by_xpath('//*[@id="input"]/input').send_keys(query+'\n')
time.sleep(5)

lst_news=list()
content=driver.find_elements_by_css_selector('.gsc-webResult.gsc-result')
for link in content:
    fua=link.find_element_by_tag_name('a')
    lst_news.append(fua.get_attribute('href'))

#loop through multiple pages and fetch the Data
max_p=10
for i in range(1,max_p):
    pages=driver.find_elements_by_css_selector("div[class^='gsc-cursor-page']")
    driver.execute_script("(arguments[0]).click();", pages[i])
    time.sleep(3)
    con='cont'+str(i)
    con=driver.find_elements_by_css_selector('.gsc-webResult.gsc-result')
    for link in con:
        fua=link.find_element_by_tag_name('a')
        lst_news.append(fua.get_attribute('href'))
print(lst_news)
driver.quit()

#Loop through the urls in the list and fetch the category, publication_date, author's name, title, and content of the article

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

records_thenews=[]
sum=0
for link in lst_news:
    #GET TITLE OF THE ARTCILE
    url=link
    req= Request(link,headers={'User-Agent': 'Mozilla/5.0'})
    link_r= urlopen(req, context=ctx).read()
    link_soup=BeautifulSoup(link_r,'html.parser')
    try:
        value=link_soup.find('h1')
        title=value.get_text().rstrip()
        print(title)
    except AttributeError:
        print('exception alert')
        print(url)
        continue

    #GET DATE OF PUBLICATION
    try:
        date=link_soup.find('div',class_='category-date')
        date_updated=date.get_text().rstrip()
        print(date_updated)
    except AttributeError or IndexError:
        date=link_soup.select('div[class*="time"]')
        datun=str(date[0])
        quoted = re.compile('>([^>]*)</')
        for value in quoted.findall(datun):
            date_updated=value.rstrip()
            print(date_updated)
    #GET THE CONTENT OF THE BODY
    article_body=list()
    try:
        body=link_soup.find('div',class_='story-detail')
        content=body.get_text().rstrip()

    except AttributeError:
        if link_soup.find('div',class_='detail-desc') is None:
            body=link_soup.find('div', class_='detail-content')
            content=body.get_text().rstrip()
        else:
            body=link_soup.find('div',class_='detail-desc')
            content=body.get_text().rstrip()
    sum=sum+1
    records_thenews.append((url, title, date_updated,content))
    print('done')

    df2 = pd.DataFrame(records_thenews, columns=['url', 'title', 'date_updated', 'article_body'])
    df2.to_csv('thenews_articles.csv', index=False, encoding='utf-8')
    print(df2)
