'''
import requests
import pprint
import json

pp = pprint.PrettyPrinter(indent=4)

url = 'http://www.khanacademy.org/api/v1/exercises'

r = requests.get(url)

resp = r.json()

# Reading data back
with open('khan.json', 'r') as f:
	data = json.load(f)
	exers = data['exers']
	with open("khan.txt",'w') as openfile:
	    openfile.write("\n".join(map(str,exers)))
'''
from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
#client = MongoClient('mongodb://neil:squ33ler@52.24.174.234/admin')
conceptsDb = client.Concepts
userDb = client.ArchiveUsers

coursesCur = conceptsDb['courses'].find()

for course in coursesCur:
	print course['name']
	for whyLink in course['whyLinks']:
		if 'date' not in whyLink.keys():
			print whyLink['url']+'would add'
		else:
			print whyLink['url']+'wouldnt ass'