from email import header
import os, sys
import pandas as pd
from DataUtil.DataUtil import DataUtil
from datetime import datetime, timedelta
import pytz
from tqdm import tqdm
import numpy as np

class Processor:
    def __init__(self) -> None:
        self.rawDataDir = "./RawData"
        self.dataUtil = DataUtil()
        print("Road network link is loaded")
        self.dict = self.dataUtil.dict
        if not os.path.exists("./ProcessedData"):
            os.mkdir("./ProcessedData")
    
    def ProcessDataInPeriod(self, sTime: datetime, eTime: datetime):
        print("Process data from {} to {}".format(sTime, eTime))
        year, month = sTime.year, sTime.month
        date = "{}{}.csv".format(year, str(month).zfill(2))
        InfoInDate = pd.read_csv(os.path.join(self.rawDataDir, date))
        print("Information in {} is loaded".format(date))
        InfoInDate["TIME"] = pd.to_datetime(InfoInDate["TIME"], utc=True).dt.tz_convert('America/Chicago')
        InfoInDate["TIME"] = (InfoInDate["TIME"].astype('int64')//1e9).astype('int64')
        InfoInDate = InfoInDate[InfoInDate["TIME"] > int(sTime.timestamp())]
        InfoInDate = InfoInDate[InfoInDate["TIME"] <= int(eTime.timestamp())]
        Updates = []
        print("Number of Updates: {}".format(InfoInDate.shape[0]))
        for row in tqdm(InfoInDate.iterrows()):
            row = row[1]
            edges, speed = self.ProcessLine(row)
            for edge in edges:
                (s, d) = edge
                if speed != -1 and speed != 0:
                    Updates.append([str(int(s)), str(int(d)), self.dict[s][d]/(speed/3.6), speed, str(row.loc["TIME"])])
        self.saveData(Updates, sTime, eTime)
    
    def saveData(self, Updates, sTime: datetime, eTime: datetime):
        Updates = np.array(Updates)
        Updates = pd.DataFrame(Updates)
        sTimeStr = sTime.strftime("%Y-%m-%d-%H-%M-%S")
        eTimeStr = eTime.strftime("%Y-%m-%d-%H-%M-%S")
        Updates.to_csv("./ProcessedData/{}-{}.csv".format(sTimeStr, eTimeStr), header=None, index=None)
        print("Traffic file from {} to {} is generated".format(sTime, eTime))

    def ProcessLine(self, row):
        [slat, slon] = [row.loc["START_LATITUDE"], row.loc["START_LONGITUDE"]]
        [elat, elon] = [row.loc["END_LATITUDE"], row.loc["END_LONGITUDE"]]
        speed = row.loc["SPEED"]
        edges = self.dataUtil.getEdgeList([slat, slon], [elat, elon])
        return edges, speed

    def run(self, sTimeStr, hours):
        sTime = datetime.strptime(sTimeStr, "%Y-%m-%d %H:%M")
        sTime.replace(tzinfo=pytz.timezone('America/Chicago'))
        eTime = sTime + timedelta(hours=hours)
        self.ProcessDataInPeriod(sTime, eTime)

