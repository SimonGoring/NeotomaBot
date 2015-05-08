#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!python3

import tweepy, time, sys, json, requests, random, imp, datetime
 
def check_neotoma():
    ## This function call to neotoma, reads a text file, compares the two
    ## and then returns all the 'new' records to a different text file.

    #  inputs:
    #  1. text file: old_results.json
    #  2. text file: to_print.json
    #  3. json call: neotoma

    with open('old_results.json', 'r') as old_file:
        old_calls = json.loads(old_file.read())
    
    with open('to_print.json', 'r')    as print_file:
        to_print  = json.loads(print_file.read())
    
    neotoma  = requests.get("http://ceiwin10.cei.psu.edu/NDB/RecentUploads?months=1")
    inp_json = json.loads(neotoma.text)['data']

    def get_datasets(x):
        did = []
        for y in x:
            did.append(y["DatasetID"])
        return did

    neo_datasets = get_datasets(inp_json)
    old_datasets = get_datasets(old_calls)
    new_datasets = get_datasets(to_print)
    
    #  So this works
    #  We now have the numeric dataset IDs for the most recent month of
    #  new files to neotoma (neo_datasets), all the ones we've already tweeted
    #  (old_datasets) and all the ones in our queue (new_datasets).
    #
    #  The next thing we want to do is to remove all the neo_datasets that
    #  are in old_datasets and then remove all the new_datasets that are
    #  in neo_datasets, append neo_datasets to new_datasets (if new_datasets
    #  has a length > 0) and then dump new_datasets.
    #
    #  Old datasets gets re-written when the tweets go out.

    #  remove all the neo_datasets:
    for i in range(len(neo_datasets)-1, 0, -1):
        if neo_datasets[i] in old_datasets:
            del inp_json[i]

    # This now gives us a pared down version of inp_json
    # Now we need to make sure to add any of the to_print to neo_dataset.
    #  We do this by cycling through new_datasets.  Any dataset number that
    #  is not in old_datasets or neo_datasets gets added to the beginning of
    #  the new list.  This way it is always the first called up when twitter
    #  posts:
    
    for i in range(0, len(new_datasets)-1):
        if new_datasets[i] not in old_datasets and new_datasets[i] not in neo_datasets:
            inp_json.insert(0,to_print[i])

    #  Now write out to file.  Old file doesn't get changed until the
    #  twitter app is run.
    with open('to_print.json', 'w')    as print_file:
        json.dump(inp_json, print_file)

def post_tweet():
    
	with open('apikeys.txt', 'r') as read_file:
		global data
		data = imp.load_source('data', '', read_file)

	CONSUMER_KEY = data.CONSUMER_KEY
	CONSUMER_SECRET = data.CONSUMER_SECRET
	ACCESS_KEY = data.ACCESS_KEY
	ACCESS_SECRET = data.ACCESS_SECRET
	
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
	api = tweepy.API(auth)

	print('Twitter authenticated \n')
		
		# Read in the printable tweets:
	with open('to_print.json', 'r') as print_file:
		to_print  = json.loads(print_file.read())
			
	with open('old_results.json', 'r') as print_file:
		old_files  = json.loads(print_file.read())
		
	print('Files opened\n')
		
	#  Now loop through the records:
	while len(to_print) > 0:
		#  flags
		message_flag = 0
		check_flag   = 0
		
		weblink = 'http://apps.neotomadb.org/Explorer/?datasetid=' + str(to_print[0]["DatasetID"])
		
		#  The datasets have long names.  I want to match to simplify:
				
		line = 'Neotoma welcomes ' + to_print[0]["SiteName"] + ', a ' + to_print[0]["DatasetType"] + ' dataset by ' + to_print[0]["Investigator"] + " " + weblink
		
		if len(line) > 170:
			line = 'Neotoma welcomes ' + to_print[0]["SiteName"] + " by " + to_print[0]["Investigator"] + " " + weblink


		if datetime.datetime.now().minute % 60 == 0 and message_flag == 0 and datetime.datetime.now().hour % 12:
			# Every 12 hours identify myself.
			line = 'This twitter bot for the Neotoma Paleoecological Database is managed by @sjgoring. Letting you know what\'s new at http://neotomadb.org'
			api.update_status(status=line)
			message_flag = 1
		elif datetime.datetime.now().minute % 60 == 0: # tweet on the hour.
			api.update_status(status=line)

			#  Add the tweeted site to `old_files` and then delete it from the to_print.
			old_files.append(to_print[0])

			del to_print[0]

			with open('to_print.json', 'w')	as print_file:
				json.dump(to_print, print_file)

			with open('old_results.json', 'w')	as print_file:
				json.dump(old_files, print_file)
				
			while datetime.datetime.now().minute % 60 == 0:
				i = 1
									
			print('%s' % line)
			message_flag = 0
			

		# Check for new records every four hours:
		if datetime.datetime.now().minute % 60 == 0 and datetime.datetime.now().hour % 4 == 0 and check_flag == 0:
			check_neotoma()
			
			# reload files:
			old_toprint = to_print
			with open('to_print.json', 'r') as print_file:
				to_print  = json.loads(print_file.read())
			
			with open('old_results.json', 'r') as print_file:
				old_files  = json.loads(print_file.read())
		
			print('Neotoma dataset updated.\n')
			if (len(to_print) - len(old_toprint)) == 1:
				line = "I've got a backlog of " + len(to_print) + " sites to tweet and " + len(to_print) - len(old_toprint) + " site has been added since I last checked Neotoma. http://neotomadb.org"
			elif (len(to_print) - len(old_toprint)) > 1:
				line = "I've got a backlog of " + len(to_print) + " sites to tweet and " + len(to_print) - len(old_toprint) + " sites have been added since I last checked Neotoma. http://neotomadb.org"
			else:
				line = "I've got a backlog of " + len(to_print) + " sites to tweet.  Nothing new has been added since I last checked. http://neotomadb.org"
			
			check_flag = 1
		
		#  Clearing the check flag.	 This is probably inelegant, but I'm still just learning python :)
		if datetime.datetime.now().minute % 60 == 0 and datetime.datetime.now().hour % 4 == 0 and check_flag == 1:
			while datetime.datetime.now().minute % 60 == 0 and datetime.datetime.now().hour % 4 == 0 and check_flag == 1:
				i = 1
			check_flag = 0
		else:
			check_flag = 0
			

post_tweet()
