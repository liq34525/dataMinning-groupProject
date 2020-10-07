import pandas as pd
import xlrd
import dataMining.weatherRead
import os
import multiprocessing as mp

IS_MULTITHREAD = True

def make_allInfo(year):
    if IS_MULTITHREAD: lock.acquire()
    print("processing year: {0}".format(year))
    if IS_MULTITHREAD:lock.release()

    wb = xlrd.open_workbook("rawData/busDelayInfo/ttc-streetcar-delay-data-{0}.xlsx".format(year))
    sheets = wb.sheet_names()
    df = pd.DataFrame()
    for i in range(len(sheets)):
        df_temp = pd.read_excel("rawData/busDelayInfo/ttc-streetcar-delay-data-{0}.xlsx".format(year), sheet_name=i,
                                usecols=["Report Date", "Route", "Time", "Day", "Location", "Incident", "Min Delay",
                                         "Direction"])
        df = df.append(df_temp)

    df.drop(df[df.loc[:, "Min Delay"] > 100].index)
    df.dropna(axis=0, how='any', inplace=True)


    min_delay = df.loc[:, "Min Delay"]

    delay_classify = []
    for i in min_delay:
        if 0 <= i < 5:
            delay_classify.append("0~5")
        elif 5 <= i < 15:
            delay_classify.append("5~15")
        elif 15 <= i < 30:
            delay_classify.append("15~30")
        elif i >= 30:
            delay_classify.append(">30")
        else:
            df.drop()


    delayTime = df.loc[:, 'Time']
    newTime = []

    for i in delayTime:

        if 0 <= i.hour < 4:
            newTime.append('0-4')
        elif 4 <= i.hour < 8:
            newTime.append('4-8')
        elif 8 <= i.hour < 12:
            newTime.append('8-12')
        elif 12 <= i.hour < 16:
            newTime.append('12-16')
        elif 16 <= i.hour < 20:
            newTime.append('16-20')
        elif 20 <= i.hour <= 24:
            newTime.append('20-24')

    dateTime = df.loc[:, 'Report Date']
    newDateTime = []

    index = 0
    for i in dateTime:
        if newTime[index] == '0-4':
            newDateTime.append(str(i)[0:10] + ' 00:00')
        elif newTime[index] == '4-8':
            newDateTime.append(str(i)[0:10] + ' 04:00')
        elif newTime[index] == '8-12':
            newDateTime.append(str(i)[0:10] + ' 08:00')
        elif newTime[index] == '12-16':
            newDateTime.append(str(i)[0:10] + ' 12:00')
        elif newTime[index] == '16-20':
            newDateTime.append(str(i)[0:10] + ' 16:00')
        elif newTime[index] == '20-24':
            newDateTime.append(str(i)[0:10] + ' 20:00')
        index += 1

    direction = df.loc[:, 'Direction']
    newDirection = []
    for i in direction:
        i.upper()
        if i.find('/') == -1:
            newI = i[:1] + "/" + i[1:]
            newDirection.append(newI)
        else:
            newDirection.append(i)

    bus_data = pd.DataFrame(
        {'Date/Time': newDateTime, 'Route': df.loc[:, 'Route'], "Time": newTime,
         "Day": df.loc[:, 'Day'], 'Location': df.loc[:, 'Location'], "Incident": df.loc[:, 'Incident'],
         "Min Delay Range": delay_classify,
         "Min Delay": df.loc[:, "Min Delay"], 'Direction': newDirection})

    readWeather = dataMining.weatherRead.readWeather(year)
    df1 = pd.read_csv('rawData/cleanWeather.csv')

    #avoid merging at a same time
    if IS_MULTITHREAD: lock.acquire()
    if df1.empty:
        print('An error occurred while cleaning up weather data.')
    else:
        all_info = pd.merge(bus_data, df1)
        if os.path.isfile('rawData/allInfo-1.csv'):            # if the file exist, not insect header
            all_info.to_csv("rawData/allInfo-1.csv", mode='a', index=0, header=False)
        else:
            all_info.to_csv("rawData/allInfo-1.csv", mode='a', index=0, header=True)


    if IS_MULTITHREAD: lock.release()


def init(l):
    global lock
    lock = l

if __name__ == '__main__':

    years = range(2014,2020)
    if(IS_MULTITHREAD):
        l = mp.Lock()
        num_thread = mp.cpu_count()
        pool = mp.Pool( processes=num_thread, initializer=init, initargs=(l,))          #create thread pool and set up lock for all thread
        pool.map(make_allInfo, years)       #map the thread to each year data
        pool.close()
        pool.join()


    else:
        # for year in years:
        #     make_allInfo(year)

        # For testing
         make_allInfo('2017')    #run single years
    print('\nProcess finished!\n')