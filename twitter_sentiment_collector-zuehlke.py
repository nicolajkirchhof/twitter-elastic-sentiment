import json
import sys
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from textblob_de import TextBlobDE 
from textblob import TextBlob 
from elasticsearch import Elasticsearch
from functools import reduce

# import twitter keys and tokens
from config import *

# create instance of elasticsearch
es = Elasticsearch()

class TweetStreamListener(StreamListener):

    def __init__(self):
        self.tweet_count = 0

    # on success
    def on_data(self, data):
        
        try:
            # decode json
            dict_data = json.loads(data)
                      
            if dict_data["lang"] == 'de':
                tweet = TextBlobDE(dict_data["text"])
            elif dict_data["lang"] == 'en':
                tweet = TextBlob(dict_data["text"])
            else:
                return

            
            print(dict_data["text"].encode('ascii', 'ignore'))
            # output sentiment polarity
            #print tweet.sentiment.polarity
    
            # determine if sentiment is positive, negative, or neutral
            if tweet.sentiment.polarity < 0:
                sentiment = "negative"
            elif tweet.sentiment.polarity == 0:
                sentiment = "neutral"
            else:
                sentiment = "positive"
    
            # output sentiment
            createTimestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.strptime(dict_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y'))
            #print int(time.mktime(time.strptime(dict_data['created_at'],'%a %b %d %H:%M:%S +0000 %Y')))
    
            # add text and sentiment info to elasticsearch
            es.index(index="ztweets",
                     doc_type="ztweet_sentiment",
                     body={"date": createTimestamp,
                           "user": dict_data["user"]["id_str"],
                           "message": dict_data["text"],
                           "language": dict_data["lang"],  
                           "hashtags": reduce(lambda x,y:  { 'text' : str(x["text"]) + " " + str(y["text"]) }, dict_data["entities"]["hashtags"])["text"] if len(dict_data["entities"]["hashtags"])>0 else "",
                           "location": dict_data["coordinates"]["coordinates"] if dict_data["coordinates"] is not None else None,
                           "polarity": tweet.sentiment.polarity,
                           "subjectivity": tweet.sentiment.subjectivity,
                           "sentiment": sentiment})
            
            self.tweet_count += 1            
            if self.tweet_count % 100 == 0:
                print('Indexed {0} tweets'.format(self.tweet_count))
            
        except:
            print("error in listener:", sys.exc_info()[0])
            
        return True

    # on failure
    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    
    try:
        print('Starting to listen...')
        while True:
            # create instance of the tweepy tweet stream listener
            listener = TweetStreamListener()
        
            # set twitter keys/tokens
            auth = OAuthHandler(consumer_key, consumer_secret)
            auth.set_access_token(access_token, access_token_secret)
        
            # create instance of the tweepy stream
            stream = Stream(auth, listener)
        
            # search twitter for "congress" keyword
            stream.filter(track=['zühlke', 'zuehlke', 'zuehlke_group', ])
    
    except:
        print("error in main:", sys.exc_info()[0])
