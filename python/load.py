# -*- coding: utf-8 -*-
__author__ = 'Lara Olmos Camarena'

import re
import json

import re

"""
utils
"""

def preprocess_text(text_str):
    regular_expr = re.compile('\n|\r|\t|\(|\)|\[|\]|:|\,|\;|"|\?|\-|\%')
    text_str = re.sub(regular_expr, ' ', text_str)
    token_list = text_str.split(' ')
    token_list = [element for element in token_list if element]
    return ' '.join(token_list)


def sublist(lst1, lst2):
    if len(lst1) > 1:
        res1 = set(lst1)
    else:
        res1 = set(list(lst1))
    res2 = set(lst2)
    return res1 <= res2

"""
NER
"""

NER_TYPES = ['ORGANIZATION',  
             'PERSON', 'TITLE', 'IDEOLOGY',
             'CITY',  'COUNTRY',  'LOCATION', 'NATIONALITY', 'STATE_OR_PROVINCE',
             'DATE',  'DURATION',  'TIME',
             'PERCENT',  'NUMBER',  'ORDINAL',  'MONEY', 
             'CAUSE_OF_DEATH', 'CRIMINAL_CHARGE',  'RELIGION']

def load_data(string_element):
    data = {}
    if string_element == '{}' or string_element == '[]':
        return data
    try:
        raw_data = str(string_element).replace("',", '",').replace("['", '["').replace("']", '"]').replace("':", '":').replace("{'", '{"').replace(", '", ', "')
        data = json.loads(raw_data)
    except Exception as e:
        print(e)
        print(raw_data)
    return data

def get_ner_values(ner_dict, specific_ner):
    if ner_dict and specific_ner in ner_dict.keys():
        return list(ner_dict[specific_ner])
    return []

def get_ner_tags(ner_dict):
    if ner_dict:
        return list(ner_dict.keys())
    return []

def get_ner_count(ner_dict, specific_ner):
    if ner_dict and specific_ner in ner_dict.keys():
        return len(ner_dict[specific_ner])
    return 0

def ner_type_answer(element):
    if element in ['CAUSE_OF_DEATH', 'CITY', 'COUNTRY', 'CRIMINAL_CHARGE', 'DATE',
       'DURATION', 'IDEOLOGY', 'LOCATION', 'MISC', 'MONEY', 'MULTI',
       'NATIONALITY', 'NONE', 'NUMBER', 'ORDINAL', 'ORGANIZATION',
       'PERCENT', 'PERSON', 'RELIGION', 'SET', 'STATE_OR_PROVINCE',
       'TIME', 'TITLE']:
        return element
    return 'MISC'


"""
POS TAGGING
"""

# ALL TYPES: ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'IN', 'JJ', 'JJR', 'JJS', 'MD', 'NN', 'NNS', 'NP', 'NPS', 'PDT', 'POS', 'PP', 'PP', 'RB', 'RBR', 'RBS', 'RP', 'SENT', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBZ', 'VBP', 'VD', 'VDD', 'VDG', 'VDN', 'VDZ', 'VDP', 'VH', 'VHD', 'VHG', 'VHN', 'VHZ', 'VHP', 'VV', 'VVD', 'VVG', 'VVN', 'VVP', 'VVZ', 'WDT', 'WP', 'WP', 'WRB', ':', '$']

pattern_pos = r"pos=['\"]('?\w+|``)?[\?,.`\[\]]?['\"]"
reg_expr_pos = re.compile(pattern_pos)
def get_pos(text):
    return [item.replace('pos=','').replace("'",'') for item in re.findall(reg_expr_pos, text)]

pattern_word = r"word=['\"]([\"'`]?(\w|\.|,|\-)+)?[\?,.\[\]]?['\"]"
reg_expr_word = re.compile(pattern_word)
def get_word_pos(text):
    return [item[0].replace('word=','').replace("'",'') for item in re.findall(reg_expr_word, text)]

def get_pos_count(pos_list, specific_pos):
    if pos_list and specific_pos in pos_list:
        return pos_list.count(specific_pos)
    return 0

def pral_pos(pos_str):
    if 'NP' in pos_str:
        return 'NP'
    if 'JJ' in pos_str:
        return 'JJ'
    if 'V' in pos_str:
        return 'V'
    if 'R' in pos_str:
        return 'R'
    if 'CD' in pos_str:
        return 'CD'
    if 'NN' in pos_str:
        return 'NN'    
    return ''

import treetaggerwrapper
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR='C:\\Users\\larao_000\\Documents\\nlp\\tree-tagger-windows-3.2.3\\TreeTagger\\')

def pos_tagging(text, max_length=1000):
    results = []
    for i in range(0, len(text), max_length):
        partial_text = text[i:i+max_length]
        tags = tagger.tag_text(partial_text)
        results += treetaggerwrapper.make_tags(tags)
    return results


"""
Primer sustantivo de la pregunta, o en caso de partícula Wh, es automático. 
Where -> place, Who -> person. No tiene por qué aparecer en el texto explícito. 

WDT	wh-determiner	which;
WP	wh-pronoun	who, what;
WP$	possessive wh-pronoun	whose;
WRB	wh-abverb	where, when
"""

def wh_query(foco, common_wh=['what', 'who', 'where', 'when', 'why', 'which', 'how', 'in', 'the']):
    if foco in common_wh:
        return foco
    return 'other'


def obtener_foco(query, query_pos):
    candidate_focus = []
    minor_index = []
    if len(query) > 0:
        if (query[0].lower() == 'who') and 'WP' in query_pos:
            candidate_focus.append('person')
        if 'WP$' in query_pos[0]:
            candidate_focus.append('person')
        if (query[0].lower() == 'where') and 'WRB' in query_pos:
            candidate_focus.append('place')
        if (query[0].lower() == 'when') and 'WRB' in query_pos:
            candidate_focus.append('time')
  
        if sublist(['NN'],query_pos):
            minor_index.append(query_pos.index('NN'))
        if sublist(['NNS'],query_pos):
            minor_index.append(query_pos.index('NNS'))
        if sublist(['NPS'],query_pos):
            minor_index.append(query_pos.index('NPS'))
        if sublist(['NP'],query_pos):
            minor_index.append(query_pos.index('NP'))
        
        if sublist(['WP'], query_pos) and not sublist(['NN'], query_pos) and not sublist(['NNS'], query_pos) and not sublist(['NP'], query_pos) and not sublist(['NPS'], query_pos):
            if sublist(['VVG'], query_pos):
                minor_index.append(query_pos.index('VVG'))
            if sublist(['JJ'], query_pos):
                minor_index.append(query_pos.index('JJ'))
            if sublist(['VVN'], query_pos):
                minor_index.append(query_pos.index('VVN'))
            if sublist(['VVD'], query_pos):
                minor_index.append(query_pos.index('VVD'))
            if sublist(['RB'], query_pos):
                minor_index.append(query_pos.index('RB'))            
               
        if len(minor_index) > 0 and min(minor_index) < len(query) and min(minor_index) >= 0:
            candidate_focus.append(query[min(minor_index)])

        if ('how much' in ' '.join(query).lower()) or ('how many' in ' '.join(query).lower()):
            candidate_focus.append('quantity')
            
    if candidate_focus:
        return candidate_focus[0]
    else:
        return ''


def transform_foco(foco, common_focos=['type', 'kind', 'percentage', 'term', 'group',
    'language', 'part', 'date', 'word', 'example', 'period', 'event', 'product', 
    'title', 'ideology', 'religion', 'money', 'percentage']):
    
    # who, what
    if foco in ['person','name','people', 'names','nationalities', 'nationality']:
        return 'person'
    if foco in ['organization','company','companies','organizations']:
        return 'organization'

    # where 
    if foco in ['place', 'country', 'city', 'state', 'province', 'location', 'area', 'region', 
                     'areas','locations','states', 'cities', 'countries']:
        return 'location'

    # when
    if foco in ['time', 'duration', 'age', 'year', 'month', 'day', 'week', 'hour', 'decade', 'century',
                     'days', 'years', 'hours', 'ages', 'weeks', 'decades', 'months', 'centuries']:
        return 'time'
    
    if foco in ['number','numbers','quantity']:
    	return 'number'

    if foco in common_focos:
        return foco
    if foco[-1]=='s' and len(foco) > 2 and foco in common_focos:
        return foco[:-1]

    if foco == 'nan' or foco == '':
        return 'other'
    
    # NN, what, ...
    foco_pos = pos_tagging(str(foco))
    if foco_pos[0].pos == 'NN' or foco_pos[0].pos == 'NNS':
        return 'NN'
    if foco_pos[0].pos == 'NP' or foco_pos[0].pos == 'NPS':
        return 'NP'

    return 'other'


def validate_foco_ner(foco, ner_query, answer):
    result = 'KO'
    foco_pos = get_pos(str(pos_tagging(foco)))
    if foco_pos:
        foco_pos = foco_pos[0]
    if not isinstance(ner_query, list):
        ner_query = str(ner_query).replace('[','').replace(']','').replace("'", '').split(', ')
    if ner_query == '[]':
        result = 'NA'
    elif ner_query == []:
        result = 'NA'
    elif not foco or foco == 'NaN':
        result = 'NA'
    elif str(answer)!='' and str(answer)!='NaN' and str(answer)!='[NaN]':

        if (foco.lower() in ['person','name','people', 'names','nationalities', 'nationality'] or foco_pos in ['NP','NPS']) and sublist(ner_query,['PERSON', 'ORGANIZATION', 'TITLE', 'NATIONALITY']):
            result = 'OK-PERSON-ORG'

        if (foco.lower() in ['place', 'country', 'city', 'state', 'province', 'location', 'area', 'region', 
                     'areas','locations','states', 'cities', 'countries'] or foco_pos in ['NP','NPS']) and sublist(ner_query,['CITY', 'COUNTRY', 'LOCATION', 'STATE_OR_PROVINCE']):
            result = 'OK-LOC'

        if (foco.lower() in ['time', 'duration', 'age', 'year', 'month', 'day', 'week', 'hour', 'decade', 'century',
                     'days', 'years', 'hours', 'ages', 'weeks', 'decades', 'months', 'centuries']) and sublist(ner_query,['DATE', 'TIME', 'DURATION', 'NUMBER']):
            result = 'OK-TIME'

        if (foco.lower() in ['titles','title','role','roles']) and sublist(ner_query,['TITLE']):
            result = 'OK-TITLE'
        if (foco.lower() in ['percentage']) and sublist(ner_query,['PERCENT']):
            result = 'OK-PERCENT'
        if (foco.lower() in ['number','numbers','quantity', 'money', 'age', 'percentage'] or foco_pos in ['CD','LS', 'NNS']) and sublist(ner_query,['NUMBER', 'PERCENT', 'MONEY', 'ORDINAL', 'CARDINAL']):
            result = 'OK-NUMBER'

        if foco and sublist([foco.upper()], ner_query):
            result = 'OK-' + foco.upper()
        elif foco and foco[-1]=='s' and len(foco) > 2 and sublist([foco[:-1].upper()], ner_query):
            result = 'OK-' + foco[:-1].upper()
    else:
        result='NA'
    return result

"""
QA
"""

def load_answer_data(string_element):
    data = {}
    if string_element == '{}' or string_element == '[]':
        return data
    try:
        raw_data = str(string_element).replace("',", '",').replace("['", '["').replace("']", '"]').replace("':", '":').replace("{'", '{"').replace(", '", ', "').replace(": '", ': "').replace("'}", '"}').replace(': \\"', ': "').replace('\\"}', '"}')
        raw_data = raw_data.replace('\\""','"').replace("\\'","'").replace('""', '"\"').replace('""','"')
        answer_data = re.search(r'"answer": ".*"}', raw_data).group(0).replace('"answer": ', '').replace('"}', '').replace('"', '').replace("'", '').replace("\\",'')
        raw_data = raw_data[:raw_data.index('answer": ')+len('answer": ')] + '"'+ answer_data + '"}'
        
        data = json.loads(raw_data)
    except Exception as e:
        print(e)
        print(raw_data)
    return data


def correct(answer, model_answer, plausible):
    answer = str(answer).replace("'", '').replace('"', '').replace(',','')
    model_answer = str(model_answer).replace("'", '').replace('"', '').replace(',','')
    plausible = str(plausible).replace("'", '').replace('"', '').replace(',','').replace('.','')
    if answer and model_answer:
        if answer == model_answer:
            return True
        if str(answer).lower().replace('the ', '') == str(model_answer).lower().replace('the ', ''):
            return True
        if str(answer).lower() in str(model_answer).lower() or str(model_answer).lower() in str(answer).lower():
            return True
    elif plausible and model_answer:
        if plausible == model_answer:
            return True
        if str(plausible).lower().replace('the ', '') == model_answer.lower().replace('the ', ''):
            return True
        if str(plausible).lower() in str(model_answer).lower() or str(model_answer).lower() in str(plausible).lower():
            return True
    elif answer == '' and model_answer == '':
    	return True
    return False

def correct_medium(answer, model_answer, plausible):
    answer = answer.replace("'", '').replace('"', '').replace(',','')
    model_answer = model_answer.replace("'", '').replace('"', '').replace(',','')
    plausible = plausible.replace("'", '').replace('"', '').replace(',','')
    
    if answer and model_answer:
        if answer == model_answer:
            return 'FACIL'
        if str(answer).lower().replace('the ', '') == str(model_answer).lower().replace('the ', ''):
            return 'FACIL'
        if str(answer).lower() in str(model_answer).lower() or str(model_answer).lower() in str(answer).lower():
            return 'MEDIA'
    elif plausible and model_answer:
        if plausible == model_answer:
            return 'FACIL'
        if str(plausible).lower().replace('the ', '') == model_answer.lower().replace('the ', ''):
            return 'FACIL'
        if str(plausible).lower() in str(model_answer).lower() or str(model_answer).lower() in str(plausible).lower():
            return 'MEDIA'
    return 'DIFICIL'