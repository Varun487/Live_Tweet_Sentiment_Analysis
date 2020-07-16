from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
from tweepy import Cursor
import pandas as pd
import numpy as np
from textblob import TextBlob
import re

from StreamTweets import twitter_credentials


# -------------------- TWITTER CLIENT --------------------
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_api()
        self.twitter_client = API(self.auth)
        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# -------------------- TWITTER AUTHENTICATOR --------------------
class TwitterAuthenticator():
    '''
        Class to authenticate twitter data
    '''

    def authenticate_twitter_api(self):
        # authorization for getting twitter data
        auth = OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
        auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
        return auth


# -------------------- TWITTER STREAMER --------------------
class TwitterStreamer():
    ''' Handles authentication and connection to twitter streaming API'''

    def __init__(self):
        self.twitter_authenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # how to deal with data, errors
        listener = TwitterListener(fetched_tweets_filename)

        # authorization for getting twitter data
        auth = self.twitter_authenticator.authenticate_twitter_api()

        # continuous stream of all tweets
        stream = Stream(auth, listener)

        # filters the stream based on list of hashtags given
        stream.filter(track=hash_tag_list)


# -------------------- TWITTER STREAM LISTENER --------------------
class TwitterListener(StreamListener):
    ''' Basic class that handles when data is streamed, or error occurs'''

    def __init__(self, fetched_tweets_filename):
        super().__init__()

        # get the file where we are storing our tweets (json)
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, raw_data):

        try:
            # printing the data we are writing in the json file
            print(raw_data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(raw_data)
            return True

        except BaseException as e:
            # if error occurs, print the error
            print("Error on data", str(e))
        return True

    def on_error(self, status_code):
        if status_code == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        # when error in connection occurs, print the status code of the error
        print(status_code)


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def analyze_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        return analysis.sentiment.polarity
        # if analysis.sentiment.polarity > 0:
        #     return 1
        # elif analysis.sentiment.polarity == 0:
        #     return 0
        # else:
        #     return -1

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])
        df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])

        return df


if __name__ == '__main__':
    # hash_tag_list = ['donald trump', 'modi']
    # fetched_tweets_filename = "tweets.txt"
    # twitter_streamer = TwitterStreamer()
    # twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)

    # twitter_client = TwitterClient('ShekharGupta')
    # print(twitter_client.get_user_timeline_tweets(1)[0]._json['text'])
    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    tweets = api.user_timeline(screen_name="realDonaldTrump", count=100)
    df_tweets = tweet_analyzer.tweets_to_data_frame(tweets)

    # print(df_tweets.head(20))
    # print(np.mean(df_tweets['len']))

    #print(df_tweets)
    for tweet, sentiment in zip(df_tweets['tweets'], df_tweets['sentiment']):
        print()
        print(tweet, sentiment)
        print()