from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
generalDb = client.ArchiveGeneral

print generalDb['general'].find_one({'doc':'general'})['masterConcepts']
'''
coursesCur = conceptsDb['courses'].find()
masterConcepts = []

for courseDoc in coursesCur:
	for concept in courseDoc['concepts']:
		if concept not in masterConcepts:
			masterConcepts.append(concept)
		else:
			pass

#print masterConcepts
if generalDb['general'].update({'doc':'general'},{'$set':{'masterConcepts':masterConcepts}}):
	print 'yup'
else:
	print 'nope'
'''