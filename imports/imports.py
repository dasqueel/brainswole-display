import urllib2
from flask import redirect, url_for
from oauth import *
from pymongo import MongoClient
import json
from conceptMap import *
from courseConcepts import *
import datetime
import re
import requests
from bs4 import BeautifulSoup
import traceback
import sys
sys.path.append("../")
from helpers import *

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.ArchiveUsers

#helper functions
#return a concepts relevant courses -- type = list
def getConceptsCourses(concept, courseConcepts):
    courses = []
    for courseName, courseConcepts in courseConcepts.iteritems():
        if concept in courseConcepts:
            courses.append(courseName)
    return courses

#helper function to remove a given usernames data (when user changes username for their provider profile)
def removeProvData(userName, provUsername, provider,conceptMap):
    #loop through all userConceptDocs and check for providers data entry, could also perform a smart list to search for
    for concept in conceptMap:
        #print 'start for conceptmap'
        userConceptDoc = userDb[userName].find_one({'concept':concept,'practice.provider':provider})
        if userConceptDoc:
            userDb[userName].update({'concept':concept},{'$pull':{'practice':{'provider':provider}}},upsert=False, multi=True)
            #should delete userConceptDoc if its empty with practice, explanations, demos
            userConceptDoc = userDb[userName].find_one({'concept':concept})
            if userConceptDoc['practice'] == [] and userConceptDoc['explanations'] == [] and userConceptDoc['demos'] == []:
                #delete the userConceptDoc since its empty
                print 'here'
                userDb[userName].remove({"concept":concept})

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
        ## exercise data ##
        consumer = OAuthConsumer('9YrRjqYAjMWWF7ZP','Y45DZt2vCGV9w8W2')
        access_token = OAuthToken.from_string(access_token)
        oauth_request = OAuthRequest.from_consumer_and_token(
                consumer,
                token=access_token,
                http_url="https://www.khanacademy.org/api/v1/user/exercises"
                )
        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, access_token)

        #if request is good, remove prior khanUserNames data#
        removeProvData(userName,khanUsername,'khan','khanMap')

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
                    title = exerDisplayName +' -- Khanacademy || correct: '+str(probsCorrect)+' attempted: '+str(probsAttempted)
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
                        'probsStreak':probsStreak,
                        'provider':'khan'
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
                                userDb[userName].update({'concept':conceptNorm,'practice.name':exerName},{'$set':{'practice.$.probsAttempted':probsAttempted,'practice.$.probsCorrect':probsCorrect,'practice.$.probsStreak':probsStreak}})
                            else:
                                #add first time khan expUrl
                                userDb[userName].update({'concept':conceptNorm},{'$push':{'practice':practExpObj}})
                        #else create a userConceptDoc for the concept
                        else:
                            doc = {
                                'concept':conceptNorm,
                                'lastVisit':datetime.datetime.utcnow(),
                                'practice':[practExpObj],
                                'explanations':[],
                                'courses':[],
                                'demos':[]
                            }
                            #add course(s) the concept its part of ** could redo this more efficiently  **
                            for courseName,courseList in courseConcepts.iteritems():
                                if conceptNorm in courseList:
                                    doc['courses'].append(courseName)

                            #insert the doc
                            userDb[userName].insert(doc)

        ## video data ##
        #consumer = OAuthConsumer('9YrRjqYAjMWWF7ZP','Y45DZt2vCGV9w8W2')
        #access_token = OAuthToken.from_string(access_token)
        print 'doing khan vids'
        oauth_request = OAuthRequest.from_consumer_and_token(
                consumer,
                token=access_token,
                http_url="https://www.khanacademy.org/api/v1/user/videos"
                )
        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, access_token)

        resp = urllib2.urlopen(oauth_request.to_url())
        response = resp.read()
        respJson = json.loads(response)
        for vid in respJson:
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

        return redirect(url_for('imports'))

#codewars
#remember to remove all languages if user changes codewars usernames
def codewars(brainswoleUserName,providerUsername):
    r = requests.get('https://www.codewars.com/api/v1/users/'+providerUsername)
    if r.status_code == 404:
        error = providerUsername+' does not exist in Codewars database :('
        #return render_template('')
        return url_for('imports', error=error)

    #if request is good, remove prior codeWarsUserNames data#
    #have to make a codeWars map and design codewars importing design
    #removeProvData(userName,providerUsername,'codeWars','khanMap')

    resp = r.json()
    langs = resp['ranks']['languages']

    #update lang(concept) doc
    for langName,v in langs.iteritems():
        #import lang to langConceptDoc
        statusStr = 'codewars score: '+str(v['score'])+' || rank: '+v['name']

        #check to see if its first time import codewars
        #check to see if python conceptUserDoc as been created
        langPractObjs = None
        if userDb[brainswoleUserName].find_one({'concept':str(langName)}):
            langPractObjs = userDb[brainswoleUserName].find_one({'concept':str(langName)})['practice']
        else:
            #create userDoc for language concept
            conceptDoc = {
                'concept': langName,
                'lastVisit':datetime.datetime.utcnow(),
                'practice':[],
                'explanations':[],
                'courses':['programming languages'], #could change if codewars does other concepts
                'demos':[]
            }
            #appropiately add valid courses to language (for now just add programming languages)
            #insert new conceptDoc
            userDb[brainswoleUserName].insert(conceptDoc)
            #set the new langPractObjs
            langPractObjs = []

        #update users codewars data
        if filter(lambda langObj: langObj['provider'] == 'codeWars', langPractObjs) == []:
            #add new codeWars langPractObj
            #create provider pract obj
            practExpObj = {'title':statusStr,'provider':'codeWars'}
            #update codeWars statusStr if not already added
            userDb[brainswoleUserName].update({'concept':str(langName)},{'$push':{'practice':practExpObj}})
        #else update the existing experience
        else:
            langPractObj = filter(lambda langObj: langObj['provider'] == 'codeWars', langPractObjs)[0]
            langPractObj['title'] = statusStr
            #set updated title
            userDb[brainswoleUserName].update({'concept':str(langName), 'practice.provider':'codeWars'},{'$set':{'practice.$.title':statusStr}})

        return redirect(url_for('imports'))

#scrape codecamey for skills
#remember to remove all skills if user changes codecadey usernames
def codecad(brainswoleUserName,codecadUsername):
    #get users code cad skills and add them to appropiate concept docs
    url = 'http://codecademy.com/'+codecadUsername

    r = requests.get(url)

    # Turn the HTML into a Beautiful Soup object
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        #if request is good, remove prior codeCadUserNames data#
        removeProvData(brainswoleUserName,codecadUsername,'codeCad',codeCadMap)
        for row in soup.findAll("h5", { "class" : "text--ellipsis" }):
            for concept, conceptList in codeCadMap.iteritems():
                if row.text in conceptList:
                    #add skill if it hasnt been added before
                    #create new conceptdoc if not created
                    if userDb[brainswoleUserName].find_one({'concept':concept}):
                        #check to see if row.text is in users concept doc pratice
                        codeCadPractMods = userDb[brainswoleUserName].find_one({'concept':concept})['practice']
                        #add new codeCad practMod/skill
                        if filter(lambda codeCadObj: codeCadObj['provider'] == 'codeCad' and codeCadObj['title'] == 'Codecademy: '+row.text, codeCadPractMods) == []:
                            skillObj = {'provider':'codeCad','title':'Codecademy: '+row.text}
                            #push new skillObj
                            userDb[brainswoleUserName].update({'concept':concept},{'$push':{'practice':skillObj}})
                    #creat new conceptDoc
                    else:
                        doc = {
                            'concept':concept,
                            'lastVisit':datetime.datetime.utcnow(),
                            'practice':[{'provider':'codeCad','title':'Codecademy: '+row.text}],
                            'explanations':[],
                            'courses':getConceptsCourses(concept,courseConcepts),
                            'demos':[]
                        }
                        userDb[brainswoleUserName].insert(doc)
    except:
        print traceback.print_exc()
        pass

    return redirect(url_for('imports'))

#a listing of providers concept modules