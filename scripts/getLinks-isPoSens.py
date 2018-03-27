########################################
#
#get containsLink predicates for tweetIDs listed as isPossiblySensitive 
#in inference-intersect file as well as listed as malicious
#
#usage: getLinks-isPoSens.py -i <idsList> -e <evidenceFile> -o <outputFile> > <location of another output file, in the form "containsLink(tweetId, link)">
#
#INPUT: list of IDs from isPossiblySensitive predicates in intersect output file
#		Location of list of MentionsList,
#		Location of file to store the links in "containsLink()"
#OUTPUT: links in "containsLink()" without predicate,
#		links in  "containsLink()" with predicate
#
########################################

import sys, getopt #for accepting command line args
import re   #regular expressions
import os	#for I/O
from string import capwords #to sort strings
import json #to parse json

reload(sys)
sys.setdefaultencoding('utf-8') #to resolve error for ascii encoding

#def getLinks(record):


def getPredicateIds(record):
	tokens = record.split('containsLink(')[1]
	if ',' in tokens:
		tokens = tokens.split(',')
		tokens[0] = tokens[0] #tweet ID
		tokens[1] = tokens[1].split('\"')[1] #link
		return tokens#.strip('\n')



def getLinks(idsList, evidenceFile, outputFile):
	tweetIds = []
	#get list of IDs from IDs list
	with open(idsList, 'r') as lstIds:
		for ids in lstIds:
			tweetIds.append(ids.strip("\n"))
	count = 0 
	#print tweetIds

	#get the containsLink predicates from evidence file
	with open(evidenceFile, 'r') as evdf:
		containsLinkList = []
		for line in evdf:
			if line.startswith('containsLink'):
				containsLinkList.append(line.strip("\n"))

	containsLinkList1 = set(containsLinkList)
	arrToWrite = []
	for ids in tweetIds: #from IDsList
		for link in containsLinkList: #from evidence file
			rowArr = getPredicateIds(link)
			if ids == rowArr[0]:
				print link
				arrToWrite.append(rowArr[1])

	with open(outputFile, "a+") as outfile:
		for a in arrToWrite:
			outfile.write(a)
			outfile.write("\n")

def main(argv):
	try:
		opts, args = getopt.getopt(argv, "hi:e:o:", ["idsList= ", "evidenceFile=", "outputFile="])
	except getopt.GetoptError:	
		print 'usage: getLinks-isPoSens.py -i <idsList> -e <evidenceFile> -o <outputFile> > <location of another output file>'
		sys.exit(2)
	for opt, args in opts:
		if opt == '-h':
			print 'getLinks-isPoSens.py -i <idsList> -e <evidenceFile> -o <outputFile> > <location of another output file>'
			sys.exit()
		elif opt in ("-i", "--idsList"):
			idsList = args
		elif opt in ("-e", "--evidenceFile"):
			evidenceFile = args
		elif opt in ("-o", "--outputFile"):
			outputFile = args
	getLinks(idsList, evidenceFile, outputFile)
	
if __name__ == "__main__":
   main(sys.argv[1:])