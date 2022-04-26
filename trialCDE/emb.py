import yaml
import sys
from pyperseo.functions import milisec
from rdflib import Graph, Namespace

class EMB():
    def __init__(self, config, prefixes, triplets):
        self.config = config
        self.prefixes = prefixes
        self.triplets = triplets
        self.main_dict = dict()
        self.tree = dict()

        # Check all objects are fine:
        if not isinstance(config and prefixes, dict):
            sys.exit("Both configuration and prefixes objects must be a dictionary. Please, check your input objects")
        if not isinstance(triplets, list):
            sys.exit("Triplets objects must be a list. Please, check your input objects")
        for i in self.triplets:
            if not len(i) == 4:
                sys.exit("Triplet object must be formed by four string based list [subject, predicate, object, datatype]. Please, check your input objects")

    
    def xmas_tree(self, data, model):
        """
        Transform list-based idependant triplets as [spo],[spo],[spo] into tree-based triplets organized by common Subject. For example: s[po],[po]
        
        This transformation will allow to reduce redundant structures at your resulting artefact.

        Depending on your input data: [spo] or [spod], it will work based on your choices using model parameter.
        """
        if model == "ShEx":
            for tri in data:
                s, p, o = tri
                if not s in self.tree.keys():
                    map = dict()
                    map.update({s:{p:o}}) 
                    self.tree.update(map)
                else:
                    po = {p:o} 
                    self.tree[s].update(po)
            return self.tree
        elif model == "YARRRML":
            for quad in data:
                s, p, o ,d = quad
                if not s in self.tree.keys():
                    map = dict()
                    map.update({s:[[p,o,d]]}) 
                    self.tree.update(map)
                else:
                    po = [p,o,d] 
                    self.tree[s].append(po)
            return self.tree
        else:
            sys.exit("No correct model tag was added to pick the transformation pathway")

    def transform_YARRRML(self):
        """
        Transform your input triplets, prefixes into YARRRML based on your configuration input dictionary.
        """
        self.tree = dict() # Reset tree object

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
        self.tree = self.xmas_tree(self.triplets,"YARRRML")

        mapping_dict = dict(mapping = dict())
        for t in self.tree.items():
            s_mapp = dict(name_node = dict(
                            sources = [self.config["source_name"]], # SOURCE
                            subjects = t[0], # SUBJECT
                            predicateobject = []))
            for l in t[1]:
                if l[2] == "iri":
                    pod_map = dict(
                                predicate = l[0], # PREDICATE
                                objects = dict(
                                    value = l[1], # OBJECT
                                    type = l[2])) # DATATYPE
                else:
                    pod_map = dict(
                                predicate = l[0], # PREDICATE
                                objects = dict(
                                    value = l[1], # OBJECT
                                    datatype = l[2])) # DATATYPE

                s_mapp["name_node"]["predicateobject"].append(pod_map)
                
            stamp = milisec() + "_" + self.config["source_name"] # Creating a unique name for each object using timestamp and source_name 
            s_mapp[stamp] = s_mapp.pop("name_node") # rename name_mode using an unique name per node
            mapping_dict["mapping"].update(s_mapp)
        self.main_dict.update(mapping_dict) # append mapping object into main

        document = yaml.dump(self.main_dict)
        return document

    def transform_ShEx(self, basicURI):
        """
        Transform your input triplets and prefixes into Shape Expression (ShEx) based on your configuration input dictionary.
        """
        self.triplets_curated = list()
        self.tree = dict() # Reset tree object
        self.all = ""

        # prefixes addtion:
        for k,v in self.prefixes.items():
            prefix = "PREFIX " + k + ": <" + v + ">"
            self.all = self.all + prefix + "\n"

        # triplets curation:
        for quad in self.triplets:
            s,p,o,d = quad
            if s.startswith(basicURI + ":" ): # Get rid of the whole URI, only focused on representative name's node
                c_element = s[::-1].split("_")[0]
                c_element = c_element[::-1]
                s_curated = c_element.lower() + "Shape"
            elif s.startswith("http"): # Right syntax in case of IRI
                s_curated = "<" + s + ">"
            else:
                s_curated = s

            if p == "rdf:type": # Turn rdf:type into "a" statement
                p_curated = "a"
            else:
                p_curated = p

            if not str(d) == "iri": # At non-IRI objects, all you need is the datatype
                o_curated = d
            else:
                if o.startswith(basicURI + ":" ):
                    c_element = o[::-1].split("_")[0]
                    c_element = c_element[::-1]
                    o_curated = "@:" + c_element.lower() + "Shape"
                elif "$(" in o and d == "iri":
                    o_curated = "IRI"
                elif o.startswith("http"):
                    o_curated = "IRI"
                else:
                    o_curated = o
            
            triplet = [s_curated,p_curated,o_curated]
            self.triplets_curated.append(triplet) # Append curated triplets

        # individual triplets transformation into xmas_tree:
        self.tree = self.xmas_tree(self.triplets_curated,"ShEx") # Transform your data into a subject-sorted dictionary

        # triplets into ShEx:
        for s in self.tree:
            subj= "\n" + s + " IRI {"
            self.all = self.all + subj
            for p,o in self.tree[s].items():
                if o.startswith("@") or o.startswith("xsd"):
                    pred_obj = "\n" + "\t" + p + " " + o + " ;"
                elif o == "IRI":
                    pred_obj = "\n" + "\t" + p + " " + o + " ;"
                else:
                    pred_obj = "\n" + "\t" + p + " [" + o + "]" + " ;"
                self.all = self.all + pred_obj
            self.all = self.all[:-1]
            end = "\n" + "} ;" + "\n"
            self.all = self.all + end
        return self.all

    def transform_RML(self):
        """
        Transform your input triplets, prefixes into YARRRML based on your configuration input dictionary.
        """
        self.tree = dict() # Reset tree object
        self.tree = self.xmas_tree(self.triplets,"YARRRML")
        g = Graph()

        # scaffold prefixes:
        rr = Namespace("http://www.w3.org/ns/r2rml#")
        rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
        rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#>")
        void = Namespace("http://rdfs.org/ns/void#")
        rml = Namespace("http://semweb.mmlab.be/ns/rml#")
        ql = Namespace("http://semweb.mmlab.be/ns/ql#")
        ex = Namespace("http://mapping.example.com/")



        # flexible prefixes using prefixes object:

        count = 0
        for i in self.tree:
            count += 1
            time = milisec()
            g.add((ex.rules, rdf.type, void.Dataset))
            g.add((ex.rules, void.exampleResource, ex.f)) ## add interpolation
            g.add(())
            g.add(())
            g.add(())
            g.add(())
            g.add(())
            g.add(())
            g.add(())
            g.add(())
            g.add(())
            g.add(())
            g.add(())

            

        


























        

prefixes = dict(
  rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#" ,
  rdfs = "http://www.w3.org/2000/01/rdf-schema#" ,
  obo = "http://purl.obolibrary.org/obo/" ,
  sio = "http://semanticscience.org/resource/" ,
  xsd = "http://www.w3.org/2001/XMLSchema#",
  this = "http://my_example.com/")


triplets = [

# sio nodes
["this:$(pid)_$(uniqid)_ID","sio:denotes","this:$(pid)_$(uniqid)_Role","iri"],
["this:$(pid)_$(uniqid)_Entity","sio:has-role","this:$(pid)_$(uniqid)_Role","iri"],
["this:$(pid)_$(uniqid)_Role","sio:is-realized-in","this:$(pid)_$(uniqid)_Process","iri"],
["this:$(pid)_$(uniqid)_Process","sio:has-output","this:$(pid)_$(uniqid)_Output","iri"],
["this:$(pid)_$(uniqid)_Output","sio:refers-to","this:$(pid)_$(uniqid)_Attribute","iri"],
["this:$(pid)_$(uniqid)_Entity","sio:has-attribute","this:$(pid)_$(uniqid)_Attribute","iri"],

# sio types
["this:$(pid)_$(uniqid)_ID","rdf:type","sio:identifier","iri"],
["this:$(pid)_$(uniqid)_Entity","rdf:type","$(datetime)","iri"],
["this:$(pid)_$(uniqid)_Role","rdf:type","sio:role","iri"],
["this:$(pid)_$(uniqid)_Process","rdf:type","sio:process","iri"],
["this:$(pid)_$(uniqid)_Output","rdf:type","sio:information-content-entity","iri"],
["this:$(pid)_$(uniqid)_Attribute","rdf:type","sio:attribute","iri"],

# data
["this:$(pid)_$(uniqid)_Output","sio:has-value","$(datetime)","xsd:date"]]



config = dict(
  source_name = "source_cde_test",
  configuration = "ejp",    # Two options for this parameter:
                            # ejp: it defines CDE-in-a-Box references, being compatible with this workflow  
                            # csv: No workflow defined, set the source configuration for been used by CSV as data source
                            
  csv_name = "source_1" # parameter only needed in case you pick "csv" as configuration
)

yarrrml = EMB(config, prefixes,triplets)

# test = yarrrml.transform_ShEx("this")
# print(test)

# test2 = yarrrml.transform_YARRRML()
# print(test2)

test2 = yarrrml.transform_RML()
print(test2)