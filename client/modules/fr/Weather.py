# -*- coding: utf-8-*-

# Copyright 2016 g10dras.

import re
import pyowm
from semantic.numbers import NumberService

WORDS = ["TEMPS", "METEO", "PREVISION"]
PRIORITY = 4

def handle(text, mic, profile):

    serviceNum = NumberService()
    
    def formatTimeStamp(unix_time):
        return datetime.fromtimestamp(unix_time).strftime("%B %d")
        
    def getWeeklyWeatherReport(forecast,loc,temp_unit='celsius',report='current'):
        weather_report = "Les prévisions météo de la semaine pour "+loc +". "
        rainy_days = len(forecast.when_rain())
        if rainy_days > 0:
            rainy_days_str = "Les jours de pluie sont. "
            for d in range(rainy_days):
                rain_day = forecast.when_rain()[d].get_reference_time()
                date_str = formatTimeStamp(rain_day)
                rainy_days_str += date_str + ". "

            weather_report += rainy_days_str
            date_str = ''
        
        most_rainy = forecast.most_rainy()
        if most_rainy:
            weather_report += "Vous aurez de forte pluie. "
            ref_time = most_rainy.get_reference_time()
            date_str = formatTimeStamp(ref_time)
            weather_report += date_str + ". "
            date_str = ''
            
        sunny_days = len(forecast.when_sun())
        if sunny_days > 0:
            sunny_days_str = "Les jours ensoleillés sont. "
            for d in range(sunny_days):
                sunny_day = forecast.when_rain()[d].get_reference_time()
                date_str = formatTimeStamp(sunny_day)
                sunny_days_str += date_str + ". "

            weather_report += sunny_days_str
            date_str = ''
        
        most_hot = forecast.most_hot()
        if most_hot:
            weather_report += "Vous aurez le plus chaud. "
            ref_time = most_hot.get_reference_time()
            date_str = formatTimeStamp(ref_time)
            weather_report += date_str + ". "
            date_str = ''
            
        most_windy = forecast.most_windy()
        if most_windy:
            weather_report += "Le jour avec le plus de vent sera. "
            ref_time = most_windy.get_reference_time()
            date_str = formatTimeStamp(ref_time)
            weather_report += date_str + ". "
            date_str = ''
            
        most_humid = forecast.most_humid()
        if most_humid:
            weather_report += "Le jour le plus humide sera. "
            ref_time = most_humid.get_reference_time()
            date_str = formatTimeStamp(ref_time)
            weather_report += date_str + ". "
            date_str = ''

        most_cold = forecast.most_cold()
        if most_cold:
            weather_report += "Le jour le plus agréable sera. "
            ref_time = most_cold.get_reference_time()
            date_str = formatTimeStamp(ref_time)
            weather_report += date_str + ". "
            date_str = ''
            
        return weather_report
        
    def getWeatherReport(weather,loc,temp_unit='celsius',report='current'):
        weather_report = 'Server Down.'
        wind = weather.get_wind()
        wind_speed = serviceNum.parseMagnitude(wind["speed"])
        humi = serviceNum.parseMagnitude(weather.get_humidity())
        clou = serviceNum.parseMagnitude(weather.get_clouds())
        stat = weather.get_status()
        detstat = weather.get_detailed_status()
        
        if report == 'current':
            temp = weather.get_temperature(temp_unit)
            temp_max = serviceNum.parseMagnitude(temp['temp_max'])
            temp_min = serviceNum.parseMagnitude(temp['temp_min'])
            curr_temp = serviceNum.parseMagnitude(temp['temp'])
            weather_report = "Météo pour "+loc+". Il fait actuellement "+stat+". Il y a une chande de "  \
                              +detstat+". La température actuelle est de "+curr_temp+" degré "  \
                              +temp_unit+". "+humi+" pourcent d'humidité. Vitesse du vent "  \
                              +wind_speed+". avec "+clou+" pourcent de nuage."
        
        elif report == 'tommorow':
            temp = weather.get_temperature(temp_unit)
            temp_morn = serviceNum.parseMagnitude(temp['morn'])
            temp_day = serviceNum.parseMagnitude(temp['day'])
            temp_night = serviceNum.parseMagnitude(temp['night'])
            weather_report = "Météo pour "+loc+". Demain il fera "+stat+". Il y aura une chance de "  \
                              +detstat+". La température durant la matinée sera de "+temp_morn+" degré "  \
                              +temp_unit+". La température durant la journée sera de "+temp_day+" degré "  \
                              +temp_unit+". et la Température dans la soirée sera de "+temp_night+" degré "  \
                              +temp_unit+". "+humi+" Pourcent d'humidité. Vitesse du vent "  \
                              +wind_speed+". avec "+clou+" pourcent de nuage."
        
        return weather_report
        
    if 'OpenWeatherMap' in profile:
        if 'api_key' in profile['OpenWeatherMap']:
            api_key = profile['OpenWeatherMap']['api_key']
        if 'city_name' in profile['OpenWeatherMap']:
            city_name = profile['OpenWeatherMap']['city_name']
        if 'country' in profile['OpenWeatherMap']:
            country = profile['OpenWeatherMap']['country']
        if 'temp_unit' in profile['OpenWeatherMap']:
            temp_unit = profile['OpenWeatherMap']['temp_unit']
                        
    owm = pyowm.OWM(api_key)
    
    if re.search(r"\b(ACTUELLEMENT|ACTUEL|ACTUELLE|AUJOURD'HUI|MAINTENANT)\b",text,re.IGNORECASE):
        cw = owm.weather_at_place(city_name+","+country)
        loc = cw.get_location().get_name()
        weather = cw.get_weather()
        weather_report = getWeatherReport(weather,loc,temp_unit,report='current')
        mic.say(weather_report)

    elif re.search(r'\b(DEMAIN)\b',text,re.IGNORECASE):
        forecast = owm.daily_forecast(city_name)
        fore = forecast.get_forecast()
        loc = fore.get_location().get_name()
        tomorrow = pyowm.timeutils.tomorrow()
        weather = forecast.get_weather_at(tomorrow)
        weather_report = getWeatherReport(weather,loc,temp_unit,report='tommorow')
        mic.say(weather_report)
        
    elif re.search(r'\b(SEMAINE|SEMAINES|PROCHAINEMENT)\b',text,re.IGNORECASE):
        forecast = owm.daily_forecast(city_name)
        fore = forecast.get_forecast()
        loc = fore.get_location().get_name()
        weather_report = getWeeklyWeatherReport(forecast,loc,temp_unit,report='weekly')
        mic.say(weather_report)
        
def isValid(text):
    return any(word in text.upper() for word in WORDS)
    
