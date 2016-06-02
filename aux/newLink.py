#give every concept that a conceptLinkDoc that doesnt have one
#already updates from already made courses

from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts

#linkCol = conceptsDb['conceptLinks']

#courseCol = conceptsDb['courses']

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

#insert link to appropiate concept
#linkCol.update({"name":name},{"$push",{"practice":link}})