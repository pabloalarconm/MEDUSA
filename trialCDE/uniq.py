
from rdflib import Graph, URIRef
from os import listdir
from os.path import isfile, join
from datetime import datetime
import pandas as pd

import os
import sys


def get_files(path,format):
    """
    Obtain all files from current directory with certain format
    """
    files = [f for f in listdir(path) if isfile(join(path, f))]
    format_files = [ff for ff in files if ff.endswith(str("." + format))]
    if len(format_files) == 0:
        print("No resources are present at {} path with .{} format.".format(path,format))
    else:
        return format_files


def milisec():
    """
    Creates a milisecond timestamp.
    """
    now = datetime.now()
    now = now.strftime('%Y%m%d%H%M%S%f')
    return now


def uniqid(path_file):
    """
    Creates unique identifier column based on milisecond timestamp.
    """
    data = pd.read_csv(path_file)
    #print(data)


    data['uniqid'] = ""
    for i in data.index:
        data.at[i, "uniqid"] = milisec()
    #print(data['uniqid'])
    #print(data)
    data.to_csv(path_file, sep="," , index=False)





argv = sys.argv[1:]

all_files = get_files(argv[0],"csv")

for a in all_files:
    afile = argv[0] + "/" + a
    print(afile)
    uniqid(afile)

