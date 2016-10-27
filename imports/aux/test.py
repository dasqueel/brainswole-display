from pymongo import MongoClient

#connect to mongo
client = MongoClient('localhost')
conceptsDb = client.Concepts
userDb = client.ArchiveUsers

userDb['neilbarduson'].update({'concept':'determinant','explanations.url': {'$ne': 'youtube.com/watch?v=H9BWRYJNIsdfv4'}},{'$push':{'explanations':{'test':1,'test2':2,'url':'youtube.com/watch?v=H9BWRYJNIsdfv4'}}})

'''
db.coll.update(
    {_id: id, 'profile_set.name': {$ne: 'nick'}}, 
    {$push: {profile_set: {'name': 'nick', 'options': 2}}})
'''