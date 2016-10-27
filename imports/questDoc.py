"""
functions to:

1) add what course (interview questionaire) questionDoc
"""

from courseConcepts import courseConcepts
from pymongo import MongoClient

client = MongoClient('localhost')
conceptsDb = client.Concepts

for quest in courseConcepts['back-end developer']:
	questionDoc = concepts