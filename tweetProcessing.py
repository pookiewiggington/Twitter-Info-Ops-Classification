import pandas as pd
from numpy import NaN
import re
import gensim
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer
from collections import Counter
from nltk.tag import pos_tag
from nltk.tokenize import WhitespaceTokenizer
import statistics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from cmath import rect, phase
from math import radians, degrees
from sklearn.naive_bayes import MultinomialNB
#from scipy.stats import mode
from collections import Counter
import json
from json import JSONDecodeError

# Calculate ratio of retweets to original tweets
def retweetRatio(user_df, tweet_df):
    users = list(user_df.loc[:,'userid'].unique())
    rt_ratios = []
    for user in users:
        ratio = 0
        user_tweets = tweet_df[(tweet_df.loc[:,'userid'] == user)].copy()
        user_tweets = user_tweets.loc[:,'is_retweet'].astype('int')
        tweet_proportions = user_tweets.value_counts(normalize = True)
        try:
            rt_ratios.append(tweet_proportions[1])
        except KeyError:
            rt_ratios.append(0)
    user_df.loc[:,'retweet_ratio'] = rt_ratios

# Calculate proportion of English language tweets
def englishRatio(user_df, tweet_df):
    users = list(user_df.loc[:,'userid'].unique())
    en_ratios = []
    for user in users:
        ratio = 0
        user_tweets = tweet_df[(tweet_df.loc[:,'userid'] == user)].copy()
        user_tweets = user_tweets.loc[:,'tweet_language']
        en_tweet_proportions = user_tweets.value_counts(normalize = True)
        try:
            en_ratios.append(en_tweet_proportions['en'])
        except KeyError:
            en_ratios.append(0)
    user_df.loc[:,'english_tweet_proportion'] = en_ratios

# Calculate average number of tweets per hour/day
def averageTweetNum(user_df, tweet_df):
    users = list(user_df.loc[:,'userid'].unique())
    avg_hour_list = []
    avg_week_list = []
    avg_day_list = []
    avg_min_list = []
    for user in users:
        user_tweets = tweet_df[(tweet_df.loc[:,'userid'] == user)].copy()
        user_tweets = user_tweets[(user_tweets.loc[:,'tweet_time'] != '1900-01-01 00:00')]
        weektweet = user_tweets.groupby(pd.Grouper(key="tweet_time", freq="1W")).count()
        daytweet = user_tweets.groupby(pd.Grouper(key="tweet_time", freq="1D")).count()
        hourtweet = user_tweets.groupby(pd.Grouper(key="tweet_time", freq="1H")).count()
        mintweet = user_tweets.groupby(pd.Grouper(key="tweet_time", freq="1min")).count()

        weektweet = weektweet.reset_index()
        daytweet = daytweet.reset_index()
        hourtweet = hourtweet.reset_index()
        mintweet = mintweet.reset_index()

        avg_week = weektweet['tweetid'].mean()
        avg_day = daytweet['tweetid'].mean()
        avg_hour = hourtweet['tweetid'].mean()
        avg_min = mintweet['tweetid'].mean()

        avg_week_list.append(avg_week)
        avg_day_list.append(avg_day)
        avg_hour_list.append(avg_hour)
        avg_min_list.append(avg_min)

    user_df.loc[:,'avg_tweets_per_week'] = avg_week_list
    user_df.loc[:,'avg_tweets_per_day'] = avg_day_list
    user_df.loc[:,'avg_tweets_per_hour'] = avg_hour_list
    user_df.loc[:,'avg_tweets_per_min'] = avg_min_list

# Average quotes, likes, retweet, hashtags, urls, user mentions per tweet
def avgTweetMetrics(user_df, tweet_df):
    users = list(user_df.loc[:,'userid'].unique())
    metric_columns = ['avg_quote_count', 'avg_like_count', 'avg_retweet_count', 'avg_hashtags', 'avg_urls', 'avg_user_mentions']
    metric_df = pd.DataFrame(columns = metric_columns)
    for user in users:
        user_tweets = tweet_df[(tweet_df.loc[:,'userid'] == user)].copy()
        avg_quotes = user_tweets['quote_count'].mean()
        avg_likes = user_tweets['like_count'].mean()
        avg_retweets = user_tweets['retweet_count'].mean()
        avg_hashtags = user_tweets['hashtags'].mean()
        avg_urls = user_tweets['urls'].mean()
        avg_user_mentions = user_tweets['user_mentions'].mean()
        metrics_list = [avg_quotes, avg_likes, avg_retweets, avg_hashtags, avg_urls, avg_user_mentions]
        tweet_metrics = pd.Series(metrics_list, index=metric_columns)
        metric_df = metric_df.append(tweet_metrics, ignore_index=True)

    user_df.loc[:, metric_columns] = metric_df

# Proportion of tweet clients for most used twitter clients
# This is currently not being used, because it makes the dataframe too large for RAM
def tweetClientProportion(user_df, tweet_df):
    users = list(user_df.loc[:,'userid'].unique())
    client_names = tweet_df.columns[12:]
    client_df = pd.DataFrame(columns = client_names)

    for user in users:
        #user_clients = pd.Dataframe()
        user_client_proportions = []
        user_tweets = tweet_df[(tweet_df.loc[:,'userid'] == user)].copy()

        for name in client_names:
            user_tweets.loc[:,name] = user_tweets.loc[:,name].astype('int')
            proportion = user_tweets[name].value_counts(normalize=True)
            try:
                user_client_proportions.append(proportion[1])
            except KeyError:
                user_client_proportions.append(0)
        
        user_client_proportions = pd.Series(user_client_proportions, index=client_names)
        client_df = client_df.append(user_client_proportions, ignore_index=True)

    user_df.loc[:,client_names] = client_df

def lemmatize_all(sentence):
    wnl = WordNetLemmatizer()
    for word, tag in pos_tag(WhitespaceTokenizer().tokenize(sentence)):
        if tag.startswith("NN"):
            yield wnl.lemmatize(word, pos='n')
        elif tag.startswith('VB'):
            yield wnl.lemmatize(word, pos='v')
        elif tag.startswith('JJ'):
            yield wnl.lemmatize(word, pos='a')
        else:
            yield word
            
# Function to preprocess data with Gensim
def preprocess_gensim(text):
    # Remove non-alphanumeric characters from data, remove URLs, remove retweet annotation and usernames
    text = re.sub(r'https?://[^\s]+', '', text, re.IGNORECASE)
    text = re.sub(r'RT @[^\s]+', '', text, re.IGNORECASE)
    text = re.sub(r'@[^\s]+', '', text, re.IGNORECASE)
    text = ''.join([re.sub(r'[^a-zA-Z0-9]', ' ', text) for text in text])
    text = re.sub("\s+", " ", text)
    
    # Lemmatize, stem and tokenize words in the dataset, removing stopwords
    
    #print('lemmatizing')
    text = ' '.join(lemmatize_all(text))
    tokens = [token for token in gensim.utils.simple_preprocess(text) 
          if not token in gensim.parsing.preprocessing.STOPWORDS]
    #print(tokens)
    return tokens

def process_users(user_df, tweet_df, toList):
    user_df.loc[:,'BoW'] = 'NaN'
    user_df.loc[:,'BoW'] = user_df.loc[:,'BoW']
    
    users = list(user_df['userid'].unique())
    bigBoW = []
    for user in users:
        user_tweets = tweet_df[(tweet_df['userid'] == user) & (tweet_df['tweet_language'] == 'en')].copy()
        flatBoW = [x for y in user_tweets['BoW'] for x in y]
        if toList == False:
            flatBoW = ' '.join(flatBoW)
        bigBoW.append(flatBoW)
    user_df.loc[:,'BoW'] = bigBoW

def process_tweets(tweet_df):
    tweet_df.loc[:,'BoW'] = 'NaN'
    tweet_df.loc[:,'BoW'] = tweet_df.loc[:,'BoW'].astype('object')
    BoW = [preprocess_gensim(tokens) for tokens in tweet_df['tweet_text']]
    #tweet_df['BoW'] = BoW
    tweet_df.loc[:,'BoW'] = BoW

def preprocess_frame(tweet_df, user_df, toList=True):
    process_tweets(tweet_df)
    process_users(user_df, tweet_df, toList)

def download_wordlists():
    from nltk import download
    download('punkt')
    download('wordnet')
    download('averaged_perceptron_tagger')

#time functions adapted from:
#from https://rosettacode.org/wiki/Averages/Mean_time_of_day#Python
def angle_to_time(angle):
    day = 24 * 60 * 60
    seconds = angle * day / 360.
    if seconds < 0:
        seconds += day
    h, m = divmod(seconds, 3600)
    m, s = divmod(m, 60)
    return int(str(int(h)) + str(int(m)))

def mean_time_from_angles(deg):
    return angle_to_time(degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg))))

def median_time_from_angles(deg):
    return(angle_to_time(statistics.median(deg)))
    
def stddev_time_from_angles(deg):
    return(angle_to_time(statistics.pstdev(deg)))

def time_to_angle(time):
    seconds = ((time % 100) * 60) + ((time // 100) * 3600)            
    day = 24 * 60 * 60
    angle = seconds * 360. / day
    return angle

def multimode(hours):
    hourmode = []
    counted = Counter(hours)
    max_occur = counted.most_common()[0][1]
    for hour in set(hours):
        if hours.count(hour) == max_occur:
            hourmode.append(hour)
    return hourmode
            
def mode_dict(hours):
    hourdict = dict.fromkeys(range(24),0)
    for hour in set(hours):
        hourdict[hour] = 1
    return hourdict
        

def tweet_time_statistics(tweet_df, user_df, en=True, non=False):
    users = list(user_df['userid'].unique())
    earliest_tweet = []
    latest_tweet = []
    average_tweet = []
    tweet_mode = {k:[] for k in range(24)}
    median_tweet = []
    tweet_count = []
    tweet_stddev = []
    
    for user in users:
        earliest = 2359
        latest = 0
        count = 0
        tweet_times = []
        tweet_hours = []
        if en == True and non==False:
            user_tweets = tweet_df[(tweet_df['userid'] == user) & (tweet_df['tweet_language'] == 'en')].copy()
        elif en == False and non == True:
            user_tweets = tweet_df[(tweet_df['userid'] == user) & (tweet_df['tweet_language'] != 'en')].copy()
        elif en == True and non == True:
            user_tweets = tweet_df[(tweet_df['userid'] == user)].copy()
        else:
            print("tweet_time_statistics_error: one or both en/non must be true")
            return
        user_tweets = user_tweets[(user_tweets.loc[:,'tweet_time'] != '1900-01-01 00:00')]
        
        for tweet in user_tweets['tweet_time']:
            t = pd.Timestamp(tweet)
            count += 1
            time = int(str(t.hour) + str(t.minute).zfill(2))
            tweet_times.append(time_to_angle(time))
            tweet_hours.append((t.hour))
            if time < earliest:
                earliest = time
            if time > latest:
                latest = time
                
        if count == 0:
            average_tweet.append(NaN)
            earliest_tweet.append(NaN)
            latest_tweet.append(NaN)
            median_tweet.append(NaN)
            #tweet_mode.append(NaN)
            tweet_count.append(NaN)
            tweet_stddev.append(NaN)
            for k in tweet_mode.keys():
                tweet_mode[k].append(NaN)
        else:
            average_tweet.append(mean_time_from_angles(tweet_times))
            earliest_tweet.append(earliest)
            latest_tweet.append(latest)
            median_tweet.append(median_time_from_angles(tweet_times))
            #tweet_mode.append(statistics.multimode(tweet_hours))
            #tweet_mode.append(mode(tweet_hours)[0][0])
            tweet_stddev.append(stddev_time_from_angles(tweet_times))
            tweet_count.append(count)
            mode_hours = multimode(tweet_hours)
            mode_dictionary = mode_dict(mode_hours)
            for k in mode_dictionary.keys():
                tweet_mode[k].append(mode_dictionary[k])
            
    user_df.loc[:,'earliest_tweet_time'] = earliest_tweet
    user_df.loc[:,'latest_tweet_time'] = latest_tweet
    user_df.loc[:,'average_tweet_time'] = average_tweet
    user_df.loc[:,'median_tweet_time'] = median_tweet
    user_df.loc[:,'tweet_count'] = tweet_count
    user_df.loc[:,'stddev_tweet_time'] = tweet_stddev
    #user_df.loc[:,'mode_tweet_hour'] = tweet_mode
    for k in tweet_mode.keys():
        user_df.loc[:,"mode_" + str(k)] = tweet_mode[k]
    
def predictionVoting(a, b, c):
    votes = zip(a,b,c)
    winner = [statistics.mode(x) for x in votes]
    return winner

#should run on import
download_wordlists()

if __name__ == "__main__":
    pass