from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
usersDb = client.ArchiveUsers

#add a key value to all docs

#add demos key and [] value to all users concepts docs

names = usersDb.collection_names()

names.remove('system.indexes')

#usersDb['neilbarduson'].update({'concept':'power rule'},{'$set':{'demos':[]}})

for name in names:
	userConceptDocs = usersDb[name].find({"concept":{'$exists': True}})
	for conceptDoc in userConceptDocs:
		if 'demos' not in conceptDoc.keys():
			usersDb[name].update({'concept':conceptDoc['concept']},{'$set':{'demos':[]}})
			print 'updated '+name+' '+conceptDoc['concept']+' with a demo key [] val'