# -*- coding: utf-8-*-
import re
import psutil
import platform
import datetime

WORDS = ["STATUS", "ETAT"]

def isValid(text):
    
    return bool(re.search(r'\b(status)\b', text, re.IGNORECASE))

def handle(text, mic, profile):
    os, name, version, _, _, _ = platform.uname()
    version = version.split('-')[0]
    cores = psutil.cpu_count()
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory()[2]
    disk_percent = psutil.disk_usage('/')[3]
    boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
    running_since = boot_time.strftime("%A %d. %B %Y")
    response = "Je suis actuellement sous %s en version %s.  " %(os, version)
    response += "Ce système est nommé %s et possède un CPU de %s coeurs.  " %(name, cores)
    response += "L'utilisation du CPU est de %s pourcent.  " %cpu_percent
    response += "L'utilisation de la mémoire vive est de %s pourcent." %memory_percent
    mic.say(response)
