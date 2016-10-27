import sys
sys.path.append('/Users/squeel/sites/brainswole/imports')
#sys.path.append('/home/ubuntu/brainswole/imports')
from pymongo import MongoClient
from courseConcepts import *

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
generalDb = client.ArchiveGeneral

name = 'Back-End Developer Interview Questions'
concepts = courseConcepts[name]

doc = {'name':name,'concepts':concepts,'whyLinks':[],'type':'questions'}

if conceptsDb['courses'].find_one({'name':name}):
	print name+' already added'
else:
	conceptsDb['courses'].insert(doc)
	print name+' added to courses!!'