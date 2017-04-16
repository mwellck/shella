# -*- coding: utf-8-*-
import re
from imdb import IMDb

WORDS = ["FILM", "FILMS", "OUI"]

def format_names(people):
    del people[5:] # Max of 5 people listed
    ret = ''
    for person in people:
        ret += '%s.  ' %person.get('name')
    return ret.strip('. ')

def yes(text):
    return bool(re.search(r'\b(oui)\b', text, re.IGNORECASE))

def isValid(text):
    """
        Returns True if the text is related to Jasper's status.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(film|films)\b', text, re.IGNORECASE))

def handle(text, mic, profile):
    mic.say('Quel film?')
    movie_name = mic.activeListen()
    mic.say('Recherche des meilleurs résultats pour.  %s' %movie_name)
    ia = IMDb()
    movie_query = ia.search_movie(movie_name)
    del movie_query[5:]
    for movie in movie_query:
        mic.say('Est-ce %s (%s)?' %(movie.get('title'), movie.get('year')))
        response = mic.activeListen()
        if yes(response):
            ia.update(movie)
            movie_info = '%s (%s).  ' %(movie.get('title'), movie.get('year'))
            if movie.get('rating'): movie_info += 'Note.  %s sur 10.  ' %movie.get('rating')
            if movie.get('runtimes'): movie_info += 'Durée.  %s minutes.  ' %movie.get('runtimes')[0]
            if movie.get('genres'): movie_info += 'Genres.  %s.  ' %'.  '.join(movie.get('genres'))
            if movie.get('plot outline'): movie_info += 'Synopsis.  %s  ' %movie.get('plot outline')
            if movie.get('director'): movie_info += 'Directeurs.  %s.  ' %format_names(movie.get('director'))
            if movie.get('producer'): movie_info += 'Producteurs.  %s.  ' %format_names(movie.get('producer'))
            if movie.get('cast'): movie_info += 'Casting.  %s.  ' %format_names(movie.get('cast'))
            mic.say(movie_info)
            return
    mic.say('Impossible de trouver des informations sur le film demandé')
