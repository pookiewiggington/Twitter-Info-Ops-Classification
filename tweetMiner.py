
# Author: Nicholas Villemez
# Environment: CS3315
# Description: Module intended to make access to the Twitter API via tweepy more accessible. Users can query
#              for tweets by topic or user, or for user profile information. Raw and formatted versions of the query
#              are returned. Formatting is optimized for merging and analysis with the public Twitter Disinformation
#              datasets (https://transparency.twitter.com/en/reports/information-operations.html).

# Sources: https://towardsdatascience.com/tweepy-for-beginners-24baf21f2c25

import tweepy
import pandas as pd
import datetime
import json
import time

class TweetMiner(object):

    result_limit    =   20    
    data            =   []
    api             =   False
    
    twitter_keys = {
        'consumer_key':        'my-key',
        'consumer_secret':     'my-secret',
        'access_token_key':    'my-token',
        'access_token_secret': 'my-token-secret'
    }
    
    
    def __init__(self, keys_dict=twitter_keys, api=api, result_limit = 20):
        
        self.twitter_keys = keys_dict
        
        auth = tweepy.OAuthHandler(keys_dict['consumer_key'], keys_dict['consumer_secret'])
        auth.set_access_token(keys_dict['access_token_key'], keys_dict['access_token_secret'])
        
        self.api = tweepy.API(auth)
        self.twitter_keys = keys_dict
        
        self.result_limit = result_limit


    # Queries profile information and returns a list of formatted information and raw information. 
    # If 15 minute query quota reach, script sleeps for 15 minutes and resumes queries
    def mine_user_info(self, users=[]):
        data           =  []
        raw_data       =  []
        usersnotfound  = 0

        for name in users:
            try:
                user_info = self.api.get_user(id=name)
                print('Mining ', name)
                mined = {
                    'userid':                    user_info.id,
                    'user_display_name':         user_info.name,
                    'user_screen_name':          user_info.screen_name,
                    'user_reported_location':    user_info.location,
                    'user_profile_description':  user_info.description,
                    'user_profile_url':          user_info.url,
                    'follower_count':            user_info.followers_count,
                    'following_count':           user_info.friends_count,
                    'account_creation_date':     user_info.created_at,
                    'account_language':          user_info.lang   
                }

                data.append(mined)
                raw_data.append(user_info)
            except tweepy.error.RateLimitError:
                print('15 minute query limit reached, wait 15 minutes until query resumes')
                print('Have executed' + str(users.index(name)) + ' of ' + str(len(users)) + ' total user queries.')
                time.sleep(60*16)
                print('Query resumed')
                user_info = self.api.get_user(id=name)
                print('Mining ', name)
                mined = {
                    'userid':                    user_info.id,
                    'user_display_name':         user_info.name,
                    'user_screen_name':          user_info.screen_name,
                    'user_reported_location':    user_info.location,
                    'user_profile_description':  user_info.description,
                    'user_profile_url':          user_info.url,
                    'follower_count':            user_info.followers_count,
                    'following_count':           user_info.friends_count,
                    'account_creation_date':     user_info.created_at,
                    'account_language':          user_info.lang 
                }
                
                data.append(mined)
                raw_data.append(user_info)

            except tweepy.error.TweepError:
                usersnotfound += 1
                continue

        return data, raw_data, usersnotfound

    # Query tweets by topic, returns specified number of tweets or pages by topic search. Returns list of 
    # formatted tweets and a list of all raw data. If 15 minute quota reached, the script sleeps for 15 minutes and
    # resumes queries.
    def mine_topical_tweets(self, topic="", mine_retweets=False, max_pages=5):
        data           =  []
        raw_data       =  []
        last_tweet_id  =  False
        page           =  1
        print('Mining ', topic)
        while page <= max_pages:
            try:
                if last_tweet_id:
                    statuses   =   self.api.search(q=topic,
                                                        count=self.result_limit,
                                                        max_id=last_tweet_id - 1,
                                                        tweet_mode = 'extended',
                                                        include_retweets=True
                                                        )        
                else:
                    statuses   =   self.api.search(q=topic,
                                                            count=self.result_limit,
                                                            tweet_mode = 'extended',
                                                            include_retweets=True)
                print('    Mining ' + str(page) + ' of '+ str(max_pages) +' total pages')
                for item in statuses:
                    
                    RT = False
                    if 'RT' in item.full_text: 
                        RT = True

                    mined = {
                        'tweetid':         item.id,
                        'userid':          item.user.id,
                        'user_display_name':         item.user.name,
                        'user_screen_name':          item.user.screen_name,
                        'user_reported_location':    item.user.location,
                        'user_profile_description':  item.user.description,
                        'user_profile_url':          item.user.url,
                        'follower_count':            item.user.followers_count,
                        'following_count':           item.user.friends_count,
                        'account_creation_date':     item.user.created_at,
                        'account_language':          item.user.lang,
                        'tweet_language':            item.lang,
                        'tweet_text':            item.full_text,
                        'tweet_time':      item.created_at,
                        'tweet_client_name':   item.source,
                        'in_reply_to_userid':        item.in_reply_to_user_id,
                        'in_reply_to_tweetid':       item.in_reply_to_status_id
                    }
                    try:
                        mined['quoted_tweet_tweetid'] = item.quoted_status_id
                        
                    except:
                        mined['quoted_tweet_tweetid'] = 'None'

                    mined.update({'is_retweet': RT})

                    try:
                        mined['retweet_userid']  = item.retweeted_status.user.id
                        mined['retweet_tweetid'] = item.retweeted_status.id
                        
                    except:
                        mined['retweet_userid']  = 'None'
                        mined['retweet_tweetid'] = 'None'

                    mined.update({

                        'latitude':       'absent',
                        'longitude':      'absent',
                        'quote_count':     item.retweet_count,
                        'reply_count':    None,
                        'like_count':      item.favorite_count,
                        'retweet_count':   item.retweet_count,
                        'hashtags':        item.entities['hashtags'],
                        'urls':            item.entities['urls'],
                        'user_mentions':   item.entities['user_mentions']
                    })
                    
                    last_tweet_id = item.id
                    data.append(mined)
                    raw_data.append(item)
                    
                page += 1
            
            except tweepy.error.RateLimitError:
                print('15 minute query limit reached, wait 15 minutes until query resumes')
                print(str(page) + ' pages of '+ str(max_pages) +' total pages have been queried')
                time.sleep(60*16) 
                print('Query resumed')
                if last_tweet_id:
                    statuses   =   self.api.search(q=topic,
                                                        count=self.result_limit,
                                                        max_id=last_tweet_id - 1,
                                                        tweet_mode = 'extended',
                                                        include_retweets=True
                                                        )        
                else:
                    statuses   =   self.api.search(q=topic,
                                                            count=self.result_limit,
                                                            tweet_mode = 'extended',
                                                            include_retweets=True)
                print('    Mining ' + str(page) + ' of '+ str(max_pages) +' total pages')
                for item in statuses:
                    
                    RT = False
                    if 'RT' in item.full_text: 
                        RT = True

                    mined = {
                        'tweetid':         item.id,
                        'userid':          item.user.id,
                        'user_display_name':         item.user.name,
                        'user_screen_name':          item.user.screen_name,
                        'user_reported_location':    item.user.location,
                        'user_profile_description':  item.user.description,
                        'user_profile_url':          item.user.url,
                        'follower_count':            item.user.followers_count,
                        'following_count':           item.user.friends_count,
                        'account_creation_date':     item.user.created_at,
                        'account_language':          item.user.lang,
                        'tweet_language':            item.lang,
                        'tweet_text':            item.full_text,
                        'tweet_time':      item.created_at,
                        'tweet_client_name':   item.source,
                        'in_reply_to_userid':        item.in_reply_to_user_id,
                        'in_reply_to_tweetid':       item.in_reply_to_status_id
                    }
                    try:
                        mined['quoted_tweet_tweetid'] = item.quoted_status_id
                        
                    except:
                        mined['quoted_tweet_tweetid'] = 'None'

                    mined.update({'is_retweet': RT})

                    try:
                        mined['retweet_userid']  = item.retweeted_status.user.id
                        mined['retweet_tweetid'] = item.retweeted_status.id
                        
                    except:
                        mined['retweet_userid']  = 'None'
                        mined['retweet_tweetid'] = 'None'

                    mined.update({

                        'latitude':       None,
                        'longitude':      None,
                        'quote_count':     item.retweet_count,
                        'reply_count':    None,
                        'like_count':      item.favorite_count,
                        'retweet_count':   item.retweet_count,
                        'hashtags':        item.entities['hashtags'],
                        'urls':            item.entities['urls'],
                        'user_mentions':   item.entities['user_mentions']
                    })
                    
                    last_tweet_id = item.id
                    data.append(mined)
                    
                page += 1
            
            except tweepy.error.TweepError:
                break

        return data, raw_data        

    # Query tweets by user, returns specified number of tweets or pages by topic search. Returns list of 
    # formatted tweets and a list of all raw data. If 15 minute quota reached, the script sleeps for 15 minutes and
    # resumes queries.
    def mine_user_tweets(self, user="", #BECAUSE WHO ELSE!
                         mine_rewteets=False,
                         max_pages=5):

        data           =  []
        raw_data       =  []
        last_tweet_id  =  False
        page           =  1
        print('Mining ', user)
        while page <= max_pages:

            try:
                if last_tweet_id:
                    statuses   =   self.api.user_timeline(screen_name=user,
                                                        count=self.result_limit,
                                                        max_id=last_tweet_id - 1,
                                                        tweet_mode = 'extended',
                                                        include_retweets=True
                                                        )        
                else:
                    statuses   =   self.api.user_timeline(screen_name=user,
                                                            count=self.result_limit,
                                                            tweet_mode = 'extended',
                                                            include_retweets=True)
                print('    Mining ' + str(page) + ' of '+ str(max_pages) +' total pages')   
                for item in statuses:

                    RT = False
                    if 'RT' in item.full_text: 
                        RT = True

                    mined = {
                        'tweetid':         item.id,
                        'userid':          item.user.id,
                        'user_display_name':         item.user.name,
                        'user_screen_name':          item.user.screen_name,
                        'user_reported_location':    item.user.location,
                        'user_profile_description':  item.user.description,
                        'user_profile_url':          item.user.url,
                        'follower_count':            item.user.followers_count,
                        'following_count':           item.user.friends_count,
                        'account_creation_date':     item.user.created_at,
                        'account_language':          item.user.lang,
                        'tweet_language':            item.lang,
                        'tweet_text':            item.full_text,
                        'tweet_time':      item.created_at,
                        'tweet_client_name':   item.source,
                        'in_reply_to_userid':        item.in_reply_to_user_id,
                        'in_reply_to_tweetid':       item.in_reply_to_status_id
                    }
                    try:
                        mined['quoted_tweet_tweetid'] = item.quoted_status_id
                        
                    except:
                        mined['quoted_tweet_tweetid'] = 'None'

                    mined.update({'is_retweet': RT})

                    try:
                        mined['retweet_userid']  = item.retweeted_status.user.id
                        mined['retweet_tweetid'] = item.retweeted_status.id
                        
                    except:
                        mined['retweet_userid']  = 'None'
                        mined['retweet_tweetid'] = 'None'

                    mined.update({

                        'latitude':       None,
                        'longitude':      None,
                        'quote_count':     item.retweet_count,
                        'reply_count':    None,
                        'like_count':      item.favorite_count,
                        'retweet_count':   item.retweet_count,
                        'hashtags':        item.entities['hashtags'],
                        'urls':            item.entities['urls'],
                        'user_mentions':   item.entities['user_mentions']
                    })
                    
                    last_tweet_id = item.id
                    data.append(mined)
                    raw_data.append(item)
                    
                page += 1
            
            except tweepy.error.RateLimitError:
                print('15 minute query limit reached, wait 15 minutes until query resumes')
                print(str(page) + ' pages of '+ str(max_pages) +' total pages have been queried')
                time.sleep(60*16) 
                print('Query resumed')
                if last_tweet_id:
                    statuses   =   self.api.user_timeline(screen_name=user,
                                                        count=self.result_limit,
                                                        max_id=last_tweet_id - 1,
                                                        tweet_mode = 'extended',
                                                        include_retweets=True
                                                        )        
                else:
                    statuses   =   self.api.user_timeline(screen_name=user,
                                                            count=self.result_limit,
                                                            tweet_mode = 'extended',
                                                            include_retweets=True)

                print('    Mining ' + str(page) + ' of '+ str(max_pages) +' total pages')    
                for item in statuses:

                    RT = False
                    if 'RT' in item.full_text: 
                        RT = True

                    mined = {
                        'tweetid':         item.id,
                        'userid':          item.user.id,
                        'user_display_name':         item.user.name,
                        'user_screen_name':          item.user.screen_name,
                        'user_reported_location':    item.user.location,
                        'user_profile_description':  item.user.description,
                        'user_profile_url':          item.user.url,
                        'follower_count':            item.user.followers_count,
                        'following_count':           item.user.friends_count,
                        'account_creation_date':     item.user.created_at,
                        'account_language':          item.user.lang,
                        'tweet_language':            item.lang,
                        'tweet_text':            item.full_text,
                        'tweet_time':      item.created_at,
                        'tweet_client_name':   item.source,
                        'in_reply_to_userid':        item.in_reply_to_user_id,
                        'in_reply_to_tweetid':       item.in_reply_to_status_id
                    }
                    try:
                        mined['quoted_tweet_tweetid'] = item.quoted_status_id
                        
                    except:
                        mined['quoted_tweet_tweetid'] = 'None'

                    mined.update({'is_retweet': RT})

                    try:
                        mined['retweet_userid']  = item.retweeted_status.user.id
                        mined['retweet_tweetid'] = item.retweeted_status.id
                        
                    except:
                        mined['retweet_userid']  = 'None'
                        mined['retweet_tweetid'] = 'None'

                    mined.update({

                        'latitude':       None,
                        'longitude':      None,
                        'quote_count':     item.retweet_count,
                        'reply_count':    None,
                        'like_count':      item.favorite_count,
                        'retweet_count':   item.retweet_count,
                        'hashtags':        item.entities['hashtags'],
                        'urls':            item.entities['urls'],
                        'user_mentions':   item.entities['user_mentions']
                    })
                    
                    last_tweet_id = item.id
                    data.append(mined)
                    raw_data.append(item)
                    
                page += 1

            except tweepy.error.TweepError:
                break
            
        return data, raw_data

    # Takes responses from above functions, returns the formatted json in prettyprint
    def formatRawTweet(self, raw_tweets):
        formatted_raw_tweets = []
        for obj in raw_tweets:
            json_str = json.dumps(obj._json)
            parsed = json.loads(json_str)
            formatted_raw_tweets.append(json.dumps(parsed, indent=4, sort_keys=True))

        return formatted_raw_tweets