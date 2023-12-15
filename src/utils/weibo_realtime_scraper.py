
from jsonpath import jsonpath  # 解析json数据
import numpy as np
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import pandas as pd
import re
import json
from datetime import datetime
import os

driver = webdriver.Chrome()    

import os
import requests
import pandas as pd
import datetime
from time import sleep
import random
# from fake_useragent import UserAgent
import re



def base62_decode(string, 
                  alphabet= "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"):
    """Decode a Base X encoded string into the number
    Arguments:
    - `string`: The encoded string
    - `alphabet`: The alphabet to use for encoding
    """
    base = len(alphabet)
    strlen = len(string)
    num = 0
    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += alphabet.index(char) * (base ** power)
        idx += 1
    return num

def id2mid (id):
    id = str (id)[::-1]
    size = int (len (id) / 4) if len (id) % 4 == 0 else int (len (id) / 4 + 1)
    result = []
    for i in range (size):
        s = id [i * 4: (i + 1) * 4][::-1]
        s = str (base62_decode(str (s)))
        s_len = len (s)
        if i < size - 1 and s_len < 7:
            s = (7 - s_len) * '0' + s
        result.append (s)
    result.reverse ()
    return ''.join (result)

def get_mid(link:str) -> str:
    s1 = link.split('?')[0]
    sid = s1.split('/')[-1]
    mid = id2mid(sid)
    return mid

def get_uid(link:str)->str:
    s1 = link.split('?')[0]
    uid = s1.split('/')[-2]
    return uid


def Scrape_realtime_weibo_by_keyword(driver, keyword, folder_path, page_count):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = folder_path + '/' + f'{keyword}' + '_realtime_posts.csv'

    # Remove original file if it already exists
    if os.path.exists(filename):
        os.remove(filename)

    sourceweb = 'https://s.weibo.com/weibo'

    # Add parameters to the source web to a) simulate keyword researching; b)ensure the posts are sorted by publish date to get the latest posts
    url_with_query = sourceweb + '?' + "q=" + keyword + "&nodup=1"
    driver.get(url_with_query)
      

    for page in range(page_count):

        # Get three sets of nodes from the query result page
        nodes1 = driver.find_elements(By.CSS_SELECTOR,'div.card > div.card-feed > div.content')
        nodes2 = driver.find_elements(By.CSS_SELECTOR,'div.card > div.card-act')
        nodes3 = driver.find_elements(By.CSS_SELECTOR,'div.card > div.card-feed > div.avator')
        
        for i in range(0,len(nodes1),1):

            # The dynamic website will fold long posts
            # To scrape the full post, check whether there's a button starting with 'unfold'; if so, click to unfold the content
            flag = False
            try:
                nodes1[i].find_element(By.CSS_SELECTOR,"p>a[action-type='fl_unfold']").is_displayed()
                flag = True 
            except:
                flag = False

            if (flag and nodes1[i].find_element(By.CSS_SELECTOR,"p>a[action-type='fl_unfold']").text.startswith('展开c')):
                nodes1[i].find_element(By.CSS_SELECTOR,"p>a[action-type='fl_unfold']").click()
                content = nodes1[i].find_element(By.CSS_SELECTOR,'p[node-type="feed_list_content_full"]').text
            else:
                content = nodes1[i].find_element(By.CSS_SELECTOR,'p[node-type="feed_list_content"]').text


            # Special identity verification, such as [institution account] [government account] [influencer account] will be displayed through user icon annotation. 
            # Check whether the post user displays some verification and scrape the title of their identity
            fl = False
            try:
                nodes3[i].find_element_by_css_selector("span").is_displayed()
                fl = True
            except:
                fl = False  

            if (fl and nodes3[i].find_element(By.CSS_SELECTOR,"span").get_attribute("title").startswith('微博')):
                verification = nodes3[i].find_element(By.CSS_SELECTOR,"span").get_attribute("title")

            # General users do not have any identity verification or show special information on the post page. Asign them with '0'
            else:
                verification = '0' #user

            # Get information using CSS selector    
            weibolink = nodes1[i].find_elements(By.CSS_SELECTOR,"div.from > a:nth-child(1)")[-1].get_attribute('href')
            #posttime = nodes1[i].find_elements(By.CSS_SELECTOR,"div.from > a:nth-child(1)")[-1].text
            username = nodes1[i].find_element(By.CSS_SELECTOR,"div.info>div:nth-child(2)>a").text
            date = nodes1[i].find_element(By.CSS_SELECTOR,"div.from>a").text
            repost_count = nodes2[i].find_element(By.CSS_SELECTOR,"li:nth-child(1)").text
            comment_count = nodes2[i].find_element(By.CSS_SELECTOR,"li:nth-child(2)").text
            like_count = nodes2[i].find_element(By.CSS_SELECTOR,"button").text


            # For posts with no likes, comments or reposts, information scraped show as 'comment', 'repost', 'like'. Keep them aligned as numbers.
            if comment_count == '评论':
                comment_count = '0'
            if repost_count == '转发':
                repost_count = '0'
            if like_count == '赞':
                like_count = '0' 

            # Concate paragraphs within one post into one paragraph to make it easier for reading data for anallysis
            content = ' '.join(content.split('\n'))

            # Call functions to strip mid and uid information from microblog link
            mid = get_mid(weibolink)
            uid = get_uid(weibolink)

            # Join all variables of one post into a string and write into file
            oneline = ','.join([current_time,mid,uid,username,content,date,weibolink,repost_count,like_count,comment_count,verification,keyword])

            with open (filename,'a') as f:
                f.write(oneline+'\n')
  
            
        print('Page {} in the search of keyword: {} is scraped and written to file.'.format(page,keyword) )

        # Position and click 'next page' 
        try:
            nextpage_button = driver.find_element(By.PARTIAL_LINK_TEXT,'下一页')
            driver.execute_script("arguments[0].click();", nextpage_button)
        except:
            print(page,'break')
            continue

    print(f'{filename} is ready!')
    return f'{filename} is ready!'
    


