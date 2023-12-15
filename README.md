
# Moral judgement and sentimental analysis on Chinese social media platform
This project extracts textual features from posts and comments on Sinaweibo.com and gives a fundamental analysis on how moral judgement and sentiments on social media are correlated with other variables.

## Datasets
### How to get data
Data collection is done through running [src/get_data.py](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/src/get_data.py) in two steps:
1. Scrape source posts using Selenium and Chromedriver.
2. Scrape comments data through mid information in step 1. All comments data are from the sourceposts comment areas.
> - Run [get_data.py](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/src/get_data.py), by default the realtime scraper is commented out.
> - Make sure you have a Sinaweibo.com account before removing the comments and call the [realtime scraper](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/utils/weibo_realtime_scraper.py), as it requires __manual login onto Sinaweibo.com__.

### Data overview
1. Source posts: first 50 pages of data covering seven topics, including __2784 source posts__.
>    - Openai 
>    - AI risk
>    - Post deletion
>    - Sexual assault
>    - Homeless dogs attacking people
>    - Cat abusing
>    - Du Meizhu scandal

2. Comments: all comments from source posts, including __5781 comments__.

## Data cleaning
1. Data is cleaned through running [clean_features.py](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/src/clean_features.py)
2. New data files will be generated in folder [/data/processed](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/data/processed).
3. All processed data are concated into [post_comment_df.csv](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/data/processed/post_comment_df.csv) for further analysis.

## Data analysis & visualization
> All results are stored in sub folders within the ``/results`` folder.
> You can delete all folders in results and run scripts to re-create them.

### Output overview
There are 5 sub folders and 2 documents in the ``/results`` folder.
> - __Final_report_LeyiS.pdf__
> - __Final_report_APPENDIX_LeyiS.pdf__
> - ``/description``: contain txt files
> - ``/distribution_plots``: contain png files
> - ``/correlation_plots``: contain png files 
> - ``/anova``: contain png and txt files
> - ``/regression``: contain png and txt files

### How to create or update output files
1. Run [analyze_data.py](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/src/analyze_data.py) to create outputs of variable descriptions. Results stored in ``/description``
2. Run [visualize_results.py](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/src/visualize_results.py) to create plots corresponding to step 1 analysis. Plots stored in two folders: ``/correlation_plots`` and ``/distribution_plots``
3. Run [statistic_testing.py](https://github.com/Fall23-DSCI-510/final-project-helensun2001/blob/main/src/statistic_testing.py) to create outputs of ANOVA analysis and linear regression. Results stored in two folders: ``/anova`` and ``/regression``

## Version and installation
Python == 3.11.5 
All requirements can be installed by pip.


