#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Anas Katib July 26, 2016
#
# Usage ./evaluate-urls.py <evdb.db> <inference_outputfile>
#
#	Reads predicates from an input file (inference_outputfile) and expands the urls if shortened.
#	Then it checks if these urls are also considered by urlblacklist.com[disabled]
#	and VirusTotal[enabled]
#	Notes:
#		* Expands urls within the 'malicious' predicate	e.g. malicious("https://short.co/example")
#
#
#	Performs a four-level matching using VirusTotal:
#		Level 1: Direct original url search.
#		Level 2: If original url is shortened, expand url and do a direct search using expanded url.
#		Level 3: Search using expanded url resolved ip.
#		Level 4: Search using original (shortend) url resolved ip.
#


import sys, getopt
import requests
import os, re
import socket
from datetime import datetime as dt
from sets import Set
from time import gmtime, strftime
def print_err(*args):
    sys.stderr.write(' '.join(map(str,args)) + '\n')

######################################
# Ref: http://stackoverflow.com/questions/4201062/how-can-i-unshorten-a-url-using-python/28918160
# By: GermainZ

def expand_url(url):
	try:
		session = requests.Session()  # so connections are recycled
		resp = session.head(url, allow_redirects=True,timeout=30)
		return resp.url
	except requests.exceptions.TooManyRedirects as e1:
		 print("EXCEPTION: TOO MANY REDIRECTS FOR "+url)
	except requests.exceptions.ConnectionError as e2:
		 print("EXCEPTION: CONNECTION ERROR FOR "+url)
	except:
 		er = sys.exc_info()[0]
		print_err("ERROR: PROCESSING "+url)
		print_err(er)
		print("EXCEPTION FOR "+url)
	return url

# Ref: http://stackoverflow.com/questions/14625693/find-http-and-or-www-and-strip-from-domain-leaving-domain-com
# By: sidi
# Modified by Anas Katib
def rmv_prefix(url):
	link = url.replace("http://","")
	link = link.replace("https://","")
	if link.startswith("www."):
    		link = link.replace("www.", "",1)
	return link

# Ref: http://stackoverflow.com/questions/1863236/grep-r-in-python

def file_match(fname, pat):
    matched = []
    try:
        f = open(fname, "rt")
    except IOError:
        return
    for i, line in enumerate(f):
        if pat.search(line):
            #print "%s: %i: %s" % (fname, i+1, line),
            matched.append(("%s: %i: %s" % (fname, i+1, line)).strip())
    f.close()
    return matched


def grep(dir_name, s_pat):
    matches = []
    pat = re.compile(s_pat)
    for dirpath, dirnames, filenames in os.walk(dir_name):
        for fname in filenames:
            fullname = os.path.join(dirpath, fname)
            matches = matches + file_match(fullname, pat)
    return matches

######################################
# Ref: https://github.com/clairmont32/VT-Domain-Scanner/blob/master/VT_Domain_Scanner.py
# By: Matthew Clairmont
#_author__ = 'Matthew Clairmont'
#_email__ = 'matthew.clairmont1@gmail.com'
#_version__ = '1.0'
#_date__ = '07/01/2015'

#Designed for Python 2.7, this is the initial creation of this script with no error checking. Any errors may be related to incorrect API key, or bad domain formatting in input file. Updates will be provided in intervals over the next few months.
#VT Domain Scanner takes a file of domains, submits them to the Virus Total domain scanning API and outputs the domain and AV hits to a text file.

import urllib
import urllib2
import time
import json as simplejson

#submits domain to VT to generate a fresh report for DomainReportReader()
def DomainScanner(domain):
    url = 'https://www.virustotal.com/vtapi/v2/url/scan'

    parameters = {'url': domain,
                  'apikey': 'afc'}

    try:
        #URL encoding and submission
        data = urllib.urlencode(parameters)
        req = urllib2.Request(url, data)
        response = urllib2.urlopen(req)
        #print_err('Domain scanned successfully ')
    except Exception as Er:
        print_err("DomainScanner Problem: "+domain)
        print_err(Er)
    #for URL scan report debugging only
    #print_err(response)

def DomainReportReader(domain, shorturl,print_type):
    #sleep 25 to control requests/min to API. Public APIs only allow for 4/min threshold, you WILL get a warning email to the owner of the account if you exceed this limit. Private API allows for tiered levels of queries/second.
    time.sleep(25)

    #this is the VT url scan api link
    url = 'https://www.virustotal.com/vtapi/v2/url/report'

    #API parameters
    parameters = {'resource': domain,
                  'apikey': 'e2afc'}
    json = "none"
    #URL encoding and submission
    try:
    	data = urllib.urlencode(parameters)
    	req = urllib2.Request(url, data)
    	response = urllib2.urlopen(req)
    	json = response.read()
    except Exception as Er:
    	print_err("DomainReportReader Attempt 1: ERROR")
	print_err(Er)
	json=""


    if len(json) < 1:
	print_err("Sleeping..")
	time.sleep(70)
	try:
    		response = urllib2.urlopen(req)
    		json = response.read()
		#print_err("DomainReportReader Attempt 2: SUCCESS")
	except Exception as Er:
		print_err("DomainReportReader Attempt 2: FAIL")
		print_err(Er)
		json=""

	if len(json) < 1:
		print_err("PROBLEM PROCESSING: "+shorturl+" -> "+domain)
		return -1
    try:
    	#stores json response to variable for calling specific sections in the next block of code
    	response_dict = simplejson.loads(json)
    except ValueError as e:
		print_err("JSON ERROR PROCESSING "+ shorturl +" "+str(e))
		return -1
    except:
                er = sys.exc_info()[0]
		print_err("ERROR PROCESSING "+shorturl+" "+str(er))
		return -1
    #pull critical snippets from report and convert to strings for output formatting
    permalink = response_dict.get('permalink', "")
    scanDate = response_dict.get('scan_date', strftime("%Y-%m-%d %H:%M:%S", gmtime()))

    avHit = response_dict.get('positives', "")
    total = response_dict.get('total', "")

    #convert numbers to string for output formatting
    avHit = str(avHit)
    total = str(total)
    ratio = avHit + '/' + total

    #format results and write to screent
    #resultsString = (domain + ' was scanned on ' + scanDate + ' and contained a ' + ratio + ' AV detection ratio. See full report in results file for further information')
    #print(resultsString)
    resultsOutput = None
    if len(avHit) < 1:
    	print_err("RESPONSE ERROR: "+str(json))
	resultsOutput = scanDate + '\t'  + '-/-' + '\t\t' + str(shorturl)
	if print_type == 'err':
    		#print(resultsOutput)
    		print (">>>>>>>>>>>>>>")
    else:
	resultsOutput = str(scanDate) + '\t'  + ratio + '\t\t' + str(shorturl)
	if int(avHit) > 0:
    		#print(resultsOutput)
    		print (">>>>>>>>>>>>>>")
		return 1
    	else:
		if print_type == 'err' or print_type == 'neg':
    			#print(resultsOutput)
    			print (">>>>>>>>>>>>>>")
		return 0
    # possibly resource does not exist in the dataset
    return -1


# Ref: https://github.com/clairmont32/VirusTotal-IP-Scanner/blob/VirusTotal_IP_Scanner_1.0/VT_IP_Scanner.py
#__author__ = 'Matthew Clairmont'
#__version__= '1.0'

"""
Submits single IP entry to VT IP scanner API and returns total AV detected file results
With public API only 4 requests/min are allowed. You will get an email registered to the account
if you repeatedly violate this threshold
"""

def IpScanner(ipaddress,shorturl,print_type):
    	time.sleep(20)
	#Virus total API info
	url = 'https://www.virustotal.com/vtapi/v2/ip-address/report'
	parameters = {'ip': ipaddress,'apikey': 'e2afc'}
    	response = ''
    	try:
	    #URL encoding, IP submission, and json response storage
	    response = urllib.urlopen('%s?%s' % (url, urllib.urlencode(parameters))).read()
    	except Exception as Er:
        	print_err("IpScanner Problem: "+ipaddress+" "+shorturl)
        	print_err(Er)

	if len (response) < 1:
		print_err("RESPONSE ERROR: "+str(json))
        	resultsOutput = str(scanDate) + '\t'  + '-/-' + '\t\t' + str(shorturl)
        	#print(resultsOutput)
        	print (">>>>>>>>>>>>>>")
        	return -1

	response_dict = simplejson.loads(response)

	#harvest important info from JSON response
	positiveResults, totalResults, scanDate = count_detected(response_dict)

	#convert results to string for output formatting
	resultsOutput = scanDate + '\t'  + str(positiveResults) + '/' + str(totalResults) + '\t\t' + shorturl+'\t'+ipaddress
	if positiveResults > 0:
		#print(resultsOutput)
		print (">>>>>>>>>>>>>>")
		return 1
	elif positiveResults == 0:
		if print_type == 'neg' or print_type == 'all':
			#print(resultsOutput)
			print (">>>>>>>>>>>>>>")
		return 0
	return -1

def count_detected(jOb):
	positiveResults = totalResults = 0
	recent_date = dt.strptime("1990-01-30 13:59:59", "%Y-%m-%d %H:%M:%S")
        try:
                for key in jOb.keys():
		  if key.startswith("detected_"):
			for x in jOb[key]:
                        	positiveResults = positiveResults + x.get("positives")
                        	totalResults = totalResults + x.get("total")
				this_date = None
				if 'date' in x.keys():
					this_date = dt.strptime(x.get("date"), "%Y-%m-%d %H:%M:%S")
				elif 'scan_date' in x.keys():
					this_date = dt.strptime(x.get("scan_date"), "%Y-%m-%d %H:%M:%S")
				if this_date != None:
					if recent_date < this_date:
						recent_date = this_date
        except TypeError as e: #if no results found program throws a TypeError
                print_err ("NO RESULTS")
		print_err (e)
		positiveResults = totalResults = -1
	return positiveResults, totalResults, str(recent_date)

######################################

def check_dg_urlblacklist(mal_dom,  mal_url, originals):
	print("Matching links with url blacklist..")
	print "Trying exact urls..",
	mfound = False
	dfound = False
	for u in Set(mal_url):
		urls = grep("/etc/dansguardian/blacklists/","^"+u)
		if len(urls) > 0:
			print ('\n\tMATCHED "'+u+'"  ORIGINALLY "'+originals[u]+'"')
			mfound = True
			for url in urls:
				print("\t    "+url)
	if(mfound == False):
		print " no match!"
	print "Trying domains..",
	for d in Set(mal_dom):
		domains = grep("/etc/dansguardian/blacklists/","^"+d)
		if len(domains) > 0:
			print ('\n\tMATCHED "'+d+'"  ORIGINALLY "'+originals[d]+'"')
			dfound = True
			for domain in domains:
				print("\t    "+domain)

	if(dfound == False):
		print " no match!"

def extract_domain (url):
	#assumes no http(s) or www. in url
	domain = url.split("//")[-1].split("/")[0]
	if ':' in domain:
		domain = domain.split(':')[0]
	return domain
def main(args):
	print ("Reading evidence from: "+args[0])
	db = open(args[0])
	truePos = 0
	original = []
    	for line in db:
		if 'malicious' in line:
	        	link = line.split("(")[1].strip()
                	link = link[1:-2]
			original.append(link)
			truePos += 1
	db.close()
	db_details = "TOTAL DB EVIDENCE: "+str(len(original))

 	filename  = args[1]
	f = open(filename)
	malicious = {}
	mal_count = 0
        minProb = 0.8000
	level_matches ={1:None,2:None,3:None,4:None}
	print ("Parsing malicious links from: "+filename)
	lineCount = 0
    	for line in f:
		lineCount += 1
		consider = False
		if 'malicious' in line:
		    probability = line[0:6]
                    # if there is marginal probability
                    if probability.replace('.','',1).isdigit():
                    	probability = float(probability)
                    	if probability >= minProb:
                        	consider = True
                    else:
                        consider = True
		    if consider:
			if "(" in line:
				link = line.split("(")[1].strip()
				link = link[1:-2]
			if len(link) > 0 and link not in malicious.keys():
			    if link not in original:
				mal_count += 1
				short_url = rmv_prefix(link)
				short_domain =  extract_domain(short_url)
				short_ip = ""

                                try:
                                        short_ip = socket.gethostbyname(short_domain)
                                except:
                                        print_err("HOSTNAME IP ERROR: "+short_domain)
                                        short_ip = short_domain
				url    = expand_url(link)
				url    = rmv_prefix(url)
				domain = extract_domain(url)
				ip = ""

				try:
					ip = socket.gethostbyname(domain)
				except:
					print_err("HOSTNAME IP ERROR: "+domain)
					ip = domain

				malicious[link] = {'url':url, 'domain':domain,'ip':ip, 'done':None,'sip':short_ip}
			else:
				print_err("Ignoring Line:"+str(lineCount))
	f.close()

	print("Parsing Complete.")
	print("Checking urls with VirusTotal..")
	print_err("\nChecking urls with VirusTotal..")
	# check_dg_urlblacklist(mal_dom,  mal_url, originals) //code has changed!

	process_count = match_count = no_match_count = error_count  = 0
	# check original urls with VirusTotal
	for orig_url in malicious.keys():
		print_err("Checking orignal URL "+orig_url)
		process_count += 1
		DomainScanner(orig_url)
    		isMalicious = DomainReportReader(orig_url,orig_url,'pos')
		# record every status (even errors)
		malicious[orig_url]['done'] = isMalicious
		if   isMalicious ==  1:
			truePos  +=  1
			match_count += 1
			print ('LEVEL 1 MATCH: '+orig_url)
			# no further processing needed, delete it
			del malicious[orig_url]
		elif isMalicious == 0:
			no_match_count += 1
		elif isMalicious == -1:
			error_count += 1
		else:
			print_err("Unknown isMalicious! "+orig_url)

	print("Done.")
	print_err("\nLEVEL 1:")
       	print_err("PROCESSED:   "+str(process_count))
        print_err("MATCHED:     "+str(match_count))
        print_err("NOT MATCHED: "+str(no_match_count))
        print_err("ERORR:       "+str(error_count))
	level_matches[1] = str(match_count)

	process_count = match_count = no_match_count = error_count  = 0
	print("Checking expanded url with VirusTotal..")
	print_err("\nChecking with expanded urls..")
	# check full urls with VirusTotal
	for orig_url in malicious.keys():
		full_url = malicious[orig_url]['url']
		# if expanded link is not the same as the original
		if full_url[0:-1] not in orig_url:
			process_count += 1
			print_err("Checking expanded URL for "+orig_url+" : "+full_url)
			DomainScanner(orig_url)
    			isMalicious = DomainReportReader(full_url,orig_url,'pos')

			# record statuses except errors
			if isMalicious in [0,1]:
				malicious[orig_url]['done'] = isMalicious

			if   isMalicious ==  1:
				truePos  +=  1
				match_count += 1
				print ('LEVEL 2 MATCH: '+orig_url)#+' : '+ full_url)#>>>>>>>>>>>>>>
				# no further processing needed, delete it
				del malicious[orig_url]
			elif isMalicious == 0:
				no_match_count += 1
			elif isMalicious == -1:
				error_count += 1
			else:
				print_err("Unknown isMalicious! "+orig_url)


	print("Done.")
	print_err("\nLEVEL 2:")
       	print_err("PROCESSED:   "+str(process_count))
        print_err("MATCHED:     "+str(match_count))
        print_err("NOT MATCHED: "+str(no_match_count))
        print_err("ERORR:       "+str(error_count))

	level_matches[2] = str(match_count)

	process_count = match_count = no_match_count = error_count  = 0
	# recheck with ip addresses
	print_err("\nChecking with expanded url ip addresses..")
	print("Checking expanded url ips with VirusTotal..")
	for orig_url in malicious.keys():
		process_count += 1
		ip = malicious[orig_url]['ip']
		print_err("Checking IP for "+orig_url+" : "+ip)
		isMalicious = IpScanner(ip,orig_url,'pos')

		# record statuses except errors
		if isMalicious in [0,1]:
			malicious[orig_url]['done'] = isMalicious

		if isMalicious == 1:
			print ('LEVEL 3 MATCH: '+orig_url)#+' '+ip)#>>>>>>>>>>>>>>
			truePos  += 1
			match_count += 1
			del malicious[orig_url]

		# if there was an error
		elif  isMalicious == -1:
			error_count += 1
		elif isMalicious == 0: # no match
			no_match_count += 1
		else:
			print_err("Unknown isMalicious! "+orig_url)


	print("Done.")
	print_err("\nLEVEL 3:")
       	print_err("PROCESSED:   "+str(process_count))
        print_err("MATCHED:     "+str(match_count))
        print_err("NOT MATCHED: "+str(no_match_count))
        print_err("ERORR:       "+str(error_count))

	level_matches[3] = str(match_count)

	process_count = match_count = no_match_count = error_count  = 0
	print("Checking original url ips with VirusTotal..")
	print_err("\nChecking with original url ip addresses..")
	for orig_url in malicious.keys():
		process_count += 1
		ip = malicious[orig_url]['sip']
		print_err("Checking SHORT IP for "+orig_url+" : "+ip)
		isMalicious = IpScanner(ip,orig_url,'neg')

		# record statuses except errors
		if isMalicious in [0,1]:
			malicious[orig_url]['done'] = isMalicious

		if isMalicious == 1:
			print ('LEVEL 4 MATCH: '+orig_url)#+' '+ip)#>>>>>>>>>>>>>>
			truePos  += 1
			match_count +=1
			del malicious[orig_url]
		elif  isMalicious == -1:
			error_count += 1
		elif isMalicious == 0:
			no_match_count += 1
		else:
			print_err("Unknown isMalicious! "+orig_url)

	print("Done.")
	print_err("\nLEVEL 4:")
       	print_err("PROCESSED:   "+str(process_count))
        print_err("MATCHED:     "+str(match_count))
        print_err("NOT MATCHED: "+str(no_match_count))
        print_err("ERORR:       "+str(error_count))

	print_err("\nDone.")

	level_matches[4] = str(match_count)

	falsePos = error = un_processed = 0
	for orig_url in malicious.keys():
		status = malicious[orig_url]['done']
		if status == 0:
			falsePos += 1
		elif status == 1:
			error += 1
		else:
			un_processed += 1
			print_err("Unprocessed: "+str(malicious[orig_url]))

        print("\nRESULTS:")
	print("    "+db_details)
	print("    TOTAL INPUT READ:  "+str(mal_count))
	print("    TRUE POSITIVES:    "+str(truePos))
	print("    FALSE POSITIVES:   "+str(falsePos))
	print("    ERRORS:            "+str(error))
	print("    NOT PROCESSED:     "+str(un_processed))
	print("    MATCH COUNTS:")
	print("         LEVEL 1:      "+level_matches[1])
	print("         LEVEL 2:      "+level_matches[2])
	print("         LEVEL 3:      "+level_matches[3])
	print("         LEVEL 4:      "+level_matches[4])

if __name__ == "__main__":
   main(sys.argv[1:])
