# Classifying Twitter Information Operations Using Natural Language Processing, User Patterns of Life, and Ensemble Methods

## Purpose: 
The purpose of this project is to evaluate different approaches to classifying information operations and disinformation activity targeting from legitimate user activity on Twitter. This project specifically attempts to classify Russian information operations (IO) users targeting English-language victims from legitimate users.

## Method: 
The IO data was from Twitter's publically released datasets. This data was used to generate a comprehensive list of words, which were used to randomly query legitimate users by topic via Twitter's API. These legitimate users were then filtered for bots using the Botometer API. A Bag of Words was then developed for every user from the aggregate of their tweets, and additional pattern-of-life metrics and statistics were calculated from their posting and engagement behavior. We then evaluated machine learning models on the BoW vectors and pattern-of-life metrics separately, and then performed ensemble voting methods using models trained on both BoW and pattern of life features. Models trained on the BoW vectors include Multinomial Naive Bayes, Stochastic Gradient Descent, and a Multilayer Perceptron Network. Models trained on the user pattern of life metrics included Random Forests and a Support Vector Classifier.

## Environment: 
Code was developed in Google Colab Pro using a High-RAM and TPU runtime environment with data stored in Google Drive, because the amount of RAM required exceeded the capabilities of a personal PC, so file storage and retrieval operations in the code reflect this.

## Data: 
Original datasets can be downloaded from Twitter's public Information Operations datasets: https://transparency.twitter.com/en/reports/information-operations.html. Data used for this project includes the Russian datasets released in September 2020, May 2020, June 2019, January 2019, and October 2018.
