import json

fo = open('C:/Users/user/Desktop/output.json', 'r')
fw = open('C:/Users/user/Desktop/corpus.txt', 'a')


for line in fo:
	try:
		tweet = json.loads(line)
		fw.write(tweet['text']+"\n")
	except:
		continue 