import pandas as pd
import numpy as np

from pandas import ExcelWriter, DataFrame
from pandas import ExcelFile


def map_weather(ele, weather_list):
    if isinstance(ele, str):
        arr = ele.split(",")
        for k in arr:
            if k == "Clear":
                weather_list[0] = True
            if k == "Mainly Clear":
                weather_list[1] = True
            if k == "Mostly Cloudy":
                weather_list[2] = True
            if k == "Cloudy":
                weather_list[3] = True
            if k == "Drizzle":
                weather_list[4] = True
            if k == "Freezing Drizzle":
                weather_list[5] = True
            if k == "Rain":
                weather_list[6] = True
            if k == "Freezing Rain":
                weather_list[7] = True
            if k == "Fog":
                weather_list[8] = True
            if k == "Snow Grains":
                weather_list[9] = True
            if k == "Snow Showers":
                weather_list[10] = True
            if k == "Snow":
                weather_list[11] = True
            if k == "Blowing Snow":
                weather_list[12] = True
            if k == "Moderate Snow":
                weather_list[13] = True
            if k == "Heavy Snow":
                weather_list[14] = True
            if k == "Ice Pellets":
                weather_list[15] = True
            if k == "Moderate Ice Pellets":
                weather_list[16] = True,


def readWeatherUtil(month, year):
    df = pd.read_csv('rawData/weather/en_climate_hourly_ON_6158731_' + month + '-' + year + '_P1H.csv',
                     usecols=["Date/Time", "Temp (°C)", "Weather"])

    date = df.loc[:, "Date/Time"]
    tempe = df.loc[:, "Temp (°C)"]
    weather = df.loc[:, "Weather"]
    newDate = []
    newTemp = []
    newWeather = []
    previousWeather = [[], [], [], [], [], []]

    for i in range(0, len(date) - 1, 4):
        newDate.append(date[i])
        sumTemp = sum([tempe[i], tempe[i + 1], tempe[i + 2], tempe[i + 3]])
        newTemp.append(round((sumTemp / 4), 2))
        weatherMap = [False] * 17
        map_weather(weather[i], weatherMap)
        map_weather(weather[i + 1], weatherMap)
        map_weather(weather[i + 2], weatherMap)
        map_weather(weather[i + 3], weatherMap)
        newWeather.append(weatherMap),

    for x in range(6, len(newWeather) - 1, 6):
        previousWeatherMap = [False] * 17
        temp = []
        for j in range(0, 6):
            previousWeatherMap = np.logical_or(previousWeatherMap[0], newWeather[x + j]),

        temp = previousWeatherMap[0]

        for z in range(0, 6):
            previousWeather.append(list(temp)),

    tableWeather = []
    tablePrevWeather = []
    for j in newWeather:
        j = pd.Series(j)
        tableWeather.append(j.where(j == True).last_valid_index()),

    for j in previousWeather:
        j = pd.Series(j)
        tablePrevWeather.append("yesterday:"+str(j.where(j == True).last_valid_index())),

    weather_data = {'Date/Time': newDate, 'Temp (°C)': newTemp, 'Weather': tableWeather,
                    'YesterdayWeather': tablePrevWeather}
    new_df = DataFrame(weather_data, columns=['Date/Time', 'Temp (°C)', 'Weather', 'YesterdayWeather'])
    return new_df,


def readWeather(year):
    frames = []
    for i in range(1, 13):
        index = ''
        if i < 10:
            index = '0' + str(i),
        else:
            index = str(i),
        frames.append(readWeatherUtil(index[0], str(year))[0])

    result = pd.concat(frames)
    result.to_csv("rawData/cleanWeather.csv", index=0, header=True)

# export_csv = new_df.to_csv(r'~/Desktop/export_dataframe.csv', index=None, header=True)
