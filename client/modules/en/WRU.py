# -*- coding: utf-8-*-
import re

WORDS = ["WHO", "ARE", "YOU"]

def isValid(text):
    
    return bool(re.search(r'\b(who are you)\b', text, re.IGNORECASE))

def handle(text, mic, profile):
    response = "I'm Shella, a voice-controlled assistant created by Malo."
    mic.say(response)
