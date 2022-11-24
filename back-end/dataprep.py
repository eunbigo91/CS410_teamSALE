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

print('Attempting to download required package files...')

# Packages required for tokenization, stopwords, and sentiment analysis
if nltk.download('punkt', quiet=True) and (nltk.download('stopwords', quiet=True)) and (
        nltk.download('vader_lexicon', quiet=True)):
    print('Successfully downloaded required package files.')
else:
    print('Failed to download required packages. Please verify your internet connection and try again.')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

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


# neu: summary score == 0 and reviewText score [0, 0.89]
# pos: summary score > 0 or (summary score == 0 and reviewText score > 0.8963
# neg: summary score < 0 or (summary score == 0 and reviewText score < 0
def categorise(row):
    if row['vedarScore_summary'] == 0 and 0.8963 >= row['vedarScore_reviewText'] >= 0:
        return 'neu'
    elif row['vedarScore_summary'] > 0 or (row['vedarScore_reviewText'] > 0.8963 and row['vedarScore_summary'] == 0):
        return 'pos'
    elif row['vedarScore_summary'] < 0 or (row['vedarScore_reviewText'] < 0 and row['vedarScore_summary'] == 0):
        return 'neg'
    return 'nolabel'


def main():
    df = pd.read_csv(book_review)

    # detect non-English item
    for i in range(df.shape[0]):
        reviewtext = df['reviewText'][i]
        detect_language(reviewtext)  # not all detections are correct. need manual eyeball double check

    print("language detection is completed.")

    detect(df['reviewText'][8345])  # Spanish

    df.drop([8345], axis=0, inplace=True)

    # tokenize and remove stop words
    # df['cleanText'] = df["reviewText"].apply(lambda x: remove_stopwords(x.lower()))
    df['cleanText'] = df["reviewText"].apply(lambda x: remove_stopwords(x))

    # check short reviews
    df['count'] = df['cleanText'].apply(lambda x: len(x))
    df['short'] = np.where(df['count'] < 3, 'True', 'False')
    short_word = df[df['short'] == 'True']

    # check if data is balanced
    df.rating.value_counts()
    '''
    5    3000
    4    3000
    3    2000
    2    2000
    1    2000
    '''

    df.isnull().sum()  # no NAs

    df['finalText'] = df['cleanText'].apply(lambda x: " ".join(map(str, x)))

    sentiment = SentimentIntensityAnalyzer()
    df['vedarScore'] = df['finalText'].apply(lambda x: sentiment.polarity_scores(x)['compound'])
    df['vedarScore_reviewText'] = df['reviewText'].apply(lambda x: sentiment.polarity_scores(x)['compound'])
    df['vedarScore_summary'] = df['summary'].apply(lambda x: sentiment.polarity_scores(x)['compound'])

    # data analysis to determine cut-off of sentiment score
    data = df[['asin', 'rating', 'reviewText', 'summary', 'vedarScore', 'vedarScore_reviewText', 'vedarScore_summary']]

    vedar_summary_neg = data.loc[data['vedarScore_summary'] < 0]
    vedar_summary_neg.rating.value_counts()
    (vedar_summary_neg.vedarScore_reviewText < 0).sum() / vedar_summary_neg.shape[0]
    (vedar_summary_neg.vedarScore < 0).sum() / vedar_summary_neg.shape[0]
    (vedar_summary_neg.rating < 3).sum() / vedar_summary_neg.shape[0]
    (vedar_summary_neg.rating <= 3).sum() / vedar_summary_neg.shape[0]

    neu_rating = data.loc[data['rating'] == 3]
    neu_rating.vedarScore.describe()
    neu_rating.vedarScore_reviewText.describe()
    neu_rating.vedarScore_summary.describe()

    neg_rating = data.loc[data['rating'] < 3]
    neg_rating.vedarScore.describe()
    neg_rating.vedarScore_reviewText.describe()
    neg_rating.vedarScore_summary.describe()

    pos_rating = data.loc[data['rating'] > 3]
    pos_rating.vedarScore.describe()
    pos_rating.vedarScore_reviewText.describe()
    pos_rating.vedarScore_summary.describe()

    data['label'] = data.apply(lambda row: categorise(row), axis=1)
    data.label.value_counts()

    # nolabel = data.loc[data['label'] == 'nolabel']

    data.to_csv('back-end/output/sentiment_output.csv', index = False)
