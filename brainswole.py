import flask
from flask import *
from passlib.hash import pbkdf2_sha256
from operator import itemgetter
import datetime
from support import *
from rauth import OAuth1Service
import requests
from imports.imports import *
from imports.courseConcepts import *
from oauth import *
from stuff import *
from helpers import *
from itertools import chain

app = flask.Flask(__name__)
app.secret_key = aaabbbbccc

import flask_login

login_manager = flask_login.LoginManager()

login_manager.init_app(app)

from pymongo import MongoClient
from rauth import OAuth2Service
import base64
import urllib2
from bs4 import BeautifulSoup

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.ArchiveUsers
generalDb = client.ArchiveGeneral
tubeTestDb = client.TubeTest

class User(flask_login.UserMixin):
    def __init__(self, userName, email, firstName):
            self.userName = userName
            self.id = email
            self.email = email
            self.firstName = firstName

            @property
            def is_authenticated(self):
                return True

            @property
            def is_active(self):
                return True

            @property
            def is_anonymous(self):
                return False

            def get_id(self):
                try:
                    return unicode(self.id)  # python 2
                except NameError:
                    return str(self.id)  # python 3

            def __repr__(self):
                return '<User %r>' % (self.userName)

@login_manager.user_loader
def user_loader(email):
    generalDoc = generalDb['general'].find_one({'doc':'general'})
    registeredEmails = generalDoc['registeredEmails']
    userNameEmails = generalDoc['userNameEmail']

    if email not in registeredEmails:
        return
    userName = None
    for user in userNameEmails:
        if user['email'] == email:
            userName = user['userName']
    #from email get users attributes, firstName, etc...
    userDoc = userDb[userName].find_one({'userName':userName})
    user = User(userName,email,userDoc['firstName'])

    return user

@app.route('/register', methods=['GET','POST'])
def register():
    generalDoc = generalDb['general'].find_one({'doc':'general'})
    registeredEmails = generalDoc['registeredEmails']
    userNameEmails = generalDoc['userNameEmail']
    registeredUserNames = generalDoc['registeredUserNames']

    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        pwd = request.form['pwd']
        rpwd = request.form['rpwd']
        hashpwd = pbkdf2_sha256.encrypt(pwd, rounds=20000, salt_size=16)

        #start checking user validation
        error = None
        if email=='' or firstName=='' or lastName=='' or pwd=='' or rpwd=='':
            error = 'please fill in all data'
            return render_template('register.html', error=error)
        elif pwd != rpwd:
            error = 'passwords dont match, try again'
            return render_template('register.html', error=error)
        elif email in registeredEmails:
            error = email+' has already been registered'
            return render_template('register.html', error=error)
        else:
            #insert the user to database

            #create an unqiue userName
            invalidUserNames = ['questions','login','archived','liked','import','logout']
            userName = None
            if (firstName+lastName).lower() not in registeredUserNames:
                userName = str((firstName+lastName).lower())
            elif (lastName+firstName).lower() not in registeredUserNames:
                userName = str((lastName+firstName).lower())
            else:
                #do the number naming
                x = 1
                while(x < 200):
                    if (firstName+lastName+str(x)).lower() not in registeredUserNames:
                        userName = str((firstName+lastName+str(x)).lower())
                        break
                    else:
                        x += 1
                        pass
            userDoc = {
                'userName':userName,
                'firstName':firstName,
                'lastName':lastName,
                'pwd':hashpwd,
                'email':email,
                'liked':[],
                'archived':[],
                'imported':[]
            }

            #create mongo stuff
            userCol = userDb[userName]
            userCol.insert(userDoc)

            #add userName and email to registered
            userNameEmail = {"userName":userName,"email":email}
            generalDb['general'].update({"doc":"general"},{"$push":{"registeredEmails":email,"registeredUserNames":userName,"userNameEmail":userNameEmail}})

            #create session for user
            user = User(userName,email,firstName)

            flask_login.login_user(user)

            return redirect(url_for('courses'))

@app.route('/login', methods=['GET','POST'])
def login():
    generalDoc = generalDb['general'].find_one({'doc':'general'})
    registeredEmails = generalDoc['registeredEmails']
    userNameEmails = generalDoc['userNameEmail']
    registeredUserNames = generalDoc['registeredUserNames']
    error = None

    if request.method == 'GET':
        return render_template('login.html')

    elif request.method == 'POST':
        email = request.form['email']

        #check to see if email is registered
        if email not in registeredEmails:
            error = email+' is not registered.'
            return render_template('login.html',error=error)

        #proceed to checking password
        else:

            #get userName from email
            userName = None
            for user in userNameEmails:
                if user['email'] == email:
                    userName = str(user['userName'])
            userDoc = userDb[userName].find_one({'userName':userName})

            pwd = request.form['pwd']
            userDoc = userDb[userName].find_one({'userName':userName})
            hashpwd = userDoc['pwd']
            pwdCheck = pbkdf2_sha256.verify(pwd, hashpwd)
            if pwdCheck == False:
                error = 'incorrect password'
                return render_template('login.html',error=error)
            else:
                #creating the session
                user = User(userName,email,userDoc['firstName'])

                flask_login.login_user(user)
                return redirect(url_for('courses'))
    else:
        return render_template('login.html')

@app.route('/')
def index():
    return redirect(url_for('imports'))

@app.route('/courses')
@flask_login.login_required
def courses():
    courses =[]
    courseCol = conceptsDb['courses'].find()
    for doc in courseCol:
        courses.append(doc['name'])
    return render_template('courses.html', courses=courses)

@app.route('/course/<course>')
@flask_login.login_required
def course(course):
    courseDoc = conceptsDb['courses'].find_one({'name':course})
    linksWhy = courseDoc['whyLinks']
    concepts = courseDoc['concepts']

    #ordered links by expl
    linksWhy = sorted(linksWhy, key=itemgetter('likes'), reverse=True)

    #get users liked and archived links
    userDoc = userDb[flask_login.current_user.userName].find_one({'userName':flask_login.current_user.userName})
    userLiked = userDoc['liked']

    for link in linksWhy:
        if link['url'] in userLiked:
            link['liked'] = True
        else:
            link['liked'] = False

    linksWhyNew = sorted(linksWhy, key=lambda k: k['date'], reverse=True)

    return render_template('course.html', concepts=concepts, course=course, linksWhy=linksWhy, linksWhyNew=linksWhyNew)

@app.route('/questions/<course>')
@flask_login.login_required
def questions(course):
    courseDoc = conceptsDb['courses'].find_one({'name':course})
    concepts = courseDoc['concepts']

    #get users added answers urls
    #{'question':'Why is refactoring useful?','urlObjs':[{'url':'test.com','title':'this is a test'}]}
    userQuestionDocs = userDb[flask_login.current_user.userName].find({'question':{'$exists': True}})

    #get users added anwers to questions
    addedAnswers = []

    for questionDoc in userQuestionDocs:
        if course in questionDoc['courses']:
            addedAnswers.append({questionDoc['question']:questionDoc['demos']})

    return render_template('questions.html', concepts=concepts, course=course, addedAnswers=addedAnswers)

@app.route('/logout')
def logout():
    flask_login.logout_user()
    #return 'Logged out'
    return redirect(url_for('login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return redirect(url_for('login'))

##### concepts end points #####

@app.route('/home')
@flask_login.login_required
def home():
    return render_template('home.html')

@app.route('/result')
@flask_login.login_required
def result():
    query = request.args.get('query')
    return query

@app.route('/concept/<concept>')
@flask_login.login_required
def concept(concept):
    #make sure concept is a valid one, not "butt stuff"
    masterConcepts = generalDb['general'].find_one({'doc':'general'})['masterConcepts']

    if concept in masterConcepts:

        #get concept links from mongo database
        conceptLinksDoc = conceptsDb['conceptLinks'].find_one({'name':concept})

        linksExpl = conceptLinksDoc['explanations']
        if linksExpl != []:
            linksPract =  conceptLinksDoc['practice']

            #ordered links by expl
            linksExpl = sorted(linksExpl, key=itemgetter('likes'), reverse=True)
            linksPract = sorted(linksPract, key=itemgetter('likes'), reverse=True)

            #get users liked and archived links
            userDoc = userDb[flask_login.current_user.userName].find_one({'userName':flask_login.current_user.userName})
            userLiked = userDoc['liked']
            userArchived = userDoc['archived']

            #determine if user has liked or archived explanation links
            for link in linksExpl:
                if link['url'] in userLiked and link['url'] in userArchived:
                    link['liked'] = True
                    link['archived'] = True
                elif link['url'] in userLiked and link['url'] not in userArchived:
                    link['liked'] = True
                    link['archived'] = False
                elif link['url'] in userArchived and link['url'] not in userLiked:
                    link['archived'] = True
                    link['liked'] = False
                else:
                    link['archived'] = False
                    link['liked'] = False

            return render_template('concept.html', concept=concept, linksExpl=linksExpl, linksPract=linksPract,error=None)
        else:
            return render_template('concept.html', concept=concept, error='no resources are this time :(')

    else:
        #not a valid concept
        error = concept+' is not a valid concept'
        return render_template('concept.html', concept=concept, error=error)

#add demo for questions
@app.route('/back/addquestion', methods=['POST'])
@flask_login.login_required
def backQuestion():
    ## code for a url constituting for multipe concepts ##
    url = request.form.get("url")
    question = request.form.get("question")

    #add url to users question
    #see if question doc exists
    #parse the https:// or http://
    url = re.sub('https://', '', url)
    url = re.sub('http://', '', url)
    url = re.sub('https://www.', '', url)
    url = re.sub('http://www.', '', url)
    url = re.sub('www.', '', url)
    httpLinkUrl = "http://"+url
    #recalibrate youtube url with /v/
    url = url.replace('watch?v=','v/')

    #title
    response = urllib2.urlopen(httpLinkUrl)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.html.head.title.text.strip()

    #linkObj for the question
    newLinkObj = {"url":url,"title":title}

    #check to see if userQuestionDoc is already inserted
    if userDb[flask_login.current_user.userName].find_one({'question':question}):
        #check to see if demo is already added
        userQuestionDoc = userDb[flask_login.current_user.userName].find_one({'question':question})
        #print url, userQuestionDoc['demos']

        #check to see if url has already been added
        if url in [d['url'] for d in userQuestionDoc['demos']]:
            #demo has already been added
            return 'already added'
        else:
            #add new demo
            userDb[flask_login.current_user.userName].update({'question':question},{'$push':{'demos':newLinkObj}})
            return 'added new'

    else:
        #user hasnt created a userQuestionDoc, create one and insert the url
        ##### recreate when creating other interview questionaires
        newUserQuestionDoc = {'question':question,'courses':['back end developer'],'demos':[newLinkObj],'lastVisit':datetime.datetime.utcnow()}

        #add course(s) the concept its part of ** could redo this more efficiently  **
        for courseName,courseList in courseConcepts.iteritems():
            if concept in courseList:
                newUserQuestionDoc['courses'].append(courseName)
        userDb[flask_login.current_user.userName].insert(newUserQuestionDoc)
        return 'added new'

    #print question, url
    #return url

@app.route('/adddemo/<concept>')
@flask_login.login_required
def adddemo(concept):
    return render_template('adddemo.html', concept=concept)

@app.route('/back/adddemo', methods=['POST'])
@flask_login.login_required
def backDemo():
    ## code for a url constituting for multipe concepts ##
    url = request.form.get("url")
    concept = request.form.get("concept")

    #parse the https:// or http://
    url = re.sub('https://', '', url)
    url = re.sub('http://', '', url)
    url = re.sub('https://www.', '', url)
    url = re.sub('http://www.', '', url)
    url = re.sub('www.', '', url)
    httpLinkUrl = "http://"+url
    #recalibrate youtube url with /v/
    url = url.replace('watch?v=','v/')

    #title
    response = urllib2.urlopen(httpLinkUrl)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.html.head.title.text.strip()

    #urlId
    urlId = re.sub(r"[^a-zA-Z_0-9]", '', url)
    newLinkObj = {"url":url,"urlId":urlId,"title":title}

    #check to see if userConceptDoc is already inserted
    if userDb[flask_login.current_user.userName].find_one({'concept':concept}):

        #check to see if demo is already added
        userConceptDoc = userDb[flask_login.current_user.userName].find_one({'concept':concept})

        if url in userConceptDoc['demos']:
            #demo has already been added
            flash('that demonstration has already been added')
            return redirect("adddemo/"+concept)
        else:
            #add new demo
            userDb[flask_login.current_user.userName].update({'concept':concept},{'$push':{'demos':newLinkObj}})
            #return 'yup'
            return redirect(url_for('home'))

    else:
        #user hasnt created a userConceptDoc, create one and insert the url
        newUserConceptDoc = {'concept':concept,'courses':[],'practice':[],'explanations':[],'demos':[newLinkObj],'lastVisit':datetime.datetime.utcnow()}

        #add course(s) the concept its part of ** could redo this more efficiently  **
        for courseName,courseList in courseConcepts.iteritems():
            if concept in courseList:
                newUserConceptDoc['courses'].append(courseName)
        userDb[flask_login.current_user.userName].insert(newUserConceptDoc)
        return redirect(url_for('home'))

@app.route('/addresource/<concept>')
@flask_login.login_required
def addresource(concept):
    return render_template('addresource.html', concept=concept)

@app.route('/back/addresource', methods=['POST'])
@flask_login.login_required
def backResource():
    ## code for a url constituting for multipe concepts ##
    url = request.form.get("url")
    tubeStart = request.form.get("youtubeStart")
    tubeEnd = request.form.get("youtubeEnd")
    concept = request.form.get("concept")

    #parse the https:// or http://
    url = re.sub('https://', '', url)
    url = re.sub('http://', '', url)
    url = re.sub('https://www.', '', url)
    url = re.sub('http://www.', '', url)
    url = re.sub('www.', '', url)
    httpLinkUrl = "http://"+url
    #recalibrate youtube url with /v/
    url = url.replace('watch?v=','v/')

    #check for proper tubetime syntax
    good = '0123456789:'
    if tubeStart.strip(good) != '' or tubeEnd.strip(good) != '':
        flash('youtube start points can only contain numbers and a :')
        return redirect("addresource/"+concept)
    #continue on, youtubeStart and End are valid
    else:
        #check to see if resource is added already
        conceptDoc = conceptsDb['conceptLinks'].find_one({"name":concept})
        searchResult = False
        #loop through the concepts explanation links
        if any(d['url'] == url for d in conceptDoc['explanations']):
            searchResult = True

        #add new url
        if searchResult == False:
            #uniquie url id
            urlId = re.sub(r"[^a-zA-Z_0-9]", '', url)

            #get title for webpage
            #check to see if its youtube and has time constraints
            tubeTimeUrl = None
            if tubeStart != '' or tubeEnd != '' and 'youtube' in url:
                tubeTimeUrl = tubeTimeConvert(tubeStart,tubeEnd,url)
            #try doing beautifulsoup stuff
            try:
                response = urllib2.urlopen(httpLinkUrl)
                html = response.read()
                soup = BeautifulSoup(html, 'html.parser')
                title = soup.html.head.title.text.strip()

                #conceptDoc = conceptsDb['conceptLinks'].find_one({"name":concept})
                linkObjs = conceptDoc['explanations']

                #if its the first linkObj in explanations
                if len(linkObjs) == 0:
                    #add link to explanations
                    newLinkObj = {"url":url,"urlId":urlId,"likes":1,"title":title}
                    if tubeTimeUrl != None:
                        newLinkObj['tubeTime'] = tubeTimeUrl
                        #add new newLinkObj to explanations
                        conceptsDb['conceptLinks'].update({"name":concept},{"$push":{"explanations":newLinkObj}})

                        #add to users likes
                        userDb[flask_login.current_user.userName].update({'userName':flask_login.current_user.userName},{'$push':{'liked':url}})
                        return redirect("concept/"+concept)
                    else:
                        #add new non-tubeTime newLinkObj to explanations
                        conceptsDb['conceptLinks'].update({"name":concept},{"$push":{"explanations":newLinkObj}})

                        #add to users likes
                        userDb[flask_login.current_user.userName].update({'userName':flask_login.current_user.userName},{'$push':{'liked':url}})
                        return redirect("concept/"+concept)

                else:
                    addedUrls = []
                    for linkObj in linkObjs:
                        addedUrls.append(linkObj['url'])

                    if url in addedUrls:
                        pass
                    else:
                        #add link to explanations
                        newLinkObj = {"url":url,"urlId":urlId,"likes":1,"title":title}

                        if tubeTimeUrl != None:
                            newLinkObj['tubeTime'] = tubeTimeUrl
                            #add new newLinkObj to explanations
                            conceptsDb['conceptLinks'].update({"name":concept},{"$push":{"explanations":newLinkObj}})

                            #add to users likes
                            userDb[flask_login.current_user.userName].update({'userName':flask_login.current_user.userName},{'$push':{'liked':url}})
                            return redirect("concept/"+concept)
                        else:
                            #add new non-tubeTime newLinkObj to explanations
                            conceptsDb['conceptLinks'].update({"name":concept},{"$push":{"explanations":newLinkObj}})

                            #add to users likes
                            userDb[flask_login.current_user.userName].update({'userName':flask_login.current_user.userName},{'$push':{'liked':url}})
                            return redirect("concept/"+concept)
            except:
                #add resource to 'add manually' list#
                flash('there was an error adding that resource, we will try adding the resource.  thanks for the suggestion!')
                return redirect("addresource/"+concept)
        else:
            flash('that resource has already been added')
            return redirect("addresource/"+concept)

@app.route('/addwhy/<course>')
@flask_login.login_required
def addwhy(course):
    return render_template('addwhy.html', course=course)

@app.route('/back/addwhy', methods=['POST'])
@flask_login.login_required
def backWhy():
    ## code for a url constituting for multipe concepts ##
    url = request.form.get("url")
    tubeStart = request.form.get("youtubeStart")
    tubeEnd = request.form.get("youtubeEnd")
    course = request.form.get("course")

    #parse the https:// or http://
    url = re.sub('https://', '', url)
    url = re.sub('http://', '', url)
    url = re.sub('https://www.', '', url)
    url = re.sub('http://www.', '', url)
    url = re.sub('www.', '', url)
    httpLinkUrl = "http://"+url
    #recalibrate youtube url with /v/
    url = url.replace('watch?v=','v/')

    #check for proper tubetime syntax
    good = '0123456789:'
    if tubeStart.strip(good) != '' or tubeEnd.strip(good) != '':
        flash('youtube start points can only contain numbers and a :')
        return redirect("addwhy/"+concept)

    #continue on, youtubeStart and End are valid
    else:
        #check to see if resource is added already
        courseDoc = conceptsDb['courses'].find_one({"name":course})
        searchResult = False
        if any(d['url'] == url for d in courseDoc['whyLinks']):
            searchResult = True

        #add new url
        if searchResult == False:
            #uniquie url id
            urlId = re.sub(r"[^a-zA-Z_0-9]", '', url)
            #check to see if its youtube and has time constraints
            tubeTimeUrl = None
            if tubeStart != '' or tubeEnd != '' and 'youtube' in url:
                tubeTimeUrl = tubeTimeConvert(tubeStart,tubeEnd,url)

            response = urllib2.urlopen(httpLinkUrl)
            html = response.read()
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.html.head.title.text.strip()

            courseDoc = conceptsDb['courses'].find_one({"name":course})
            linkObjs = courseDoc['whyLinks']
            newLinkObj = {"url":url,"urlId":urlId,"likes":1,"title":title,"reports":0,"date":datetime.datetime.utcnow()}

            addedUrls = []
            for linkObj in linkObjs:
                addedUrls.append(linkObj['url'])

            if url in addedUrls:
                pass
            else:
                #add link to explanations
                if tubeTimeUrl != None:
                    newLinkObj['tubeTime'] = tubeTimeUrl
                    #add new newLinkObj to explanations
                    conceptsDb['courses'].update({"name":course},{"$push":{"whyLinks":newLinkObj}})

                    #add to users likes
                    userDb[flask_login.current_user.userName].update({'userName':flask_login.current_user.userName},{'$push':{'liked':url}})
                    return redirect("course/"+course)
                else:
                    #add new non-tubeTime newLinkObj to explanations
                    conceptsDb['courses'].update({"name":course},{"$push":{"whyLinks":newLinkObj}})

                    #add to users likes
                    userDb[flask_login.current_user.userName].update({'userName':flask_login.current_user.userName},{'$push':{'liked':url}})
                    return redirect("course/"+course)
        #url has already been added
        else:
            flash('that resource has already been added')
            return redirect("addwhy/"+course)

@app.route('/back/report', methods=['POST'])
@flask_login.login_required
def report():
    url = request.form.get("url")
    courseOrConcept = request.form.get("type")

    if courseOrConcept == 'course':
        course = request.form.get("course")

        #update courselink is courseWhy
        if conceptsDb['courses'].update({'name':course, 'whyLinks.url':url},{'$inc':{"whyLinks.$.reports":1}}):
            #add to report
            return 'yup'
        else:
            #add to report
            return 'nope'

@app.route('/experience/<concept>')
@flask_login.login_required
def experience(concept):
    #get users explanations experience
    userConceptDoc = userDb[flask_login.current_user.userName].find_one({"concept":concept})
    #check to see if concept exists or user has experience with the concept
    if userConceptDoc:
        linksExpl = userConceptDoc['explanations']
        linksPract = userConceptDoc['practice']

        return render_template('experience.html', linksExpl=linksExpl, linksPract=linksPract, concept=concept, error=None )
    #invalid concept
    else:
        error = flask_login.current_user.firstName+' has not archived any experience with concept: '+concept
        return render_template('experience.html', concept=concept, error=error )

@app.route('/liked', methods=['POST'])
@flask_login.login_required
def liked():
    if request.method == 'POST':
        userDoc = userDb[flask_login.current_user.userName].find_one({"userName":flask_login.current_user.userName})
        userLiked = userDoc['liked']

        url = request.form.get("url")
        concept = request.form.get("concept")
        course = request.form.get("course")
        courseOrConcept = request.form.get("type")

        if courseOrConcept == 'concept':

            if url in userLiked:
                #remove url from usersLiked
                userDb[flask_login.current_user.userName].update({"userName":flask_login.current_user.userName},{"$pull":{"liked":url}})
                #decrement url likes
                conceptsDb['conceptLinks'].update({"name":concept, "explanations.url":url},{"$inc":{"explanations.$.likes":-1}})

                return 'successful removed'
            else:
                #increment url likes
                conceptsDb['conceptLinks'].update({"name":concept, "explanations.url":url},{"$inc":{"explanations.$.likes":1}})
                #add link to users likes
                userDb[flask_login.current_user.userName].update({"userName":flask_login.current_user.userName},{"$push":{"liked":url}})
                #print 'add url'
                return 'successful added'
        elif courseOrConcept == 'course':
            if url in userLiked:
                #remove url from usersLiked
                userDb[flask_login.current_user.userName].update({"userName":flask_login.current_user.userName},{"$pull":{"liked":url}})
                #decrement url likes
                conceptsDb['courses'].update({"name":course, "whyLinks.url":url},{"$inc":{"whyLinks.$.likes":-1}})

                return 'successful removed'
            else:
                #increment url likes
                conceptsDb['courses'].update({"name":course, "whyLinks.url":url},{"$inc":{"whyLinks.$.likes":1}})
                #add link to users likes
                userDb[flask_login.current_user.userName].update({"userName":flask_login.current_user.userName},{"$push":{"liked":url}})
                #print 'add url'
                return 'successful added'
    else:
        pass

@app.route('/archived', methods=['POST'])
@flask_login.login_required
def archived():
    if request.method == 'POST':
        url = request.form.get("url")
        concept = request.form.get("concept")

        userDoc = userDb[str(flask_login.current_user.userName)].find_one({"userName":flask_login.current_user.userName})
        userArchived = userDoc['archived']

        #get concepts linkObj
        conceptDoc = conceptsDb['conceptLinks'].find_one({'name':concept})
        linkObjs = conceptDoc['explanations']
        linkObj = None
        for obj in linkObjs:
            if obj['url'] == url:
                linkObj = obj
                linkObj.pop('likes',None)

        if url in userArchived:
            #remove url from users Archived
            userDb[flask_login.current_user.userName].update({"userName":flask_login.current_user.userName},{"$pull":{"archived":url}})
            #remove from users conceptDoc Archived list
            userDb[flask_login.current_user.userName].update({"concept":concept},{"$pull":{"explanations":{"url":url}}})

            return 'successful removed'
        else:
            #add link to users archived
            userDb[flask_login.current_user.userName].update({"userName":flask_login.current_user.userName},{"$push":{"archived":url}})

            #check to see if the user has a conceptDoc for the concept
            userConceptDoc = userDb[flask_login.current_user.userName].find_one({'concept':concept})
            if userConceptDoc:
                #add timestamp to linkObj
                linkObj['lastVisit'] = datetime.datetime.utcnow()
                #insert url into usersConceptDoc explanations
                userDb[flask_login.current_user.userName].update({"concept":concept},{"$push":{"explanations":linkObj}})
                return 'successful added'
            else:
                #create new concept doc
                newUserConceptDoc = {
                    'concept':concept,
                    'explanations':[linkObj],
                    'practice':[],
                    'demos':[],
                    'lastVisit':datetime.datetime.utcnow(),
                    'courses':[]
                }
                #add course(s) the concept its part of ** could redo this more efficiently  **
                for courseName,courseList in courseConcepts.iteritems():
                    if concept in courseList:
                        newUserConceptDoc['courses'].append(courseName)

                userDb[flask_login.current_user.userName].insert(newUserConceptDoc)
                return 'successful added'
    else:
        pass

@app.route('/import', methods=['GET'])
@flask_login.login_required
def imports():
    if request.method == 'GET':
        userName = flask_login.current_user.userName
        imported = []
        provList = ['khan','codeWars','codeCad']
        providers = [{'name':'Khan Academy','varName':'khan'},{'name':'Codewars','varName':'codeWars'},{'name':'Codecademy','varName':'codeCad'}]

        #seperate already imported and non-imported providers
        userDoc = userDb[userName].find_one({'userName':userName})
        for imprt in userDoc['imported']:
            if imprt['provider'] in provList:
                provObj = [d for d in providers if d.get('varName') == imprt['provider']][0]
                imported.append(provObj)
                #remove from providers
                providers[:] = [d for d in providers if d.get('varName') != imprt['provider']]

        return render_template('import2.html',imported=imported,providers=providers)

@app.route('/importProvider')
@flask_login.login_required
def importProvider():
    provider = request.args.get("provider")
    if provider == 'khan':
        return khan(flask_login.current_user.userName)
    elif provider == 'codeWars':
        #add codeWars to users imported, if not already
        userName = str(flask_login.current_user.userName)
        imported = userDb[userName].find_one({'userName':userName})['imported']
        #providers username
        provUsername = request.args.get("username")
        if filter(lambda prov: prov['provider'] == 'codeWars', imported) == []:
            #push codeWars into imported, might throw error for other providers since other imports are dictTypeObjs
            provDoc = {'provider':'codeWars','userName':provUsername}
            userDb[userName].update({'userName':userName}, {'$push':{'imported':provDoc}})

        return codewars(flask_login.current_user.userName, provUsername)
    elif provider == 'codeCad':
        #add codeWars to users imported, if not already
        userName = str(flask_login.current_user.userName)
        imported = userDb[userName].find_one({'userName':userName})['imported']
        #providers username
        provUsername = request.args.get("username")
        #search if codeCad has been added to usersDoc['imported']
        if filter(lambda prov: prov['provider'] == 'codeCad', imported) == []:
            #push codeWars into imported, might throw error for other providers since other imports are dictTypeObjs
            provDoc = {'provider':'codeCad','userName':provUsername}
            userDb[userName].update({'userName':userName}, {'$push':{'imported':provDoc}})
        #else reupdate the new codeCad userName
        else:
            userDb[userName].update({'userName':userName, 'imported.provider': 'codeCad'}, {'$set':{'imported.$.userName':provUsername}})

        return codecad(flask_login.current_user.userName, provUsername)

@app.route('/import/username')
@flask_login.login_required
def getUserNameImport():
    #get variable provider
    provider = request.args.get("provider")
    #provider varName and regName map
    nameMap = {'codeWars':'Codewars','codeCad':'Codecademy'}
    regName = None
    if provider in nameMap.keys():
        regName = nameMap[provider]
    return render_template('getUserName.html',provider=provider,regName=regName)

@app.route('/profile/<userName>')
def profile(userName):
    #get userDoc and display users information
    userCol = userDb[userName]
    firstName = userCol.find_one({'userName':userName})['firstName']

    #grab all of users conceptLinkObjs
    userConceptDocs = userCol.find({"concept":{'$exists': True}})
    userQuestionDocs = userCol.find({"question":{'$exists': True}})
    #userDocs = userConceptDocs + userQuestionDocs
    conceptObjs = []
    #get users courses and concepts
    courses = {}

    #for conceptDoc in userConceptDocs:
    for conceptDoc in chain(userConceptDocs,userQuestionDocs):
        #get users courses and build courses dict with the keys(course names) and values (list of concepts in course)
        for course in conceptDoc['courses']:
            #print course
            if course not in courses.keys():
                courses[course] = []

        conceptObjs.append(conceptDoc)
        #get users concepts in their courses
        for course, courseList in courseConcepts.iteritems():
            try:
                if conceptDoc['concept'] in courseList:
                    #print conceptDoc['concept'], course
                    courses[course].append(conceptDoc)
            except:
                continue
            try:
                if conceptDoc['question'] in courseList:
                    #print conceptDoc['concept'], course
                    courses[course].append(conceptDoc)
            except:
                continue
    #get users recent concepts
    conceptObjs.sort(key=lambda item:item['lastVisit'], reverse=True)

    return render_template('profile3.html', courses=courses, conceptObjs=conceptObjs,firstName=firstName,userName=userName)

@app.route('/<userName>/concept/<concept>')
def usersConcept(userName,concept):
    conceptDoc = userDb[userName].find_one({'concept':concept})
    expllinks = conceptDoc['explanations']
    practlinks = conceptDoc['practice']
    demolinks = conceptDoc['demos']

    return render_template('userConcept.html', concept=concept, expllinks=expllinks,practlinks=practlinks,demolinks=demolinks)

@app.route('/requesttoken')
@flask_login.login_required
def requesttoken():
    userName = flask_login.current_user.userName
    #callback for service, get access token and store it
    provider = request.args.get('provider')
    oauth_token_secret = request.args.get('oauth_token_secret')
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_token = request.args.get('oauth_token')

    request_token = OAuthToken(oauth_token, oauth_token_secret)
    request_token.set_verifier(oauth_verifier)

    if provider == 'khan':
        consumer = OAuthConsumer('9YrRjqYAjMWWF7ZP','Y45DZt2vCGV9w8W2')

        oauth_request = OAuthRequest.from_consumer_and_token(
                consumer,
                token=request_token,
                verifier=request_token.verifier,
                http_url="https://www.khanacademy.org/api/auth/access_token"
                )

        oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, request_token)

        resp = urllib2.urlopen(oauth_request.to_url())
        accessToken = resp.read()
        #store access token
        #check to see if its first time importing or refreshing the token
        #refresh a token
        if userDb[userName].find_one({'userName':userName,'imported.site':provider}):
            userDb[userName].update({'userName':userName,'imported.site':provider},{'$set':{'imported.$.accessToken':accessToken}})
            #return redirect(url_for('imports'))
            return khan(userName)
        #first time importing
        else:
            #make /api/v1/user call to get users khan username
            access_token = OAuthToken.from_string(accessToken)
            oauth_request = OAuthRequest.from_consumer_and_token(
                    consumer,
                    token=access_token,
                    http_url="https://www.khanacademy.org/api/v1/user"
                    )
            oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, access_token)

            resp = urllib2.urlopen(oauth_request.to_url())
            response = resp.read()
            respJson = json.loads(response)
            khanUsername = respJson['student_summary']['username']

            doc = {'provider':provider,'accessToken':accessToken,'providerUsername':khanUsername}
            userDb[userName].update({'userName':userName},{'$push':{'imported':doc}})
            #return redirect(url_for('imports'))
            return khan(userName)

@app.route('/oauth2')
@flask_login.login_required
def oauth2():
    userName = flask_login.current_user.userName
    client_id = "227G4B"
    client_secret = "91d95c06c8d0558a0509c4f844696280"
    concat = client_id+":"+client_secret
    url = 'https://api.fitbit.com/oauth2/token'
    base = base64.b64encode(concat)
    code = request.args.get('code')

    headers = {"Authorization":"Basic " + base,"Content-Type":"application/x-www-form-urlencoded"}
    payload = {'code': code,
            'redirect_uri' : 'https://brainswole.com/oauth2',
            'grant_type': 'authorization_code',
            'client_id':'227G4B'}
    r = requests.post(url, params=payload,headers=headers)
    access_token = r.json()['access_token']
    refresh_token = r.json()['refresh_token']
    #store the tokens
    if userDb[userName].find_one({'userName':userName,'imported.provider':'fitbit'}):
        userDb[userName].update({'userName':userName,'imported.provider':'fitbit'},{'$set':{'imported.$.accessToken':access_token,'imported.$.refreshToken':refresh_token}})
    else:
        doc = {'provider':'fitbit','accessToken':access_token,'refreshToken':refresh_token}
        userDb[userName].update({'userName':userName},{'$push':{'imported':doc}})

    return redirect(url_for('importdata'))

@app.route('/getAccessToken')
@flask_login.login_required
def getAccessToken():
    #provider = request.args.get('provider')
    consumer = OAuthConsumer('9YrRjqYAjMWWF7ZP','Y45DZt2vCGV9w8W2')
    callback = 'https://brainswole.com/requesttoken'
    oauth_request = OAuthRequest.from_consumer_and_token(
            consumer,
            callback=callback,
            http_url="https://www.khanacademy.org/api/auth/request_token"
            )

    oauth_request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), consumer, None)
    return redirect(oauth_request.to_url())

@app.route('/importdata', methods=['GET','POST'])
@flask_login.login_required
def importdata():
    if request.method == 'GET':
        userName = flask_login.current_user.userName
        provList = ['khan']
        providers = [{'name':'Khan Academy','varName':'khan'}]
        imported = []
        userDoc = userDb[userName].find_one({'userName':userName})
        for imprt in userDoc['imported']:
            if imprt['provider'] in provList:
                provObj = [d for d in providers if d.get('varName') == imprt['provider']][0]
                imported.append(provObj)
                #remove from providers
                providers[:] = [d for d in providers if d.get('varName') != imprt['provider']]
        return render_template('importdata.html',providers=providers,imported=imported)

@app.route('/testtube/<vidId>')
@flask_login.login_required
def testtube(vidId):
    vidDoc = tubeTestDb['problems'].find_one({'vidId':vidId})
    userVidDoc = userDb[flask_login.current_user.userName].find_one({'type':'testTube','vidId':vidId})
    #if first time user visits this videos questions
    if userVidDoc == None:
        #create userVidDoc
        newUserVidDoc = {'vidId':vidId,'type':'testTube','probs':[]}
        userDb[flask_login.current_user.userName].insert(newUserVidDoc)
    userVidDoc = userDb[flask_login.current_user.userName].find_one({'type':'testTube','vidId':vidId})

    #get new finished prob
    userFinishedProbs = userVidDoc['probs']
    finishedprobIds = [d['id'] for d in userFinishedProbs]
    #remove finished probs
    probs = vidDoc['probs']
    for prob in probs:
        for userProb in userFinishedProbs:
            if prob['id'] in userProb.values():
                #remove that prob
                probs[:] = [d for d in probs if d.get('id') not in finishedprobIds]
                #pass
    if probs == []:
        prob = vidDoc['probs'][0]
        return render_template('testtube.html',prob=prob,vidId=vidId)
    else:
        prob = probs[0]
        return render_template('testtube.html',prob=prob,vidId=vidId)

@app.route('/testtube/back/v1', methods=['POST'])
@flask_login.login_required
def testtubeback():

    vidId = request.form.get("vidId")
    probId = request.form.get("probId")
    probType = request.form.get("probType")

    userVidDoc = userDb[flask_login.current_user.userName].find_one({'type':'testTube','vidId':vidId})

    vidDoc = tubeTestDb['problems'].find_one({'vidId':vidId})
    probObj = (item for item in vidDoc['probs'] if item["id"] == probId).next()
    #return 'yup'

    if probType == 'resp':
        response = request.form.get("resp")
        userVidDoc = userDb[flask_login.current_user.userName].find_one({'type':'testTube','vidId':vidId})
        #check to see if prob has already been done
        userProbObj = None
        try:
            userProbObj = (prob for prob in userVidDoc['probs'] if prob["id"] == probId).next()
        except:
            pass
        if userProbObj == None:
            #add resp to probObj
            probObj['resp'] = response

            userDb[flask_login.current_user.userName].update({'type':'testTube','vidId':vidId},{'$push':{'probs':probObj}})
            return 'added response!'
        else:
            #update response and set
            return 'would do but didnt update set'

    if probType == 'freeResp':
        response = request.form.get("resp")
        userVidDoc = userDb[flask_login.current_user.userName].find_one({'type':'testTube','vidId':vidId})
        #check to see if prob has already been done
        userProbObj = None
        try:
            userProbObj = (prob for prob in userVidDoc['probs'] if prob["id"] == probId).next()
        except:
            pass
        if userProbObj == None:
            #add resp to probObj
            probObj['correct'] = True

            userDb[flask_login.current_user.userName].update({'type':'testTube','vidId':vidId},{'$push':{'probs':probObj}})
            return 'added response!'
        else:
            #update response and set
            return 'would do but didnt update set'

    '''
    #find and return a new problem
    vidDoc = tubeTestDb['problems'].find_one({'vidId':vidId})
    probs = vidDoc['probs']
    prob = probs[2]
    return render_template('testtube.html',prob=prob)
    '''

@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(e)
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    app.logger.error(e)
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug = True)
