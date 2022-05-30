from embuilder.builder import EMB

prefixes = dict(
  rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#" ,
  rdfs = "http://www.w3.org/2000/01/rdf-schema#" ,
  obo = "http://purl.obolibrary.org/obo/" ,
  sio = "http://semanticscience.org/resource/" ,
  xsd = "http://www.w3.org/2001/XMLSchema#",
  biolink = "https://w3id.org/biolink/vocab/",
  this = "http://my_example2.com/")


triplets = [

# Nodes
["this:$(pid)_$(uniqid)#Entity","biolink:hasID","this:$(pid)_$(uniqid)#ID","iri"],

# Types


# Biolink types
["this:$(pid)_$(uniqid)#Entity","rdf:type","biolink:Case","iri"],
["this:$(pid)_$(uniqid)#ID","rdf:type","biolink:ID","iri"],


# Values
["this:$(pid)_$(uniqid)#ID","biolink:hasnumerical_value","$(pid)","xsd:string"]]

config = dict(
  source_name = "source_cde_test",
  configuration = "ejp",    # Two options for this parameter:
                            # ejp: it defines CDE-in-a-Box references, being compatible with this workflow  
                            # csv: No workflow defined, set the source configuration for been used by CSV as data source
                            
  csv_name = "source_1" # parameter only needed in case you pick "csv" as configuration
)

yarrrml = EMB(config)
test = yarrrml.transform(prefixes, triplets)
print(test)