# -*- coding: utf-8-*-
import os
import re
from getpass import getpass
import yaml
import shellapath


def main():
    p_shella = open(shellapath.config("profile.yml"), "a")
    
    print("*******************************************************")
    print("*         SHELLA - MODULES CONFIGURATION TOOL         *")
    print("*               (c) 2017 Malo Wellbrock               *")
    print("*******************************************************")
    
    print("Note: This tool will help you to configure all the current available modules" + '\n')

    # Domoticz
    domoticz_keys = {
		"server": "server",
		"username": "username",
		"password": "password"
    }
    
    print("Do you want to configure a Domoticz Server?")
    configure = raw_input('(Y)es or (N)o: ')
    if configure == 'Y':
		server_value = raw_input("\nPlease enter your server IP: ")
		server_key = server_value
		server_name = domoticz_keys['server']
		username_value = raw_input("\nPlease enter your Username: ")
		username_key = username_value
		username_name = domoticz_keys['username']
		password_value = raw_input("\nPlease enter your Password: ")
		password_key = password_value
		password_name = domoticz_keys['password']
		p_shella.write('\n' + 'domoticz:' + '\n' +
						'   ' + server_name + ': ' + server_key + '\n' +
						'   ' + username_name + ': ' + username_key + '\n' +
						'   ' + password_name + ': ' + password_key + '\n')
		print("Server configured" + '/n')

	# Google Calendar
    google_keys = {
		"id_client": "client_id",
		"secret_client": "client_secret"
    }
    
    print("Do you want to configure Google Calendar?")
    configure = raw_input('(Y)es or (N)o: ')
    if configure == 'Y':
		id_value = raw_input("\nPlease enter your Google Client ID: ")
		id_key = id_value
		id_name = google_keys['id_client']
		secret_value = raw_input("\nPlease enter your Client Secret: ")
		secret_key = secret_value
		secret_name = google_keys['secret_client']
		p_shella.write('\n' + 'google:' + '\n' +
						'   ' + id_name + ': ' + id_key + '\n' +
						'   ' + secret_name + ': ' + secret_key + '\n')
		print("Calendar configured" + '/n')

	# Twitter
    twitter_keys = {
		"secret_client": "CLIENT_SECRET",
		"key_consumer": "TW_CONSUMER_KEY",
		"secret_consumer": "TW_CONSUMER_SECRET",
		"token_access": "TW_ACCESS_TOKEN",
		"secret_token_access": "TW_ACCESS_TOKEN_SECRET"
    }
    
    print("Do you want to configure Twitter?")
    configure = raw_input('(Y)es or (N)o: ')
    if configure == 'Y':
		api_value = raw_input("\nPlease enter your API Key: ")
		api_key = api_value
		api_name = twitter_keys['secret_client']
		api_name_2 = twitter_keys['key_consumer']
		api_secret_value = raw_input("\nPlease enter your API Secret: ")
		api_secret_key = api_secret_value
		api_secret_name = twitter_keys['secret_consumer']
		token_value = raw_input("\nPlease enter your Access Token: ")
		token_key = token_value
		token_name = twitter_keys['token_access']
		token_secret_value = raw_input("\nPlease enter your API Secret: ")
		token_secret_key = token_value
		token_secret_name = twitter_keys['secret_token_access']
		p_shella.write('\n' + 'twitter:' + '\n' +
						'   ' + api_name + ': ' + api_key + '\n' +
						'   ' + api_name_2 + ': ' + api_key + '\n' +
						'   ' + api_secret_name + ': ' + api_secret_key + '\n' +
						'   ' + token_name + ': ' + token_key + '\n' +
						'   ' + token_secret_name + ': ' + token_secret_key + '\n')
		print("Twitter configured" + '/n')

    # Finish
    p_shella.close()
    print("Exiting..")

if __name__ == "__main__":
    main()
