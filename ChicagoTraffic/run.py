import os, sys
from DataUtil.Processor import Processor
import argparse

os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

def run(timeStr):
    processer = Processor()
    processer.run(timeStr, 2)

if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument("-t")
    args = parse.parse_args()
    run(args.s)