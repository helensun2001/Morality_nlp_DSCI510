import re
import os

def remove_punctuation(text):
    # 使用正则表达式匹配标点符号，并将其替换为空字符串
    cleaned_text = re.sub(r'[^\w\s]', '', text)
    return cleaned_text

def Check_file_existence(filenames, datapath):
    '''
    Check whether the input filename exist in the datapath 
    '''
    for filename in filenames:
        if os.path.exists(datapath + filename):
            print('csv file alreayd exist, remove first:', datapath + filename)
            os.remove(datapath + filename)

def Write_to_files (results,filename):
    if os.path.exists(filename):
        os.remove(filename)
    for result in results:
        with open(filename,'a') as f:
            f.writelines(','.join(map(str,result))+'\n')
    print(filename +' is ready!')