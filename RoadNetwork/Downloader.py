'''
Download the road network by OSMnx - in this time, we mix up the vehicle road network
and pedestrian road at first, in this way, our BFS would forbid the bug caused by the 
difference between vehicle road network and pedestrain road network
i.e.,

Edge: vehicle travel time, pedestrian travel time, (mixed edge = 0, vehicle edge = 1, pedestrian edge = 2)
source (lat, lon), destination (lat, lon), 

'''


import osmnx as ox
import os
import pickle
import warnings
 
warnings.filterwarnings('ignore')

class Downloader:
    def __init__(self) -> None:
        if not os.path.exists("TempMapCache"):
            os.mkdir("TempMapCache")
        if not os.path.exists("RoadNetworks"):
            os.mkdir("RoadNetworks")

    def DownloadMapByLocation(self, locationName):
        if locationName == None:
            print("No location name")
            os._exit(0)
        locationTempDir = "./TempMapCache/{}".format(locationName)
        if not os.path.exists(locationTempDir):
            os.mkdir(locationTempDir)
        pdfPath = "{}/{}_map.pickle".format(locationTempDir, locationName)
        VpdfPath = "{}/{}_vmap.pickle".format(locationTempDir, locationName)
        if os.path.exists(pdfPath):
            checkLabel = input("{} exists, download it again? (Y/N)   ".format(pdfPath))
            if checkLabel.upper() == "Y":
                pdf = ox.graph_from_place(locationName)
                pdf = ox.add_edge_speeds(pdf)
                pdf = ox.add_edge_travel_times(pdf)
                with open(pdfPath, "wb") as f:
                    pickle.dump(pdf, f)
                Vpdf = ox.graph_from_place(locationName, network_type='drive')
                Vpdf = ox.add_edge_speeds(Vpdf)
                Vpdf = ox.add_edge_travel_times(Vpdf)
                with open(VpdfPath, "wb") as Vf:
                    pickle.dump(Vpdf, Vf)
        else:
            with open(pdfPath, "wb") as f:
                pdf = ox.graph_from_place(locationName)
                pdf = ox.add_edge_speeds(pdf)
                pdf = ox.add_edge_travel_times(pdf)
                pickle.dump(pdf, f)
            with open(VpdfPath, "wb") as Vf:
                Vpdf = ox.graph_from_place(locationName, network_type='drive')
                Vpdf = ox.add_edge_speeds(Vpdf)
                Vpdf = ox.add_edge_travel_times(Vpdf)
                pickle.dump(Vpdf, Vf)
        print("Map in {} is downloaded".format(locationName))

    def ProcessArgs(self, args):
        self.DownloadMapByLocation(args.c)
        self.DownloadPOIByLocation(args.c)

    def DownloadPOIByLocation(self, locationName):
        if locationName == None:
            print("No location name")
            os._exit(0)
        locationTempDir = "./TempMapCache/{}".format(locationName)
        if not os.path.exists(locationTempDir):
            os.mkdir(locationTempDir)
        pdfPath = "{}/{}_poi.pickle".format(locationTempDir, locationName)
        if os.path.exists(pdfPath):
            checkLabel = input("{} exists, download it again? (Y/N)    ".format(pdfPath))
            if checkLabel.upper() == "Y":
                with open(pdfPath, "wb") as f:
                    pdf = ox.geometries_from_place(locationName, tags={"amenity": True}) 
                    pickle.dump(pdf, f)
        else:
            with open(pdfPath, "wb") as f:
                pdf = ox.geometries_from_place(locationName, tags={"amenity": True}) 
                pickle.dump(pdf, f)
        print("POI in {} is downloaded".format(locationName))

