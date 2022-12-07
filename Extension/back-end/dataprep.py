print('''

##################################################################
# Project: Book review sentiment analysis and recommendation     #
# Team: SALE (Eunbi, Sruthi, Lingfei, Akarsh)                    #
# Authors: Lingfei Yang                                          #
# Part I: data preparation and Sentiment analysis                #
##################################################################

''')

import nltk
import numpy as np
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from langdetect import detect  # for language detection
pd.options.mode.chained_assignment = None  # default='warn'

print('Attempting to download required package files...')

# Packages required for tokenization, stopwords, and sentiment analysis
if nltk.download('punkt', quiet=True) and (nltk.download('stopwords', quiet=True)) and (
        nltk.download('vader_lexicon', quiet=True)):
    print('Successfully downloaded required package files.')
else:
    print('Failed to download required packages. Please verify your internet connection and try again.')

from nltk.sentiment.vader import SentimentIntensityAnalyzer

book_review = 'data/kindle_review.csv' # full path: Extension/back-end/data/kindle_review.csv

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
def detect_language(review, i):
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

    print("Reading raw data...")
    df = pd.read_csv(book_review)

    print("Raw data is read successfully. \n")

    # detect non-English item
    print("Step 1: Data preparation\n" )
    print("(1) detect non-English item... eye manual double confirmation. The following shows the rows package identified as non-English...\n")

    for i in range(df.shape[0]):
        reviewtext = df['reviewText'][i]
        detect_language(reviewtext, i)  # not all detections are correct. need manual eyeball double check

    print("\nlanguage detection is completed. After double confiramtion, only row 8345 is Spanish. All others are valid English reviews.")

    #detect(df['reviewText'][8345])  # Spanish

    #df.drop([8345], axis=0, inplace=True)

    #print("non-English reviews are removed. ")


    print("\n(2) tokenize and remove stop words ...")
    # tokenize and remove stop words
    # df['cleanText'] = df["reviewText"].apply(lambda x: remove_stopwords(x.lower()))
    df['cleanText'] = df["reviewText"].apply(lambda x: remove_stopwords(x))

    print("\n(3) checking short reviews ... ")
    # check short reviews
    df['count'] = df['cleanText'].apply(lambda x: len(x))
    df['short'] = np.where(df['count'] < 3, 'True', 'False')
    short_word = df[df['short'] == 'True']

    print(short_word.head())
    print("Short Reviews look reasonable to be kept as they are meaningful.")


    # check if data is balanced
    print("\n(4) checking if data is balanced...")
    print(df.rating.value_counts())
    '''
    5    3000
    4    2999
    3    2000
    2    2000
    1    2000
    '''
    print("\n(5) checking if data has blank reviews...")
    print(df.isnull().sum()) # no NAs
    print("no blank reviews.")

    print("\n (6) Obtain final text by combining words that are not stopwords in the review after tokenization..")
    df['finalText'] = df['cleanText'].apply(lambda x: " ".join(map(str, x)))
    print("Done.")

    print("\n Step 2: Sentiment Analysis \n Apply Vedar models on \n (1) final text generated from the data prep \n (2) original review text \n (3) review summary (title)")
    sentiment = SentimentIntensityAnalyzer()
    df['vedarScore'] = df['finalText'].apply(lambda x: sentiment.polarity_scores(x)['compound'])
    df['vedarScore_reviewText'] = df['reviewText'].apply(lambda x: sentiment.polarity_scores(x)['compound'])
    df['vedarScore_summary'] = df['summary'].apply(lambda x: sentiment.polarity_scores(x)['compound'])

    # data analysis to determine cut-off of sentiment score
    data = df[['asin', 'rating', 'reviewText', 'summary', 'vedarScore', 'vedarScore_reviewText', 'vedarScore_summary']]

    print("\n identifying cut-offs for positive, neutral and negative...")
    print("\n Vedar Score with summary text: ")
    vedar_summary_neg = data.loc[data['vedarScore_summary'] < 0]
    print("count of score of summary < 0: \n", vedar_summary_neg.rating.value_counts())
    print("Among summary score <0 reviews, the percentage of review text Vedar score < 0: ", (vedar_summary_neg.vedarScore_reviewText < 0).sum() / vedar_summary_neg.shape[0])
    print("Among summary score <0 reviews, the percentage of final cleaned version of review text Vedar score < 0: ", (vedar_summary_neg.vedarScore < 0).sum() / vedar_summary_neg.shape[0])
    print("Among summary score <0 reviews, the percentage of rating score < 3: ", (vedar_summary_neg.rating < 3).sum() / vedar_summary_neg.shape[0])
    print("Among summary score <0 reviews, the percentage of rating score <= 3: ", (vedar_summary_neg.rating <= 3).sum() / vedar_summary_neg.shape[0])

    print("Check the performance by observing rating = 3 reviews")
    neu_rating = data.loc[data['rating'] == 3]
    print("Vedar score statistics for cleaned version of text after tokenization: ", neu_rating.vedarScore.describe())
    print("Vedar score statistics for review text without tokenization: ", neu_rating.vedarScore_reviewText.describe())
    print("Vedar score statistics for summary (title): ", neu_rating.vedarScore_summary.describe())

    print("\nCheck the performance by observing rating < 3 reviews")
    neg_rating = data.loc[data['rating'] < 3]
    print("Vedar score statistics for cleaned version of text after tokenization: ", neg_rating.vedarScore.describe())
    print("Vedar score statistics for review text without tokenization: ", neg_rating.vedarScore_reviewText.describe())
    print("Vedar score statistics for summary (title): ", neg_rating.vedarScore_summary.describe())

    print("\nCheck the performance by observing rating > 3 reviews")
    pos_rating = data.loc[data['rating'] > 3]
    print("Vedar score statistics for cleaned version of text after tokenization: ", pos_rating.vedarScore.describe())
    print("Vedar score statistics for review text without tokenization: ",pos_rating.vedarScore_reviewText.describe())
    print("Vedar score statistics for summary (title): ", pos_rating.vedarScore_summary.describe())

    print("\nApply the cut-off based on the following rules: \n")
    print(" neutral: summary score == 0 and reviewText score [0, 0.8963]; \n positive: summary score > 0 or (summary score == 0 and reviewText score > 0.8963; \n negative: summary score < 0 or (summary score == 0 and reviewText score < 0")

    data['label'] = data.apply(lambda row: categorise(row), axis=1)
    data.label.value_counts()

    # nolabel = data.loc[data['label'] == 'nolabel']

    print("\nLabel of sentiment has been created successfully, output saving ...")
    data.to_csv('back-end/output/sentiment_output_original.csv', index = False)

    print("\nOutput sentiment_output_original.csv has been saved. ")


main()