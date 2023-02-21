#pip install xlrd==1.2.0
import os
import xlsxwriter
import pandas as pd
import re
import csv 
import nltk
from nltk import *
from nltk.corpus import wordnet
import spacy
from fuzzywuzzy import fuzz
import json

keyword_dict = list()
nlp = spacy.load('en_core_web_sm')

with open('config/Keyword_list.json') as conf_f:
    keyword_dict = json.load(conf_f)

# In order to avoid naming issues in sheet, use the following formatting
sheet_name_list = ["McDonalds Data","Wendy's Data","Chipotle Data","Yum! Data","Taco Bell Data",
                    "KFC Data","Starbucks Data","Chick Fil A Data","Subway Data","Panera Data"]

def Fuzzy_Matcher(strings,keyword):
    match_key_words = list()

    #Iterating words in Keyword.
    for word in keyword.split():
        #From setntence, selecting words matching with initial two letters of keyword
        a = [s for s in strings.split() if str(s).lower().startswith(str(word).lower()[:2]) ]#and len(s) > 2]        	
        match_key_words += a
    #remove duplicate words from matching list
    match_key_words = list(set(match_key_words))
    match_dict = dict()
    for key_idx,keywords in enumerate(keyword.split()):#loop keywords to find matching character count
        keyword_dict = dict()
        common_word_count = 0
        web_count_dict = dict()
        flag =False
        for key_char_idx,key_chr in enumerate(keywords):	#loop words in keywrod
            for web_idx,web_data in enumerate(match_key_words):#loop maching data list
                if str(web_data).lower().startswith(str(keywords).lower()[:2]):
                    try:
                        if web_count_dict[web_idx]:
                            pass
                    except:
                        web_count_dict[web_idx] = common_word_count
                    try:	
                        wed_data_char = web_data[key_char_idx] 
                        if str(wed_data_char).lower() == str(key_chr).lower():	
                            #print(keywords,key_chr,web_data)
                            web_count_dict[web_idx] += 1
                            keyword_dict[web_data] = web_count_dict[web_idx]
                    except:
                        continue
            
        match_dict[keywords] = keyword_dict
    match_dict_temp = dict()
    #removing words having no matches from keyword match dict
    for k,v in match_dict.items():
        if len(match_dict[k]) != 0 : 
            match_dict_temp[k] = v
    match_ratio_list = list()
    final_match_dict = dict()
    for match_keys in match_dict.keys():
        # calculate match ratio for each matching word using the following equation  /     
        # match_ratio = (common_word_count/keywrd_len)*100
        match_list = list()
        for match_data in match_dict[match_keys]:
            common_word_count = match_dict[match_keys][match_data]
            keywrd_len = len(match_keys)
            match_ratio = (int(common_word_count)/int(keywrd_len))*100
            match_list.append(match_ratio)
        try:
            final_match_dict[match_keys] = max(match_list)
        except:
            pass
    try:
        final_match_ratio = max(final_match_dict.values())
    except ValueError:
        return 0
    return final_match_ratio 


df = pd.read_excel(os.path.join('input','RBI_TextExtraction_Output.xlsx'),sheet_name=None) #input file
op_f = pd.ExcelWriter('./output/RBI_Output.xlsx') #output file
for name, sheet in df.items():
    #Analysis sheet Dataframe
    df1= pd.DataFrame(columns=['Pillar','Bucket','Key Word','Match Type (Exact/Close/Match Ratio >= 80% /Match Ratio >= 70%)','URL','Text','URL - Level'])
    if name in sheet_name_list:
        # row index variable for Analysis sheet.
        key_data_row_index = 1
        #index_flag = False
        for piller_key in keyword_dict.keys():
            bucket_key_list = keyword_dict[piller_key].keys()
            for bucket_key in bucket_key_list:
                keyword_list = keyword_dict[piller_key][bucket_key]
                for key_id, keyword in enumerate(keyword_list):
                    #Removing special charactors from Keyword
                    keyword = re.sub(r'[^a-zA-Z0-9 \.]', ' ', keyword)
                    if str(keyword).lower() == 'greenhouse gas':
                        keyword = 'Greenhouse Gas GHG'
                    print(piller_key,",",bucket_key,",",keyword)
                    #Iterate Data Rows
                    for index,row in df[name].iterrows():
                        print(keyword,"................."+name+".................>Row",index)
                        match_count_exact = 0
                        match_data_list_exact = list()
                        match_count_close = 0
                        match_data_list_close = list()
                        match_count_80 = 0
                        match_data_list_80 = list()
                        match_count_70 = 0 
                        match_data_list_70 = list()
                        url_value = row['URL']                
                        web_data_text = row['Text']
                        record_level = row['Level(Column A)'] 
                        #Spliting sentences in Text column.
                        about_doc = nlp(web_data_text)
                        web_data_list = list(about_doc.sents)                        
                        #Iterate sentences in Text column.
                        for web_idx,web_data in enumerate(web_data_list):                          
                            if str(web_data) != ' ' and str(web_data) != ''  and len(str(web_data).strip()) > 2 :
                                #cleaning splitted sentences.
                                web_data = re.sub(r"[^a-zA-Z0-9 \.]", ' ', str(web_data))
                                web_data = web_data.strip()
                                if (keyword).lower() in web_data.lower():
                                    #Exact matches and close matches checks
                                    pattern1 = keyword 
                                    pattern2 = keyword + str('\w+')
                                    pattern3 = str('\w+') + keyword
                                    a = re.search(pattern1,web_data)
                                    b = re.search(pattern2,web_data)
                                    c = re.search(pattern3,web_data)
                                    if b or c: #Close matches
                                        match_count_close += 1
                                        match_data_list_close.append(web_data)
                                    else: #Exact match
                                        match_count_exact +=1
                                        match_data_list_exact.append(web_data)
                                elif (keyword).lower() == 'greenhouse gas' and ('greenhouse gas' in web_data.lower() or 'ghg' in web_data.lower()):
                                    match_count_exact +=1
                                    match_data_list_exact.append(web_data)        
                                else:#Fuzzy Matching
                                    final_match_ratio = Fuzzy_Matcher(web_data,keyword)
                                    
                                    if final_match_ratio >= 80:
                                        match_count_80 += 1
                                        match_data_list_80.append(web_data) 
                                    elif final_match_ratio >= 70: 
                                        match_count_70 += 1
                                        match_data_list_70.append(web_data)
                        
                        
                        #Analysis Report Sheet
                        no_rows = max(match_count_exact,match_count_close,match_count_80,match_count_70)                
                        temp_df = pd.DataFrame()
                        #loop Exact Matching Record
                        for add_row,exact_match_data in enumerate(match_data_list_exact):                            
                            try:
                                last_row = df1.index[-1] +1
                            except:
                                last_row = 1                            
                            df1.loc[last_row, 'Match Type (Exact/Close/Match Ratio >= 80% /Match Ratio >= 70%)'] = 'Exact Match'
                            df1.loc[last_row, 'Pillar'] = piller_key
                            df1.loc[last_row, 'Bucket'] = bucket_key
                            df1.loc[last_row, 'Key Word'] = keyword                                
                            df1.loc[last_row, 'URL'] = url_value
                            df1.loc[last_row, 'Text'] = exact_match_data
                            df1.loc[last_row, 'URL - Level'] = record_level
                        #loop close Matching Record
                        for add_row,close_match_data in enumerate(match_data_list_close):
                            try:
                                last_row = df1.index[-1] +1
                            except:
                                last_row = 1
                            df1.loc[last_row, 'Match Type (Exact/Close/Match Ratio >= 80% /Match Ratio >= 70%)'] = 'Close Match'
                            df1.loc[last_row, 'Pillar'] = piller_key
                            df1.loc[last_row, 'Bucket'] = bucket_key
                            df1.loc[last_row, 'Key Word'] = keyword                                
                            df1.loc[last_row, 'URL'] = url_value
                            df1.loc[last_row, 'Text'] = close_match_data
                            df1.loc[last_row, 'URL - Level'] = record_level  
                        #loop Records of Match Ratio >= 80%
                        for add_row,match_data_80 in enumerate(match_data_list_80):
                            try:
                                last_row = df1.index[-1] +1
                            except:
                                last_row = 1
                            df1.loc[last_row, 'Match Type (Exact/Close/Match Ratio >= 80% /Match Ratio >= 70%)'] = 'Match Ratio >= 80%'
                            df1.loc[last_row, 'Pillar'] = piller_key
                            df1.loc[last_row, 'Bucket'] = bucket_key
                            df1.loc[last_row, 'Key Word'] = keyword                                
                            df1.loc[last_row, 'URL'] = url_value
                            df1.loc[last_row, 'Text'] = match_data_80
                            df1.loc[last_row, 'URL - Level'] = record_level 
                        #loop Records of Match Ratio >= 70%
                        for add_row,match_data_70 in enumerate(match_data_list_70):
                            try:
                                last_row = df1.index[-1] +1
                            except:
                                last_row = 1
                            df1.loc[last_row, 'Match Type (Exact/Close/Match Ratio >= 80% /Match Ratio >= 70%)'] = 'Match Ratio >= 70%'
                            df1.loc[last_row, 'Pillar'] = piller_key
                            df1.loc[last_row, 'Bucket'] = bucket_key
                            df1.loc[last_row, 'Key Word'] = keyword                                
                            df1.loc[last_row, 'URL'] = url_value
                            df1.loc[last_row, 'Text'] = match_data_70
                            df1.loc[last_row, 'URL - Level'] = record_level  
                    #break #break keywrd
                    print(df1.head())
                #break #break bucket
            #break#break piller
        df[name].to_excel(op_f, sheet_name=name,index= False)
        df1.to_excel(op_f, sheet_name=name+" Analysis",index= False)
        #break
    else:
        print(name)
op_f.save() 
