#takes a youtube url along with start and stop times with syntax of xx:xx and returns url with starting and stopping
def tubeTimeConvert(tubeStart,tubeEnd,url):
	if tubeStart and tubeEnd != '':
		startMins = int(tubeStart.split(':')[0])
		startSecs = int(tubeStart.split(':')[1])
		endMins = int(tubeEnd.split(':')[0])
		endSecs = int(tubeEnd.split(':')[1])
		startTotal = startMins*60 + startSecs
		endTotal = endMins*60 + endSecs

		return url+'?start='+str(startTotal)+'&end='+str(endTotal)

	elif tubeStart == '':
		endMins = int(tubeEnd.split(':')[0])
		endSecs = int(tubeEnd.split(':')[1])
		endTotal = endMins*60 + endSecs

		return url+'?end='+str(endTotal)

	else:
		startMins = int(tubeStart.split(':')[0])
		startSecs = int(tubeStart.split(':')[1])
		startTotal = startMins*60 + startSecs

		return url+'?start='+str(startTotal)


#getting a concepts courses it is in, for when creating a new userConceptDoc