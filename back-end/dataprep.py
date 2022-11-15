##################################################################
# Project: Book review sentiment analysis and recommendation     #
# Team: SALE                                                     #
# Authors: Lingfei Yang                                          #
# Part I: data preparation                                       #
##################################################################

import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langdetect import detect  # for language detection

book_review = 'back-end/data/kindle_review.csv'
# index_file = 'back-end/text_retrieval/bm25.pkl'

# tokenize and remove stopwords
stop_words = set(stopwords.words('english'))


def remove_stopwords(review):
    word_tokens = word_tokenize(review)
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    return filtered_sentence


# Detect the language of the review
def detect_language(review):
    review = review.lower()
    if detect(review) != 'en':
        print(i, ": ", review)


def main():
    df = pd.read_csv(book_review)

    # detect non-English item
    for i in range(df.shape[0]):
        reviewtext = df['reviewText'][i]
        detect_language(reviewtext) # not all detections are correct. need manual eyeball double check

    print("language detection is completed.")

    detect(df['reviewText'][8345])  # Spanish

    df.drop([8345], axis=0, inplace=True)

    # tokenize and remove stop words
    df['cleanText'] = df["reviewText"].apply(lambda x: remove_stopwords(x.lower()))

    # check short reviews
    df['count'] = df['cleanText'].apply(lambda x: len(x))
    df['short'] = np.where(df['count'] < 3, 'True', 'False')
    short_word = df[df['short'] == 'True']