import sys
#sys.path.append('/Users/squeel/sites/brainswole/imports')
sys.path.append('/home/ubuntu/brainswole/imports')
from pymongo import MongoClient
from courseConcepts import *

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
generalDb = client.ArchiveGeneral

name = 'web development'
concepts = courseConcepts[name]

doc = {'name':name,'concepts':concepts,'whyLinks':[]}

if conceptsDb['courses'].find_one({'name':name}):
	print name+' already added'
else:
	conceptsDb['courses'].insert(doc)
	print name+' added to courses!!'


##update masterConcepts from courseConcepts
newMaster = []

for course,concepts in courseConcepts.iteritems():
	for concept in concepts:
		if concept not in newMaster:
			newMaster.append(concept)

generalDb['general'].update({'doc':'general'},{'$set':{'masterConcepts':newMaster}})
print 'updated masterConcepts'