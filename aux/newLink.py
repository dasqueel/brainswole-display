#give every concept, a conceptLinkDoc that doesnt have one
#already updates from already made courses

#also adds concept to masterConcepts if not already added

from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
generalDb = client.ArchiveGeneral

for courseDoc in conceptsDb['courses'].find():
	courseConcepts = courseDoc['concepts']

	for concept in courseConcepts:
		linkDoc = {"name":concept,"practice":[],"explanations":[]}

		#add a blank linkDoc for the concept if it doenst have one
		if conceptsDb['conceptLinks'].find_one({"name":concept}):
			print "passed on "+concept
			pass
		else:
			conceptsDb['conceptLinks'].insert(linkDoc)
			print 'added '+concept
			#add concept to master list if it is not already added
			masterConcepts = generalDb['general'].find_one({'doc':'general'})['masterConcepts']
			if concept not in masterConcepts:
				generalDb['general'].update({'doc':'general'},{'$push':{'masterConcepts':concept}})
				print 'pushed '+concept+' into masterConcepts'
			else:
				print concept+' already in masterConcepts'