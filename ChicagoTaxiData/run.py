'''
File format: 
Trip ID,Taxi ID,Trip Start Timestamp,Trip End Timestamp,Trip Seconds,Trip Miles,Pickup Census Tract,Dropoff Census Tract,
Pickup Community Area,Dropoff Community Area,Fare,Tips,Tolls,Extras,Trip Total,Payment Type,Company,Pickup Centroid Latitude,
Pickup Centroid Longitude,Pickup Centroid Location,Dropoff Centroid Latitude,Dropoff Centroid Longitude,Dropoff Centroid  Location
'''

from ast import parse
from cmath import nan
import os, sys
from numpy import NAN
import pandas as pd
from datetime import timedelta, datetime
from tqdm import tqdm
import pytz
import numpy as np
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

class ChicagoTaxiUtil:
    def __init__(self) -> None:
        self.RawDataPath = "./RawData/Taxi_Trips.csv"
        self.rawData = pd.read_csv(self.RawDataPath)
        self.rawData = self.rawData.fillna(1000000)
        # Convert the time string to the timestamp value
        self.rawData['Trip Start Timestamp'] = pd.to_datetime(self.rawData['Trip Start Timestamp'], utc=True).dt.tz_convert('America/Chicago')
        self.rawData['Trip End Timestamp'] = pd.to_datetime(self.rawData['Trip End Timestamp'], utc=True).dt.tz_convert('America/Chicago')
        self.rawData['Trip Start Timestamp'] = (self.rawData['Trip Start Timestamp'].astype('int64')//1e9).astype('int64')
        self.rawData['Trip End Timestamp'] = (self.rawData['Trip End Timestamp'].astype('int64')//1e9).astype('int64')

    def GetTrips(self, sTime: datetime, hours: int):
        '''
        Input start time and time slice, return all requests 
        '''
        eTime = sTime + timedelta(hours=hours)

        # get all requests in range
        trip_PDf = self.rawData[self.rawData['Trip Start Timestamp'] > int(sTime.timestamp())]
        trip_PDf = trip_PDf[trip_PDf['Trip Start Timestamp'] <= int(eTime.timestamp())]

        trip_VDf = self.rawData[self.rawData['Trip End Timestamp'] > int(sTime.timestamp())]
        trip_VDf = trip_VDf[trip_VDf['Trip End Timestamp'] <= int(eTime.timestamp())]

        print("Raw csv file from {} to {} is converted it to csv file".format(sTime, eTime))

        # Convert the dataframe to a list
        trip_Pedestrian_list = []
        for row in trip_PDf.iterrows():
            row = row[1]
            if not (row["Pickup Centroid Longitude"] == 1000000 or row["Dropoff Centroid Longitude"] == 1000000):
                trip_Pedestrian_list.append([int(row.loc['Trip Start Timestamp']), str(0), row.loc['Pickup Centroid Latitude'], \
                    row.loc['Pickup Centroid Longitude'], row.loc['Dropoff Centroid Latitude'], row.loc['Dropoff Centroid Longitude']])

        trip_Vehicle_list = []
        for row in trip_VDf.iterrows():
            row = row[1]
            if not (row["Pickup Centroid Longitude"] == 1000000 or row["Dropoff Centroid Longitude"] == 1000000):
                trip_Pedestrian_list.append([int(row.loc['Trip End Timestamp']), str(1),\
                    row.loc['Dropoff Centroid Latitude'], row.loc['Dropoff Centroid Longitude'], 0, 0])

        return trip_Pedestrian_list + trip_Vehicle_list

    def run(self, sTime, hours_add, add_times):
        for i in range(add_times):
            print("Collecting request from {} to {}".format(sTime, sTime + timedelta(hours=hours_add)))
            requestList = self.GetTrips(sTime, hours_add)
            requestList = pd.DataFrame(np.array(requestList), index=None)
            requestList = requestList.sort_values(by=0, ascending=True)
            self.saveRequstFile(sTime, hours_add, requestList)
            sTime += timedelta(hours=hours_add)

    def saveRequstFile(self, sTime: datetime, hours, requestList: pd.DataFrame):
        processedDirPath = "./ProcessedData"
        if not os.path.exists(processedDirPath):
            os.mkdir(processedDirPath)
        eTime = sTime + timedelta(hours=hours)
        sTimeStr = sTime.strftime("%Y-%m-%d-%H-%M-%S")
        eTimeStr = eTime.strftime("%Y-%m-%d-%H-%M-%S")
        fileName = "{}_{}.csv".format(sTimeStr, eTimeStr)
        requestList.to_csv(os.path.join(processedDirPath, fileName), index=None, header=None)

def run():
    parse = argparse.ArgumentParser()
    parse.add_argument("-t")
    args = parse.parse_args()
    timeStr = args.t
    sTime = datetime.strptime(timeStr, "%Y-%m-%d %H:%M")
    sTime.replace(tzinfo=pytz.timezone('America/Chicago'))
    chicagoTaxiTool = ChicagoTaxiUtil()
    chicagoTaxiTool.run(sTime, 2, 1)

if __name__ == '__main__':
    run()
