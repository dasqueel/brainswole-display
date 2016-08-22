import requests
from bs4 import BeautifulSoup


#print soup.prettify()
skills = []
users = ['dasqueel','ericadu','ryan','artursapek','daniellakisza','ysmg','jackjackjackj','andresiga','ccho1']

for user in users:
	url = 'http://codecademy.com/'+user

	r = requests.get(url)

	# Turn the HTML into a Beautiful Soup object
	soup = BeautifulSoup(r.text, 'html.parser')


	for row in soup.find_all('h5'):
		try:
			if 'text--ellipsis' in row.attrs['class']:
				#print row.text
				if row.text not in skills:
					skills.append(row.text)
		except:
			pass

print skills