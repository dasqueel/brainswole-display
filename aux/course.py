from pymongo import MongoClient
import json


with open('courses.json') as data_file:
    data = json.load(data_file)

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts

name = 'algorithms'
concepts = data[name]

doc = {'name':name,'concepts':concepts}
conceptsDb['courses'].insert(doc)