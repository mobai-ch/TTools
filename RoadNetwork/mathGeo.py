import imp
from matplotlib.font_manager import list_fonts
import torch
import math

class DistanceUtil:
    def __init__(self) -> None:
        if torch.cuda.is_available():
            self.cuda_status = True
        else:
            self.cuda_status = False
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.R = 6371e3

    def initEdges(self, edges):
        self.edges = torch.from_numpy(edges).to(self.device)
        self.edges[:, 2] = self.edges[:, 2] * torch.pi/180
        self.edges[:, 3] = self.edges[:, 3] * torch.pi/180
        self.edges[:, 4] = self.edges[:, 4] * torch.pi/180
        self.edges[:, 5] = self.edges[:, 5] * torch.pi/180
        delta_lat = self.edges[:, 4] - self.edges[:, 2]
        delta_lon = self.edges[:, 5] - self.edges[:, 3]
        temp = torch.sin(delta_lat/2) * torch.sin(delta_lat/2) + torch.cos(self.edges[:, 2]) \
            * torch.cos(self.edges[:, 4]) * torch.sin(delta_lon/2) * torch.sin(delta_lon/2)
        self.edges[:, 6] = 2 * torch.atan2(torch.sqrt(temp), torch.sqrt(1-temp)) * self.R

    def findEdgeWithMinDistance(self, coordinate: list) -> list:
        '''
            Compute with the matrix operation
        '''
        [latH, lonH] = coordinate
        latH = latH * torch.pi/180
        lonH = lonH * torch.pi/180

        # Compute distance from point to source
        delta_lats = latH - self.edges[:, 2]
        delta_lons = lonH - self.edges[:, 3]
        temp = torch.sin(delta_lats/2) * torch.sin(delta_lats/2) + torch.cos(self.edges[:, 2]) \
            * math.cos(latH) * torch.sin(delta_lons/2) * torch.sin(delta_lons/2)
        lens = 2 * torch.atan2(torch.sqrt(temp), torch.sqrt(1-temp)) * self.R

        # Compute distance from point to destination
        delta_latd = latH - self.edges[:, 4]
        delta_lond = lonH - self.edges[:, 5]
        temp = torch.sin(delta_latd/2) * torch.sin(delta_latd/2) + torch.cos(self.edges[:, 4]) \
            * math.cos(latH) * torch.sin(delta_lond/2) * torch.sin(delta_lond/2)
        lend = 2 * torch.atan2(torch.sqrt(temp), torch.sqrt(1-temp)) * self.R

        # Get the Euclidean distance from source to destination
        lenH = self.edges[:, 6]

        cosH = (lens ** 2 + lenH ** 2 - lend ** 2)/(2* lens * lenH + 0.0001)
        Heights = lens * torch.sqrt(1-cosH**2)
        DX = lens * cosH
        LX = torch.where(DX < 0, 1, 0)
        RX = torch.where(DX > lenH, 1, 0)

        # Compute all distance from the point to edge
        all_Distance = LX * lens + RX * lend + (1 - LX - RX) * Heights
        index = torch.argmin(all_Distance)
        index_val = all_Distance[index]

        s, d = self.edges[index, 0], self.edges[index, 1]
        Partition = DX / (lenH+0.0001) 
        Partition = torch.where(Partition < 0.0, 0.0, Partition)
        Partition = torch.where(Partition > 1.0, 1.0, Partition) 
        
        part = Partition[index].cpu().item()

        return [int(s.cpu().item()), int(d.cpu().item())], part



