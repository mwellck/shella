# -*- coding: utf-8-*-
import re
import facebook


WORDS = ["FACEBOOK", "NOTIFICATION"]


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a summary of
        the user's Facebook notifications, including a count and details
        related to each individual notification.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    oauth_access_token = profile['keys']['FB_TOKEN']

    graph = facebook.GraphAPI(oauth_access_token)

    try:
        results = graph.request("me/notifications")
    except facebook.GraphAPIError:
        mic.say("Je n'es pas été autorisée à avoir accès à votre compte Facebook." +
                "Si vous voulez me donner l'accès, merci de consulter la documentation sur GitHub.")
        return
    except:
        mic.say(
            "Veuillez m'excuser, il y a actuellement un problème avec ce service.")

    if not len(results['data']):
        mic.say("Vous n'avez aucune notification Facebook. ")
        return

    updates = []
    for notification in results['data']:
        updates.append(notification['title'])

    count = len(results['data'])
    mic.say("Vous avez " + str(count) +
            " notifications Facebook. " + " ".join(updates) + ". ")

    return


def isValid(text):
    """
        Returns True if the input is related to Facebook notifications.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bnotification|Facebook\b', text, re.IGNORECASE))
