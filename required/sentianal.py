##########################################################
# Simple Tweet Sentiment Analyzer using Sentiment Lexicon
# Assumption : tweets have been normalized
#
# Author: Alfan Farizki Wicaksono
#
# Information Retrieval Lab.
# Faculty of Computer Science
# University of Indonesia
##########################################################

class Sentianal(object):

   def __init__(self, filepos="positif.txt", fileneg="negatif.txt"):
      self.filepos = filepos
      self.fileneg = fileneg
      self.posSet  = set()
      self.negSet  = set()
      self.loadLexicon()

   def loadFile(self, fileName, cset):
      fin = open(fileName, "r")
      for line in fin:
         line = line.strip()
         if (line not in cset):
            cset.add(line)
      fin.close()

   def loadLexicon(self):
      self.loadFile(self.filepos, self.posSet)
      self.loadFile(self.fileneg, self.negSet)
   
   def score(self, word):
      if   ((word in self.posSet) and (word not in self.negSet)):
         return 1
      elif ((word not in self.posSet) and (word in self.negSet)):
         return -1
      else:
         return 0
   
   #tw : [("aku",0), ("suka",1), ("kamu",0)]
   def revertNeg(self, tw):
      ''' revert the word polarity after the negations '''
      for j in range(len(tw)):
         w, sc = tw[j] #word, score
         if (w == 'tidak'):
            if (j < len(tw)-1):
               #revert next !
               wn, scn = tw[j+1]
               tw[j+1] = (wn, scn*-1)
      return tw

   def compute(self, tweet):
      #convert to list
      tweet = tweet.split()

      #we add the sentiment polarity information for each word
      temp = map(lambda x:(x,self.score(x)), tweet)

      #revert the word polarity after the negations
      temp = self.revertNeg(temp)

      #we only consider the opinionated words
      temp = filter(lambda (w,sc):sc != 0, temp)

      #compute the average polarity score inside tweets
      total = reduce(lambda s1,s2:s1+s2, map(lambda (w,s):s, temp), 0)
      if (total != 0):
         return float(total)/len(temp)
      else:
         return 0.0


