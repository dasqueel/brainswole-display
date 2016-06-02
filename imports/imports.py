import urllib2
from flask import redirect, url_for
from oauth import *
from pymongo import MongoClient
import json
from conceptMap import *
from courseConcepts import *
import datetime
import re

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.ArchiveUsers

#khanacademy
def khan(userName):
    userDoc = userDb[userName].find_one({'userName':userName})
    imported = userDoc['imported']
    access_token = None
    khanUsername = None
    #check to see if user as already imported
    for imprt in imported:
        if imprt['provider'] == 'khan':
            access_token = imprt['accessToken']
            khanUsername = imprt['providerUsername']
        else:
            pass
    if access_token == None:
        print 'start of request token'
        #get an access token
        #start request token process
        consumer = OAuthConsumer('9YrRjqYAjMWWF7ZP','Y45DZt2vCGV9w8W2')
        callback = 'https://brainswole.com/requesttoken?provider=khan'
        oauth_request = OAuthRequest.from_consumer_and_token(
                consumer,
                callback=callback,
                http_url="https://www.khanacademy.org/api/auth/request_token"
                )

        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
        return redirect(oauth_request.to_url())
    else:
        #update khan academy data
        consumer = OAuthConsumer('9YrRjqYAjMWWF7ZP','Y45DZt2vCGV9w8W2')
        access_token = OAuthToken.from_string(access_token)
        oauth_request = OAuthRequest.from_consumer_and_token(
                consumer,
                token=access_token,
                http_url="https://www.khanacademy.org/api/v1/user/exercises"
                )
        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, access_token)

        resp = urllib2.urlopen(oauth_request.to_url())
        response = resp.read()
        respJson = json.loads(response)
        for exer in respJson:
            exerName = exer['exercise']
            exerDisplayName = exer['exercise_model']['display_name']
            #add experience url to users concept practice urls
            baseUrl = 'khanacademy.org/profile/'+khanUsername+'/vital-statistics/problems/'
            expUrl = baseUrl+exerName
            #get users attempted anc correct probs -- might have to check to see if total_done and total_correct exist
            probsCorrect = exer['total_correct']
            probsAttempted = exer['total_done']
            probsStreak = exer['streak']
            #only add exercises with a prbolem attempted
            if probsAttempted > 0:
            #loop through khanMap
                for conceptNorm, conceptKhanList in khanMap.iteritems():
                    #create practExpObj
                    #get urlId
                    urlId = re.sub(r"[^a-zA-Z_0-9]", '', expUrl)
                    #get url title
                    title = exerDisplayName +' -- Khanacademy'
                    #create practExpId
                    practExpObj = {
                        'url':expUrl,
                        'lastVisit':datetime.datetime.utcnow(),
                        'urlId':urlId,
                        'name':exerName,
                        'title':title,
                        'displayName':exerDisplayName,
                        'probsCorrect':probsCorrect,
                        'probsAttempted':probsAttempted,
                        'probsStreak':probsStreak
                        }
                    if exerName in conceptKhanList:
                        #add expUrl to usersConceptPract
                        #check to see if user has already made conceptDoc for the concept
                        userConceptDoc = userDb[userName].find_one({'concept':conceptNorm})
                        #if userConceptDoc exists, add expUrl
                        if userConceptDoc:
                            addedPractUrls = []
                            #get all practice urls already added by user
                            for practMod in userConceptDoc['practice']:
                                addedPractUrls.append(practMod['url'])

                            if expUrl in addedPractUrls:
                                #update attempted and correct
                                print 'updated'
                                userDb[userName].update({'concept':conceptNorm,'practice.name':exerName},{'$set':{'practice.$.probsAttempted':probsAttempted,'practice.$.probsCorrect':probsCorrect,'practice.$.probsStreak':probsStreak}})
                            else:
                                #add first time khan expUrl
                                print 'added'
                                userDb[userName].update({'concept':conceptNorm},{'$push':{'practice':practExpObj}})
                        #else create a userConceptDoc for the concept
                        else:
                            doc = {
                            'concept':conceptNorm,
                            'lastVisit':datetime.datetime.utcnow(),
                            'practice':[practExpObj],
                            'explanations':[],
                            'courses':[]
                            }
                            #add course(s) the concept its part of ** could redo this more efficiently  **
                            for courseName,courseList in courseConcepts.iteritems():
                                if conceptNorm in courseList:
                                    doc['courses'].append(courseName)

                            #insert the doc
                            userDb[userName].insert(doc)
        return redirect(url_for('imports'))

