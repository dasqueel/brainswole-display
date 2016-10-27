from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
#client = MongoClient('mongodb://neil:squ33ler@52.24.174.234/admin')
conceptsDb = client.Concepts
generalDb = client.ArchiveGeneral

course = 'web development'

concepts = [
	'mvc'
]

for concept in concepts:
	#add concept to course course if it hasnt already
	courseDoc = conceptsDb['courses'].find_one({"name":course})
	courseConcepts = courseDoc['concepts']

	if concept not in courseConcepts:
		conceptsDb['courses'].update({"name":course},{"$push":{"concepts":concept}})
		print 'added '+concept+' to '+course+' concepts'

	#add concept to conceptLinks if it hasnt already
	if conceptsDb['conceptLinks'].find_one({"name":concept}) == None:
		doc = {"name":concept,"practice":[],"explanations":[]}
		conceptsDb['conceptLinks'].insert(doc)
		print 'added '+concept+' to conceptLinks'

	#add what courses the concept is used under

	#update masterConcepts
	generalDb['general'].update({"doc":"general"},{"$addToSet":{"masterConcepts":concept}})