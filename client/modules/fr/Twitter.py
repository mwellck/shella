import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import *

import sys
import time
import re

# Written by Marc Laventure 

WORDS = ["TWITTER", " NOTIFICATION TWITTER", "MESSAGE DIRECT", "FEED", "TWEET", "TENDANCE", "NOTIFICATION", "NOTIFICATIONS"] 

PRIORITY = 1

# Input is latest retweet, mention, direct message ID
def getNotifications(mic,latestRetweet,latestMention,latestDirectMessage, api):
	
	latestRetweets = []
	latestRetweetsID = []
	latestDirectMessages = []
	latestDirectMessagesID = []
	latestMentions = []
	latestMentionsID = []
	
	mentions = api.mentions_timeline()
	retweets = api.retweets_of_me()
	directMessages = api.direct_messages()
	
	for mention in mentions:
		if mention.id > latestMention:
			latestMentions.append(mention)
			latestMentionsID.append(mention.id)

	for retweet in retweets:
		if retweet.id > latestRetweet:
			latestRetweets.append(retweet)
			latestRetweetsID.append(retweet.id)

	for directMessage in directMessages:
		if directMessage.id > latestDirectMessage:
			latestDirectMessages.append(directMessage)
			latestDirectMessagesID.append(directMessage.id)

	if len(latestRetweets) > 0:
		mic.say("Les derniers retweet sont")
		for retweetFinal in latestRetweets:
			mic.say(retweetFinal.text + " par " + retweetFinal.user.screen_name) 

		latestRetweetsID.sort()
		latestRetweet = latestRetweetsID[-1]
		retweetsIDFile = open('retweetsIDFile.txt', 'w')
		retweetsIDFile.write(str(latestRetweet))
		retweetsIDFile.close()
		
	else:
		mic.say("Vous n'avez aucun nouveau retweet.")

	if len(latestMentions) > 0:
		mic.say("Les dernières mentions sont")
		
		for mentionFinal in latestMentions:
			mic.say(mentionFinal.text + " par " + mentionFinal.user.screen_name)

		latestMentionsID.sort()
		latestMention = latestMentionsID[-1]
		mentionIDFile = open('mentionIDFile.txt', 'w')
		mentionIDFile.write(str(latestMention))
		mentionIDFile.close()
	
	else:
		mic.say("Vous n'avez aucune nouvelle mention.")

	if len(latestDirectMessages) > 0:
		mic.say("Vos derniers messages directes sont")
		
		for directMessageFinal in latestDirectMessages:
			mic.say(directMessageFinal.text + " par " + directMessageFinal.user.screen_name)

		latestDirectMessagesID.sort()
		latestDirectMessage = latestDirectMessagesID[-1]
		directMessageIDFile = open('directMessageID.txt', 'w')
		directMessageIDFile.write(str(latestDirectMessage))
		directMessageIDFile.close()

	else:
		mic.say("Vous n'avez aucun Message Direct")

	return

# No input needed
def getWhatsTrending(mic,api):

	# mic.say
	data = api.trends_place(1) # Grabs global trends
	trends = data[0]['trends']
	for trend in trends:
		name = trend['name'] #Grabs name of each trend
		if name.startswith('#'):
			mic.say(name) #Only grabs hashtags

# No input needed
def sendTweet(mic,api):
	#mic.listen for message

	#Command line input for debugging sakes

	mic.say("Que desirez vous tweeter?")
	tweet = mic.activeListen()
	api.update_status(tweet)

def handle(text, mic, profile):
	
	consumer_key = profile['twitter']["TW_CONSUMER_KEY"]
	consumer_secret = profile['twitter']["TW_CONSUMER_SECRET"]
	access_token = profile['twitter']["TW_ACCESS_TOKEN"]
	access_token_secret = profile['twitter']["TW_ACCESS_TOKEN_SECRET"]


	auth = OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	myTwitterID = api.me().id
	directMessages = api.direct_messages(count=1)

	try:
		directMessageIDFile = open('directMessageID.txt', 'r')
		directMessageID = directMessageIDFile.readline()
		latestDirectMessage = int(directMessageID)
		directMessageIDFile.close()
	except IOError:
		for directMessage in directMessages:
			latestDirectMessage = directMessage.id
		directMessageIDFile = open('directMessageID.txt', 'w')
		directMessageIDFile.write(str(latestDirectMessage))
		directMessageIDFile.close()

	mentions = api.mentions_timeline(count=1)

	try:
		mentionIDFile = open('mentionIDFile.txt', 'r')
		latestMentionID = mentionIDFile.readline()
		latestMention = int(latestMentionID)
		mentionIDFile.close()
	except IOError:
		mentionIDFile = open('mentionIDFile.txt', 'w')
		for mention in mentions:
			latestMention = mention.id
		mentionIDFile.write(str(latestMention))
		mentionIDFile.close()

	retweets = api.retweets_of_me(count=1)

	try:
		retweetsIDFile = open('retweetsIDFile.txt', 'r')
		retweetsID = retweetsIDFile.readline()
		latestRetweet = int(retweetsID)
		retweetsIDFile.close()
	except IOError:
		retweetsIDFile = open('retweetsIDFile.txt', 'w')
		for retweet in retweets:
			latestRetweet = retweet.id
		retweetsIDFile.write(str(latestRetweet))
		retweetsIDFile.close()


	if bool(re.search(r'\bTweet\b', text, re.IGNORECASE)):
		sendTweet(mic, api)

	if bool(re.search(r'\bnotification?\b', text, re.IGNORECASE)):
		getNotifications(mic,latestRetweet,latestMention,latestDirectMessage, api)

	if bool(re.search(r'\btendance\b', text, re.IGNORECASE)):
		getWhatsTrending(mic, api)

def isValid(text):
	
	tweetBool = bool(re.search(r'\bTweet\b', text, re.IGNORECASE))
	twitterBool = bool(re.search(r'\bTwitter\b', text, re.IGNORECASE))

	if tweetBool:
		return tweetBool
	elif twitterBool:
		return twitterBool
	else:
		return False

