import os, sys
import pickle
from DataUtil.Processor import Processor
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

def run(timeStr):
    '''
    Create the folder and Get the road network from the road roadnetwork directory
    '''
    if not os.path.exists("ProcessedData"):
        os.mkdir("ProcessedData")
    # Generate the travel time
    processor = Processor(True)
    processor.run(timeStr, 2)

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("-t")
    args = parse.parse_args()
    run(args.s)

# run("2016-01-01 12:00")

