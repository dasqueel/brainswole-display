from conceptMap import *


#function to add khan resource links to khanMap
def insertKhanResource(concept,resourceList):
	if concept in khanMap.keys():
		print concept+' already in khanMap'
		#add resource list
		for resource in resourceList:
			if resource not in khanMap[concept]:
				khanMap[concept].append(resource)
				print 'added '+resource
	else:
		#create new concept key
		khanMap[concept] = resourceList
		print 'created '+concept+' key and its resource list'

#insertKhanResource('empirical rule',['empirical_rule'])