import os
import tweepy
import requests
from ics import Calendar
from datetime import datetime, timezone, timedelta
import math
import json
from PIL import Image, ImageDraw, ImageFont
import csv


def main(event, context):
    schedules = scheduleGetter()
    text = textComposer(schedules)

    # tweetPoster("text composed successfully", 0)

    weatherCodes, timePalette, weatherInfo = GetWeather()
    ImageComposer(weatherCodes, timePalette, weatherInfo)

    # tweetPoster(text, "/tmp/weather.png")
    # tweetPoster(text, "weather.png")


def tweetPoster(texts, images):
    API_KEY = "api_key"
    CLIENT_ID = "client_id"
    CLIENT_ID_SECRET = "client_id_secret"
    API_KEY_SECRET = "api_key_secret"
    BEARER_TOKEN = "bearer_token"
    ACCESS_TOKEN = "access_token"
    ACCESS_TOKEN_SECRET = "access_token_secret"

    auth = tweepy.OAuthHandler(consumer_key=API_KEY,
                               consumer_secret=API_KEY_SECRET,
                               access_token=ACCESS_TOKEN,
                               access_token_secret=ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    client = tweepy.Client(bearer_token=BEARER_TOKEN,consumer_key=API_KEY,consumer_secret=API_KEY_SECRET,access_token=ACCESS_TOKEN,access_token_secret=ACCESS_TOKEN_SECRET)
    
    if images == 0:
        api.update_status(texts)
    else:
        media = api.media_upload(images)
        client.create_tweet(text=texts, media_ids=[media.media_id])
        # api.update_status_with_media(texts, images)

def scheduleGetter():
    tz_jst = timezone(timedelta(hours=9))
    dn = datetime.now().astimezone(tz_jst)
    ics_file_url = "https://calendar.google.com/calendar/ical/secret.group.calendar.google.com/public/basic.ics"

    ics_file_text = requests.get(ics_file_url).text
    events = Calendar(ics_file_text)
    upcoming_events = Calendar()

    for event in events.events:
        if event.begin.datetime.astimezone(tz_jst) >= dn:
            upcoming_events.events.add(event)

    upcoming_events_sorted = upcoming_events.timeline
    upcoming_events_reduced = [[0, 0], [0, 0], [0, 0], [0, 0]]
    for i in range(0, 4):
        upcoming_events_reduced[i][0] = list(upcoming_events_sorted)[i].name
        upcoming_events_reduced[i][1] = list(upcoming_events_sorted)[i].begin.datetime.astimezone(tz_jst)
    return upcoming_events_reduced


def textComposer(events):
    tz_jst = timezone(timedelta(hours=+9))
    dn = datetime.now().astimezone(tz_jst)

    text = str(dn.month) + "月" + str(dn.day) + "日 " + str(dn.hour) + "時\n "
    text += "\n\n"
    for i in range(0, 4):
        dif = events[i][1] - dn
        if events[i][1].hour == 23 and events[i][1].minute == 45:
            shujitsu = 1
        else:
            shujitsu = 0

        if dif.days >= 2:
            text += "🟢"
        elif dif.days == 1:
            text += "🟡"
        elif dif.days == 0:
            text += "🔴"

        text += "  " + events[i][0] + " ... "
        text += str(events[i][1].month) + "/" + str(events[i][1].day) + " "
        if shujitsu != 1:
            text += str(events[i][1].hour) + "時 "
        text += "(残り " + str(dif.days) + "日"
        if shujitsu != 1:
            text += str(int(math.floor(dif.seconds / 3600))) + "時間"
        text += ")\n\n"

    return text


def GetWeather():
    jma_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/280000.json"
    jma_json = requests.get(jma_url).json()
    weatherCode = [0, 0, 0]
    date = ["----------T--:00:00+09:00", "----------T--:00:00+09:00", "----------T--:00:00+09:00"]
    weather = [0, 0, 0]

    try:
        for i in range(3):
            date[i] = jma_json[0]["timeSeries"][0]["timeDefines"][i]
        for i in range(3):
            weatherCode[i] = jma_json[0]["timeSeries"][0]["areas"][0]["weatherCodes"][i]
        for i in range(3):
            weather[i] = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][i]
    except IndexError:
        for i in range(2):
            date[i] = jma_json[0]["timeSeries"][0]["timeDefines"][i]
        for i in range(2):
            weatherCode[i] = jma_json[0]["timeSeries"][0]["areas"][0]["weatherCodes"][i]
        for i in range(2):
            weather[i] = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][i]

    print(weatherCode[0], weatherCode[1], weatherCode[2])
    # print(type(date[0])) # date is read as "str"
    print(date[0], date[1], date[2])
    for i in range(3):
        print(date[i][5:7], date[i][8:10], date[i][11:13])
    print(weather[0], weather[1], weather[2])

    return weatherCode, date, weather[0]


def ImageComposer(weatherStats, dateStr, weatherStr):
    f = open("table.csv", encoding="utf-8-sig")
    box = csv.DictReader(f)
    dict = [row for row in box]

    source_dir = ""

    bg = Image.open(source_dir + "weather/bg.png")
    right_array = Image.open(source_dir + "weather/right-arrow.png").resize((40, 40))

    try:
        weather_left = Image.open(source_dir + "weather/" + dict[0][str(weatherStats[0])] + ".png").resize((128, 128))
        bg.paste(weather_left, (75, 32), weather_left)
    except KeyError:
        qq = 0

    try:
        weather_middle = Image.open(source_dir + "weather/" + dict[0][str(weatherStats[1])] + ".png").resize((64, 64))
        bg.paste(weather_middle, (295, 32), weather_middle)
    except KeyError:
        qq = 0

    try:
        weather_right = Image.open(source_dir + "weather/" + dict[0][str(weatherStats[2])] + ".png").resize((64, 64))
        bg.paste(weather_right, (451, 32), weather_right)
    except KeyError:
        qq = 0

    bg.paste(right_array, (229, 47), right_array)
    bg.paste(right_array, (385, 47), right_array)

    numberfont1 = ImageFont.truetype(source_dir + 'weather/font.ttf', 24)
    numberfont2 = ImageFont.truetype(source_dir + 'weather/font.ttf', 15)

    draw = ImageDraw.Draw(bg)
    draw.text((139, 28), dateStr[0][5:7] + "/" + dateStr[0][8:10] + " " + dateStr[0][11:13] + ":00", "white", font=numberfont1, anchor="md")
    draw.text((327, 23), dateStr[1][5:7] + "/" + dateStr[1][8:10] + " " + dateStr[1][11:13] + ":00", "white", font=numberfont2, anchor="md")
    draw.text((483, 23), dateStr[2][5:7] + "/" + dateStr[2][8:10] + " " + dateStr[2][11:13] + ":00", "white", font=numberfont2, anchor="md")

    # bg.save(source_dir + "/tmp/weather.png")
    bg.save(source_dir + "weather.png")

main(1,1)
