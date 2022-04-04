from rdflib import Graph #, Literal, RDF, URIRef
# from rdflib.namespace import FOAF, XSD, RDF
# import re
# import sys
# import requests

from ldpy import ldp

cli=ldp.Client(endpoint="http://localhost:8890/DAV/home/LDP/",
                username="ldp",
                password="ldp")

cont=cli.addNewContainer(location="LDP",slug="Container_trial")

g1=Graph()
g1.parse("/home/pabloalarconm/Desktop/EJP/MEDUSA/trialCDE/data/triples/test1.ttl", format="turtle")

g2=Graph()
g2.parse("/home/pabloalarconm/Desktop/EJP/MEDUSA/trialCDE/data/triples/test2.ttl", format="turtle")

res1=cli.addNewResource(location="Container_trial",slug="test1",g=g1)


res2=cli.addNewResource(location="Container_trial",slug="test2",g=g2)
res1.get()
res2.get()

