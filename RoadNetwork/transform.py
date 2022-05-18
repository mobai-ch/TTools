'''
Transform the downloaded map and poi to the graph file that we need
'''
from email import header
import pickle
import os, sys
from re import I
import numpy as np
import warnings
import time
from tqdm import tqdm

from requests import head
from mathGeo import DistanceUtil
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
 
warnings.filterwarnings('ignore')
pedestrianWays = set(['footway', 'pedestrian', 'steps', 'cycleway'])      # only available for pedestrian or bike
vehicleWays = set(['motorway', 'motorway_link'])                          # pedestrian is avoid to walk in motorway

class Transformer:
    def __init__(self) -> None:
        if not os.path.exists("./RoadNetworks"):
            os.mkdir("./RoadNetworks")


    def processArgs(self, args):
        locationName = args.c
        vertex_dict, edgeMatrix = self.readMapAndTrans(locationName)
        print("In {}, Number of vertices and edges are {} and {} respectively".format(locationName,\
            len(vertex_dict), edgeMatrix.shape[0]))
        self.saveMapFile(vertex_dict, edgeMatrix, locationName)
        print("File of map is loaded")
        poiList = self.readPOIAndTrans(locationName)
        print("File of POI is loaded")
        poiEdges = self.mapPOI2Edge(edgeMatrix, poiList)
        self.savePOIFile(poiEdges, locationName)

    def readMapAndTrans(self, cityName: str):
        '''
            read map file and tranform it to a matrix
        '''
        filePath = os.path.join("./TempMapCache", cityName)
        filePath = os.path.join(filePath, "{}_map.pickle".format(cityName))
        if not os.path.exists(filePath):
            print("{} does not exist, please download the ordinary road network by Downloader")
            os._exit()
        # format of the matrix: [source, destination, source_lat, source_lon, dest_lat, dest_lon,
        # distance, travel time, road type(0-all/1-pedestrian/2-vehicle)]
        edgeMatrix = []
        # clip the last two column when transform to the torch.tensor
        ox_map = pickle.load(open(filePath, "rb"))
        vertex_dict = {}
        record_num = 0
        # Process the vertices
        for node in ox_map.nodes:
            vertex_dict[node] = {"record_id": int(record_num), "lat": ox_map.nodes[node]['y'], "lon": ox_map.nodes[node]['x']}
            record_num = record_num + 1

        # Process the edges
        for source in ox_map.nodes:
            for dest in ox_map[source].keys():
                rTInfo = ox_map[source][dest][0]['highway']
                highways = []
                if type(rTInfo) == type([]):
                    highways = rTInfo
                else:
                    highways = [rTInfo]
                # save the edge
                sInfo = [int(vertex_dict[source]["record_id"]), int(vertex_dict[dest]["record_id"]), ox_map.nodes[source]['y'], ox_map.nodes[source]['x'], \
                    ox_map.nodes[dest]['y'], ox_map.nodes[dest]['x'], ox_map[source][dest][0]['length'], ox_map[source][dest][0]['travel_time']]
                for highway_type in highways:
                    if highway_type in vehicleWays:
                        sInfo.append(int(2))
                        break
                    elif highway_type in pedestrianWays:
                        sInfo.append(int(1))
                        break
                if len(sInfo) == 8:
                    sInfo.append(int(0))
                edgeMatrix.append(sInfo)
        
        edgeMatrix = np.array(edgeMatrix)
        return vertex_dict, edgeMatrix


    def readPOIAndTrans(self, locationName: str):
        '''
            read POI file and transform it to a list
        '''
        filePath = os.path.join("./TempMapCache", locationName)
        filePath = os.path.join(filePath, "{}_poi.pickle".format(locationName))
        if not os.path.exists(filePath):
            print("{} does not exist, please download the ordinary road network by Downloader")
            os._exit()
        pdf = pickle.load(open(filePath, "rb"))
        poiList = []
        index_count = 10000000
        for index, row in pdf.iterrows():
            coord = []
            if type(row["geometry"]) == type(Point((0, 0))):
                coord = self.meanList(row["geometry"].coords[:])
            elif type(LineString([(0, 1), (2, 3), (4, 5)])) == type(row["geometry"]):
                coord = self.meanList(list(row["geometry"].coords))
            elif type(Polygon([(0, 0), (0, 1), (1, 1), (0, 0)])) == type(row["geometry"]):
                coord = self.meanList(row["geometry"].exterior.coords[:])
            else:
                poly_list = []
                for poly in list(row["geometry"].geoms):
                    poly_list += poly.exterior.coords
                coord = self.meanList(poly_list)
            poiList.append([index_count] + coord + [row["amenity"], row["name"]])
            index_count += 1
        return poiList
    
    def meanList(self, polyList):
        # compute the mean value for all points in poly list
        sum_val = [0, 0]
        for poly in polyList:
            sum_val[0] += poly[0]
            sum_val[1] += poly[1]
        sum_val[0] /= len(polyList)
        sum_val[1] /= len(polyList)
        return sum_val

    def saveMapFile(self, verticesDict, edgeMatrix, locationName):
        dirPath = os.path.join("./RoadNetworks", locationName)
        if not os.path.exists(dirPath):
            os.mkdir(dirPath)
        edge_filePath = os.path.join(dirPath, "edges.csv")
        vertex_filePath = os.path.join(dirPath, "vertices.csv")
        vertex_infos = []
        for node in verticesDict.keys():
            vertex_infos.append([verticesDict[node]["record_id"], node, verticesDict[node]['lat'], verticesDict[node]['lon']])
        vertex_infos = np.array(vertex_infos)
        vertex_infos = pd.DataFrame(vertex_infos, index=None)
        vertex_infos.to_csv(vertex_filePath, header=None, index=None)
        edge_infos = pd.DataFrame(edgeMatrix)
        edge_infos.to_csv(edge_filePath, header=None, index=None)

    def savePOIFile(self, poiEdges, locationName):
        dirPath = os.path.join("./RoadNetworks", locationName)
        if not os.path.exists(dirPath):
            os.mkdir(dirPath)
        poi_filePath = os.path.join(dirPath, "poi.csv")
        poiEdges = np.array(poiEdges)
        poiEdges = pd.DataFrame(poiEdges, index=None)
        poiEdges.to_csv(poi_filePath, header=None, index=None)

    def mapPOI2Edge(self, edgeMatrix, poiList) -> list:
        distanceUtil = DistanceUtil()
        poiEdges = []
        distanceUtil.initEdges(edgeMatrix[:, 0: 7])
        num = 0
        print("POI is mapping")
        for poiInfo in tqdm(poiList):
            lat, lon = poiInfo[2], poiInfo[1]
            # Compute the nearest edge by GPU
            [source, destination], partition = distanceUtil.findEdgeWithMinDistance([lat, lon])
            # judge if the destination-source is available in your future work
            poiEdges.append([poiInfo[0], lat, lon, source, destination, partition, poiInfo[3], poiInfo[4]])
        return poiEdges


def Test():
    transformer = Transformer()
    locationName = "New York City, New York, USA"
    vertex_dict, edgeMatrix = transformer.readMapAndTrans(locationName)
    print("In {}, Number of vertices and edges are {} and {} respectively".format(locationName,\
         len(vertex_dict), edgeMatrix.shape[0]))
    transformer.saveMapFile(vertex_dict, edgeMatrix, locationName)
    print("Map read")
    poiList = transformer.readPOIAndTrans(locationName)
    print("POI read")
    poiEdges = transformer.mapPOI2Edge(edgeMatrix, poiList)

def TestPOI():
    transformer = Transformer()
    locationName = "New York City, New York, USA"
    vertex_dict, edgeMatrix = transformer.readMapAndTrans(locationName)
    poiList = transformer.readPOIAndTrans(locationName)
    poiEdges = transformer.mapPOI2Edge(edgeMatrix, poiList)


if __name__ == '__main__':
    TestPOI()