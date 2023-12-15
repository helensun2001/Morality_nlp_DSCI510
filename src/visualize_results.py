import os
import pandas as pd
import seaborn as sns
from scipy import stats
import matplotlib.pyplot as plt

def Plot_sample_distribution(df,r,p,labels):
    '''
    Plot 4 pie charts to show how sample distribution across topics change as data cleaning is conducted.
    '''
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    sns.set_palette("pastel") 

    ax1 = fig.add_subplot(2, 2, 1)
    ax1.pie(r.groupby('keyword').count()['mid'],autopct='%1.1f%%', startangle=140)
    ax1.set_title('Raw data count')
    sns.despine(ax=ax1) 

    ax2 = fig.add_subplot(2, 2, 2)
    ax2.pie(p.groupby('keyword').count()['mid'], autopct='%1.1f%%', startangle=140)
    ax2.set_title('Cleaned data count')
    
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.pie(df.groupby('keyword_code').count().reset_index()['mid'], autopct='%1.1f%%', startangle=140)
    ax3.set_title('Source posts count with comments data')

    ax4 = fig.add_subplot(2, 2, 4)
    ax4.pie(df[['comments_count','keyword_code']].groupby('keyword_code').sum()['comments_count'], autopct='%1.1f%%', startangle=140)
    ax4.set_title('Comments count')
    plt.legend(labels=labels, prop={'size': 8},bbox_to_anchor=(1.4, 0), loc='lower right')
    plt.axis('off')

    plt.tight_layout()
    plt.savefig(dist_dir + '/sample_distribution_pies.png')
    #plt.show()


def Heatmap(df,filename):
    '''
    Draw a heatmap of selected variables to observe potential correlation
    '''
    qv = df.drop(columns = ['mid','uid','keyword_code','average_commenter_follower','comments_count','verification'])
    sqv = (qv-qv.mean())/qv.std()
    cor_data = sqv.corr()
    plt.figure(figsize=(18,18))
    ax = sns.heatmap(cor_data, square=True,
                    annot = True, fmt = '.2f',
                    linewidths = .5, 
                    cmap = 'YlGnBu',
                    cbar_kws= {'fraction': 0.046, 'pad':0.03})
    ax.set_title('Correlation between quantitative variables')
    
    plt.savefig(corr_dir + f'{filename}_heatmap.png')
    plt.close()


def descriptive_plots(dataframe, cols:list, filename):
    '''
    Plot histograms and boxplots of all quantitative variables in a dataframe
    '''
    dfcolumns = dataframe[cols]
    num_cols = len(cols)
    num_rows = (num_cols + 1) // 2 
    
    fig, axes = plt.subplots(nrows=num_rows, ncols=2, figsize=(25, num_rows * 5))
    axes = axes.flatten()
    
    for i, col in enumerate(dfcolumns.columns):
        sns.histplot(dataframe[col], ax=axes[i], kde=True)
        axes[i].set_title(f'Histogram of {col}')

    plt.tight_layout()
    plt.savefig(dist_dir + f'{filename}_histgram.png')
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data= dfcolumns, orient='h')
    plt.title('Boxplot of Numeric Variables')
    plt.xlabel('Value')
    plt.tight_layout()
    plt.savefig(dist_dir + f'{filename}_boxplots.png')
    plt.close()


def Plot_groupby_events(grouped_dataframe, k):
    '''
    param k: the number of subplot in one line, equals to the number of variables you're interested, equals to the column number in the dataframe
    '''
    
    fig, axes = plt.subplots(1, k, figsize=(2*k+2, 2)) 
    sns.color_palette('PuOr')
    plt.xticks(range(0,7),list(range(1,8)))
    
    i = 0
    for v in list(grouped_dataframe.columns):
        sns.barplot(x= list(range(1,8)), y= v , data= grouped_dataframe, ax=axes[i])
        i += 1
    plt.tight_layout()
    plt.savefig(corr_dir + '/mean_comparison_by_event.png')


def Plot_groupby_histogram(dataframe, groupby_column, compare_columns, q, adjust,filename):
    if pd.api.types.is_numeric_dtype(dataframe[groupby_column]):
        groups = pd.qcut(dataframe[groupby_column], q=q, duplicates='drop')  
        dataframe['Group'] = groups
        # For numerical variables, group the distribution by quantile parameter of q
    else:
        dataframe['Group'] = dataframe[groupby_column]
        # For categorical variable, use the variable levels to group
    
    if adjust == 1:
        # when adjust == 1, remove outliers beyong 3 std 
        for var in compare_columns:
            mean0 = dataframe[var].mean()
            std_dev = dataframe[var].std()
            min_val = mean0 - 3 * std_dev
            max_val = mean0 + 3 * std_dev
            dataframe = dataframe[(dataframe[var] >= min_val) & (dataframe[var] <= max_val)]
    
    plt.figure(figsize=(12, 6))
    #plt.legend(title = groupby_column)

    # Use seaborn to add histograms to the figure
    for i, var in enumerate(compare_columns):
        plt.subplot(1, len(compare_columns), i+1)
        sns.histplot(data=dataframe, x=var, hue='Group', kde=True, palette='YlGnBu')
        plt.title(f'{var} by Groups',pad =20)
        # plt.xlabel(var)
        plt.ylabel('Frequency')
        plt.grid(True)

    plt.subplots_adjust(wspace=0.5) 
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(corr_dir + f'{filename}_{groupby_column}_hist.png')


def Plot_groupby_boxplot(dataframe, groupby_column, compare_columns,q , adjust, filename):
    '''
    Group dataframe according to groupby_column param, and use boxplots to depict distribution of different groups for a list of variables
    
    param groupby_column: the variable used to group data
    param compare_columns: the list of variable names to compare distribution across groups
    '''
    
    if pd.api.types.is_numeric_dtype(dataframe[groupby_column]):
        groups = pd.qcut(dataframe[groupby_column], q=q, duplicates='drop')  
        dataframe['Group'] = groups
    else:
        dataframe['Group'] = dataframe[groupby_column]

    if adjust == 1:
        for var in compare_columns:
            mean0 = dataframe[var].mean()
            std_dev = dataframe[var].std()
            min_val = mean0 - 3 * std_dev
            max_val = mean0 + 3 * std_dev
            dataframe = dataframe[(dataframe[var] >= min_val) & (dataframe[var] <= max_val)]
    
    plt.figure(figsize=(12, 6))
    # Use seaborn to draw box plots
    for i, var in enumerate(compare_columns):
        plt.subplot(1, len(compare_columns), i+1)
        sns.boxplot(x='Group', y=var, data=dataframe, palette='YlGnBu')
        plt.xticks(rotation=45)
        plt.title(f'{var} by Groups', pad = 10)
        plt.xlabel(groupby_column)
        plt.grid(True)

    plt.subplots_adjust(wspace=0.5) 
    plt.tight_layout()
    plt.savefig(corr_dir + f'{filename}_{groupby_column}_boxplot.png')
    plt.close()


if __name__ == "__main__": 

    root_dir = os.getcwd ()
    # os.mkdir(root_dir +"/results/distribution_plots" ,exist_ok=True)
    # os.mkdir(root_dir +"/results/correlation_plots" , exist_ok=True)
    dist_dir = root_dir +"/results/distribution_plots" 
    corr_dir = root_dir +"/results/correlation_plots" 

    df = pd.read_csv(root_dir+'/data/processed/post_comment_df.csv',index_col=0)
    r = pd.read_csv(root_dir + '/data/raw/unique_weibo_raw_data.csv',index_col=0)
    p = pd.read_csv(root_dir + '/data/processed/posts_for_label.csv',index_col=0)

    #Assign labels with the topic keywords and plot pie charts
    labels =  ['openai','Artificial intelligence risk','Post deletion','Sexual assault','Homeless dogs hurt','Cat abusement','Du Meizhu celebrity scandal']
    Plot_sample_distribution(df,r,p,labels)
    
    # Visualize popularity features
    descriptive_plots(df, 
                      ['textlength','comments_count','repost_count', 'like_count', 'average_commenter_follow','average_text_lenth'], 
                      '/posts_basic_info')
    
    # Visualize textual features
    descriptive_plots(df, 
                      ['moral_wc',
                        'immoral_wc', 
                        'moral_score',
                        'moral_emo',
                        'nonmoral_emo',
                        'average_moral_word', 
                       'average_immoral_word',
                        'positive_prob'], 
                       '/textual_features')

    # Plot a heatmap to observe correlation
    Heatmap(df,'/quant_variables')

    # Based on the heatmap correlation matrix, several variables have general impact on multiple textual features. Therefore, group data to see whether different level of popularity and word count show strong variance.

    vars = ['textlength', 'moral_score', 'moral_wc',
       'immoral_wc', 'positive_prob', 'comments_count',
       'average_moral_word', 'average_immoral_word', 'commenter_gender_ratio',
       'average_positive_possibility', 'positive_negative_ratio',
       'average_text_lenth', 'average_moral_score', 'keyword_code']
    mean_grouped = df[vars].groupby('keyword_code').mean()
    B = df['immoral_wc'] > 0
    C = df['moral_wc'] > 0
    d = df[B & C]
    Plot_groupby_events(mean_grouped,len(vars)-1)
  
    # Try grouping data by popularity measurements
    Plot_groupby_histogram(df,'like_count',['moral_score', 'positive_prob', 'average_moral_score'], q = 4,adjust = 1, filename = '/group_by')

    Plot_groupby_boxplot(df,'like_count',['moral_score', 'positive_prob', 'average_moral_score'], q = 4, adjust = 1, filename = '/group_by')

    # Try grouping data by popularity measurements
    Plot_groupby_boxplot(df,'textlength',['moral_score', 'positive_prob', 'average_moral_score','positive_negative_ratio'], q = 4, adjust = 1, filename = '/group_by')
    Plot_groupby_histogram(df,'textlength',['moral_score', 'positive_prob', 'average_moral_score','positive_negative_ratio'], q = 4, adjust = 1, filename = '/group_by')

    ############################################
    # Try grouping the data based on moral score. 
    Plot_groupby_histogram(df,'moral_score',[ 'comments_count',
       'average_commenter_follow','average_moral_score','positive_negative_ratio'], q = 4, adjust = 1, filename = '/group_by')
    
    Plot_groupby_boxplot(df,'moral_score',[ 'comments_count',
       'average_commenter_follow','average_moral_score','positive_negative_ratio'], q = 4, adjust = 1, filename = '/group_by')


    # The 4 quantile grouping does not show strong variance between groups
    # Try assigning 3 labels to moral scores according to the theoretical implication of this measurement

    bins = [-40, -0.1, 0.1, 40]  
    labels = ['Negative', 'Non-moral', 'Positive']
    df['moral_bins'] = pd.cut(df['moral_score'], bins=bins, labels=labels)

    Plot_groupby_histogram(df,'moral_bins',[ 'comments_count',
       'average_commenter_follow','average_moral_score','positive_negative_ratio'], q = 0, adjust = 1, filename = '/group_by')
    
    Plot_groupby_boxplot(df,'moral_bins',[ 'comments_count',
       'average_commenter_follow','average_moral_score','positive_negative_ratio'], q = 0, adjust = 1, filename = '/group_by')
    
