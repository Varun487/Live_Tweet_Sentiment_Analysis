from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import pandas as pd
import numpy as np
from textblob import TextBlob
import re
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from StreamTweets import twitter_credentials


# ---------- TWITTER LISTENER ----------

class TwitterListener(StreamListener):
    ''' Basic class that handles when data is streamed, or error occurs'''

    def __init__(self):
        super().__init__()

        # get the file where we are storing our tweets (json)
        self.tweet_analyzer = TweetAnalyzer()

    def on_status(self, status):
        if hasattr(status, 'retweeted_status'):
            print("RETWEET")
            tweet = ''
            try:
                tweet = status.retweeted_status.extended_tweet["full_text"]
            except BaseException as e:
                tweet = status.retweeted_status.text
        else:
            try:
                tweet = status.extended_tweet["full_text"]
            except AttributeError:
                tweet = status.text
        print("tweet: ", tweet)
        tweet = self.tweet_analyzer.clean_tweet(tweet)
        print("cleaned tweet: ", tweet)
        polarity_textblob = self.tweet_analyzer.analyze_sentiment_textblob(tweet)
        polarity_vader = self.tweet_analyzer.analyze_sentiment_vadersentiment(tweet)
        print("polarity TextBlob: ", polarity_textblob)
        print("polarity vader sentiment: ", polarity_vader)
        print("--------------------")

    def on_error(self, status_code):
        if status_code == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        # when error in connection occurs, print the status code of the error
        print(status_code)


# ---------- TWITTER STREAMER ----------

class TwitterStreamer():
    ''' Handles authentication and connection to twitter streaming API'''

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, hash_tag_list):
        # how to deal with data, errors
        listener = TwitterListener()

        # authorization for getting twitter data
        auth = self.twitter_authenticator.authenticate_twitter_api()

        # continuous stream of all tweets
        stream = Stream(auth, listener)

        # filters the stream based on list of hashtags given
        stream.filter(track=hash_tag_list)


# ---------- TWITTER AUTHENTICATOR ----------

class TwitterAuthenticator():
    '''
        Class to authenticate twitter data
    '''

    def authenticate_twitter_api(self):
        # authorization for getting twitter data
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|(^#)", " ", tweet).split())

    def analyze_sentiment_textblob(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.sentiment.polarity

    def analyze_sentiment_vadersentiment(self, tweet):
        analysis_obj = SentimentIntensityAnalyzer()
        return analysis_obj.polarity_scores(tweet)['compound']


hash_tag_list = ['narendramodi', 'RahulGandhi']
twitter_streamer = TwitterStreamer()
twitter_streamer.stream_tweets(hash_tag_list)
