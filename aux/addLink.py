#add a new linkObj to conceptLinks

import re
from pymongo import MongoClient
import urllib2
from bs4 import BeautifulSoup

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts

linkUrl = "http://setosa.io/ev/markov-chains/"
#parse the https:// or http://
linkUrl = re.sub('https://', '', linkUrl)
linkUrl = re.sub('http://', '', linkUrl)
linkUrl = re.sub('https://www.', '', linkUrl)
linkUrl = re.sub('http://www.', '', linkUrl)
linkUrl = re.sub('www.', '', linkUrl)
httpLinkUrl = "http://"+linkUrl

#create symbol-less urlid
urlId = re.sub(r"[^a-zA-Z_0-9]", '', linkUrl)

#get title for webpage
response = urllib2.urlopen(httpLinkUrl)
html = response.read()
soup = BeautifulSoup(html, 'html.parser')
title = soup.html.head.title.text.strip()

concept = "markov chains"
explOrPract = "expl"

conceptDoc = conceptsDb['conceptLinks'].find_one({"name":concept})
linkObjs = conceptDoc['explanations']

if explOrPract == "expl":
	linkObjs = conceptDoc['explanations']

	#if its the first linkObj in explanations
	if len(linkObjs) == 0:
		#add link to explanations
		newLinkObj = {"url":linkUrl,"urlId":urlId,"likes":0,"title":title}
		#print newLinkObj
		#add new newLinkObj to explanations
		conceptsDb['conceptLinks'].update({"name":concept},{"$push":{"explanations":newLinkObj}})
		print 'added '+linkUrl+' object!'
	else:
		addedUrls = []
		for linkObj in linkObjs:
			addedUrls.append(linkObj['url'])

		if linkUrl in addedUrls:
			print linkUrl+" link already added"
			pass
		else:
			#add link to explanations

			newLinkObj = {"url":linkUrl,"urlId":urlId,"likes":0,"title":title}

			#print newLinkObj
			#add new newLinkObj to explanations
			conceptsDb['conceptLinks'].update({"name":concept},{"$push":{"explanations":newLinkObj}})
			print 'added '+linkUrl+' object!'
