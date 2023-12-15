# When you run this get_data.py, you have to wait for 30min to scrape social media post comments based on the realtime weibo data prestored in the data folder.
# If you do not want to wait, do not run this file and go directly to clean_features.py to process data

import pandas as pd
import os
from utils.weibo_comment_scraper import *
from utils.weibo_realtime_scraper import *
from utils.data_processing import Check_file_existence

# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.common.by import By

pwd = os.getcwd ()
datapath = pwd +"/data/raw"

# Create a list of keywords in Chinese for social media posts scraping
scraping_keywords = ['流浪狗 咬人 负责',
                    '人工智能 风险',
                    '都美竹', 
                    'openai',
                    '虐猫',
                    '删帖',
                    '性骚扰']

# Createn a list of translated keywords to name the file of scraped data
keywords = ['homeless_dogs',
            'artificial_intelligence_risks',
            'DuMeizhu_scandal',
            'openai',
            'cat_abuse',
            'content_moderation',
            'sexual_harrassment']

# driver = webdriver.Chrome()    
# #send request to log in to sina weibo
# driver.get("https://login.sina.com.cn/signup/signin.php")
# wait = WebDriverWait(driver,5)
# #wait for one minute to log in manually
# time.sleep(60)


# Scrape data based on Chinese keywords.
# Store the data of each keyword in a separate file
# Because sinaweibo.com only displays the latest 50 pages of realtime posts, each time the scraper only flip the page for 50 times 

# for i in len(keywords):
#     filename = datapath + '/' + f'{keywords[i]}' + '_realtime_posts.csv'
#     Scrape_realtime_weibo_by_keyword(driver = driver, 
#                                     keyword = scraping_keywords[i], 
#                                     folder_path = datapath, 
#                                     page_count = 49)


# Concate all data from 7 separate files and remove duplicates
data0 = pd.DataFrame()
variables = ['current_time','mid','uid','username','content','date','weibolink','repost_count','like_count','comment_count','verification','keyword']
for keyword in keywords:
    filename = datapath + '/' + f'{keyword}' + '_realtime_posts.csv'  
    data1 = pd.read_csv(filename,names = variables, on_bad_lines='skip')
    data0 = pd.concat([data0,data1])

Check_file_existence('/weibo_raw_data.csv',datapath)
Check_file_existence('/unique_weibo_raw_data.csv',datapath)

data0.to_csv(datapath+'/weibo_raw_data.csv')
data0.drop_duplicates(subset=['content'], inplace=True, keep='first')
data0.to_csv(datapath+ '/unique_' + 'weibo_raw_data.csv', index=False, encoding='utf_8_sig')
print('Data is cleaned and restored in unique_weibo_raw_data')

# Scrape comments of sourceposts 
# This scraper does not need simulation of user login. It's based on indexing the unique id of each sourcepost
rawdata = pd.read_csv(datapath+'/unique_weibo_raw_data.csv')
data_with_comment = rawdata[rawdata['comment_count']>0]
mid_to_scrape = list(data_with_comment['mid'])
max_page = 50  # The maximum page of comments to scrape under each ;ost
comment_file = '/comments.csv'

# Check whether the file already exist
if os.path.exists(datapath + comment_file):
    print('csv file alreayd exist, remove first:', datapath + comment_file)
    os.remove(datapath + comment_file)
    
# Get comments of all realtime posts with a positive comment count
get_comments(v_weibo_ids = mid_to_scrape, 
             v_comment_file= datapath + comment_file, 
             v_max_page = max_page)

df = pd.read_csv(datapath + comment_file)
# Remove repeated comments
df.drop_duplicates(subset=['comment_id'], inplace=True, keep='first')

# Store unique comments to file
df.to_csv(datapath + '/unique_comments.csv', index=False)#, encoding='utf_8_sig')
print('Data cleaned')


