import yaml
import sys
from pyperseo.functions import milisec


class EMB():
    def __init__(self, config):
      self.config = config

    def transform(self,prefixes,triplets):
        self.prefixes = prefixes
        self.triplets = triplets
        self.main_dict = dict()
        self.reg = dict()

        # prefixes object:
        if self.config["configuration"] == "ejp":
            prefixes_dict = dict(prefixes=self.prefixes) # create prefixes object
            prefixes_dict["prefixes"]["this"] = str("|||BASE|||")
            self.main_dict.update(prefixes_dict) # append prefixes object into main
        elif self.config["configuration"] == "csv":
            prefixes_dict = dict(prefixes=self.prefixes) # create prefixes object
            self.main_dict.update(prefixes_dict) # append prefixes object into main
        else:
            sys.exit('You must provide a configuration parameter: use "ejp" for using this template for EJP-RDs workflow, or "csv" for defining CSV data source')


        # sources object:
        if self.config["configuration"] == "ejp":
            sources_dict = dict(sources= dict(
                                    source_prov=dict(
                                    access = str("|||DATA|||"),
                                    referenceFormulation= str("|||FORMULATION|||"),
                                    iterator = str("$"))))
            sources_dict["sources"][self.config["source_name"]] = sources_dict["sources"].pop("source_prov") # rename source_name using an unique name from config
            self.main_dict.update(sources_dict)
        elif self.config["configuration"] == "csv":
            if "csv_name" in self.config:
                sources_dict = dict(sources= dict(
                                    source_prov=dict(
                                        access = self.config["csv_name"]+ ".csv",
                                        referenceFormulation= "csv",
                                        iterator = str("$"))))
                sources_dict["sources"][self.config["source_name"]] = sources_dict["sources"].pop("source_prov") # rename source_name using an unique name from config
                self.main_dict.update(sources_dict)
            else:
                sys.exit('You must provide a csv_name parameter for defining the name of your CSV data source')

        else:
            sys.exit('You must provide a configuration parameter: use "ejp" for using this template for EJP-RDs workflow, or "csv" for defining CSV data source')

        # mapping object:
        mapping_dict = dict(mapping = dict())

        for e in self.triplets:

            if not e[0] in self.reg.keys():
                triplet_map = dict(name_node = dict(
                                        sources = [self.config["source_name"]], # SOURCE
                                        subjects = e[0], # SUBJECT
                                        predicateobject = [dict(
                                            predicate = e[1], # PREDICATE
                                            objects = dict(
                                                value = e[2], # OBJECT
                                                datatype = e[3]))]))  # DATATYPE

                stamp = milisec() + "_" + self.config["source_name"] # Creating a unique name for each object using timestamp and source_name 
                if e[3] == "iri":
                    triplet_map["name_node"]["predicateobject"][0]["objects"]["type"] = triplet_map["name_node"]["predicateobject"][0]["objects"].pop("datatype") # rename name_mode using an unique name per node
                triplet_map[stamp] = triplet_map.pop("name_node") # rename name_mode using an unique name per node
                mapping_dict["mapping"].update(triplet_map) # append dict into dict
                self.reg.update( {e[0] : stamp } )
            else:
                for k, v in self.reg.items():
                    if k == e[0]:
                        predicate_map = dict(
                                        predicate = e[1], # PREDICATE
                                        objects = dict(
                                            value = e[2], # OBJECT
                                            datatype = e[3])) # DATATYPE

                        if e[3] == "iri":
                            predicate_map["objects"]["type"] = predicate_map["objects"].pop("datatype") # rename name_mode using an unique name per node

                        mapping_dict["mapping"][v]["predicateobject"].append(predicate_map)

        self.main_dict.update(mapping_dict) # append mapping object into main

        # dump
        document = yaml.dump(self.main_dict)
        return document



prefixes = dict(
  rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#" ,
  rdfs = "http://www.w3.org/2000/01/rdf-schema#" ,
  obo = "http://purl.obolibrary.org/obo/" ,
  sio = "http://semanticscience.org/resource/" ,
  xsd = "http://www.w3.org/2001/XMLSchema#",
  this = "http://my_example.com/")


triplets = [

# sio nodes
["this:$(pid)_$(uniqid)#ID","sio:denotes","this:$(pid)_$(uniqid)#Role","iri"],
["this:$(pid)_$(uniqid)#Entity","sio:has-role","this:$(pid)_$(uniqid)#Role","iri"],
["this:$(pid)_$(uniqid)#Role","sio:is-realized-in","this:$(pid)_$(uniqid)#Process","iri"],
["this:$(pid)_$(uniqid)#Process","sio:has-output","this:$(pid)_$(uniqid)#Output","iri"],
["this:$(pid)_$(uniqid)#Output","sio:refers-to","this:$(pid)_$(uniqid)#Attribute","iri"],
["this:$(pid)_$(uniqid)#Entity","sio:has-attribute","this:$(pid)_$(uniqid)#Attribute","iri"],

# sio types
["this:$(pid)_$(uniqid)#ID","rdf:type","sio:identifier","iri"],
["this:$(pid)_$(uniqid)#Entity","rdf:type","sio:person","iri"],
["this:$(pid)_$(uniqid)#Role","rdf:type","sio:role","iri"],
["this:$(pid)_$(uniqid)#Process","rdf:type","sio:process","iri"],
["this:$(pid)_$(uniqid)#Output","rdf:type","sio:information-content-entity","iri"],
["this:$(pid)_$(uniqid)#Attribute","rdf:type","sio:attribute","iri"],

# data
["this:$(pid)_$(uniqid)#Output","sio:has-value","$(datetime)","xsd:date"]]



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

