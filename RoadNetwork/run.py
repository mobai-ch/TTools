import argparse
from Downloader import *
from transform import *

parse = argparse.ArgumentParser(prefix_chars= '-')
parse.add_argument('-c')
args = parse.parse_args()
downloader = Downloader()
transformer = Transformer()
downloader.ProcessArgs(args)
transformer.processArgs(args)

'''
Input example -c "Boston, Massachusetts, USA"
              -c "New York City, New York, USA"
              -c "Chicago, Illinois, USA"
'''