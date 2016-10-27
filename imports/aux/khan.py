import urllib2
from oauth import *
from pymongo import MongoClient
import json
from conceptMap import *
import datetime
import re
import pprint
from courseConcepts import courseConcepts

from bs4 import BeautifulSoup
import urllib2

#return explantions dict as url as input
## later update function if its a tube time situation ##
def explMaker(url):
    #parse the https:// or http://
    url = re.sub('https://', '', url)
    url = re.sub('http://', '', url)
    url = re.sub('https://www.', '', url)
    url = re.sub('http://www.', '', url)
    url = re.sub('www.', '', url)
    explObj = {
        'lastVist' : datetime.datetime.utcnow(),
        'title' : None,
        'url' : url,
        'tubeTime' : None,
        'urlId' : None
    }
    #get video title through beautifulsoup
    response = urllib2.urlopen('http://'+url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.html.head.title.text.strip()
    explObj['title'] = title

    urlId = re.sub(r"[^a-zA-Z_0-9]", '', url)
    explObj['urlId'] = urlId

    return explObj

pp = pprint.PrettyPrinter(indent=4)

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.ArchiveUsers

#khanacademy
def khan(userName):
    CONSUMER_KEY = "9YrRjqYAjMWWF7ZP"
    CONSUMER_SECRET = "Y45DZt2vCGV9w8W2"
    SERVER_URL = "https://www.khanacademy.org"

    userDoc = userDb[userName].find_one({'userName':userName})
    imported = userDoc['imported']
    access_token = None
    for imprt in imported:
        if imprt['provider'] == 'khan':
            access_token = imprt['accessToken']
        else:
            pass
    if access_token == None:
        #get an access token
        pass
        #redirect(url_for('getAccessToken'),{'provider':'khan'})
    else:
        consumer = OAuthConsumer('9YrRjqYAjMWWF7ZP','Y45DZt2vCGV9w8W2')
        access_token = OAuthToken.from_string(access_token)
        oauth_request = OAuthRequest.from_consumer_and_token(
                consumer,
                token=access_token,
                http_url="https://www.khanacademy.org/api/v1/user"
                )
        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, access_token)

        resp = urllib2.urlopen(oauth_request.to_url())
        response = resp.read()
        respJson = json.loads(response)
        return respJson
        '''
        #pp.pprint(respJson)
        for vid in respJson:
            #print vid['video']['url'], vid['video']['title']
            #if vid['completed'] == True:
                #add video to users explanations
            khanTubeUrl = vid['video']['url'].replace("&feature=youtube_gdata_player", "") #simple youtube url for video
            khanTubeUrl = khanTubeUrl.replace("http://www.", "") #simple youtube url for video
            for conceptNorm,vidList in khanVidMap.iteritems():
                if khanTubeUrl in vidList:
                    #check to see if user has already made conceptDoc for the concept
                    userConceptDoc = userDb[userName].find_one({'concept':conceptNorm})
                    #if userConceptDoc exists, add expUrl
                    if userConceptDoc:
                        #add khanTubeUrl into users conceptdocs explanations
                        #create possible new explObj
                        explObj = explMaker(khanTubeUrl)
                        userDb['neilbarduson'].update({'concept':conceptNorm,'explanations.url': {'$ne': khanTubeUrl}},{'$push':{'explanations':explObj}})
                    #else create a userConceptDoc for the concept
                    else:
                        explObj = explMaker(khanTubeUrl)

                        doc = {
                            'concept':conceptNorm,
                            'lastVisit':datetime.datetime.utcnow(),
                            'practice':[],
                            'explanations':[explObj],
                            'courses':[],
                            'demos':[]
                        }
                        #add course(s) the concept its part of ** could redo this more efficiently  **
                        for courseName,courseList in courseConcepts.iteritems():
                            if conceptNorm in courseList:
                                doc['courses'].append(courseName)

                        #insert the doc
                        userDb[userName].insert(doc)
                        '''

print khan('neilbarduson')
#else get import/udate users khanacademy progress