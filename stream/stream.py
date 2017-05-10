#Import the necessary methods from tweepy library
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from pymongo import MongoClient
import json
import os


print "Loading the config file"
print "Changing the directory"
os.chdir('..')

print os.getcwd()
print "Loading the configuration file"
config_dir = os.getcwd()+"/config.json"
f = open(config_dir, "r")
config = json.loads(f.read())
f.close()
		
#Variables that contains the user credentials to access Twitter API 
consumer_key = config["consumer_key"]
consumer_secret = config["consumer_secret"]
access_token = config["access_token"]
access_token_secret = config["access_token_secret"]


#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(StreamListener):

	def on_data(self, data):
		print data
		#This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
		client = MongoClient()
		#client = MongoClient('localhost', 27017)
		db = client.TwitterStream
		#collection = db.tweets 
		print db.snowflakes.insert_one(json.loads(data))
		
		return True

	def on_error(self, status):
		print status


if __name__ == '__main__':

	#This handles Twitter authetification and the connection to Twitter Streaming API
	mcp_raw = raw_input("Give the terms, separated by comma(,) e.g ocean,sea,seagull,beach,sand : ");
	mcp = mcp_raw.split(",")
	
	while True:
		try:
			#This line filter Twitter Streams to capture data by the keywords: 'India'
			l = StdOutListener()
			auth = OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_token, access_token_secret)
			stream = Stream(auth, l)
			
			stream.filter(track=mcp)
		except:
			l = StdOutListener()
			auth = OAuthHandler(consumer_key, consumer_secret)
			auth.set_access_token(access_token, access_token_secret)
			stream = Stream(auth, l)
			
			stream.filter(track=mcp)