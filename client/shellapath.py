# -*- coding: utf-8-*-
import os
import yaml

# Shella main directory
APP_PATH = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir))

DATA_PATH = os.path.join(APP_PATH, "static")
LIB_PATH = os.path.join(APP_PATH, "client")
PLUGIN_PATH = os.path.join(LIB_PATH, "modules")

CONFIG_PATH = os.path.expanduser(os.getenv('SHELLA_CONFIG', '~/.shella'))

def config(*fname):
    return os.path.join(CONFIG_PATH, *fname)


def data(*fname):
    return os.path.join(DATA_PATH, *fname)
    
def getLang():
	profile_path = config('profile.yml')
	if os.path.exists(profile_path):
		with open(profile_path, 'r') as f:
			profile = yaml.safe_load(f)
			if 'language' in profile:
				lang = profile['language']
			else:
				lang = 'en'
	return os.path.join(PLUGIN_PATH, lang)
