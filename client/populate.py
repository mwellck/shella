# -*- coding: utf-8-*-
import os
import re
from getpass import getpass
import yaml
from pytz import timezone
import feedparser
import shellapath


def run():
    profile = {}

    # intro
    print("*******************************************************")
    print("*         SHELLA - PROFILE CONFIGURATION TOOL         *")
    print("*               (c) 2017 Malo Wellbrock               *")
    print("*******************************************************")

    def simple_request(var, cleanVar, cleanInput=None):
        input = raw_input(cleanVar + ": ")
        if input:
            if cleanInput:
                input = cleanInput(input)
            profile[var] = input

    # Name
    simple_request('first_name', 'First name')
    simple_request('last_name', 'Last name')

    # Gmail
    print("\nShella uses your Gmail to send notifications. Alternatively, " +
          "you can skip this step (or just fill in the email address if you " +
          "want to receive email notifications) and setup a Mailgun " +
          "account, as at http://jasperproject.github.io/documentation/" +
          "software/#mailgun.\n")
    simple_request('gmail_address', 'Gmail address')
    profile['gmail_password'] = getpass()

    # Phone number
    def clean_number(s):
        return re.sub(r'[^0-9]', '', s)

    phone_number = clean_number(raw_input("\nPhone number (no country " +
                                          "code). Any dashes or spaces will " +
                                          "be removed for you: "))
    profile['phone_number'] = phone_number

    # Carrier
    print("\nPhone carrier (for sending text notifications).")
    print("If you have a US phone number, you can enter one of the " +
          "following: 'AT&T', 'Verizon', 'T-Mobile' (without the quotes). " +
          "If your carrier isn't listed or you have an international " +
          "number, go to http://www.emailtextmessages.com and enter the " +
          "email suffix for your carrier (e.g., for Virgin Mobile, enter " +
          "'vmobl.com'; for T-Mobile Germany, enter 't-d1-sms.de').")
    carrier = raw_input('Carrier: ')
    if carrier == 'AT&T':
        profile['carrier'] = 'txt.att.net'
    elif carrier == 'Verizon':
        profile['carrier'] = 'vtext.com'
    elif carrier == 'T-Mobile':
        profile['carrier'] = 'tmomail.net'
    else:
        profile['carrier'] = carrier

    # Location
    def verifyLocation(place):
        feed = feedparser.parse('http://rss.wunderground.com/auto/rss_full/' +
                                place)
        numEntries = len(feed['entries'])
        if numEntries == 0:
            return False
        else:
            print("Location saved as " + feed['feed']['description'][33:])
            return True

    print("\nLocation should be a 5-digit US zipcode (e.g., 08544). If you " +
          "are outside the US, insert the name of your nearest big " +
          "town/city.  For weather requests.")
    location = raw_input("Location: ")
    while location and not verifyLocation(location):
        print("Weather not found. Please try another location.")
        location = raw_input("Location: ")
    if location:
        profile['location'] = location

    # Timezone
    print("\nPlease enter a timezone from the list located in the TZ* " +
          "column at https://en.wikipedia.org/wiki/" +
          "List_of_tz_database_time_zones, or none at all.")
    tz = raw_input("Timezone: ")
    while tz:
        try:
            timezone(tz)
            profile['timezone'] = tz
            break
        except:
            print("Not a valid timezone. Try again.")
            tz = raw_input("Timezone: ")

    # Notifications
    response = raw_input("\nWould you prefer to have notifications sent by " +
                         "email (E) or text message (T)? ")
    while not response or (response != 'E' and response != 'T'):
        response = raw_input("Please choose email (E) or text message (T): ")
    profile['prefers_email'] = (response == 'E')

    # Write temp
    if not os.path.exists(shellapath.CONFIG_PATH):
        os.makedirs(shellapath.CONFIG_PATH)
    outputFile = open(shellapath.config("profile.yml"), "w")
    yaml.dump(profile, outputFile, default_flow_style=False)
    p_shella = open(shellapath.config("profile.yml"), "a")

    # STT Engines
    stt_engines = {
        "sphinx": None,
        "google": "GOOGLE_KEY",
        "wit": "WITAI_KEY",
        "watson": None
    }

    response = raw_input("\nPlease choose a STT Engine (else PocketSphinx will be set as default)" +
                          " from the available implementations: %s " % stt_engines.keys())
    if response == "watson":
		user_value = raw_input("\nPlease enter your username: ")
		user_key = user_value
		pass_value = raw_input("\nPlease enter your password: ")
		pass_key = pass_value
		p_shella.write('watson-stt:' + '\n' +
              '   ''username: ' + user_key + '\n' +
              '   ''password: ' + pass_key + '\n')
    elif (response in stt_engines):
          profile["stt_engine"] = response
          api_key_name = stt_engines[response]
          if api_key_name:
              key = raw_input("\nPlease enter your API key: ")
              profile["stt-keys"] = {api_key_name: key}
    if response == "google" or response == "wit" or response == "watson":
		response = raw_input("\nChoosing this engine means every sound " +
                             "makes a request online. " +
                             "\nWould you like to process the wake up word " +
                             "locally with PocketSphinx? (Y) or (N)?")
		while not response or (response != 'Y' and response != 'N'):
			response = raw_input("Please choose PocketSphinx (Y) " +
                                 "or keep your engine (N): ")
		if response == 'Y':
			profile['stt_passive_engine'] = "sphinx"

    # TTS Engines
    tts_engines = {
        "dummy-tts": None,
        "espeak-tts": None,
        "festival-tts": None,
        "flite-tts": None,
        "mimic-tts": None,
        "osx-tts": None,
        "pico-tts": None,
        "google-tts": None,
        "mary-tts": None,
        "ivona-tts": None
    }

    response = raw_input("\nPlease choose a TTS Engine (else flite-tts will be set as default)" +
                          " from the available implementations: %s " % tts_engines.keys())
    if response == "ivona-tts":
		access_value = raw_input("\nPlease enter your Access Key: ")
		access_key = access_value
		secret_value = raw_input("\nPlease enter your Secret Key: ")
		secret_key = secret_value
		p_shella.write('ivona-tts:' + '\n' + '   access_key: ' + access_key + '\n' + '   secret_key: ' + secret_key + '\n')
    if response == "google-tts":
		lang_value = raw_input("\nPlease enter your language (eg. en, fr, etc.): ")
		lang_key = lang_value
		p_shella.write('google-tts:' + '\n' + '   language: ' + lang_key + '\n')
    if (response in tts_engines):
          profile["tts_engine"] = response
    if response == "google-tts" or response == "ivona-tts":
	response = raw_input("\nChoosing this engine means every reply " +
                             "makes a request online. " +
                             "\nWould you like to use an offline TTS? (Y) or (N)?")
	while not response or (response != 'Y' and response != 'N'):
		response = raw_input("Please choose Flite (Y) or keep your engine (N): ")
		if response == 'Y':
			profile['tts_engine'] = "flite-tts"

    # Write profile
    print("Writing your profile")
    outputFile = open(shellapath.config("profile.yml"), "w")
    yaml.dump(profile, outputFile, default_flow_style=False)
    print("Done.")

if __name__ == "__main__":
    run()
