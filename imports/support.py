from pymongo import MongoClient
from courseConcepts import *

#client = MongoClient('localhost')
client = MongoClient('mongodb://neil:squ33ler@52.24.174.234/admin')
generalDb = client.ArchiveGeneral

#update masterConcepts from courseConcepts
newMaster = []

for name,concepts in courseConcepts.iteritems():
	for concept in concepts:
		if concept not in newMaster:
			newMaster.append(concept)

generalDb['general'].update({'doc':'general'},{'$set':{'masterConcepts':newMaster}})