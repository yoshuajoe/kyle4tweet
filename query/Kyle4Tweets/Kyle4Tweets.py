import json
from subprocess import check_output
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import re
import os 

class Kyle4Tweets(object):
	
	def __init__(self):
		
		print "Changing the directory"
		os.chdir('..')
		
		print "Loading the configuration file"
		config_dir = os.getcwd()+"/config.json"
		f = open(config_dir, "r")
		self.config = json.loads(f.read())
		f.close()

	def intersect(a, b):
		""" return the intersection of two lists """
		return list(set(a) & set(b))

	def __init__(self, dt = [], ty = True):
		
		self.FLAG_FALSE_DIR = True
		print "Changing the directory"
		
		if ty == True:
			os.chdir('..')
		else:
			if self.FLAG_FALSE_DIR:
				os.chdir('..')
				self.FLAG_FALSE_DIR = False

		print "Loading the configuration file"
		config_dir = os.getcwd()+"/config.json"
		f = open(config_dir, "r")
		self.config = json.loads(f.read())
		f.close()

		# Set the dataset
		print "Dataset has been applied"
		self.dataset = dt

	def contains(self, small, big):
		res = [item for item in small if item in big]
		if len(res) > 0:
			return True
		else:
			return False

	def kill_bots(self):
		ar = []
		buzz_c = 0
		for d in self.dataset:
			if self.is_buzzer(d):
				buzz_c += 1
				continue
			else:
				ar.append(d)
		self.dataset = ar
		print "Detected bots : %s" % buzz_c
		return buzz_c

	def set_dataset(self, dt=[]):
		# Set the dataset
		print "Dataset has been applied"
		self.dataset = dt
	
	def remove_tags(self, text):
		TAG_RE = re.compile(r'<[^>]+>')
		return TAG_RE.sub('', text)

	def dump_dataset(self, topic="", dump=False):
		if dump == True:			
			f = open("%s%s_dump_%s.txt"%(self.config["dump_file"], topic,what), "w")
			f.write('\n'.join(self.dataset))
			f.close()

			# Determine the operating system
			opsys = os.name
			
			if opsys == "nt":
				check_output("notepad %s%s_dump_%s.txt"%(self.config["dump_file"],topic,what), shell=True)
			else:
				check_output("open -e %s%s_dump_%s.txt"%(self.config["dump_file"],topic,what), shell=True)

		return json.loads(self.dataset)

	def cleanse(self, component=[]):
		cleanse_term = ['$',':','.',',','"','\'','&','*','!','-','^','=','?','}','{','|','\\']
		
		stopword = []
		
		opsys = os.name
			
		if opsys == "nt":
			f = open(self.config["stopword_file_win"],"r")
		else:
			f = open(self.config["stopword_file"],"r")
		
		stopword = f.read().split()
		f.close()

		new_dataset = []

		print "Cleansing the tweets from unused punctuations"
		print "Cleansing the tweets from unused stopwords"
		c_err = 0
		for u in self.dataset:
			try:
				if "punctuation" in component:
					for c in cleanse_term:
						u["text"] = u["text"].replace(c,"")

				if "stopword" in component:
					u["text"] = ' '.join([t for t in u["text"].split() if t not in stopword])

				new_dataset.append(u)
			except KeyError:
				c_err += 1
				pass
				continue

			
		print "Unparsed tweets (due to an emptiness of entities) : %s" % c_err

		self.dataset = new_dataset
		self.unparsed_tweets = c_err

	def extract(self, what="mention", option="10", customExpression=[], ignoreCase=False, export=False):
		arr = {}
		if what == "mention":
			for d in self.dataset:
				text = d["text"]
				for t in text.split():

					# Ignoring case
					if ignoreCase == True:
						t = t.lower()

					if t.startswith("@"):
						if t not in arr:
							arr.setdefault(t,1)
						else:
							arr[t] += 1
		elif what == "hashtag":
			for d in self.dataset:
				text = d["text"]
				for t in text.split():

					# Ignoring case
					if ignoreCase == True:
						t = t.lower()

					if t.startswith("#"):
						if t not in arr:
							arr.setdefault(t,1)
						else:
							arr[t] += 1
		elif what == "url":
			for d in self.dataset:
				text = d["text"]
				
				# regex 
				res = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',text)
				for r in res:
					if r not in arr:
						arr.setdefault(r,1)
					else:
						arr[r] += 1

		elif what == "emoticon":
			for d in self.dataset:
				text = d["text"]
			
				# regex 
				# approach 2: disjunction of a list of smileys
				
				smileys = """:-) :) :o) :] :3 :c) :> =] 8) =) :} :^) 
				             :D 8-D 8D x-D xD X-D XD =-D =D =-3 =3 B^D""".split()
				
				pattern = "|".join(map(re.escape, smileys))

				res = re.findall(pattern, text)
				for r in res:
					if r not in arr:
						arr.setdefault(r,1)
					else:
						arr[r] += 1

		elif what == "term_freq":
		
			for d in self.dataset:
				text = d["text"]
				for t in text.split():
					
					# Ignoring case
					if ignoreCase == True:
						t = t.lower()
					
					if t not in arr:
						arr.setdefault(t,1)
					else:
						arr[t] += 1

		elif what == "custom":
			
			res = {}

			for d in self.dataset:
				text = d["text"]
				for t in text.split():

					# Ignoring case
					if ignoreCase == True:
						t = t.lower()
					
					if t not in arr:
						arr.setdefault(t,1)
					else:
						arr[t] += 1

			for cus in customExpression:
				res.setdefault(cus, arr[cus])

			arr = res


		elif what == "number":
			for d in self.dataset:
				text = d["text"]
			
				# regex 
				
				pattern = r'(?:(?:\d+,?)+(?:\.?\d+)?)'

				res = re.findall(pattern, text)
				for r in res:
					if r not in arr:
						arr.setdefault(r,1)
					else:
						arr[r] += 1
		
		import operator
		upperbound = int(option)

		sorted_x = sorted(arr.items(), key=lambda x:x[1], reverse=True)[0:upperbound]
		arrs = []
		for item in sorted_x:
			arrs.append({item[0]:item[1]})

		if export == True:
			# Determine the operating system
			opsys = os.name
						
			if opsys == "nt":
				f = open(("%s%s.json"%(self.config["base_dir_data_win"], what)),"w")
			else:
				f = open(("%s%s.json"%(self.config["base_dir_data"], what)),"w")

			arr_json = []
			for item in sorted_x:
				arr_json.append({"text":item[0], "size":item[1]})
			f.write(json.dumps(arr_json))
			f.close()

		return arrs

	def get_profile_from_tweets(self, by="id", value=""):
		for d in self.dataset:
			if d["user"][by] == value:
				return d["user"]

	def get(self, topic="", what="text", option="all", dump = False):
		text = []
		try:
			if what == "text":
				for g in self.dataset:
					t = g["text"]
					text.append(t)
			elif what == "created_at":
				for g in self.dataset:
					t = g["created_at"].encode('utf-8')
					text.append(t)
			elif what == "created_at_parsed":
				for d in self.dataset:
					dwtz = d["created_at"].split()
					del dwtz[4]
					tweetDate = ' '.join(dwtz)
					d = datetime.strptime(tweetDate,'%a %b %d %H:%M:%S %Y');
					tweetDate = d + timedelta(hours=self.config["timezone"])
					text.append(tweetDate.strftime('%Y-%m-%d %H:%M:%S'))
			elif what == "profile_image":
				for g in self.dataset:
					t = g["user"]["profile_image_url"].encode('utf-8')
					text.append(t)
			elif what == "user_id":
				for g in self.dataset:
					t = g["user"]["id"]
					text.append(t)
			elif what == "user_location":
				for g in self.dataset:
					t = g["user"]["loaction"].encode('utf-8')
					text.append(t)
			elif what == "user_sname":
				for g in self.dataset:
					t = g["user"]["screen_name"].encode('utf-8')
					text.append(t)
			elif what == "user_name":
				for g in self.dataset:
					t = g["user"]["name"].encode('utf-8')
					text.append(t)
			elif what == "source":
				for g in self.dataset:
					t = g["source"].encode('utf-8')
					text.append(t)
			elif what == "lang":
				for g in self.dataset:
					t = g["lang"].encode('utf-8')
					text.append(t)
			elif what == "id":
				for g in self.dataset:
					t = g["id"]
					text.append(t)
			elif what == "in_reply_to_user_id":
				for g in self.dataset:
					t = g["in_reply_to_user_id"].encode('utf-8')
					text.append(t)
			elif what == "in_reply_to_status_id":
				for g in self.dataset:
					t = g["in_reply_to_status_id"].encode('utf-8')
					text.append(t)
			elif what == "friends":
				for g in self.dataset:
					t = g["friends"]
					text.append(t)
			elif what == "followers":
				for g in self.dataset:
					t = g["followers"].encode('utf-8')
					text.append(t)
		except KeyError:
			pass
			
		if option != "all":
			import operator
			upperbound = int(option)
			text = sorted(text, reverse=True)[0:upperbound]

		if dump == True:			
			f = open("%s_get_%s.txt"%(topic,what), "w")
			f.write('\n'.join(text).encode("utf-8"))
			f.close()

			# Determine the operating system
			opsys = os.name
			
			if opsys == "nt":
				check_output("notepad %s_get_%s.txt"%(topic,what), shell=True)
			else:
				check_output("open -e %s_get_%s.txt"%(topic,what), shell=True)
		
		return text
		
	def split_dataset(self, to=[],n="all", topic="", distinct=False, export=False ,dump = False):
		arr = {}
		
		if distinct == False:
			if n == "all":
				for rec in to:
					arr.setdefault(rec,[])
					for d in self.dataset:
						text = d["text"].lower()
						if rec.lower() in text:
							arr[rec].append(d)

					if dump == True:	
						# Determine the operating system
						opsys = os.name		
						
						if opsys == "nt":
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,rec), "w")
						else:
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file"],topic,rec), "w")
					
						f.write('\n'.join([ar["text"].encode("utf-8") for ar in arr[rec]]))
						f.close()
						
						if opsys == "nt":
							check_output("notepad %s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,rec), shell=True)
						else:
							check_output("open -e %s%s_dataset_%s.txt"%(self.config["dump_file"],topic,rec), shell=True)

				arr.setdefault("other",[])

				for d in self.dataset:
					text = d["text"].lower()
					if self.contains(to,text.split()) == False:
						arr["other"].append(d)

				if dump == True:	
					# Determine the operating system
					opsys = os.name		
					
					if opsys == "nt":
						f = open("%s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,"other"), "w")
					else:
						f = open("%s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), "w")
				
					f.write('\n'.join([ar["text"].encode('utf-8') for ar in arr[rec]]))
					f.close()
					
					if opsys == "nt":
						check_output("notepad %s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), shell=True)
					else:
						check_output("open -e %s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), shell=True)

			else:
				for rec in to:
					arr.setdefault(rec,[])
					c = 0

					for d in self.dataset:
						text = d["text"]
						if rec.lower() in text.lower() and c < int(n):
							arr[rec].append(text.encode('utf-8'))
							c += 1

					if dump == True:	
						# Determine the operating system
						opsys = os.name		
					
						if opsys == "nt":
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,rec), "w")
						else:
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file"],topic,rec), "w")
					
						f.write('\n'.join(ar["text"].encode('utf-8') for ar in arr[rec]))
						f.close()
						
						if opsys == "nt":
							check_output("notepad %s_dataset_%s.txt"%(topic,rec), shell=True)
						else:
							check_output("open -e %s_dataset_%s.txt"%(topic,rec), shell=True)

				arr.setdefault("other",[])
				for d in self.dataset:
					text = d["text"].lower()
					if self.contains(to,text.split()):
						arr["other"].append(d)

				if dump == True:	
					# Determine the operating system
					opsys = os.name		
					
					if opsys == "nt":
						f = open("%s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,"other"), "w")
					else:
						f = open("%s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), "w")
				
					f.write('\n'.join([ar["text"].encode('utf-8') for ar in arr[rec]]))
					f.close()
					
					if opsys == "nt":
						check_output("notepad %s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), shell=True)
					else:
						check_output("open -e %s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), shell=True)


			if export == True:
				# Determine the operating system
				opsys = os.name
							
				if opsys == "nt":
					f = open(("%s%s.json"%(self.config["base_dir_data_win"], "split_dataset_pie")),"w")
				else:
					f = open(("%s%s.json"%(self.config["base_dir_data"], "split_dataset_pie")),"w")

				arr_json = []
				for item in arr.items():
					arr_json.append({"text":item[0], "size":len(arr[item[0]])})
				f.write(json.dumps(arr_json))
				f.close()	

		else:
			#distinct == True
			if n == "all":
				arr.setdefault("other",[])
				to.append("other")
				for rec in to:
					arr.setdefault(rec,[])
					for d in self.dataset:
						text = d["text"].lower()

						if rec != "other":
							if rec.lower() in text:
								arr[rec].append(d)
						else:
							if self.contains(to,text.lower().split()) == False:
								arr["other"].append(d)

					print len(arr[rec])

					if dump == True:	
						# Determine the operating system
						opsys = os.name		
						
						if opsys == "nt":
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,rec), "w")
						else:
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file"],topic,rec), "w")
					
						f.write('\n'.join([ar["text"].encode('utf-8') for ar in arr[rec]]))
						f.close()
						
						if opsys == "nt":
							check_output("notepad %s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,rec), shell=True)
						else:
							check_output("open -e %s%s_dataset_%s.txt"%(self.config["dump_file"],topic,rec), shell=True)


			else:
				
				c = 0
				arr.setdefault("other",[])
				for d in self.dataset:
					text = d["text"].lower()
					if self.contains(to,text.lower().split()) == False and c < int(n):
						arr["other"].append(d)
						c += 1

				for rec in to:
					arr.setdefault(rec,[])
					c = 0

					for d in self.dataset:
						text = d["text"]
						if rec.lower() in text.lower() and c < int(n):
							arr[rec].append(text.encode('utf-8'))
							c += 1

					if dump == True:	
						# Determine the operating system
						opsys = os.name		
					
						if opsys == "nt":
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,rec), "w")
						else:
							f = open("%s%s_dataset_%s.txt"%(self.config["dump_file"],topic,rec), "w")
					
						f.write('\n'.join(ar["text"].encode('utf-8') for ar in arr[rec]))
						f.close()
						
						if opsys == "nt":
							check_output("notepad %s_dataset_%s.txt"%(topic,rec), shell=True)
						else:
							check_output("open -e %s_dataset_%s.txt"%(topic,rec), shell=True)

				if dump == True:	
					# Determine the operating system
					opsys = os.name		
					
					if opsys == "nt":
						f = open("%s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,"other"), "w")
					else:
						f = open("%s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), "w")
				
					f.write('\n'.join([ar["text"].encode('utf-8') for ar in arr["other"]]))
					f.close()
					
					if opsys == "nt":
						check_output("notepad %s%s_dataset_%s.txt"%(self.config["dump_file_win"],topic,"other"), shell=True)
					else:
						check_output("open -e %s%s_dataset_%s.txt"%(self.config["dump_file"],topic,"other"), shell=True)

			# yoo I knew this is the most complicated codes ever
			# to find the pure element
			# the distiction
			arr_temp = {}
			to.remove("other")
			distinct_list = []
			for rec in to:
				for rec2 in to:
					if rec != rec2:
						if ("%s-%s"%(rec,rec2)) not in arr and ("%s-%s"%(rec2,rec)) not in arr and self.contains(rec.split('-'), rec2.split('-')) == False:
							# Intersection of unhashable object
							inter = [item_ for item_ in arr[rec] if item_ in arr[rec2]]
							arr[rec] = [item for item in arr[rec] if item not in inter]
							arr[rec2] = [item for item in arr[rec2] if item not in inter]
							to.append("%s-%s"%(rec,rec2))
							arr.setdefault(("%s-%s"%(rec,rec2)), inter)

			arr["other"] = []
			for rec in to:
				for d in arr[rec]:
					distinct_list.append(d)

			for d in self.dataset:
				if d not in distinct_list:
					arr["other"].append(d)


			if export == True:
				# Determine the operating system
				opsys = os.name
							
				if opsys == "nt":
					f = open(("%s%s.json"%(self.config["base_dir_data_win"], "split_dataset_pie")),"w")
				else:
					f = open(("%s%s.json"%(self.config["base_dir_data"], "split_dataset_pie")),"w")

				arr_json = []
				for item in arr.items():
					arr_json.append({"text":item[0], "size":len(arr[item[0]])})
				f.write(json.dumps(arr_json))
				f.close()	


		return arr

	def dataset_count(self, dataset, what="geo", option=['blue','yellow','red'], geo_center=[{"lat": -.789275,"lng": 117.25781}], export=True):
		import googlemaps

		gmaps = googlemaps.Client(key=self.config["google_map_key"])

		
		if what == "geo":
			labels = []
			locations = {}
			for d in dataset:
				labels.append(d)
				if d not in locations:
					locations.setdefault(d, [])
				for dt in dataset[d]:
					try:
						if dt["place"] != None:
							full_place = dt["place"]["full_name"]
							geocode_result = gmaps.geocode(full_place)
							locations[d].append({'loc':{'lat':geocode_result[0]["geometry"]["bounds"]["northeast"]["lat"], 'lng':geocode_result[0]["geometry"]["bounds"]["northeast"]["lng"]}, 'label':dt["text"].encode('utf-8')})
						elif ["location"] != None:
							full_place = dt["location"]
							#print full_place
						elif ["geo"] != None:
							full_place = dt["geo"]
							#print full_place

							#exit()
							#locations[d].append()
					except KeyError:
						pass
						continue

			if export == True:
				# Determine the operating system
				opsys = os.name
							
				if opsys == "nt":
					f = open(("%s%s.json"%(self.config["base_dir_data_win"], "geo")),"w")
				else:
					f = open(("%s%s.json"%(self.config["base_dir_data"], "geo")),"w")

				f.write(json.dumps(locations))
				f.close()	

			return locations

	def man(self, wtk="anatomy"):
		if wtk == "anatomy":
			print """ 
				text: the text of the tweet itself \n
				created_at: the date of creation \n
				favorite_count, retweet_count: the number of favourites and retweets \n
				favorited, retweeted: boolean stating whether the authenticated user (you) have favourited or retweeted this tweet \n
				lang: acronym for the language (e.g. "en" for english) \n
				id: the tweet identifier \n
				place, coordinates, geo: geo-location information if available \n
				user: the author's full profile \n
				entities: list of entities like URLs, @-mentions, hashtags and symbols \n
				in_reply_to_user_id: user identifier if the tweet is a reply to a specific user \n
				in_reply_to_status_id: status identifier id the tweet is a reply to a specific status \n\
				"""

	def countTweets(self, mode="language",per = "daily", option = "all"):
		if mode == "language":
			langs = self.config["language_description"]
			
			arr = {}
			res = []
			c_err = 0

			for d in self.dataset:
				lang = None
		
				# prevent error of an empty entities
				try:
					lang = self.remove_tags(d["lang"])
					dwtz = d["created_at"].split()
				except KeyError:
					c_err += 1
					pass
					continue
				
				if lang not in arr:
					arr.setdefault(lang,1)
				else:
					arr[lang] += 1
					#print arr
			
			print "Unparsed tweets (due to an emptiness of entities) : %s" % c_err

			res = []

			for a in arr.items():
				res.append({"country":langs[a[0]], "visits":a[1]})
			
			res = sorted(res, key= lambda x:x["visits"], reverse=True)

			# Determine the operating system
			opsys = os.name
						
			if opsys == "nt":
				f = open(("%slang.json"%self.config["base_dir_data_win"]),"w")
			else:
				f = open(("%slang.json"%self.config["base_dir_data"]),"w")
	
			f.write(json.dumps(res))
			f.close()
		elif mode == "source":
			arr = {}
			res = []
			c_err = 0

			for d in self.dataset:
				source = None
		
				# prevent error of an empty entities
				try:
					source = self.remove_tags(d["source"])
					dwtz = d["created_at"].split()
				except KeyError:
					c_err += 1
					pass
					continue
				
				if source not in arr:
					arr.setdefault(source,1)
				else:
					arr[source] += 1
					#print arr
			
			print "Unparsed tweets (due to an emptiness of entities) : %s" % c_err

			res = []

			for a in arr.items():
				res.append({"country":a[0], "visits":a[1]})
			
			res = sorted(res, key= lambda x:x["visits"], reverse=True)

			# Determine the operating system
			opsys = os.name
						
			if opsys == "nt":
				f = open(("%ssource.json"%self.config["base_dir_data_win"]),"w")
			else:
				f = open(("%ssource.json"%self.config["base_dir_data"]),"w")
	
			f.write(json.dumps(res))
			f.close()

		elif mode == "user":
			arr = {}
			res = []
			c_err = 0

			for d in self.dataset:
				user = None
		
				# prevent error of an empty entities
				try:
					user = d["user"]["screen_name"]
				except KeyError:
					c_err += 1
					pass
					continue
				
				if user not in arr:
					arr.setdefault(user,1)
				else:
					arr[user] += 1
					#print arr
			
			print "Unparsed tweets (due to an emptiness of entities) : %s" % c_err

			res = []

			for a in arr.items():
				res.append({"country":a[0], "visits":a[1]})
			
			if option != "all":
				upperbound = int(option)
				res = sorted(res, key= lambda x:x["visits"], reverse=True)[0:upperbound]

			res = sorted(res, key= lambda x:x["visits"], reverse=True)
			# Determine the operating system
			opsys = os.name
						
			if opsys == "nt":
				f = open(("%susers.json"%self.config["base_dir_data_win"]),"w")
			else:
				f = open(("%susers.json"%self.config["base_dir_data"]),"w")
	
			f.write(json.dumps(res))
			f.close()

		elif mode == "peak":
			
			arr = {}
			res = []
			c_err = 0
			
			if per == "daily":
				for d in self.dataset:
					dwtz = None

					# prevent error of an empty entities
					try:
						dwtz = d["created_at"].split()
					except KeyError:
						c_err += 1
						pass
						continue
					del dwtz[4]
					tweetDate = ' '.join(dwtz)
					d = datetime.strptime(tweetDate,'%a %b %d %H:%M:%S %Y');
					tweetDate = d + timedelta(hours=self.config["timezone"])
					
					key = tweetDate.strftime('%Y-%m-%d')
					
					if key not in arr:
						arr.setdefault(key,1)
					else:
						arr[key] += 1
						#print arr
				
				print "Unparsed tweets (due to an emptiness of entities) : %s" % c_err

				for a in arr.items():
					res.append({"date":a[0], "value":a[1]})
				
				# Determine the operating system
				opsys = os.name
				
				res = sorted(res)
				
				if opsys == "nt":
					f = open(("%sdate_d.json"%self.config["base_dir_data_win"]),"w")
				else:
					f = open(("%sdate_d.json"%self.config["base_dir_data"]),"w")
		
				f.write(json.dumps(res))
				f.close()
					
			elif per == "hourly":
				c_err = 0
				for d in self.dataset:
					dwtz = None

					# prevent error of an empty entities
					try:
						dwtz = d["created_at"].split()
					except KeyError:
						c_err += 1
						pass
						continue

					del dwtz[4]
					tweetDate = ' '.join(dwtz)
					d = datetime.strptime(tweetDate,'%a %b %d %H:%M:%S %Y');
					tweetDate = d + timedelta(hours=self.config["timezone"])
					
					key = tweetDate.strftime('%Y-%m-%d %H:%M:00')
					
					if key not in arr:
						arr.setdefault(key,1)
					else:
						arr[key] += 1
						#print arr
				
				print "Unparsed tweets (due to an emptiness of entities) : %s" % c_err

				for a in arr.items():
					res.append({"date":a[0], "value":a[1]})
			
				# Determine the operating system
				opsys = os.name
				
				res = sorted(res)
				
				if opsys == "nt":
					f = open(("%sdate_m.json"%self.config["base_dir_data_win"]),"w")
				else:
					f = open(("%sdate_m.json"%self.config["base_dir_data"]),"w")
		
				f.write(json.dumps(res))
				f.close()

	# not implemented yet
	# implemented : temporarily by using its source 
	# https://www.eecis.udel.edu/~hnw/paper/acsac10.pdf
	def is_buzzer(self, tweet=None, text=""):
		source_buzzer = ['Twitterfeed', 'twitRobot', 'TweetDeck', 'bit.ly']

		if tweet == None:
			return False
		else:
			try:
				source = tweet["source"]
				source =  self.remove_tags(source)

				if source in source_buzzer:
					return True
				else:
					return False
			except KeyError:
				return False
		return False
		
	def building_coocurence(self, dump=False):
		print "Building the matrix"
		samples = self.get(what="text")
		#print len(samples)
		bigram_vectorizer = CountVectorizer(ngram_range=(2, 2)) 
		co_occurrences = bigram_vectorizer.fit_transform(samples)
		populate_bigram = bigram_vectorizer.get_feature_names()
		#print bigram_vectorizer.get_feature_names()
		
		dictio = {}
		for pop in populate_bigram:
			div = pop.split()
			
			if div[0] not in dictio:
				dictio.setdefault(div[0],{div[1]:1})
				
			if div[1] not in dictio[div[0]]:
				dictio[div[0]].setdefault(div[1],1)
			else:
				getchildkeyval = dictio[div[0]][div[1]] 
				dictio[div[0]][div[1]] = getchildkeyval+1	
		
			if div[1] not in dictio:
				dictio.setdefault(div[1],{div[0]:1})
		
			if div[0] not in dictio[div[1]]:
				dictio[div[1]].setdefault(div[0],1)
			else:
				getchildkeyval = dictio[div[1]][div[0]] 
				dictio[div[1]][div[0]] = getchildkeyval+1
		
		if dump == True:
			opsys = os.name
			if opsys == "nt":
				f = open(("%sdump_dictio.json"%self.config["base_dir_data_win"]),"w")
			else:
				f = open(("%sdump_dictio.json"%self.config["base_dir_data"]),"w")

			f.write(json.dumps(dictio))
			f.close()

		return dictio
		
	def inspect_term(self, dictionary, term="what", export=False, depth=5):
		if export == False:
			import operator
			sorted_x = sorted(dictionary[term].items(), key=operator.itemgetter(1), reverse=True)
			return sorted_x
		else:
			arr = {}

			i = 0
			while i < depth:
				res = self.inspect_term(dictionary, term=term, export=False)
				term = res[0][0]					
				if term not in arr:
					arr.setdefault(term, dictionary[res[0][0]])
				else:
					term = res[1][0]
					arr.setdefault(term, dictionary[res[1][0]])
				i += 1

			json_arr = {"nodes":[], "links":[]}

			#for i in range(0, len(arr)):


			return arr

	def network_analysis(self, screen_name="", what="friends"):
		if what=="friends":
			from tweepy import OAuthHandler
			import tweepy
			import time

			ids = []
			auth = OAuthHandler(self.config["consumer_key"], self.config["consumer_secret"])
			auth.set_access_token(self.config["access_token"], self.config["access_token_secret"])

			api = tweepy.API(auth)
			acc = {}
			
			acc.setdefault(screen_name, {})
			
			for page in tweepy.Cursor(api.followers_ids, screen_name=screen_name).pages(10):
				ids.extend(page)
				#print ids
			
			screen_names = [user.screen_name for user in api.lookup_users(user_ids=ids)]
			
			for scr in screen_names:
				acc[screen_name].setdefault(scr, {})
				idsk = []
				for pages in tweepy.Cursor(api.followers_ids, screen_name=scr).pages():
					idsk.extend(pages)
					time.sleep(2)
				
				screen_names_k = [user.screen_name for users in api.lookup_users(user_ids=idsk)]
				
				for scrk in screen_names_k:
					acc[screen_name].setdefault(scrk, {})
			#print acc
			return acc
				
	def write_param(self, topic="", total="", unparsed_tweets="", bots=""):

		if topic == "":
			topic = "no_topic_is_set"

		# Determine the operating system
		opsys = os.name
					
		if opsys == "nt":
			f = open(("%s%s.json"%(self.config["base_dir_data_win"], "param")),"w")
		else:
			f = open(("%s%s.json"%(self.config["base_dir_data"], "param")),"w")

		f.write(json.dumps({"topic":topic, "total":total, "unparsed_tweets":unparsed_tweets, "bots":bots}))
		f.close()