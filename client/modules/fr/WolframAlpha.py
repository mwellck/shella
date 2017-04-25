# -*- coding: utf-8-*-
import random
import re
import wolframalpha
import time
import sys
from sys import maxint

from client import shellapath
WORDS = ["QUI", "QUOI", "COMBIEN", "QUEL", "OU", "COMMENT", "QUELLE"]


def handle(text, mic, profile):
    app_id = profile['keys']['WOLFRAMALPHA']
    client = wolframalpha.Client(app_id)

    query = client.query(text)
    if len(query.pods) > 0:
        texts = ""
        pod = query.pods[1]
        if pod.text:
            texts = pod.text
        else:
            texts = (u"Je n'ai pas pu trouver une réponse")

        mic.say(texts.replace("|",""))
    else:
        mic.say(u"Veuillez m'excuser mais pourriez vous être plus précis?")




def isValid(text):
    if re.search(r'\bqui|quoi|ou|où|combien|quel|quelle|comment\b', text, re.IGNORECASE):
        return True
    else:
        return False
