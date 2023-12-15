
import os
import pandas as pd
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.formula.api import ols
import seaborn as sns
from ISLP.models import (ModelSpec as MS, summarize , poly)
from sklearn.linear_model import LinearRegression

def Remove_outlier(df, var):
    mean0 = df[var].mean()
    std_dev = df[var].std()
    min_val = mean0 - 4 * std_dev
    max_val = mean0 + 4 * std_dev
    df = df[(df[var] >= min_val) & (df[var] <= max_val)]
    return df[var]

def Corr_by_topic(df):
    '''
    Write correlation matrix to txt files by topics
    '''
    with open(output_dir + '/anova/correlation_matrix_by_events.txt','w') as file:
            file.write('\n')
    labels=['Openai',
            'AI risk',
            'Post deletion',
            'Sexual assault',
            'Homeless dogs hurt', 
            'Cat abusing',
            'Du Meizhu scandal']
    for k in range(0,7):
        B = df['keyword_code'] == k
        d = df[B]
        data = pd.DataFrame({'X': d['average_text_lenth'], 
                            'Y1' :d['positive_prob'],
                            'Y2': d['immoral_wc'],
                            'Y3':d['moral_emo'],
                            })
        data_sorted = data.sort_values(by='X')
        cor_data = data.corr()
        with open(output_dir + '/correlation_matrix_by_events.txt','a') as file:
            file.write('X: comment length \n Y1: sentiment positivity of source posts \n Y2: immoral judgement word count in source post \n Y3: moral emotion of source post\n')
            file.write('The analysis is based on {} samples from the topic of {}.'.format(len(d),labels[k]))
            file.write(str(data.corr()))
            file.write('\n__________________________________________________\n')


def Oneway_ANOVA(df, vars:list):
    '''
    Conduct one-way ANOVA analysis on each varaible in the input variables list.
    Write F statistics and p values into the txt file if results is statistically significant.
    Plot boxlpots for each significant result, stored in /results/anova folder.
    '''
    grouped = df.groupby('keyword_code')
    sig_v = {}
    with open(output_dir + '/anova/significant_variables.txt', 'w') as file:
                    file.write('\n')
    
    for v in vars:
        if v != 'keyword_code':
        
            group_values = []
            for group_name, group_data in grouped:
                group_values.append(Remove_outlier(group_data,v))

            f_statistic, p_value = stats.f_oneway(*group_values)
        
            if p_value < 0.05:
                sig_v[v] = (f_statistic,p_value)
            
                plt.figure(figsize=(10, 4))
                sns.set_palette('pastel')
                sns.boxplot(data=group_values)
                plt.xticks(ticks=range(0,7), 
                        labels=['Openai',
                                'AI risk',
                                'Post deletion',
                                'Sexual assault',
                                'Homeless dogs hurt', 
                                'Cat abusing',
                                'Du Meizhu scandal'],
                            rotation = 0)
                plt.title('{} One-way'.format(v))
                plt.xlabel('Groups')
                plt.ylabel('Values')
                plt.figtext(0.5, -0.1, 
                            'ANOVA analysis of {}:\n F-statistic: {}  P-value:{}.'.format(v,f_statistic,p_value),
                            ha="center", fontsize=10, color = 'black')
                plt.tight_layout()
                plt.savefig(output_dir +'/anova/' + f'{v}_by_topic.png')
                plt.close()

                with open(output_dir + '/anova/significant_variables.txt', 'a') as file:
                    file.write('\n {}: \n f statistic - {}; p value - {}.\n'.format(v,f_statistic,p_value))
            
def Regression_plot(x,y, xtitle, ytitle):
        '''
        Plot the regression model.
        Called to run when parameters are statistically significant.
        '''
        plt.scatter(x, y, label='Data')

        model = LinearRegression()
        results = model.fit(x.reshape(-1, 1), y)  # Reshape x for sklearn input

        slope = model.coef_[0]
        intercept = model.intercept_

        plt.plot(x, slope * x + intercept, color='red', label='Linear Regression')

        plt.title('Scatter Plot with Linear Regression')
        plt.xlabel(xtitle)
        plt.ylabel(ytitle)
        plt.legend() 
        plt.figtext(0.5, -0.1, 
                    'Linear Regression plot contains {} samples'.format(len(x)),
                    ha="center", fontsize=10)
        

def Summerize_LR(df, X_name: str, X_v, Y_v):
    '''
    Fit a linear regression to X_v and Y_v.
    Write the model summary to the file and create a plot for models with a p-value <0.05
    '''
    X = pd.DataFrame({'intercept': np.full(df.shape[0],10), 
                X_name: df[X_v]})
    y = df[Y_v]
    model = sm.OLS(y, X) 
    results = model.fit()
    if results.pvalues[1] < 0.05:
        #dp = Remove_outlier(df[[X_v,Y_v]],X_v)
        
        Regression_plot(x= np.array(df[X_v]),
                        y= np.array(df[Y_v]),
                        xtitle = X_v,
                        ytitle = Y_v)
        plt.savefig(LR_dir + '/{}_{}_LR.png'.format(X_v,Y_v))
        plt.close()

    return str(summarize(results))+'\n_______________________________________\n'



if __name__ == "__main__": 

    root_dir = os.getcwd ()
    output_dir = root_dir +"/results"
    data_dir = root_dir +"/data/processed"
    LR_dir = output_dir + '/regression'
    # os.mkdir(output_dir + '/ttest',exist_ok=True )
    # os.mkdir(output_dir + '/anova',exist_ok=True)

    df = pd.read_csv(root_dir+'/data/processed/post_comment_df.csv',index_col=0)
    d = df
    Corr_by_topic(d)

    # Prepare new variables for anova test
    d['pmoral'] = d['moral_wc']/d['textlength']
    d['ave_pmoral'] = d['average_moral_word']/d['average_text_lenth']
    d['moral_emo_bylenth'] = d['moral_emo']/d['textlength']
    d['average_moral_emo_bylenth'] = d['average_moral_emo']/d['average_text_lenth']
    d['nonmoral_emo_bylenth'] = d['nonmoral_emo']/d['textlength']
    d['average_nonmoral_emo_bylenth'] = d['average_nonmoral_emo']/d['average_text_lenth']

    vars = ['repost_count', 'like_count', 'textlength',
        'moral_score', 'positive_prob', 
        'comments_count', 'average_commenter_follow',
        'average_commenter_follower', 'commenter_gender_ratio',
        'average_positive_possibility', 'positive_negative_ratio',
        'average_text_lenth', 'average_moral_score', 'keyword_code',
        'pmoral', 'ave_pmoral', 'moral_emo_bylenth',
        'average_moral_emo_bylenth', 'nonmoral_emo_bylenth',
        'average_nonmoral_emo_bylenth']

    Oneway_ANOVA(d,vars)
    print('One-way ANOVA is completed!')

    # Fit linear regression models.
    # New models and plots can be easily created by adding a file.write line and specify the variable names

    d = df[df['average_immoral_word']>0]

    with open(LR_dir+'/regression_comment_immoral_word.txt','w') as file:

        file.write(Summerize_LR(d, 
                                'comment moral emotion','average_moral_emo',        
                                'average_immoral_word'))
        file.write(Summerize_LR(d, 
                                'comment_nonmoral_emo',
                                'average_nonmoral_emo',        
                                'average_immoral_word'))
        file.write(Summerize_LR(d, 
                                'comment positivity',
                                'average_positive_possibility',        
                                'average_immoral_word'))

        
    with open(LR_dir+'/regression2_comment_count.txt','w') as file:
        file.write(Summerize_LR(d, 
                                'comment moral emotion',
                                'average_moral_word',        
                                'comment_count'))

        file.write(Summerize_LR(d, 
                                'comment immoral judgement',
                                'average_immoral_word',        
                                'comment_count'))
        file.write(Summerize_LR(d, 
                                'comment moral emotion',
                                'average_moral_word',        
                                'comment_count'))
        
    with open(LR_dir+'/regression3_comment_moral_emotion.txt','w') as file:
        file.write(Summerize_LR(d, 
                                'source post moral emotion',
                                'moral_emo',        
                                'average_moral_emo'))

        file.write(Summerize_LR(d, 
                                'source post moral emotion',
                                'moral_emo',        
                                'average_moral_emo'))
        
        file.write(Summerize_LR(d, 
                                'source post binary sentiment',
                                'positive_prob',        
                                'average_moral_emo'))


    print('Linear Rgression is conducted!')

