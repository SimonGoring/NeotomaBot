#!/usr/bin/env python
# -*- coding: utf-8 -*-
#!python3

import os, tweepy, time, sys, json, requests, random, imp, datetime, schedule, time, random

def twit_auth():
  #  Authenticate the twitter session.  Should only be needed once at the initiation of the code.

    CONSUMER_KEY = os.environ['CONSUMER_KEY']
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    ACCESS_KEY = os.environ['ACCESS_KEY']
    ACCESS_SECRET = os.environ['ACCESS_SECRET']
  
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)
    print('Twitter authenticated \n')
    return api
  
  
def check_neotoma():
    # This function call to neotoma, reads a text file, compares the two
    # and then outputs all the 'new' records to a different text file.
  #  Function returns the number of new records returned.

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
    with open('to_print.json', 'w') as print_file:
        json.dump(inp_json, print_file)
    return len(inp_json) - len(to_print)


def print_neotoma_update(api):
  # Check for new records by using the neotoma "recent" API:
  old_toprint = check_neotoma()
  
  # load files:
  with open('to_print.json', 'r') as print_file:
    to_print  = json.loads(print_file.read())  
  with open('old_results.json', 'r') as print_file:
    old_files  = json.loads(print_file.read())

  print('Neotoma dataset updated.\n')
  if (old_toprint) == 1:
    #  If only a single site has been added:
    line = "I've got a backlog of " + str(len(to_print)) + " sites to tweet and " + str(old_toprint) + " site has been added since I last checked Neotoma. http://neotomadb.org"
  elif (old_toprint) > 1:
    line = "I've got a backlog of " + str(len(to_print)) + " sites to tweet and " + str(old_toprint) + " sites have been added since I last checked Neotoma. http://neotomadb.org"
  else:
    line = "I've got a backlog of " + str(len(to_print)) + " sites to tweet.  Nothing new has been added since I last checked. http://neotomadb.org"
  
  print('%s' % line)
  try:
    print('%s' % line)
    api.update_status(status=line)
  except tweepy.error.TweepError:
    print("Twitter error raised")
    
def post_tweet(api):
  # Read in the printable tweets:
  with open('to_print.json', 'r') as print_file:
    to_print  = json.loads(print_file.read())
      
  with open('old_results.json', 'r') as print_file:
    old_files  = json.loads(print_file.read())
    
  print('Files opened\n')
  
  pr_tw = random.randint(0,len(to_print) - 1)
  site  = to_print[pr_tw]

  #  Get ready to print the first [0] record in to_print:
  weblink = 'http://apps.neotomadb.org/Explorer/?datasetid=' + str(site["DatasetID"])
    
  #  The datasets have long names.  I want to match to simplify:
        
  line = 'Neotoma welcomes ' + site["SiteName"] + ', a ' + site["DatasetType"] + ' dataset by ' + site["Investigator"] + " " + weblink
    
  #  There's a few reasons why the name might be very long, one is the site name, the other is the author name:
  if len(line) > 170:
    line = 'Neotoma welcomes ' + site["SiteName"] + " by " + site["Investigator"] + " " + weblink
  
  #  If it's still too long then clip the author list:
  if len(line) > 170 & site["Investigator"].find(','):
    author = site["Investigator"][0:to_print[0]["Investigator"].find(',')]
    line = 'Neotoma welcomes ' + site["SiteName"] + " by " + author + " et al. " + weblink  
    
  try:
    print('%s' % line)
    api.update_status(status=line)
    old_files.append(site)
    del to_print[pr_tw]
    with open('to_print.json', 'w')  as print_file:
      json.dump(to_print, print_file)
    with open('old_results.json', 'w')  as print_file:
      json.dump(old_files, print_file)
  except tweepy.error.TweepError:
    print("Twitter error raised")

          
def self_identify(api):

  # Identify myself as the owner of the bot:
  line = 'This twitter bot for the Neotoma Paleoecological Database is managed by @sjgoring. Letting you know what\'s new at http://neotomadb.org'
  try:
    print('%s' % line)
    api.update_status(status=line)
  except tweepy.error.TweepError:
    print("Twitter error raised")

def self_identify_hub(api):
  # Identify the codebase for the bot:
  line = 'This twitter bot for the Neotoma Paleoecological Database is programmed in #python and publicly available through an MIT License on GitHub: https://github.com/SimonGoring/neotomabot'
  try:
    print('%s' % line)
    api.update_status(status=line)
  except tweepy.error.TweepError:
    print("Twitter error raised")

def other_inf_hub(api):
  # Identify the codebase for the bot:
  line = ['The bot for the Neotoma Database is programmed in #python and publicly available through an MIT License on GitHub: https://github.com/SimonGoring/neotomabot',
          'Neotoma has teaching modules you can use in the class room, check it out: https://www.neotomadb.org/education/category/higher_ed/',
          'The governance for Neotoma includes representatives from our constituent databases. Find out more: https://www.neotomadb.org/about/category/governance',
          'We are invested in #cyberinfrastructure.  Our response to emerging challenges is posted on @authorea: https://www.authorea.com/users/152134/articles/165940-cyberinfrastructure-in-the-paleosciences-mobilizing-long-tail-data-building-distributed-community-infrastructure-empowering-individual-geoscientists',
          'We keep a list of all publications that have used Neotoma for their research.  Want to be added?  Contact us! https://www.neotomadb.org/references',
          'If you use #rstats then you can access Neotoma data directly thanks to @rOpenSci! https://ropensci.org/tutorials/neotoma_tutorial.html',
          'Neotoma is more than just pollen & mammals it contains 28 data types incl. phytoliths & biochemistry data. Explore! https://www.neotomadb.org/data/category/explorer',
          'Think you\'ve got better tweets? Add them to my code & make a pull request! https://github.com/SimonGoring/neotomabot',
          'This little bit of #scicomm is brought to you by @sjgoring and #NSFfunded by @nsf_geo & @earthcube.  Thanks for your support!',
          '#AGU17 is coming up, you might be interested in this session on interdisciplinary geosciences! @earthcube @sjgoring https://agu.confex.com/agu/fm17/preliminaryview.cgi/Session26195',
          'Interested in the future of integrating paleoecological data & models? Submit to: https://agu.confex.com/agu/fm17/preliminaryview.cgi/Session26532 #agu17 @AndriaEDawson',
          'Behold, the very first Neotoma dataset, ID 1: https://apps.neotomadb.org/explorer/?datasetid=1',
          'Is it a coincidence that the dataset ID for Devil\'s Lake WI is 666? Probably. . . https://apps.neotomadb.org/explorer/?datasetid=666',
          'We\'ve got some new R tutorials up online.  Is there anything you\'d like to do with Neotoma? http://neotomadb.github.io']

  try:
    print('%s' % line)
    api.update_status(status=line[random.randint(0,8)])
  except tweepy.error.TweepError:
    print("Twitter error raised")

api = twit_auth()
  
schedule.every(3).hours.do(post_tweet, api)
schedule.every().day.at("15:37").do(print_neotoma_update, api)
schedule.every().wednesday.at("14:30").do(self_identify, api)
schedule.every().monday.at("14:30").do(self_identify_hub, api)
schedule.every().day.at("10:30").do(other_inf_hub, api)

while 1:
    schedule.run_pending()
    time.sleep(61)