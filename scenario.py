#OPEN-RISOP DATASET EXTRACTION
SCENARIO = "./Dataset/countervalue.csv"
import pandas as pd
import csv

class Event:
    def __init__(self):
        self.latitude = 0
        self.longitude = 0
        self.radius = 0

def get_radius(yld, hob):
    #return value expressed in km
    if yld == 100:
        if hob == 840:
            return 5.15
        else:
            return 3.62
    elif yld == 200:
        if hob == 1060:
            return 6.49
        else:
            return 4.56
    elif yld == 250:
        if hob == 1150:
            return 6.99
        else:
            return 4.91
    elif yld == 800:
        if hob == 1690:
            return 10.3
        else:
            return 7.24

def get_scenario(file=SCENARIO):
    #LATITUDE, LONGITUDE, NAME, DESCRIPTION, YIELD, HOB
    eventList = []
    with open(file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            e = Event()
            e.latitude = float(row[0])
            e.longitude = float(row[1])
            e.radius = get_radius(int(row[4]), int(row[5]))
            eventList.append(e)
        f.close()
    return eventList


if __name__ == '__main__':
    get_scenario()