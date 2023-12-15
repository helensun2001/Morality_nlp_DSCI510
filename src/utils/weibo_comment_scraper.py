import os
import requests
import pandas as pd
import datetime
from time import sleep
import random
# from fake_useragent import UserAgent
import re

def trans_time(v_str):
    """转换GMT时间为标准格式"""
    GMT_FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
    timeArray = datetime.datetime.strptime(v_str, GMT_FORMAT)
    ret_time = timeArray.strftime("%Y-%m-%d %H:%M:%S")
    return ret_time


def tran_gender(gender_tag):
    """转换性别"""
    if gender_tag == 'm':
        return '男'
    elif gender_tag == 'f':
        return '女'
    else:  # -1
        return '未知'


def get_comments(v_weibo_ids, v_comment_file, v_max_page):
    """
    Scrape social media comments by each microblog id [mid]
    :param v_weibo_id: a list of microblog ids [mid]
    :param v_comment_file: file name for saving
    :param v_max_page: maximum page of comment to scrape
    :return: None
    """
    for weibo_id in v_weibo_ids:
        
        max_id = '0'
        max_id_type = '0'

        for page in range(1, v_max_page + 1): 
        #scrape one page of comment under one post in a loop

            wait_seconds = random.uniform(0, 1)  
            sleep(wait_seconds)  # wait
            print('Start scraping page{} '.format(page))

            if page == 1:  
            # first page of comment do not need max_id param in the url
                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type=0'.format(weibo_id, weibo_id)

            else:  
            # after the first page of comment, max_id is needed to request data
                if str(max_id) == '0':  
                    print('max_id is 0, break now')
                    break
                    # When parsing through the each page of comment;
                    # max_id param will be requested and updated. 
                    # The last page of comment has a max_id of '0', break to jump out of the loop

                url = 'https://m.weibo.cn/comments/hotflow?id={}&mid={}&max_id_type={}&max_id={}'.format(weibo_id, weibo_id, max_id_type, max_id)

            headers = {
                "user-agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                # 如果cookie失效，会返回-100响应码
                "cookie":
                 "SSOLoginState=1700181111; ALF=1702773111; WEIBOCN_FROM=1110006030; BAIDU_SSP_lcr=https://login.sina.com.cn/; loginScene=102003; geetest_token=456839f0e033855ce715a91cb5872b89; SUB=_2A25IUs1mDeRhGeBL41UZ8irNzj6IHXVrLkCurDV6PUJbkdANLXj7kW1NRtxsbTWINckxc2zs9dMZTR1v1nqTkP0c; _T_WM=75313719817; XSRF-TOKEN=ea6c46; MLOGIN=1; M_WEIBOCN_PARAMS=oid%3D4959193179882654%26luicode%3D20000061%26lfid%3D4959193179882654%26uicode%3D20000061%26fid%3D4959193179882654",
                  #"__bid_n=18809d6f64897ebb484207; FPTOKEN=35ZWJEHmLOg9F94ljL2eV/CUtJihWh4BX422Om0Wa5odVgorrajJgeUsJvQJ2upRmYwQWp+tYCEFsUUirmyMWsAx5bLI64fHkcT57fYcszXRQV/07KNFwEhMgLfHebtSnOO7wW3Dw+ZkQ7AjY/MeXT2CLdwxh2pKisD4fscS7DXyVIJv4jZZON1+Ck64gbN52gFAMR5T/02hBIEfL6jy3xziYJPbDGGG2YvdYCKSftzp4cyXrasaOLRefxNjDJr8GCGcUJ4CWDOrTPeFbtN11abNp2fRUu/SCqsJjKWvzdz711bFxehLSwTM48FCuh++04IvqsdjFZMO9OGoH+75JgS+JhXrMYWqGsMGU7udLUxkreEddrzoJWfZtvXs4T08Oy4IWSf2GNP9cabsBwExdg==|mv/tt9+8PX/ciZD0zpjZc8Ij/okf770SKO4zsr2v0Ns=|10|40b20c7b436a6c3db07e0c25e8638461; _T_WM=64956084643; WEIBOCN_FROM=1110006030; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhWcVXRXvfX3iep9.M98zpA5JpX5K-hUgL.Fo2c1K5fehe01h52dJLoIE2LxK.LBK.LB-eLxK-L1KeLBKH7wPxQdcRLxKnLB-qLBoBt; SSOLoginState=1685049447; ALF=1687641447; MLOGIN=1; SCF=AtVc4J42nyFDK7iA_NS0v87dYj28NjGa73M_0H6h8uozGXaXGWyAL0WQ8a6xi1lQjJWX4Ui_H1jYCOVymnDBEYI.; SUB=_2A25Ja6A3DeRhGedI4lIU8C3PwzyIHXVql8B_rDV6PUJbktAGLRikkW1NVoZ-2aB1ChUMtBs09-ODfr_Fm15Vv1ad; XSRF-TOKEN=dbdd42; mweibo_short_token=03412389e0; M_WEIBOCN_PARAMS=oid%3D4902006563537441%26luicode%3D20000174%26lfid%3D4902006563537441%26uicode%3D10000011%26fid%3D102803",
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
                "referer": "https://m.weibo.cn/detail/{}".format(weibo_id),
                "x-requested-with": "XMLHttpRequest",
                "mweibo-pwa": '1',
            }
            r = requests.get(url, headers=headers)  
            # print(r.status_code)  # 查看响应码
            # print(r.json())  # 查看响应内容

            try:
                # get max-id param to use in the next loop
                max_id = r.json()['data']['max_id']  
                max_id_type = r.json()['data']['max_id_type']  
                datas = r.json()['data']['data']

            except Exception as e:
                print('excepted: ' + str(e))
                #print(r.json())
                continue

            print('comment number:', len(datas))

            page_list = []  # page of comment
            id_list = []  # comment id
            text_list = []  # comment text
            time_list = []  # comment time
            like_count_list = []  # comment like count
            source_list = []  # comment user IP
            user_name_list = []  # comment user name
            user_id_list = []  # comment user id
            user_gender_list = []  # comment user gender
            follow_count_list = []  # comment follow count
            followers_count_list = []  # comment follower count

            for data in datas:
                page_list.append(page)
                id_list.append(data['id'])
                dr = re.compile(r'<[^>]+>', re.S)  
                text2 = dr.sub('', data['text']) 
                # clean the urls within thecomment text 
                text_list.append(text2)  
                time_list.append(trans_time(v_str=data['created_at'])) 
                like_count_list.append(data['like_count'])  
                source_list.append(data['source']) 
                user_name_list.append(data['user']['screen_name']) 
                user_id_list.append(data['user']['id'])  
                user_gender_list.append(tran_gender(data['user']['gender']))  
                follow_count_list.append(data['user']['follow_count'])  
                followers_count_list.append(data['user']['followers_count'])  

            df = pd.DataFrame(
                {
                    'max_id': max_id,
                    'post_id': [weibo_id] * len(time_list),
                    'comment_page': page_list,
                    'comment_id': id_list,
                    'comment_time': time_list,
                    'comment_likes': like_count_list,
                    'commenr_userIP': source_list,
                    'comment_user_name': user_name_list,
                    'comment_user_id': user_id_list,
                    'comment_user_gender': user_gender_list,
                    'comment_user_follow': follow_count_list,
                    'comment_user_follower': followers_count_list,
                    'comment_text': text_list,
                }
            )
            if os.path.exists(v_comment_file): 
                header = False
            else:  
                header = True
            
            # Save comments to csv file
            df.to_csv(v_comment_file, mode='a+', index=False, header=header, encoding='utf_8_sig')
            print('Results saved as:{}'.format(v_comment_file))

