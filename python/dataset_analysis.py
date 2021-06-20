# -*- coding: utf-8 -*-
__author__ = 'Lara Olmos Camarena'

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
import re
import seaborn as sns
from matplotlib import rcParams


def preprocess_text(text_str):
    regular_expr = re.compile('\n|\r|\t|\(|\)|\[|\]|:|\,|\;|"|\?|\'|\-')
    text_str = re.sub(regular_expr, ' ', text_str)
    text_str = text_str.lower()
    token_list = text_str.split(' ')
    token_list = [element for element in token_list if element]
    return ' '.join(token_list)

def token_frequency(raw_tokens):
	text_series = pd.Series(raw_tokens)
	word_freq = text_series.value_counts()
	return pd.DataFrame({'token': word_freq.index.values, 'count': word_freq.values})

def generate_word_cloud(text_str, max_words=15, colormap='viridis', stopwords=[]):
	word_cloud = WordCloud(max_font_size=50, background_color='white', max_words=max_words, stopwords=stopwords, colormap=colormap).generate(text_str)
	plt.figure(figsize=(10,10))
	plt.imshow(word_cloud)
	plt.axis('off')
	plt.show()

def plot_pie_chart(original_labels, original_values, element, thresold_others=5):
	labels = list(element.value_counts().index)
	sizes = list(element.value_counts().values)
	aggregate_others = 0
	compose_labels = []
	pairs = zip(original_labels, original_values)
	for (x, y) in pairs:
		if y <= thresold_others:
			element_index = labels.index(x)
			aggregate_others += y
			compose_labels.append(x)
			del labels[element_index]
			del sizes[element_index]
	try:
		if labels.index('') >= 0:
			labels[labels.index('')] = 'NO CONSTA'
	except:
		pass

	labels.append('OTROS:' + ',\n'.join(compose_labels))
	sizes.append(aggregate_others)
	fig1, ax1 = plt.subplots(figsize=(10,10))
	ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
	ax1.axis('equal')
	plt.show()

def print_means_by(data, x_tag, y_tag):
	ax = sns.barplot(x=x_tag, y=y_tag, data=data)
	element_list = []
	for p in ax.patches:
		ax.annotate(format(p.get_height(), '.1f'), (p.get_x() + p.get_width(), p.get_height()), 
			ha='center', va='center', xytext=(0,9), textcoords='offset points')
		element_list.append(p.get_height())
	return element_list


if __name__ == '__main__':
	train_data = pd.read_csv('train_queries.csv', encoding='utf-8', sep=';')
	test_data = pd.read_csv('dev_queries.csv', encoding='utf-8', sep=';')

	query_len_train = train_data['query_proc'].apply(lambda x: len(x.split(' ')))
	query_len_test = test_data['query_proc'].apply(lambda x: len(x.split(' ')))
	query_len = np.concatenate((query_len_train, query_len_test), axis=None)

	print(np.mean(query_len))
	print(np.max(query_len))
	print(np.min(query_len))