# -*- coding: utf-8-*-
import datetime
import re
import facebook
from client.app_utils import getTimezone

WORDS = ["ANNIVERSAIRE"]


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, by listing the user's
        Facebook friends with birthdays today.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    oauth_access_token = profile['keys']["FB_TOKEN"]

    graph = facebook.GraphAPI(oauth_access_token)

    try:
        results = graph.request("me/friends",
                                args={'fields': 'id,name,birthday'})
    except facebook.GraphAPIError:
        mic.say("Je n'es pas été autorisée à avoir accès à votre compte Facebook." +
                "Si vous voulez me donner l'accès, merci de consulter la documentation sur GitHub.")
        return
    except:
        mic.say(
            "Veuillez m'excuser, il y a actuellement un problème avec ce service.")
        return

    needle = datetime.datetime.now(tz=getTimezone(profile)).strftime("%m/%d")

    people = []
    for person in results['data']:
        try:
            if needle in person['birthday']:
                people.append(person['name'])
        except:
            continue

    if len(people) > 0:
        if len(people) == 1:
            output = people[0] + " a un anniversaire aujourd'hui."
        else:
            output = "Vos amis fêtant leur anniversaire aujourd'hui sont " + \
                ", ".join(people[:-1]) + " et " + people[-1] + "."
    else:
        output = "Aucun de vos amis fêtes son anniversaire aujourd'hui."

    mic.say(output)


def isValid(text):
    """
        Returns True if the input is related to birthdays.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return any(word in text.upper() for word in WORDS)
