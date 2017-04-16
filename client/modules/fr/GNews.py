# -*- coding: utf-8-*-
import feedparser
from client import app_utils
import re
from semantic.numbers import NumberService

<<<<<<< HEAD
WORDS = ["NEWS", "OUI", "NON", "PREMIER", "DEUXIEME", "DEUXI\xc8ME", "TROISI\xc8ME", "TROISIEME", "INFO", "NOUVELLE", "INFORMATION", "NEWZ", "NOUVEL"]
=======
WORDS = ["NEWS", "OUI", "NON", "PREMIER", "DEUXIEME", "TROISIEME", "INFO", "NOUVELLE", "INFORMATION"]
>>>>>>> parent of c5891c8... Improve French

PRIORITY = 3

URL = 'https://news.google.fr/?output=rss'


class Article:

    def __init__(self, title, URL):
        self.title = title
        self.URL = URL


def getTopArticles(maxResults=None):
    d = feedparser.parse("https://news.google.fr/?output=rss")

    count = 0
    articles = []
    for item in d['items']:
        articles.append(Article(item['title'], item['link'].split("&url=")[1]))
        count += 1
        if maxResults and count > maxResults:
            break

    return articles


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a summary of
        the day's top news headlines, sending them to the user over email
        if desired.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    mic.say("Récupération des nouvelles")
    articles = getTopArticles(maxResults=3)
    titles = [" ".join(x.title.split(" - ")[:-1]) for x in articles]
    all_titles = " ".join(str(idx + 1) + ")" + title for idx, title in enumerate(titles))

    def handleResponse(text):

        def extractOrdinals(text):
            output = []
            service = NumberService()
            for w in text.split():
                if w in service.__ordinals__:
                    output.append(service.__ordinals__[w])
            return [service.parse(w) for w in output]

        chosen_articles = extractOrdinals(text)
        send_all = not chosen_articles and app_utils.isPositive(text)

        if send_all or chosen_articles:
            mic.say("Bien sûr, donnez moi un moment")

            if profile['prefers_email']:
                body = "<ul>"

            def formatArticle(article):
                tiny_url = app_utils.generateTinyURL(article.URL)

                if profile['prefers_email']:
                    return "<li><a href=\'%s\'>%s</a></li>" % (tiny_url,
                                                               article.title)
                else:
                    return article.title + " -- " + tiny_url

            for idx, article in enumerate(articles):
                if send_all or (idx + 1) in chosen_articles:
                    article_link = formatArticle(article)

                    if profile['prefers_email']:
                        body += article_link
                    else:
                        if not app_utils.emailUser(profile, SUBJECT="",
                                                   BODY=article_link):
                            mic.say("J'ai quelques difficultées à vous envoyez les articles." +
                                    "Pourriez vous vérifier que votre numéro de téléphone est correcte?")
                            return

            # if prefers email, we send once, at the end
            if profile['prefers_email']:
                body += "</ul>"
                if not app_utils.emailUser(profile,
                                           SUBJECT="Les dernières nouvelles",
                                           BODY=body):
                    mic.say("J'ai quelques difficultées à vous envoyez les articles." +
                            "Pourriez vous vérifier que votre numéro de téléphone est correcte?")
                    return

            mic.say("C'est fait")

        else:

            mic.say("Aucunes nouvelles vous sera envoyés.")

    if 'phone_number' in profile:
        mic.say("Voici les dernières nouvelles." + all_titles +
				"Voulez vous que je vous envoie les nouvelles?" +
				"Si oui, lesquelles?")
        handleResponse(mic.activeListen())

    else:
        mic.say(
            "Voici les dernières nouvelles. " + all_titles)


def isValid(text):
    """
        Returns True if the input is related to the news.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(nouvelle|information|info|news)\b', text, re.IGNORECASE))
