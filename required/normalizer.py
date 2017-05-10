
#################################################
# Tweet Normalizer
# 1. lowercasting
# 2. URL Removal
# 3. change the slang-words into formal-words
#
# Author: Alfan Farizki Wicaksono
#
# Information Retrieval Lab.
# Faculty of Computer Science
# University of Indonesia
#################################################


class Normalizer(object):

   def __init__(self, dictFile="singkatan.dic"):
      ''' default dictionary file name is singkatan.dic '''
      self.dictFile = dictFile
      self.normDict = {}
      self.loadDict()
	  
   def loadDict(self):
      ''' we use this method to load content of dictionary file
          which is conveniently stored as a python dictionary object '''
      dataFile = open(self.dictFile, "r")
      for line in dataFile:
         line = line.strip() #remove \n
	     #key: slang word, #value: norm word
         slangNorm = line.split('\t')
         if (len(slangNorm) > 1):
            self.normDict[slangNorm[0]] = slangNorm[1]
      dataFile.close()
	     
   def lowerCast(self, word):
      ''' return word in lowercase version '''
      return word.strip().lower()
	  
   def arrStrToSnt(self, arrStr):
      ''' change array of string to sentence '''
      return ' '.join(arrStr)
   
   def normalize(self, tweet):
      ''' normalize the tweet, tweet must be words separated by white-space'''
      tweetWords = tweet.split()
      newTweet = map(lambda x:self.lowerCast(x), tweetWords)
      newTweet = map(lambda x:self.normDict[x] if x in self.normDict else x, newTweet)
	  #url removal
      newTweet = filter(lambda x:'http://' not in x and 'https://' not in x, newTweet)
      return self.arrStrToSnt(newTweet)
	  
	  
   