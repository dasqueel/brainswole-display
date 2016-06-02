def tubeTimeConvert(tubeStart,tubeEnd,url):
	startMins = int(tubeStart.split(':')[0])
	startSecs = int(tubeStart.split(':')[1])
	endMins = int(tubeEnd.split(':')[0])
	endSecs = int(tubeEnd.split(':')[1])
	startTotal = startMins*60 + startSecs
	endTotal = endMins*60 + endSecs

	return url+'&start='+str(startTotal)+'&end='+str(endTotal)