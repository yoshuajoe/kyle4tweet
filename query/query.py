########################################################
# this is the sample query scripting from the mongodb
# where the tweets were stored
# you can edit this script to accomodate your needs
# for the documentation please visit this URL below
# http://github.com/yoshuajoe/kyle4tweets
# hope you enjoy the code :) 
# for futher and advance topic please contact me 
# by using email (yoshuajoe[at]gmail.com)
# timestamps : 23 feb 2017 
########################################################


from pymongo import MongoClient
import re
import json
from Kyle4Tweets.Kyle4Tweets import Kyle4Tweets
import time

# this is how you instantiate the driver
client = MongoClient()

# an instruction to prompt the user what term you want to search
database = raw_input("Database name [default : TwitterStream] >> ")
col = raw_input("Collection name [default : tweets] >> ")

# set default database
if len(database) < 1:
	database = "TwitterStream"

# set default collection
if len(col) < 1:
	col = "tweets"

# please change the database and collection with your following mongodb environment
db = getattr(client, database) 
collection = getattr(db, col) 

# an instruction to prompt the user what term you want to search
topic = raw_input("Search term e.g. indonesia >> ")
regex = re.compile(r'%s'%topic)
result = []

# let's instantiate the Kyle4Tweets library
k4t = Kyle4Tweets()

# forever looping
while True:
	try:
		# this is how you instantiate the Mongodb driver
		client = MongoClient()

		# please change the database and collection with your following mongodb environment
		db = getattr(client, database) 
		collection = getattr(db, col) 

		# if user didn't specify the keyword
		if len(topic) > 0:
			result = collection.find({"text":regex})
		# if user specify the keyword
		else:
			result = collection.find({})
		
		# transform mongodb cursor to list
		result = list(result)
		
		# get the total result rows
		total = len(result)
		
		# set up the dataset
		k4t.set_dataset(result)	

		# use the get function to explore the data
		#print k4t.get(what="text")


		# kill the bots
		bots = k4t.kill_bots()
		
		# run the cleanse phase
		k4t.cleanse(component=['punctuation','stopword','lowercased'])
		
		# print for hacker mode
		# print 

		k4t.get(what="text", dump=True)

		# text = k4t.get(what="text")
		
		# f = open("hasil_text.txt", "w")
		# f.write('\r\n'.join(text).encode('utf-8'))
		# f.close()
		# exit()

		# run the countTweets method
		k4t.countTweets(mode="peak", per="daily")
		k4t.countTweets(mode="peak", per="hourly")

		# for user
		k4t.countTweets(mode="user", option="10")

		# k4t.countTweets(mode="user", option="20")
		# k4t.countTweets(mode="language")
		
		# extract the things inside the text
		print k4t.extract(what="term_freq", option=20, ignoreCase=True, export = True)
		print k4t.extract(what="mention", option=20, export= True)
		print k4t.extract(what="hashtag", option=20, export=True)
		#print k4t.extract(what="url", option=10, export=True)
		print k4t.extract(what="custom", customExpression=['snow','bear','used','selfies'], ignoreCase=True, export=True)
		
		# write the parameter
		k4t.write_param(topic=topic, total=len(k4t.dataset), unparsed_tweets=k4t.unparsed_tweets, bots=bots)
		
		# dataset count
		dataset = k4t.split_dataset(to=["snow","bear"], n="all", dump=False, distinct=True, export=True, topic=topic)

		# geotagging
		k4t.dataset_count(dataset, what="geo")
	
		# delay the process to avoid the buffer overflow
		time.sleep(5)
	except Exception as e:
		print e
		time.sleep(5)
		pass





