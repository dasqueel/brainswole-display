import json
from pprint import pprint

with open('topictree.txt') as data_file:
    data = json.load(data_file)


for i in data['children']:
	print i['slug']['math']