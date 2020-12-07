<div align="center"><h1>Using Machine Learning to Classify Information Operations on Twitter Using Natural Language Processing, User Patterns of Life, and Ensemble Methods</h1></div>

## Purpose
The purpose of this project is to evaluate different approaches to classifying information operations and disinformation activity targeting from legitimate user activity on Twitter. This project specifically attempts to classify Russian information operations (IO) users targeting English-language victims from legitimate users.

## Method
The IO data was from Twitter's publically released datasets. This data was used to generate a comprehensive list of words, which were used to randomly query legitimate users by topic via Twitter's API. These legitimate users were then filtered for bots using the Botometer API. A Bag of Words was then developed for every user from the aggregate of their tweets, and additional pattern-of-life metrics and statistics were calculated from their posting and engagement behavior. We then evaluated machine learning models on the BoW vectors and pattern-of-life metrics separately, and then performed ensemble voting methods using models trained on both BoW and pattern of life features. Models trained on the BoW vectors include Multinomial Naive Bayes, Stochastic Gradient Descent, and a Multilayer Perceptron Network. Models trained on the user pattern of life metrics included Random Forests and a Support Vector Classifier.

## Results

### Multinomial Naive Bayes and Stochastic Gradient Descent models trained on user Bag of Words vectors using Count Vectorization and TFIDF

#### Multinomial Naive Bayes with TFIDF

Accuracy:  0.7655613728912158  
Precision:  0.9976798143851509  
Recall:  0.5168269230769231  
F1 Score: 0.6809184481393509


#### Stochastic Gradient Descent Classifier with TFIDF

Accuracy:  0.9813845258871436  
Precision:  0.977326968973747  
Recall:  0.984375  
F1 Score: 0.9808383233532934


#### Multinomial Naive Bayes with Count Vectorizer

Accuracy:  0.8987783595113438  
Precision:  0.9838235294117647  
Recall:  0.8040865384615384  
F1 Score: 0.8849206349206349


#### Stochastic Gradient Descent with Count Vectorizer

Accuracy:  0.9825479930191972  
Precision:  0.972877358490566  
Recall:  0.9915865384615384  
F1 Score: 0.9821428571428571

### Multilayer Perceptron Neural Network trained on user Bag of Words using Count Vectorization

#### Neural Network Model Performance

Accuracy:  0.9825479930191972  
Precision:  0.9844357976653697  
Recall:  0.9768339768339769  
F1 Score: 0.9806201550387598

### Random Forests and Support Vector Classifier trained on user pattern of life features

#### Random Forest prediction on non-BoW features

Accuracy:  0.9994182664339732  
Precision:  0.9987995198079231  
Recall:  1.0  
F1 Score: 0.9993993993993994


#### SVC prediction on non-BoW features

Accuracy:  0.9982547993019197  
Precision:  0.9964071856287425  
Recall:  1.0  
F1 Score: 0.9982003599280144

### Ensemble Methods combining BoW and user pattern of life features

#### SGD CV, SGD TFIDF, Random Forests Ensemble

Accuracy:  0.9901105293775451  
Precision:  0.9856972586412396  
Recall:  0.9939903846153846  
F1 Score: 0.9898264512268103

#### SGD CV, SGD TFIDF, SVC Ensemble

Accuracy:  0.9901105293775451  
Precision:  0.9856972586412396  
Recall:  0.9939903846153846  
F1 Score: 0.9898264512268103

#### SGD CV, SVC, Random Forests Ensemble

Accuracy:  0.9988365328679465  
Precision:  0.9976019184652278  
Recall:  1.0  
F1 Score: 0.9987995198079231

#### SGD TFIDF, SVC, Random Forests Ensemble

Accuracy:  0.9988365328679465  
Precision:  0.9976019184652278  
Recall:  1.0  
F1 Score: 0.9987995198079231

## Environment 
Code was developed in Google Colab Pro using a High-RAM and TPU runtime environment with data stored in Google Drive, because the amount of RAM required exceeded the capabilities of a personal PC, so file storage and retrieval operations in the code reflect this.

## Data
Original datasets can be downloaded from Twitter's public Information Operations datasets: https://transparency.twitter.com/en/reports/information-operations.html. Data used for this project includes the Russian datasets released in September 2020, May 2020, June 2019, January 2019, and October 2018. The final formatted user and tweet datasets used to train these models can be accessed on Kaggle at www.kaggle.com/dataset/d7869b0be0a52a67a49fe49465835d676e85264ef44f68d407429bc9e87253ee. This project only attempted to classify users based on the aggregate of their tweets, but the Bag of Words for each tweet is also included in the final dataset if anyone wants to classify tweets rather than users. All identifying user information has been hashed.
