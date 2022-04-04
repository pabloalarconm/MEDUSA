import sys
from pyperseo import get_files, uniqid

argv = sys.argv[1:]

all_files = get_files(argv[0],"csv")

for a in all_files:
    afile = argv[0] + "/" + a
    print(afile)
    uniqid(afile)

