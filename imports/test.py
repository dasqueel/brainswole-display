#codeCadPractMods = [{'provider':'codeCad','title':'test1'},{'provider':'codeCad','title':'test2'}]

#print filter(lambda langObj: langObj['provider'] == 'codeCad' and langObj['title'] == 'test1', codeCadPractMods)

from pymongo import MongoClient
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.ArchiveUsers

'''
codecademyMap = {
	'api':['YouTube API','NHTSA API','Twitter API','Evernote API','SoundCloud API','SendGrid API','NPR API'],
	'python':[],
	'java':['Learn Java'],
	'php':['PHP'],
	'ruby':['Ruby','Ruby on Rails: Authentication'],
	'jquery':['jQuery'],
	'sql':['Learn SQL','SQL: Table Transformation'],
	'html':['HTML & CSS'],
	'css':['HTML & CSS'],
	'javascript':['JavaScript']
}
#helper function to remove a given usernames data (when user changes username for their provider profile)
def removeProvData(userName, provUsername, provider,conceptMap):
    #loop through all userConceptDocs and check for providers data entry, could also perform a smart list to search for
    for concept in conceptMap:
        if userDb[userName].find_one({'concept':concept,'practice.provider':provider}):
            userDb[userName].update({'concept':concept},{'$pull':{'practice':{'provider':provider}}},upsert=False, multi=True)

removeProvData('testmctesty','dasqueel','codeCad',codecademyMap)
#upsert=False, multi=True

userConceptDoc = userDb['testmctesty'].find_one({'concept':'ruby'})

if userConceptDoc['practice'] == [] and userConceptDoc['explanations'] == [] and userConceptDoc['demos'] == []:
    #delete the userConceptDoc since its empty
    print 'here'
    userDb['testmctesty'].remove({"concept":'ruby'})
else:
	print 'nope'
'''

from bs4 import BeautifulSoup
import requests

url = 'http://codecademy.com/dasqueel'

r = requests.get(url)

# Turn the HTML into a Beautiful Soup object
soup = BeautifulSoup(r.text, 'html.parser')
for row in soup.findAll("h5", { "class" : "text--ellipsis" }):
	print row.text



