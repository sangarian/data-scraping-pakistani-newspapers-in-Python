
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from urllib.request import Request, urlopen
import re
import time
import pandas as pd
from bs4 import BeautifulSoup
import ssl



url='https://cse.google.com.pk/cse?cx=partner-pub-2495428981136420:9301056575&ie=UTF-8&q=Ertugrul&ref='
driver = webdriver.Chrome()
driver.get(url)
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

records_dawn=[]
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
        df = pd.DataFrame(records_dawn, columns=['url', 'title', 'date_updated', 'article_body'])
        df.to_csv('nation_articles.csv', index=False, encoding='utf-8')
        print(df)
