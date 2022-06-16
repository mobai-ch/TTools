import pickle
import os, sys
from typing import List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, tzinfo
import pytz
from tqdm import tqdm
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

'''
index of the row data: Only available in the date before 2016.12.30

'VendorID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime','passenger_count', 'trip_distance', 'pickup_longitude',
'pickup_latitude', 'RatecodeID', 'store_and_fwd_flag','dropoff_longitude', 'dropoff_latitude', 'payment_type', 'fare_amount',
'extra', 'mta_tax', 'tip_amount', 'tolls_amount','improvement_surcharge', 'total_amount'

'''

class NYCTaxiTool:
    def __init__(self) -> None:
        self.rawDataDir = "./RawData"

    def GetTrips(self, sTime: datetime, hours: int) -> List:
        '''
            Get trips in raw data from sTime to sTime + hours, all time should be integral point 
        '''
        year, day = sTime.year, sTime.day
        eTime = sTime + timedelta(hours=hours)
        # read csv file by pandas
        fileName = "yellow_tripdata_{}-{}.csv".format(year, str(day).zfill(2))
        filePath = os.path.join(self.rawDataDir, fileName)
        trip_Df = pd.read_csv(filePath)
        trip_Df["tpep_pickup_datetime"] = pd.to_datetime(trip_Df["tpep_pickup_datetime"], utc=False).dt.tz_localize('America/New_York')
        trip_Df["tpep_dropoff_datetime"] = pd.to_datetime(trip_Df["tpep_dropoff_datetime"], utc=False).dt.tz_localize('America/New_York')
        trip_Df["tpep_pickup_datetime"] = (trip_Df["tpep_pickup_datetime"].astype('int64')//1e9).astype('int64')
        trip_Df["tpep_dropoff_datetime"] = (trip_Df["tpep_dropoff_datetime"].astype('int64')//1e9).astype('int64')
        trip_PDf = trip_Df[trip_Df["tpep_pickup_datetime"] > int(sTime.timestamp())]
        trip_PDf = trip_Df[trip_Df["tpep_pickup_datetime"] <= int(eTime.timestamp())]
        trip_VDf = trip_Df[trip_Df["tpep_dropoff_datetime"] > int(sTime.timestamp())]
        trip_VDf = trip_Df[trip_Df["tpep_dropoff_datetime"] <= int(eTime.timestamp())]

        print("Raw csv file from {} is loaded, convert it to csv file".format(sTime))
        
        # print(trip_PDf["tpep_pickup_datetime"][176])
        # Record the pedestrian time
        trip_Pedestrian_list = []
        for row in tqdm(trip_PDf.iterrows()):
            row = row[1]
            if not row.loc["pickup_latitude"] == 0.0:
                trip_Pedestrian_list.append([int(row.loc["tpep_pickup_datetime"]), str(0), row.loc["pickup_latitude"], \
                    row.loc["pickup_longitude"], row.loc["dropoff_latitude"], row.loc["dropoff_longitude"]])

        trip_Vehicle_list = []
        for row in tqdm(trip_VDf.iterrows()):
            row = row[1]
            if not row.loc["dropoff_latitude"] == 0.0:
                trip_Vehicle_list.append([int(row.loc["tpep_dropoff_datetime"]), str(1), row.loc["dropoff_latitude"],\
                    row.loc["dropoff_longitude"], 0, 0])

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
    nycTaxiTool = NYCTaxiTool()
    nycTaxiTool.run(sTime, 2, 1)

if __name__ == '__main__':
    run()