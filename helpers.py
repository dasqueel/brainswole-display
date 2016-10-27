from bs4 import BeautifulSoup
import datetime
import re
import urllib2

#return explantions dict as url as input
## later update function if its a tube time situation ##
## maybe dont have to do beautiful soup call on khanacademy video urls?? ##
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