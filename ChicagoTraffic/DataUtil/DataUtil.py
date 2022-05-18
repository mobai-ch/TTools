import pandas as pd
from DataUtil.mathGeo import DistanceUtil
import numpy as np
import queue

class DataUtil:
    def __init__(self) -> None:
        self.RawDataDirPath = "./RawData/"
        # road network source-destination-length
        self.dict = {}
        edgeMatrixFile = "../RoadNetwork/RoadNetworks/Chicago, Illinois, USA/edges.csv"
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
        self.initEdges(edgeMatrix)

    def initEdges(self, orgEdgeMatrix: np.array):
        edgeMatrix = orgEdgeMatrix[:, 0: 7]
        self.distanceUtil = DistanceUtil()
        self.distanceUtil.initEdges(edges=edgeMatrix)
    
    def getEdgeList(self, loc_1: list, loc_2: list):
        edges_1 = self.distanceUtil.findEdgesWithMinDistance(loc_1, 5)
        edges_2 = self.distanceUtil.findEdgesWithMinDistance(loc_2, 5)
        allNodes, allEdges = [], []
        for edge_1 in edges_1:
            for edge_2 in edges_2:
               flag, nodeList = self.CollectConnectable(edge_1, edge_2, 5)
               if flag:
                   allNodes = nodeList
                   break
        if len(allNodes) == 0:
            # 命名相似度以后不能太高
            return [edges_1[0], edges_2[0]]
        for i in range(len(allNodes)-1):
            allEdges.append((int(allNodes[i]), int(allNodes[i+1])))
        return allEdges
    
    def CollectConnectable(self, sLink: tuple, eLink: tuple, limitLayer):
        (s1, source) = sLink
        (destination, d2) = eLink
        if sLink == eLink:
            return True, [str(s1), str(d2)]
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
                    return True, [str(s1)] + new_node[0].split(";") + [str(d2)]
                elif key not in visited:
                    visit_queue.put(new_node)
        return False, []