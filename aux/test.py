import requests
import pprint
import json

pp = pprint.PrettyPrinter(indent=4)

'''
url = 'http://www.khanacademy.org/api/v1/exercises'

r = requests.get(url)

resp = r.json()
'''

# Reading data back
with open('khan.json', 'r') as f:
	data = json.load(f)
	exers = data['exers']
	with open("khan.txt",'w') as openfile:
	    openfile.write("\n".join(map(str,exers)))