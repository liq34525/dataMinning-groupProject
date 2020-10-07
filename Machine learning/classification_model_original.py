# Import packages
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras import optimizers
from keras.utils import to_categorical
import matplotlib.pyplot as plt
import numpy as np
import csv
import random


# -------------------
# LOAD DATA
#
# Load raw data from disk and convert them into X_train and Y_train
# Please note that some extra functions require uncommenting specific codes
# -------------------
X_train = []
Y_train = []

with open('rawData/allInfo.csv') as file:
    csv_reader = csv.reader(file, delimiter=',')
    line_count = 0
    for row in csv_reader:

        # Skip header line
        if line_count == 0:
            line_count += 1
            continue

        # Skip empty data
        if row[11] == '':
            continue
        if row[12] == '':
            continue


        # Extract time (in minute) info
        # An integer(unit: minute), ranged from 0 to 1440
        time = int(float(row[9]))
        hour = int(time / 60)
        minute = time % 60
        time_label = [hour, minute]

        # Extract date info
        # A one-hot vector of length 9
        month = int(row[0][5:7])
        month_label = [0, 0]
        if 5 <= month <= 10:
            month_label[0] = 1
        else:
            month_label[1] = 1

        weekday = row[3]
        weekday_label = 0
        if weekday == 'Monday':
            weekday_label = 1
        elif weekday == 'Tuesday':
            weekday_label = 2
        elif weekday == 'Wednesday':
            weekday_label = 3
        elif weekday == 'Thursday':
            weekday_label = 4
        elif weekday == 'Friday':
            weekday_label = 5
        elif weekday == 'Saturday':
            weekday_label = 6

        weekday_label = list(to_categorical(weekday_label, 7))

        date_label = month_label + weekday_label

        # Extract direction info
        # A one-hot vector of length 6
        # 0 represents unknown
        direction = row[7]
        direction_label = 0
        if direction == 'E/B':
            direction_label = 1
        elif direction == 'W/B':
            direction_label = 2
        elif direction == 'S/B':
            direction_label = 3
        elif direction == 'N/B':
            direction_label = 4
        elif direction == 'B/W':
            direction_label = 5

        direction_label = list(to_categorical(direction_label, 6))

        # Extract delay info
        # An integer, represents delay time in minutes
        delay = row[8]
        delay_label = 0
        if delay == '5~15':
            delay_label = 1
        elif delay == '15~30':
            delay_label = 2
        elif delay == '>30':
            delay_label = 3

        delay_label = list(to_categorical(delay_label, 4))

        # Extract temperature info
        # An integer
        temp = float(row[11])
        temp_label = round(temp)

        # Extract today weather info
        # A one-hot vector of length 16
        weather_today = row[12]
        weather_today_label = int(float(weather_today))

        # Extract yesterday weather info
        # A one-hot vector of length 16
        # 0 represents unknown
        weather_yesterday = row[13][10:]
        weather_yesterday_label = 0
        if weather_yesterday != 'None':
            weather_yesterday_label = int(weather_yesterday)

        # Put things together
        data_info = time_label + date_label + direction_label
        data_info.append(temp_label)
        data_info.append(weather_today_label)
        data_info.append(weather_yesterday_label)

        X_train.append(data_info)
        Y_train.append(delay_label)
        # print("line {0} done".format(line_count))
        line_count += 1

    print(f'Processed {line_count} lines.')

    X_train = np.asarray(X_train, dtype=float)
    Y_train = np.asarray(Y_train, dtype=int)
# -------------------
# End of LOAD DATA
# -------------------



# -------------------
# GENERATE TEST
# Generate test data from X_train and Y_train
# -------------------
X_test = []
Y_test = []

size = int(1000)
for i in range(size):
    index = int(random.random() * len(X_train))
    X_test.append(X_train[index])
    Y_test.append(Y_train[index])

    X_train = np.delete(X_train, index, axis=0)
    Y_train = np.delete(Y_train, index, axis=0)

X_test = np.asarray(X_test, dtype=float)
Y_test = np.asarray(Y_test, dtype=int)
# -------------------
# End of GENERATE TEST
# -------------------



# -------------------
# BUILD MODEL
# Build the neural network model
# -------------------

# Structure
model = Sequential()
model.add(Dense(30, kernel_initializer='he_normal', activation='relu'))
model.add(Dense(10, kernel_initializer='he_normal', activation='relu'))
model.add(Dense(4, activation='softmax'))

# Optimizers
opt1 = optimizers.Adam()
opt2 = optimizers.Adam(learning_rate=0.0001)
opt3 = optimizers.Adam(learning_rate=0.00001)

# Use different optimizers (defined above) if needed
model.compile(loss="categorical_crossentropy", optimizer=opt1, metrics=['accuracy'])
# -------------------
# End of BUILD MODEL
# -------------------



# -------------------
# TRAIN
# Train and evaluate the model
# -------------------
model.fit(X_train, Y_train, epochs=10) # Train model

model.evaluate(X_train, Y_train) # Evaluate training set
model.evaluate(X_test, Y_test) # Evaluate test set
# -------------------
# End of TRAIN
# -------------------

print("Program ends successfully.")
