import os
import tweepy
import requests
from ics import Calendar
from datetime import datetime, timezone, timedelta
import math
import json
from PIL import Image, ImageDraw, ImageFont
import csv
import time

#Constants := 0 for Kobe, 1 for Osaka, 2 for Kyoto in any array


def GetWeather():
    urls = ["280000", "270000", "260000"] 
    weatherCode = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] #weatherCode[DATE][PLACE] 
    date = ["----------T--:00:00+09:00", "----------T--:00:00+09:00", "----------T--:00:00+09:00", "----------T--:00:00+09:00"]
    jma_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/"
    
    for j in range(3):
        time.sleep(2)
        jma_json = requests.get(jma_url + urls[j] + ".json").json()

        try:
            for i in range(3):
                date[i] = jma_json[0]["timeSeries"][0]["timeDefines"][i]
            for i in range(3):
                weatherCode[i][j] = jma_json[0]["timeSeries"][0]["areas"][0]["weatherCodes"][i]
        except IndexError:
            for i in range(2):
                date[i] = jma_json[0]["timeSeries"][0]["timeDefines"][i]
            for i in range(2):
                weatherCode[i][j] = jma_json[0]["timeSeries"][0]["areas"][0]["weatherCodes"][i]
    
    # print(type(date[0])) # date is read as "str"
    return weatherCode, date


def imageComposer(weatherCode, date):
    image_height = 296
    position = [(230, 174), (568, 456), (857, 144)]
    place = ("kobe", "osaka", "kyoto")
    gap_icon_text = -5
    gap_icon_place = 5
    text_height_par_width = 0.7
    
    f = open("table_new.csv", encoding="utf-8-sig")
    box = csv.DictReader(f)
    dict = [row for row in box]

    bg = Image.open("weather/imgset1/bg.jpg")
    map = Image.open("weather/imgset1/maps3.png").resize((1280, 856))
    bg.paste(map, (0, 0), map)

    for i in range(3):
        place_text = Image.open("weather/imgset1/text/" + place[i] + ".png")
        weather_icon = Image.open("weather/imgset1/icon/" + dict[1][str(weatherCode[i])] + ".png")
        weather_text = Image.open("weather/imgset1/text/" + dict[0][str(weatherCode[i])] + ".png")
        
        zoom_icon = image_height / weather_icon.height
        weather_icon_new = weather_icon.resize((int(weather_icon.width * zoom_icon), int(weather_icon.height * zoom_icon)))

        zoom_text = weather_icon_new.width / weather_text.width
        weather_text_new = weather_text.resize((int(weather_text.width * zoom_text), int(weather_text.height * zoom_text)))

        zoom_place = weather_icon_new.width / place_text.width
        place_text_new = place_text.resize((int(place_text.width * zoom_place), int(place_text.height * zoom_place * text_height_par_width)))
        
        bg.paste(weather_icon_new, position[i], weather_icon_new)
        bg.paste(weather_text_new, (position[i][0], position[i][1] + image_height + gap_icon_text), weather_text_new)
        bg.paste(place_text_new, (position[i][0], position[i][1] - place_text_new.height - gap_icon_place) , place_text_new)


    draw = ImageDraw.Draw(bg)
    font_typewriter = ImageFont.truetype('weather/imgset1/font_typewriter.ttf', 21)
    draw.text((128, 703), date[0][8:10], "black", font = font_typewriter)
    draw.text((183, 699), date[0][11:13], "black", font = font_typewriter)
    draw.text((294, 706), date[1][8:10], "black", font = font_typewriter)
    draw.text((339, 712), date[1][11:13], "black", font = font_typewriter)
    bg.save("weather/imgset1/generated.png")


k=1
# weatherStats, dateStrs = GetWeather()
# print(weatherStats[k][0], weatherStats[k][1], weatherStats[k][2])
# print(dateStrs)
# imageComposer((weatherStats[k][0], weatherStats[k][1], weatherStats[k][2]), (dateStrs[k], dateStrs[k+1]))
imageComposer((201, 204, 207), ("12345678-S1AM45", "12345678PL1E-45")) # FOR TEST USE ONLY
