
#import pandas as pd
import sys
from rdflib import Graph, Namespace, URIRef
import os

# Gets path as arguments
argv = sys.argv[1:]
path = argv[0]


def get_filename(path):
    path_split = path.split(sep="/")
    file = path_split[-1]
    name_split = file.split(sep=".")
    name = name_split[0]
    filename = name + "." + "ttl"
    return(filename)

def get_path(path):
    path_split = path.split(sep="/")
    file = path_split[:-1]
    root ='/'.join(file)
    return(root)


get1 = get_filename(path)
get2 = get_path(path)

g = Graph()
g.parse(argv[0], format="nt")

            #g.namespace_manager.bind('this', URIRef("https://w3id.org/duchenne-fdp/data/"))
            #g.namespace_manager.bind('sio', URIRef("http://semanticscience.org/resource/"))
            #g.namespace_manager.bind('obo', URIRef("http://purl.obolibrary.org/obo/"))
            # all_ns = [n for n in g.namespace_manager.namespaces()]
            # print(all_ns)


os.chdir(path=str(get2))
g.serialize(destination= get1, format="turtle")







