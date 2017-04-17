# -*- coding: utf-8-*-
import re

WORDS = ["QUI", "ES", "TU", "VOUS"]

def isValid(text):
    
    return bool(re.search(r'\b(qui es tu)\b', text, re.IGNORECASE))

def handle(text, mic, profile):
    response = "Je suis Shella, une assistante vocale créée par Malo."
    mic.say(response)
