import os
import pandas as pd
import numpy as np
from prettytable import PrettyTable
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols
import pandas as pd


def Remove_outlier(df, var):
    '''
    Remove ouliers over 4 std away
    '''
    mean0 = df[var].mean()
    std_dev = df[var].std()
    min_val = mean0 - 4 * std_dev
    max_val = mean0 + 4 * std_dev
    df = df[(df[var] >= min_val) & (df[var] <= max_val)]
    return df[var]


def descriptive_stats_table(df, cols, filename):
    '''
    Write a descritptive data summary table to files
    '''
    dfcolumns = df[cols]
    stats_summary = dfcolumns.describe().T
    table = PrettyTable()
    table.field_names = ['Variable', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max']

    for index, row in stats_summary.iterrows():
        table.add_row([index, round(row['mean'], 2), round(row['std'], 2), round(row['min'],3), round(row['25%'],3), round(row['50%'],3), round(row['75%'],3), round(row['max'],3)])
    
    with open(output_dir+ f'{filename}_stats_table.txt', 'w') as file:
        file.write(str(table))

def compare_groupby(df, groupby_v:str, compare_v:list, q,filename):
    '''
    Group the dataframe by groupby_v parameter, write descriptive table for each group for variables in compare_v parameter
    '''
    if pd.api.types.is_numeric_dtype(df[groupby_v]):  
        groups = pd.qcut(df[groupby_v], q=q, labels=["low", "medium", "high"],duplicates='drop')  
        grouped = df.groupby(groups)
    else:
        grouped = df.groupby(groupby_v)

    group_stats = grouped[compare_v].describe()
    table = PrettyTable()
    table.field_names = ['Group', 'Variable', 'Mean', 'Std Dev', 'Min', '25%', '50%', '75%', 'Max']
    
    for var in compare_v:
        for group, data in group_stats.iterrows():
            table.add_row([var, group, round(data.loc[(var, 'mean')], 2), round(data.loc[(var, 'std')], 2),
                           round(data.loc[(var, 'min')],4), round(data.loc[(var, '25%')],4), round(data.loc[(var, '50%')],4),
                           round(data.loc[(var, '75%')],4), round(data.loc[(var, 'max')],4)])

    with open(output_dir + f'{filename}_{groupby_v}_table.txt', 'w') as file:
        file.write(str(table))


def Standard_df(df):
    sdf = (df-df.mean())/df.std()
    return sdf


if __name__ == "__main__": 
    
    root_dir = os.getcwd ()
    
    output_dir = root_dir +"/results/description"
    data_dir = root_dir +"/data/processed"
    # os.mkdir(output_dir + '/ttest' )
    # os.mkdir(output_dir + '/anova' )
    # os.mkdir(root_dir +"/results/description")

    # import data
    df = pd.read_csv(root_dir+'/data/processed/post_comment_df.csv',index_col=0)

    # Create descrpitive table for posts and comments features separately
    descriptive_stats_table(df,
                            ['repost_count', 
                             'like_count', 
                             'comment_count',
                             'moral_score', 
                             'moral_wc',
                             'immoral_wc',
                             'moral_emo',
                             'nonmoral_emo'], 
                             '/sourcepost_description')
    
    descriptive_stats_table(df,
                            ['average_commenter_follow',           
                            'average_moral_word', 'average_immoral_word', 'commenter_gender_ratio',
                            'average_positive_possibility', 'positive_negative_ratio',
                            'average_text_lenth', 
                            'average_moral_score',
                            'average_moral_emo',
                            'average_nonmoral_emo'],
                              '/comment_description')
    
    # Group data by popularity feature, text length and moral scores.
    # 
    compare_groupby(df, 'like_count', 
                    ['moral_score', 'positive_prob', 'average_moral_score'], 
                    q = 3, filename='/group_by')

    compare_groupby(df, 'textlength', 
                    ['moral_score', 'positive_prob', 'average_moral_score','positive_negative_ratio'], 
                    q = 3, filename='/group_by')


    bins = [-40, -0.1, 0.1, 40]  
    labels = ['Negative', 'Non-moral', 'Positive']
    df['moral_bins'] = pd.cut(df['moral_score'], bins=bins, labels=labels)

    compare_groupby(df, 'moral_bins', 
                    ['comments_count','average_commenter_follow',
                     'average_moral_score','positive_negative_ratio'], 
                    q = 0, filename = '/group_by')
    
    