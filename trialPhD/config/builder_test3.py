from embuilder.builder import EMB

prefixes = dict(
  rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#" ,
  rdfs = "http://www.w3.org/2000/01/rdf-schema#" ,
  obo = "http://purl.obolibrary.org/obo/" ,
  sio = "http://semanticscience.org/resource/" ,
  xsd = "http://www.w3.org/2001/XMLSchema#",
  biolink = "https://w3id.org/biolink/vocab/",
  this = "http://my_example1.com/")


triplets = [

# Nodes
["this:$(person_id)_ID","sio:denotes","this:$(person_id)_Birthdate_Role","iri"],

# Types
["this:$(person_id)_ID","rdf:type","sio:SIO_000115","iri"],


# Values
["this:$(person_id)_$(uniqid)#ID","sio:SIO_000300","$(person_id)","xsd:string"]]

config = dict(
  source_name = "source_cde_test",
  configuration = "ejp",    # Two options for this parameter:
                            # ejp: it defines CDE-in-a-Box references, being compatible with this workflow  
                            # csv: No workflow defined, set the source configuration for been used by CSV as data source
                            
  csv_name = "source_1" # parameter only needed in case you pick "csv" as configuration
)


yarrrml = EMB(config, prefixes,triplets)
test2 = yarrrml.transform_YARRRML()
print(test2)

