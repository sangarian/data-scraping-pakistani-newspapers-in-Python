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

query=input('Enter the word you wish to query: ')

url='https://www.dawn.com/'

#block the notification pop up window
chrome_options = Options()
chrome_options.add_experimental_option("prefs", { "profile.default_content_setting_values.notifications": 1})
driver=webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(10)
#get the url
driver.get(url)
#click on the search bar
driver.find_element_by_xpath('/html/body/header/div[3]/div/div[1]/ul/li/button/img').click()
#query the page and press enter
driver.find_element_by_xpath('//*[@id="q"]').send_keys(query+'\n')
time.sleep(5)
lst_dawn=list()
content=driver.find_elements_by_css_selector('.gsc-webResult.gsc-result')
for link in content:
    fua=link.find_element_by_tag_name('a')
    lst_dawn.append(fua.get_attribute('href'))

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
        datun=str(dates[1]).split()
        quoted = re.compile('"([^"]*)"')
        for value in quoted.findall(datun[3]):
            date_updated=value
            print(date_updated)
    except IndexError:
        dates=link_soup.select('span[class*="story__time"]')
        datun=str(dates[0])
        quoted = re.compile('>([^>]*)</')
        for value in quoted.findall(datun):
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
    df.to_csv('dawn_articles.csv', index=False, encoding='utf-8')
   
