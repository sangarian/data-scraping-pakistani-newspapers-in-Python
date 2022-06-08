from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from urllib.request import Request, urlopen
import ssl
import re


url='https://www.thenews.com.pk/'

query=input('Enter the word you wish to query: ')

chrome_options = Options()
chrome_options.add_experimental_option("prefs", { "profile.default_content_setting_values.notifications": 1})
driver=webdriver.Chrome(chrome_options=chrome_options)
driver.implicitly_wait(10)

driver.get(url)
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

    df = pd.DataFrame(records_thenews, columns=['url', 'title', 'date_updated', 'article_body'])
    df.to_csv('dawn_articles.csv', index=False, encoding='utf-8')
    print(df)
