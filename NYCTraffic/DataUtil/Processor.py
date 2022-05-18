'''
Process all traffic information and covert all of them into traffic data
'''

import pickle
import os, sys
import pandas as pd
from datetime import datetime, timedelta
import pytz
import numpy as np
from DataUtil.DataUtil import LinkDataUtil

class Processor:
    def __init__(self, initLinks: bool) -> None:
        if initLinks:
            if not os.path.exists("./linkinfo.pickle"):
                self.linkUtil = LinkDataUtil()
                self.linkUtil.readAllLinkInfo()
        self.rawDataDir = "./RawData"
        influencedEdges = []
        self.links = pickle.load(open("./linkinfo.pickle", "rb"))
        edgeMatrixFile = "../RoadNetwork/RoadNetworks/New York City, New York, USA/edges.csv"
        self.dict = {}
        edgeMatrix = pd.read_csv(edgeMatrixFile, header=None)
        edgeMatrix = edgeMatrix[edgeMatrix[8] != 1]
        edgeMatrix = edgeMatrix.to_numpy()
        for i in range(edgeMatrix.shape[0]):
            source = int(edgeMatrix[i, 0])
            destination = int(edgeMatrix[i, 1])
            length = edgeMatrix[i, 6]
            if source not in self.dict.keys():
                self.dict[source] = {}
            if destination not in self.dict.keys():
                self.dict[destination] = {}
            self.dict[source][destination] = length
        for key in self.links:
            influencedEdges += self.links[key]
        pickle.dump(influencedEdges, open("./influencedEdges.pickle", "wb"))

    def LoadTrafficFile(self, year, day, sTime: datetime, eTime: datetime):
        date = "{}{}.csv".format(year, str(day).zfill(2))
        trafficDFPath = os.path.join(self.rawDataDir, date)
        trafficDF = pd.read_csv(trafficDFPath)
        trafficDF["DataAsOf"] = pd.to_datetime(trafficDF["DataAsOf"], utc=True).dt.tz_convert('America/New_York')
        trafficDF["DataAsOf"] = (trafficDF["DataAsOf"].astype('int64')//1e9).astype('int64')
        trafficDF = trafficDF[trafficDF["DataAsOf"] > int(sTime.timestamp())]
        trafficDF = trafficDF[trafficDF["DataAsOf"] <= int(eTime.timestamp())]
        return trafficDF
    
    def ProcessTrafficData(self, trafficDF: pd.DataFrame, sTime: datetime, hours):
        '''
        "Id","Speed","TravelTime","Status","DataAsOf","linkId"
        '''
        eTime = sTime + timedelta(hours=hours)
        sTime = int(sTime.timestamp())
        eTime = int(eTime.timestamp())
        Updates = []
        for row in trafficDF.iterrows():
            row = row[1]
            linkId, speed, timeStamp = row.loc["linkId"], row.loc["Speed"], row.loc["DataAsOf"]
            for edge in self.links[linkId]:
                (source, destination) = edge
                travelTime = self.dict[source][destination]/(speed/3.6)
                Updates.append([str(int(source)), str(int(destination)), travelTime, speed, str(int(timeStamp))])
        Updates = np.array(Updates)
        Updates = pd.DataFrame(Updates)
        return Updates

    def run(self, sTimeStr, hours):
        if not os.path.exists("./ProcessedData"):
            os.mkdir("./ProcessedData")
        sTime = datetime.strptime(sTimeStr, "%Y-%m-%d %H:%M")
        sTime.replace(tzinfo=pytz.timezone('America/New_York'))
        eTime = sTime + timedelta(hours=hours)
        print("Generate traffic file from {} to {}".format(sTime, eTime))
        trafficDF = self.LoadTrafficFile(sTime.year, sTime.month, sTime, eTime)
        Updates = self.ProcessTrafficData(trafficDF, sTime, 2)
        sTimeStr = sTime.strftime("%Y-%m-%d-%H-%M-%S")
        eTimeStr = eTime.strftime("%Y-%m-%d-%H-%M-%S")
        Updates.to_csv("./ProcessedData/{}-{}.csv".format(sTimeStr, eTimeStr), header=None, index=None)
        print("Traffic file from {} to {} is generated".format(sTime, eTime))
