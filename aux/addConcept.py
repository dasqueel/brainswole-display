from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
#client = MongoClient('mongodb://neil:squ33ler@52.24.174.234/admin')
conceptsDb = client.Concepts

curse = 'Calculus'

concepts = [
	'derivative',
	'eulers method',
	'seperable differential equations',
	'slope fields',
	'integration by parts',
	'integration by u substitution',
	'improper integrals',
	'the fundamental theorem of calculus',
	'ratio test',
	'alternating series',
	'convergence',
	'divergence',
	'product rule',
	'quotient rule',
	'power rule',
	'implicit differentiation',
	'limits',
	'squeeze theorem'
]

for concept in concepts:
	#add concept to calc course if it hasnt already
	courseDoc = conceptsDb['courses'].find_one({"name":course})
	courseConcepts = courseDoc['concepts']

	if concept not in courseConcepts:
		conceptsDb['courses'].update({"name":course},{"$push":{"concepts":concept}})
		print 'added '+concept+' to course concepts'

	#add concept to conceptLinks if it hasnt already
	if conceptsDb['conceptLinks'].find_one({"name":concept}) == None:
		doc = {"name":concept,"practice":[],"explanations":[]}
		conceptsDb['conceptLinks'].insert(doc)
		print 'added '+concept+' to conceptLinks'