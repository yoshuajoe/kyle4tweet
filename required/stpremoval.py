
#################################################
# Tweet Stopword Removal
#
# Author: Alfan Farizki Wicaksono
#
# Information Retrieval Lab.
# Faculty of Computer Science
# University of Indonesia
#################################################

import re

class StpRemoval(object):

   def __init__(self, stpFile="twitter_stp.dic"):
      self.stpFile = stpFile
      self.stpSet  = set()
      self.loadStp()

   def loadStp(self):
      ''' load stopwords '''
      dataFile = open(self.stpFile, "r")
      for line in dataFile:
          line = line.strip() #remove \n
          if (line not in self.stpSet):
             self.stpSet.add(line)
      dataFile.close()

   def removeStp(self, tweet):
      #tweetWords = tweet.split()
      tweetWords = re.findall(r'\w+', tweet)
      newTweet = filter(lambda x:x.lower() not in self.stpSet, tweetWords)
      return ' '.join(newTweet)




