# -*- coding: utf-8-*-
import re
from urllib2 import Request, urlopen, URLError
import json

WORDS = ["WIKI", "WICKY", "ARTICLE", "WIKIPEDIA", "WIKIP\xc9DIA"]

PRIORITY = 1


def handle(text, mic, profile):
    # method to get the wiki summary
    get_wiki(text,mic)


def get_wiki(text,mic):
    mic.say("Que désirez-vous savoir?")
    # get the user voice input as string
    article_title = mic.activeListen()
    # make a call to the Wikipedia API
    request = Request('https://fr.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles='+article_title)
    try:
        response = urlopen(request)
        data = json.load(response)
        # Parse the JSON to just get the extract. Always get the first summary.
        output = data["query"]["pages"]
        final = output[output.keys()[0]]["extract"]
        mic.say(final)
    except URLError, e:
        mic.say("Veuillez m'excuser mais je ne peux actuellement pas accèder à Wikipédia.")


def isValid(text):

    return any(word in text.upper() for word in WORDS)
