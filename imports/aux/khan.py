import urllib2
from oauth import *
from pymongo import MongoClient
import json
from conceptMap import *
import datetime
import re

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.Users

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
        #pass
        redirect(url_for('getAccessToken'),{'provider':'khan'})
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
        print respJson['student_summary']['username']
        '''
        for exer in respJson:
            print exer['exercise']
            print 'mastered: '+str(exer['mastered'])
            print 'total done: '+str(exer['total_done'])
            print 'total correct: '+str(exer['total_correct'])
            print '\n'
            #print exer['exercise'], exer['total_done']'''

khan('neilbarduson')
#else get import/udate users khanacademy progress