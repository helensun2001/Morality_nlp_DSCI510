# When you run this script, all files in /data/processed file will be removed. 
# Running this file needs around 5 min to extract and clean textual features from source posts and comments to save them into the final dataframe for further analysis.
# If you don't want to wait, do not run this file. Analysis and visualization scripts can be run based on original data folder.


import pandas as pd
import os
#from utils.load_dict import LoadDict as ld
from utils.get_features import Get_snownlp_score
from utils.get_features import Get_Weighted_Score
from utils.get_features import Sentiment_wordcount_by_category
from utils.get_features import translate_text
from utils.data_processing import Check_file_existence
from tqdm.notebook import trange
import re

def Get_first_string(string):
    result = string.split('//')[0] # get the text before reposting punctuations
    result = re.sub(r'#.*?#', '', result) # remove tags 
    result = re.sub(r'\s+', '', result) # remove space
    return(result)

def Clean_dataframe(df,column_name:str):
    no_na = df.dropna(subset = [column_name])
    unique_content = no_na.drop_duplicates(subset=[column_name],  keep='first')
    filtered = unique_content[unique_content[column_name].apply(lambda x: len(x)) >= 3]
    return filtered

def Get_eng_text(text_list,filepath):
    if not os.path.exists(filepath):
        print('Start translating the texts to English. Expected time over 15 minutes')
        pbar = trange(0,len(text_list))
        pbar.set_description('Translating')
        for text in text_list:
            
            try:
                en_text = translate_text(target= 'en',text = text)
            except:
                print('Translation failed. Please make sure you have set up Google Cloud Service and local Authentification to call the Google translate API.')
            else:
                pbar.update(1)
                with open(filepath,'a') as f:
                    f.write(en_text+'\n')

    enlines = []
    print('Translation finished. {} ready for reference!'.format(filepath))
    with open (filepath,'r') as f:
        for line in f.readlines():
            enlines.append(line.strip())
    return enlines


def Compute_labels(text_list,filename):
    '''
    param text_list: should be a list of cleaned texts ready for counting key words
    param filename: should be in the format of [/xxx]
    '''
    print('Now start to compute moral labels for {}'.format(filename))
    ### Moral labels
    text_length, score_list, moral_wc, immoral_wc, other_wc = Get_Weighted_Score(text_list)

    ### sentiment category
    print('Now start to compute sentiment labels for {}'.format(filename))
    goodness,happiness,sadness,anger,afraid,disgust,surprise = Sentiment_wordcount_by_category(text_list)

    positive_prob, sub_probs = Get_snownlp_score(text_list)

    enlines = Get_eng_text(text_list, processedp + filename + '_translated.csv')
    
    data = {'text':enlines,
            'textlength':text_length,
            'moral_score': score_list,
            'moral_wc':moral_wc,
            'immoral_wc':immoral_wc,
            'other_wc':other_wc,
            'goodness':goodness,
            'happiness':happiness,
            'sadness':sadness,
            'anger':anger,
            'afraid':afraid,
            'disgust':disgust,
            'surprise':surprise,
            'positive_prob':positive_prob,
            'sub_probs':sub_probs}
    
    df = pd.DataFrame(data)

    df.to_csv(processedp + filename + '_features.csv')
    print('{} + features.csv is created'.format(filename))


def Map_comments_to_sourceposts(posts,comments,post_features,comment_features):
    '''
    Join the comments dataset with source posts dataset. 
    Compute average measurements for all comments from the same source post.
    '''

    d1 = pd.read_csv(posts)
    f1 = pd.read_csv(post_features)
    d2 = pd.read_csv(comments)
    f2 = pd.read_csv(comment_features)

    d2['comment_user_gender_coded'] = d2['comment_user_gender'].astype('category').cat.codes #1= male, 0 = female
    d2.drop(columns = ['comment_user_gender'],inplace= True)

    post_v = ['mid', 'uid', 'repost_count', 'like_count', 'comment_count',
        'verification', 'keyword']
    post_f = ['text', 'textlength', 'moral_score', 'moral_wc', 'immoral_wc',
        'other_wc', 'positive_prob',
        'goodness','happiness','sadness','surprise','afraid','disgust','anger']
    cmt_v = ['post_id', 'comment_page', 'comment_id', 'comment_time',
        'comment_likes', 'commenr_userIP', 'comment_user_name',
        'comment_user_id', 'comment_user_gender_coded', 'comment_user_follow',
        'comment_user_follower']

    df1 = pd.DataFrame()
    df1[post_v] = d1[post_v]
    df1[post_f] = f1[post_f]

    df2 = pd.DataFrame()
    df2[cmt_v] = d2[cmt_v]
    df2[post_f] = f2[post_f]

    # # filter the subset of sourceposts that have comment data
    comment_id_list = list(pd.unique(d2['post_id']))

    index_list = []
    id_list = []
    for mid in comment_id_list:
        i = d1[d1['mid'] == mid].first_valid_index()
        if i not in index_list:
            index_list.append(i) 
            id_list.append(mid)

    post_comment_df = df1[df1['mid'].isin(id_list)]
    id_list = list(post_comment_df['mid'])


    print('{} sourceposts are mapped with {} comments'.format(len(id_list),len(df2)))

    # Aggregate comment scores and join to the post_comment_dataset
    feature_list = ['comments_count','average_commenter_follow','average_commenter_follower',
                    'average_moral_word',
                    'average_immoral_word',
                    'commenter_gender_ratio',
                    'average_positive_possibility',
                    'positive_negative_ratio',
                    'average_text_lenth',
                    'average_moral_score',
                    'average_moral_emo',
                    'average_nonmoral_emo'
                ]

    ########################################
    # Based on each subset of comments data, compute the average measurement and add to lists
    # The following lists are comments textual features for final analysis
    comments_count = []
    average_commenter_follow = []
    average_commenter_follower = []
    average_moral_word = []
    average_immoral_word = []
    commenter_gender_ratio = []
    average_positive_possibility = []
    positive_negative_ratio = []
    average_text_lenth = []
    average_moral_score = []
    average_moral_emo = []
    average_nonmoral_emo = []

    for mid in id_list:
        subset = df2[df2['post_id']== mid]
        comments_count.append(len(subset))
        try:
            average_commenter_follow.append(subset['comment_user_follow'].mean())
        except:
            average_commenter_follow.append(10000)
        try:
            average_commenter_follower.append(subset['comment_user_follower'].mean())
        except:
            average_commenter_follower.append(10000)
        average_moral_word.append(subset['moral_wc'].sum())
        average_immoral_word.append(subset['immoral_wc'].sum())
        commenter_gender_ratio.append(round(subset['comment_user_gender_coded'].sum()/len(subset),4))
        average_positive_possibility.append(round(subset['positive_prob'].mean(),4))

        x1 = subset[subset['positive_prob']>50].count()[0]
        x2 = subset[subset['positive_prob']<50].count()[0]
        result = (x1+1)/(1+x2)
        positive_negative_ratio.append(round(result,4))

        average_text_lenth.append(subset['textlength'].mean())
        average_moral_score.append(round(subset['moral_score'].mean(),4))

        average_moral_emo.append(round((subset['afraid']+subset['disgust']+subset['anger']).mean(),4))
        average_nonmoral_emo.append(round((subset['goodness']+subset['happiness']+subset['sadness'] + subset['surprise']).mean(),4))

    # Create a list for all newly-computed features and add to dataframe
    datalist = [comments_count,average_commenter_follow,            
                average_commenter_follower,
                average_moral_word,average_immoral_word,commenter_gender_ratio,
                average_positive_possibility,
                positive_negative_ratio,
                average_text_lenth,
                average_moral_score,
                average_moral_emo,
                average_nonmoral_emo]
    for i in range(len(feature_list)):
        v_name = feature_list[i]
        post_comment_df[v_name] = datalist[i]
    
    # Recode new features and drop useless columns
    post_comment_df['moral_emo'] = post_comment_df['anger']+post_comment_df['afraid']+post_comment_df['disgust']
    post_comment_df['nonmoral_emo'] = post_comment_df['goodness']+post_comment_df['sadness']+post_comment_df['happiness']+post_comment_df['surprise']
    post_comment_df['keyword_code'] = post_comment_df['keyword'].astype('category').cat.codes 
    post_comment_df.drop(columns=['keyword','goodness','happiness','sadness','afraid','disgust','anger'],inplace= True)

    post_comment_df.to_csv(processedp + '/post_comment_df.csv')
    return post_comment_df


if __name__ == "__main__": 
    pwd = os.getcwd ()
    rawp = pwd +'/data/raw'
    processedp = pwd +"/data/processed"
    os.makedirs(processedp, exist_ok=True)

    # Remove files already exist
    filenames = ['/sourcepost_features.csv',
                '/comments_features.csv',
                '/post_comment_df.csv',
                '/comments_for_label.csv',
                '/posts_for_label.csv']
    Check_file_existence(filenames= filenames, datapath= processedp)

    # Clean text posts using Get_first_string function
    # This function removes the reposting content contained in raw data
    rawdata = pd.read_csv(rawp+'/unique_weibo_raw_data.csv')
    texts = list(rawdata['content'])
    rawdata['content'] = [Get_first_string(text) for text in texts]

    filtered_src = Clean_dataframe(rawdata,'content')
    filtered_src.to_csv(processedp + '/posts_for_label.csv')
    print('Reposting text data are cleaned. {} individual posts are ready for computing textual features!'.format(len(filtered_src)))

    # Compute moral and sentimental labels on sourceposts
    # Store the labels in a separate file
    Compute_labels(list(filtered_src['content']), filename = '/sourcepost')

    # Clean NAs in commment texts
    comments = pd.read_csv(rawp+'/unique_comments.csv')

    filtered_comments = Clean_dataframe(comments, 'comment_text')
    filtered_comments.to_csv(processedp + '/comments_for_label.csv')
    print('Comments shorter than 2 characters are removed. {} comments are ready for computing textual features!'.format(len(filtered_comments)))

    # Compute moral and sentimental labels on comments data
    Compute_labels(list(filtered_comments['comment_text']), filename = '/comments')

    Map_comments_to_sourceposts(posts = processedp+'/posts_for_label.csv',
                                comments = processedp +'/comments_for_label.csv',
                                post_features = processedp + '/sourcepost_features.csv',
                                comment_features = processedp + '/comments_features.csv')

    print('All data are ready!')