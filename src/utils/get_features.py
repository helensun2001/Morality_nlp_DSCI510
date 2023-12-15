## Run this file to generate moral_label csv file in \data 


import spacy
import networkx as nx
from cnsenti import Emotion
import os
import pandas as pd
from snownlp import SnowNLP
import numpy as np
import re
from .load_dict import LoadDict as ld
from google.cloud import translate_v2 as translate


def translate_text(target: str, text: str) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    
    API_key = 'AIzaSyABgf913U4l0pc8mbw4gw9-FphQIOzaLXE'

    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language= target)

    return result["translatedText"]



def Check_morality(token:str, wc_dict):
    if token in ld.modict:
        wc_dict['moralwc'] = wc_dict.get('moralwc',0) + 1
        return 1
    elif token in ld.immodict:
        wc_dict['immoralwc'] = wc_dict.get('immoralwc',0) + 1
        return -1
    elif token in ld.deny_word | ld.inversedict:
        return -1
    else:
        wc_dict['otherwc'] = wc_dict.get('otherwc',0) + 1
        return 0


def Get_Weighted_Score(textlist: list):
    '''
    Compute the weighted morality score of a list of texts and count the differnt types of morality-related words in each text.
    Return a list.
    '''
    # python -m spacy download zh_core_web_sm
    m1 = spacy.load('zh_core_web_sm')

    #load all moral dictionary and d update the Spacy segment dictionary with them
    WordList = ld.modict | ld.immodict | ld.neudict | ld.passivedict
    m1.tokenizer.pkuseg_update_user_dict(WordList)

    text_length,score_list, moral_wc, immoral_wc, other_wc = [],[],[],[],[]

    for text in textlist:
        doc = m1(text)
        G = nx.Graph()

        edges = []
        nodes = []
        
        for token in doc:
            edges.append((token.text,token.head.text))
        G.add_edges_from(edges)  # using a list of edge tuplesv
        
        for n in G.nodes:
            if bool(re.match(r'[^\w\s]', n)) is False:
                nodes.append(n)
        text_length.append(len(nodes))

        try:
            weight_dict = nx.eigenvector_centrality(G)
        except:
            weight_dict = nx.degree_centrality(G)
            # There're around 0.3 % cases in the samples that eigenvector centrality cannot be computed due to the limitation of networkx's iteration limit. Shift to compute degree centrality instead when error occurs.
        
        scores = []
        
        wc_dict = {'moralwc': 0,
                   'immoralwc':0,
                   'otherwc':0}
        for word, w in weight_dict.items():
            morality_unit = Check_morality(word,wc_dict) 

            score = morality_unit * w
            scores.append(score)
        
        score_list.append(sum(scores*100)/len(scores))
        # Average the score by the wordcount of spacy word segment. Multiplied by 100 to increase to 

        moral_wc.append(wc_dict['moralwc'])
        immoral_wc.append(wc_dict['immoralwc'])
        other_wc.append(wc_dict['otherwc'])
    
    return [text_length, score_list, moral_wc, immoral_wc, other_wc]
        #moral_index = 1 + (4 * moral_count)/(moral_count + immoral_count + 1)


def Get_snownlp_score(texts:list):
    
    positive_prob, sub_probs = [],[]
    for text in texts:
        blob = SnowNLP(text)
        sub_text_list = blob.sentences

        sub_sentiment = []
        for sub in sub_text_list:
            sub_sentiment.append(SnowNLP(sub).sentiments)    
        
        positive_prob.append(round(blob.sentiments*100,4))
        #possibility of a text to be expressing positive emotions
        
        sub_probs.append(sub_sentiment)
        #variance of positive possibility between sentences

    return [positive_prob,sub_probs]


def Sentiment_wordcount_by_category(texts:list)->list:
    emotion = Emotion()
    goodness, happiness, sadness, anger, afraid, disgust, surprise = [],[],[],[],[],[],[]
    
    for text in texts:
        result = emotion.emotion_count(text)
        goodness.append(result['好'])
        happiness.append(result['乐'])
        sadness.append(result['哀'])
        anger.append(result['怒'])
        afraid.append(result['惧'])
        disgust.append(result['恶'])
        surprise.append(result['惊'])

        #ave_by_wordcount = [round(i*100,2) for i in oneline]
        #results.append(ave_by_wordcount)
    return [goodness,happiness,sadness,anger,afraid,disgust,surprise]




 
# if __name__ == "__main__":    
#     #
#     l = ['二次酒驾是不负责任和危险的行为，可能对自己和他人的安全造成严重威胁。酒后驾驶不仅违反了交通法规，也可能导致严重后果，包括发生事故，可能造成人员伤亡和财产损失。']
#     score = Get_Weighted_Score(l)
#     print(score)
#     print(Get_snownlp_score(l))          

