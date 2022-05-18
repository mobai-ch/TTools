'''
读取交通文件
'''

import os, sys
import queue
import pandas as pd
from DataUtil.mathGeo import DistanceUtil
import re
from tqdm import tqdm
import pickle

class LinkDataUtil:
    def __init__(self) -> None:
        self.RawDataDirPath = "./RawData/"
        # road network source-destination-length
        self.dict = {}
        edgeMatrixFile = "../RoadNetwork/RoadNetworks/New York City, New York, USA/edges.csv"
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

        self.distanceUtil = DistanceUtil()
        self.distanceUtil.initEdges(edgeMatrix[:, 0: 7])
    
    def readAllLinkInfo(self):
        '''
        Load the informations about the links, and convert it to the a map file, 
        i.e., linkId -> [list of road segment in OSM], save it
        '''
        linkfile = "./linkinfo.csv"

        # Get links and convert it to the edges
        linkInfo = pd.read_csv(linkfile)
        links = {}

        for row in linkInfo.iterrows():
            linkId = row[1].loc["linkId"]
            linkPointstrs = row[1].loc["linkPoints"].split(" ")[0:-1]
            linkPoints = []
            for linkPointStr in linkPointstrs:
                split_strs = re.split(",|\r\n", linkPointStr)
                if len(split_strs) == 2:
                    linkPoints.append([float(split_strs[0]), float(split_strs[1])])
            print("Process the link with link ID: {}, Number of link points: {}".format(linkId, len(linkPoints)))
            finalEdgeLists = self.simple_map_matching(linkPoints)
            links[linkId] = finalEdgeLists
            pickle.dump(links, open("./linkinfo.pickle", "wb"))

        allLinkDict = pickle.load(open("./linkinfo.pickle", "rb"))
        newLinkDict = {}
        for key in allLinkDict.keys():
            newLinkDict[key] = []
            saved = set()
            for (source, destination) in allLinkDict[key]:
                if source != destination and (source, destination) not in saved:
                    newLinkDict[key].append((source, destination))
                    saved.add((source, destination))
        pickle.dump(newLinkDict, open("./linkinfo.pickle", "wb"))
            
    
    def simple_map_matching(self, linkPoints: list):
        edgePro_lists, visitedLoc, maxTempLink = [], [], []
        finalEdgeLists = []
        for linkPoint in linkPoints:
            edgePro = self.distanceUtil.findEdgesWithMinDistance(linkPoint, 5)
            edgePro_lists.append(edgePro)
        for i in range(len(edgePro_lists)):
            visitedLoc.append(0)
            maxTempLink.append(0)
        pos = 1
        num = 0
        maxLinkPos = 0
        
        while pos < len(edgePro_lists):
            num += 1
            if num % 200000 == 0:
                break
            if pos == 0:
                # visitedLoc[pos] += 1
                if visitedLoc[pos] >= 5:
                    break
                pos += 1
                continue
            loc_now = visitedLoc[pos]
            if loc_now >= 5:
                visitedLoc[pos] = 0
                visitedLoc[pos-1] += 1
                pos -= 1
                continue
            loc_before = visitedLoc[pos-1]
            flag, flist = self.CollectConnectable(edgePro_lists[pos-1][loc_before], edgePro_lists[pos][loc_now], 10)
            # print(pos, visitedLoc[pos])
            if flag == True:
                if pos > maxLinkPos:
                    maxLinkPos = pos
                    for i in range(maxLinkPos):
                        maxTempLink[i] = visitedLoc[i]
                pos += 1
            else:
                visitedLoc[pos] += 1
        tempEdgeList = []
        for i in range(maxLinkPos):
            tempEdgeList.append(edgePro_lists[i][maxTempLink[i]])
        finalNodeList = []
        for i in range(len(tempEdgeList)-1):
            flag, nlist = self.CollectConnectable(tempEdgeList[i], tempEdgeList[i+1], 10)
            for node in nlist:
                finalNodeList += [int(node)]
        if len(tempEdgeList) > 0:
            finalNodeList += [tempEdgeList[len(tempEdgeList)-1][1]]
        for i in range(len(finalNodeList)-1):
            finalEdgeLists += [(finalNodeList[i], finalNodeList[i+1])]
        for i in range(maxLinkPos+1, len(visitedLoc)):
            finalEdgeLists += [edgePro_lists[i][0]]
        
        return finalEdgeLists

    def CollectConnectable(self, sLink, eLink, limitLayer):
        (s1, source) = sLink
        (destination, d2) = eLink
        if sLink == eLink:
            return True, [str(s1)]
        # if they are connectable, return the edges list, else, return a empty list
        visit_queue = queue.Queue()
        visited = set()
        visit_queue.put(("{}".format(source), 0))
        while not visit_queue.empty():
            (currentStr, pos) = visit_queue.get()
            if pos == limitLayer:
                return False, []
            node = int(currentStr.split(";")[-1])
            visited.add(node)
            for key in self.dict[node].keys():
                new_node = (currentStr+";"+str(key), pos+1)
                if key == destination:
                    return True, [str(s1)] + new_node[0].split(";")
                elif key not in visited:
                    visit_queue.put(new_node)
        return False, []
    

def getLinks():
    dataUtil = LinkDataUtil()
    dataUtil.readAllLinkInfo()

if __name__ == '__main__':
    getLinks()



    