import os
# from tools import ToolGeneral
# tool = ToolGeneral()

def load_d(file):  
        """
        Load dictionary
        """
        with  open(file,encoding='utf-8',errors='ignore') as fp:
            lines = fp.readlines()
            lines = [l.strip() for l in lines]
            # print("Load data from file (%s) finished !"%file)
            dictionary = [word.strip() for word in lines]
        return set(dictionary)

class LoadDict:
    '''Hyper parameters'''
    try:
        pwd = os.path.dirname(os.getcwd ())
        datapath = pwd +"/data"
        # Load sentiment dictionary
        deny_word = load_d(os.path.join(datapath,'dict','not.txt'))
    except:
        pwd = os.getcwd ()
        datapath = pwd +"/data"
        deny_word = load_d(os.path.join(datapath,'dict','not.txt'))
        modict = load_d(os.path.join(datapath,'dict','moral.txt'))
        immodict = load_d(os.path.join(datapath,'dict', 'immoral.txt'))
        neudict = load_d(os.path.join(datapath,'dict', 'neutral.txt'))
        passivedict = load_d(os.path.join(datapath,'dict', 'passive.txt'))
        pos_neg_dict = immodict|modict
        # # Load adverb dictionary
        mostdict = load_d(os.path.join(datapath,'dict','most.txt'))
        verydict = load_d(os.path.join(datapath,'dict','very.txt'))
        moredict = load_d(os.path.join(datapath,'dict','more.txt'))
        ishdict = load_d(os.path.join(datapath,'dict','ish.txt'))
        insufficientlydict = load_d(os.path.join(datapath,'dict','insufficiently.txt'))
        overdict = load_d(os.path.join(datapath,'dict','over.txt'))
        inversedict = load_d(os.path.join(datapath,'dict','inverse.txt'))



    print('All dictionaries successfully loaded!')