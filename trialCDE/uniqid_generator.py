#!python3

import pandas as pd
import sys
from datetime import datetime
from os import listdir
from os.path import isfile, join

# Gets path as arguments
argv = sys.argv[1:]
mypath = argv[0]

allfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

def milisec(): # Creates milisec timestamp:
    now = datetime.now()
    now = now.strftime('%Y-%m-%d_%H:%M:%S,%f')
    return now

for afile in allfiles:

    # Get table from each file
    filepath = mypath + "/"+ afile
    data = pd.read_csv(filepath) 

    # Add uniqid column with the timestamp:
    data['uniqid'] = ""
    for i in data.index:
        data.at[i, "uniqid"] = milisec()
    print(data['uniqid'])

    # Saving changes:
    data.to_csv(filepath, sep=',')
