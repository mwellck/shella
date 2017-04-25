# -*- coding: utf-8-*-
import re

WORDS = ["REPETE", "APRES", "MOI"]


def handle(text, mic, profile):
    mic.say('OK')

    text = mic.activeListen()
  
    mic.say(text)


def isValid(text):
    return bool(re.search(r'\brépète après moi\b', text, re.IGNORECASE))
