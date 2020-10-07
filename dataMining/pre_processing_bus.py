import xlrd
import pandas as pd
import multiprocessing as mp
from multiprocessing import Pool
import os
import sys
sys.path.append(os.getcwd())
import dataMining.weatherRead


def handle_delay(delay):
    if 0 <= delay < 5:
        return "0~5"
    elif 5 <= delay < 15:
        return "5~15"
    elif 15 <= delay < 30:
        return "15~30"
    elif delay >= 30:
        return ">30"

def handle_time(time):
    if 0 <= time.hour < 4:
        return '0-4'
    elif 4 <= time.hour < 8:
        return '4-8'
    elif 8 <= time.hour < 12:
        return '8-12'
    elif 12 <= time.hour < 16:
        return '12-16'
    elif 16 <= time.hour < 20:
        return '16-20'
    elif 20 <= time.hour <= 24:
        return '20-24'

def handle_time_ML(time):
    return time.hour * 60 + time.minute

def handle_date(time, date):
    date = str(date)
    if time == '0-4':
        return date[0:10] + ' 00:00'
    elif time == '4-8':
        return date[0:10] + ' 04:00'
    elif time == '8-12':
        return date[0:10] + ' 08:00'
    elif time == '12-16':
        return date[0:10] + ' 12:00'
    elif time == '16-20':
        return date[0:10] + ' 16:00'
    elif time == '20-24':
        return date[0:10] + ' 20:00'

def handle_date_ML(date):
    date = str(date)
    return date[0:10] + ' 20:00'

def handle_direction(direction):
    direction = str(direction).upper()
    if "/" not in direction:
        return direction[:1] + "/" + direction[1:]
    else:
        return direction


def process_row(row_index, df):
    df.ix[row_index, "Min Delay Range"] = handle_delay(df.ix[row_index, "Min Delay"])
    df.ix[row_index, "TimeML"] = handle_time_ML(df.ix[row_index, "Time"])
    df.ix[row_index, "DateML"] = handle_date_ML(df.ix[row_index, "Report Date"])

    df.ix[row_index, "Time"] = handle_time(df.ix[row_index, "Time"])
    df.ix[row_index, "Report Date"] = handle_date(df.ix[row_index, "Time"], df.ix[row_index, "Report Date"])
    df.ix[row_index, "Direction"] = handle_direction(df.ix[row_index, "Direction"])
    return df


def read_excel(path, cols):
    wb = xlrd.open_workbook(path)
    sheets = wb.sheet_names()
    df = pd.DataFrame()
    for i in range(len(sheets)):
        df_temp = pd.read_excel(path, sheet_name=i, usecols=cols)
        df = df.append(df_temp, ignore_index=True)
    return df


def excel_reader_helper(path, col):
    print("loading {0}".format(path))
    input_path = "rawData/busDelayInfo/ttc-streetcar-delay-data-{0}.xlsx".format(path)
    result = read_excel(input_path, col)
    return result


def read_year_data(start, end):
    data = []
    cols = ["Report Date", "Route", "Time", "Day", "Location", "Incident", "Min Delay",
            "Direction"]
    with Pool(processes=mp.cpu_count()) as pool:
        for i in pool.starmap(excel_reader_helper, [(j, cols) for j in range(start, end + 1)]):
            data.append(i)

    return data


def processing_single_year(data, year):
    for i in range(len(data)):
        process_row(i, data)
        progress = round((i / len(data)) * 100)

        # progressing bar
        print("\rprocessing year {3}: [{0}{1}]: {2}\t %".format("#" * (progress // 10), " " * (10 - progress // 10),
                                                                round(i / len(data) * 100, 3), year), end='',
              flush=True)
    print()


if __name__ == '__main__':
    start = 2014
    end = 2019
    num_thread = mp.cpu_count()
    if os.path.isfile('rawData/allInfo.csv'):
        os.remove('rawData/allInfo.csv')
        print("previous result removed")

    data = read_year_data(start, end)
    for i in range(start, end + 1):
        print("start processing year:{0}".format(i))
        processing_single_year(data[i - start], i)
        data[i - start] = data[i - start].rename(columns={"Report Date": "Date/Time"})
        dataMining.weatherRead.readWeather(i)
        df1 = pd.read_csv('rawData/cleanWeather.csv')
        if df1.empty:
            print('An error occurred while cleaning up weather data.')
        else:
            all_info = pd.merge(data[i - start], df1)
            if os.path.isfile('rawData/allInfo.csv'):  # if the file exist, not insect header
                all_info.to_csv("rawData/allInfo.csv", mode='a', index=0, header=False)
            else:
                all_info.to_csv("rawData/allInfo.csv", mode='a', index=0, header=True)
