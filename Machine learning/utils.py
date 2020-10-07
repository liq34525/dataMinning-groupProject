import numpy as np
import csv

from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt


def process_location():
    with open('Local ML data/allInfo.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        line_count = 0
        locations = []

        for row in csv_reader:

           # Skip header line
            if line_count == 0:
                line_count += 1
                continue

            location = row[4].lower()

            location = location.strip('`,./ ')

            location = location.replace(' ', '')
            location = location.replace('.', '')
            location = location.replace('-', '')
            location = location.replace('/', '')
            location = location.replace('@', '')
            location = location.replace(',', '')
            location = location.replace('[', '')
            location = location.replace(']', '')
            location = location.replace('(', '')
            location = location.replace(')', '')
            location = location.replace('&', '')


            location = location.replace('line', '')
            location = location.replace('route', '')
            location = location.replace('and', '')
            location = location.replace('at', '')
            location = location.replace('ave', '')
            location = location.replace('in', '')
            location = location.replace('inthe', '')
            location = location.replace('inside', '')
            location = location.replace('rd', '')
            location = location.replace('road', '')
            location = location.replace('street', '')
            location = location.replace('st', '')
            location = location.replace('of', '')
            location = location.replace('stn', '')
            location = location.replace('station', '')
            location = location.replace('niagra', 'niagara')
            location = location.replace('loop', '')

            location = location.replace('west', 'w')
            location = location.replace('east', 'e')
            location = location.replace('north', 'n')
            location = location.replace('south', 's')

            locations.append(location)

        enc = OneHotEncoder(handle_unknown='ignore')
        locations = np.reshape(locations, (-1, 1))

        enc.fit(locations)
        return locations, enc

def stats():
    with open('Local ML data/allInfo.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        line_count = 0
        weathers = []
        delays = []

        for row in csv_reader:

            # Skip header line
            if line_count == 0:
                line_count += 1
                continue

            weather = int(row[9])
            weathers.append(weather)

            delay = row[7]
            delays.append(delay)

            line_count += 1

        return weathers, delays
