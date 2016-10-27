import requests
import json

slug = 'alg-matrices'

r = requests.get('http://www.khanacademy.org/api/v1/topic/'+slug+'/videos')

print r.status_code
#print r.text

for i in r.json():
	print i['title'],i['url']
'''
with open("topictree.txt", "w") as outfile:
    json.dump(r.json(), outfile, indent=4)
'''