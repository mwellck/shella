# -*- coding: utf-8-*-
import imaplib
import email
import re
from dateutil import parser

WORDS = ["EMAIL", "EMAILS", "BOITE", "RECEPTION", "MAIL", "MAILS", "COURRIEL"]


def getSender(email):
    """
        Returns the best-guess sender of an email.

        Arguments:
        email -- the email whose sender is desired

        Returns:
        Sender of the email.
    """
    sender = email['From']
    m = re.match(r'(.*)\s<.*>', sender)
    if m:
        return m.group(1)
    return sender


def getDate(email):
    return parser.parse(email.get('date'))


def getMostRecentDate(emails):
    """
        Returns the most recent date of any email in the list provided.

        Arguments:
        emails -- a list of emails to check

        Returns:
        Date of the most recent email.
    """
    dates = [getDate(e) for e in emails]
    dates.sort(reverse=True)
    if dates:
        return dates[0]
    return None


def fetchUnreadEmails(profile, since=None, markRead=False, limit=None):
    """
        Fetches a list of unread email objects from a user's Gmail inbox.

        Arguments:
        profile -- contains information related to the user (e.g., Gmail
                   address)
        since -- if provided, no emails before this date will be returned
        markRead -- if True, marks all returned emails as read in target inbox

        Returns:
        A list of unread email objects.
    """
    conn = imaplib.IMAP4_SSL('imap.gmail.com')
    conn.debug = 0
    conn.login(profile['gmail_address'], profile['gmail_password'])
    conn.select(readonly=(not markRead))

    msgs = []
    (retcode, messages) = conn.search(None, '(UNSEEN)')

    if retcode == 'OK' and messages != ['']:
        numUnread = len(messages[0].split(' '))
        if limit and numUnread > limit:
            return numUnread

        for num in messages[0].split(' '):
            # parse email RFC822 format
            ret, data = conn.fetch(num, '(RFC822)')
            msg = email.message_from_string(data[0][1])

            if not since or getDate(msg) > since:
                msgs.append(msg)
    conn.close()
    conn.logout()

    return msgs


def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, with a summary of
        the user's Gmail inbox, reporting on the number of unread emails
        in the inbox, as well as their senders.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., Gmail
                   address)
    """
    try:
        msgs = fetchUnreadEmails(profile, limit=5)

        if isinstance(msgs, int):
            response = "Vous avez %d emails non lus." % msgs
            mic.say(response)
            return

        senders = [getSender(e) for e in msgs]
    except imaplib.IMAP4.error:
        mic.say(
            "Je suis désolée. Je n'ai pas été autorisée à me connecter à votre compte Gmail.")
        return

    if not senders:
        mic.say("Vous avez aucun nouveau email.")
    elif len(senders) == 1:
        mic.say("Vous avez un nouvel email non lu de " + senders[0] + ".")
    else:
        response = "Vous avez %d emails non lus" % len(
            senders)
        unique_senders = list(set(senders))
        if len(unique_senders) > 1:
            unique_senders[-1] = 'et ' + unique_senders[-1]
            response += ". De la part de: "
            response += '...'.join(senders)
        else:
            response += " de " + unique_senders[0]

        mic.say(response)


def isValid(text):
    """
        Returns True if the input is related to email.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\bemail|mail|emails|mails|courriel\b', text, re.IGNORECASE))
