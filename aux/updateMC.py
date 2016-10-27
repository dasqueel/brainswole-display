from pymongo import MongoClient
from courseConcepts import *

client = MongoClient('localhost')
generalDb = client.ArchiveGeneral

#update masterConcepts from courseConcepts
newMaster = []

for name,concepts in courseConcepts.iteritems():
	for concept in concepts:
		if concept not in newMaster:
			newMaster.append(concept)

generalDb['general'].update({'doc':'general'},{'$set':{'masterConcepts':newMaster}})