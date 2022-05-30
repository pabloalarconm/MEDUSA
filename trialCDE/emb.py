import yaml
import sys
from pyperseo.functions import milisec
from rdflib import Graph, Namespace, Literal, URIRef


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
            if not k == basicURI:
                prefix = "PREFIX " + k + ": <" + v + ">"
            else:
                prefix = "PREFIX " + ": <" + v + ">"

            self.all = self.all + prefix + "\n"

        # triplets curation:
        for quad in self.triplets:
            s,p,o,d = quad
            if s.startswith(basicURI + ":" ): # Get rid of the whole URI, only focused on representative name's node
                s_curated = s[::-1].partition(")")[0]
                s_curated = s_curated.replace("_","")
                s_curated = s_curated.replace("/","")
                s_curated = s_curated[::-1]
                s_curated = ":" + s_curated.lower() + "Shape"
            elif s.startswith("$("):
                s_curated = s.replace("$(","")
                s_curated = s_curated.replace(")","")
                s_curated = s_curated.replace("_","")
                s_curated = s_curated.replace("/","")
                s_curated = ":" + s_curated.lower() + "Shape"
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
                    o_curated = o[::-1].partition(")")[0]
                    o_curated = o_curated.replace("_","")
                    o_curated = o_curated.replace("/","")
                    o_curated = o_curated[::-1]
                    o_curated = "@:" + o_curated.lower() + "Shape"
                elif o.startswith("$("):
                    o_curated = o.replace("$(","")
                    o_curated = o_curated.replace(")","")
                    o_curated = o_curated.replace("_","")
                    o_curated = o_curated.replace("/","")
                    o_curated = "@:" + o_curated.lower() + "Shape"
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

    # def transform_RML(self):
    #     """
    #     Transform your input triplets, prefixes into YARRRML based on your configuration input dictionary.
    #     """
    #     self.triplets_curated = list()

    #     for quad in self.triplets:
    #         s,p,o,d = quad
    #         if s.startswith("this"):
    #             s_curated = s.replace("this","http://my_example.com/")

    #         # Aqui va una funcion para transformar a full URI
    #         if o.startswith("this"):
    #             o_curated = o.replace("this","http://my_example.com/")
    #         if d == "iri":
    #             d_curated = "IRI"
    #         # else:
    #             # Aqui va una funcion para transformar a full URI

    #         triplet = [s_curated,p,o_curated,d_curated]
    #         self.triplets_curated.append(triplet)
    #     #print(self.triplets_curated)

    #     g = Graph()

    #     # scaffold prefixes:
    #     rr = Namespace("http://www.w3.org/ns/r2rml#")
    #     rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    #     rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
    #     void = Namespace("http://rdfs.org/ns/void#")
    #     rml = Namespace("http://semweb.mmlab.be/ns/rml#")
    #     ql = Namespace("http://semweb.mmlab.be/ns/ql#")
    #     ex = Namespace("http://mapping.example.com/")

    #     g.namespace_manager.bind('rr',rr)
    #     g.namespace_manager.bind('rdf',rdf)
    #     g.namespace_manager.bind('rdfs',rdfs)
    #     g.namespace_manager.bind('void', void)
    #     g.namespace_manager.bind('rml',rml)
    #     g.namespace_manager.bind('ql',ql)
    #     g.namespace_manager.bind('ex',ex)

    #     for p in self.prefixes.items():
    #         g.namespace_manager.bind(p[0],p[1])

    #     g.add((ex.rules, rdf.type, void.Dataset))
    #     g.add((ex.source, rdf.type, rml.LogicalSource))
    #     g.add((ex.source, rdfs.label, Literal(self.config["source_name"])))
    #     g.add((ex.source, rml.source, Literal("/data/data.csv")))
    #     g.add((ex.source, rml.iterator, Literal("$")))
    #     g.add((ex.source, rml.referenceFormulation, ql.CSV))

    #     # flexible prefixes using prefixes object:
    #     for i in self.triplets_curated:
    #         time = milisec()
    #         mapp = URIRef(ex+"map_"+time)
    #         subj = URIRef(ex+"s_"+time)
    #         predobj = URIRef(ex+"pom_"+time)
    #         pred = URIRef(ex+"pm_"+time)
    #         obj = URIRef(ex+"om_"+time)

    #         su = URIRef(i[0])

    #         g.add((ex.rules, void.exampleResource, mapp))
    #         g.add((mapp, rml.logicalSource, ex.source))
    #         g.add((mapp, rdf.type, rr.TripleMap))
    #         g.add((mapp, rdfs.label,Literal(time)))
    #         g.add((mapp, rr.subjectMap, subj))
    #         g.add((mapp, rr.predicateObject, predobj))
    #         g.add((subj, rdf.type, rr.SubjectMap))
    #         g.add((subj, rr.template, su)) # Problema
    #         g.add((predobj, rdf.type, rr.PredicateObjectMap))
    #         g.add((predobj, rr.predicateMap, pred))            
    #         g.add((predobj, rr.objectMap, obj))
    #         g.add((pred, rdf.type, rr.PredicateMap))            
    #         g.add((pred, rr.constant, Literal(i[1]))) #Problemon
    #         g.add((obj, rdf.type, rr.ObjectMap))            
    #         g.add((obj, rr.template, Literal(i[2]))) # Problema
    #         g.add((obj, rr.termType, Literal(i[3])))  # TODO       

    #     print(g.serialize(format="ttl"))

            
    def transform_OBDA(self):
        """
        Transform your triplets and prefixes inputs into OBDA (Ontology-Based Database Access).
        """
        self.amaia_OBDA = ""
        self.tree = dict() # Reset tree object
        self.triplets_curated = list()

        # Prefixes:
        self.amaia_OBDA = self.amaia_OBDA + "[PrefixDeclaration]" + "\n"
        for k,v in self.prefixes.items():
            prefix = k + ":" + "\t" + v
            self.amaia_OBDA = self.amaia_OBDA + prefix + "\n"

        # Triplets preproccesing:
        for quad in self.triplets:
            s,p,o,d = quad

            if '$(' in s:   # Change reference syntax to OBDA
                s_curated = s.replace('$(', '{')
                s_curated = s_curated.replace(")" , "}")
            else:
                s_curated = s

            if p == "rdf:type": # Turn rdf:type into "a" statement
                p_curated = "a"
            else:
                p_curated = p

            if '$(' in o:   # Change reference syntax to OBDA 
                o_curated = o.replace('$(', '{')
                o_curated = o_curated.replace(")" , "}")
            else:
                o_curated = o

            triplet = [s_curated,p_curated,o_curated,d]
            self.triplets_curated.append(triplet) # Append curated triplets

        # X-tree object
        self.tree = self.xmas_tree(self.triplets_curated,"YARRRML") # Use same structure than YARRRML

        # OBDA build
        self.amaia_OBDA = self.amaia_OBDA + "\n" + "[MappingDeclaration] @collection [[" + "\n"
        for t in self.tree.items():
            self.amaia_OBDA = self.amaia_OBDA + "mappingId"	+ "\t" + self.config["source_name"] + milisec() + "\n" # milisec for unique mappingId objects
            self.amaia_OBDA = self.amaia_OBDA + "target" + "\t" + t[0]

            for l in t[1]:
                if not l[2] == "iri":
                    l[2] = l[2].replace(" ", "") # TODO Check spec for string to solve this convertion
                    l[2] = l[2].replace(":", "_") # TODO Check spec for string to solve this convertion
                    self.amaia_OBDA = self.amaia_OBDA +  " " + l[0] + " " + '"' + l[1]+ '"' + "^^" + l[2] + " ;"
                else:
                    self.amaia_OBDA = self.amaia_OBDA +  " " + l[0] + " " + l[1] + " ;"

            self.amaia_OBDA = self.amaia_OBDA + " ."
            self.amaia_OBDA = self.amaia_OBDA + "\n" + "source" + "\t" "SELECT * FROM mytable #ADD your QUERY HERE" + "\n" + "\n"

        self.amaia_OBDA = self.amaia_OBDA + "]]" + "\n"
        self.amaia_OBDA = self.amaia_OBDA.replace( "; .", ".")
        return self.amaia_OBDA
        

prefixes = dict(
  rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#" ,
  rdfs = "http://www.w3.org/2000/01/rdf-schema#" ,
  obo = "http://purl.obolibrary.org/obo/" ,
  sio = "http://semanticscience.org/resource/" ,
  xsd = "http://www.w3.org/2001/XMLSchema#",
  this = "http://my_example.com/")


triplets = [

# Nodes
["this:$(pid)_$(uniqid)_ID","sio:SIO_000020","this:$(pid)_$(uniqid)_Status_Role","iri"],
["this:$(pid)_$(uniqid)_Entity","sio:SIO_000228","this:$(pid)_$(uniqid)_Status_Role","iri"],
["this:$(pid)_$(uniqid)_Entity","sio:SIO_000008","this:$(pid)_$(uniqid)_Status_Attribute","iri"],
["this:$(pid)_$(uniqid)_Status_Role","sio:SIO_000356","this:$(pid)_$(uniqid)_Status_Process","iri"],
["this:$(pid)_$(uniqid)_Status_Process","sio:SIO_000229","this:$(pid)_$(uniqid)_Status_Output","iri"],
["this:$(pid)_$(uniqid)_Status_Process","sio:SIO_000680","this:$(pid)_$(uniqid)_Status_Startdate","iri"],
["this:$(pid)_$(uniqid)_Status_Process","sio:SIO_000681","this:$(pid)_$(uniqid)_Status_Enddate","iri"],
["this:$(pid)_$(uniqid)_Status_Output","sio:SIO_000628","this:$(pid)_$(uniqid)_Status_Attribute","iri"],

["this:$(pid)_$(uniqid)_Entity","sio:SIO_000008","this:$(pid)_$(uniqid)_Death_information_Attribute","iri"],
["this:$(pid)_$(uniqid)_Status_Role","sio:SIO_000356","this:$(pid)_$(uniqid)_Death_information_Process","iri"],
["this:$(pid)_$(uniqid)_Death_information_Process","sio:SIO_000229","this:$(pid)_$(uniqid)_Death_information_Output","iri"],
["this:$(pid)_$(uniqid)_Death_information_Output","sio:SIO_000628","this:$(pid)_$(uniqid)_Death_information_Attribute","iri"],

# Types
["this:$(pid)_$(uniqid)_ID","rdf:type","sio:SIO_000115","iri"],
["this:$(pid)_$(uniqid)_Entity","rdf:type","sio:SIO_000498","iri"],
["this:$(pid)_$(uniqid)_Status_Role","rdf:type","sio:SIO_000016","iri"],
["this:$(pid)_$(uniqid)_Status_Role","rdf:type","obo:OBI_0000093","iri"],
["this:$(pid)_$(uniqid)_Status_Process","rdf:type","sio:SIO_001052","iri"],
["this:$(pid)_$(uniqid)_Status_Process","rdf:type","sio:SIO_000006","iri"],
["this:$(pid)_$(uniqid)_Status_Output","rdf:type","sio:SIO_000015","iri"],
["this:$(pid)_$(uniqid)_Status_Attribute","rdf:type","sio:SIO_000614","iri"],
["this:$(pid)_$(uniqid)_Status_Attribute","rdf:type","obo:NCIT_C166244","iri"],
["this:$(pid)_$(uniqid)_Status_Attribute","rdf:type","$(status_uri)","iri"],
["this:$(pid)_$(uniqid)_Status_Startdate","rdf:type","sio:SIO_000031","iri"],
["this:$(pid)_$(uniqid)_Status_Enddate","rdf:type","sio:SIO_000032","iri"],

["this:$(pid)_$(uniqid)_Death_information_Process","rdf:type","sio:SIO_000006","iri"],
["this:$(pid)_$(uniqid)_Death_information_Output","rdf:type","sio:SIO_000015","iri"],
["this:$(pid)_$(uniqid)_Death_information_Attribute","rdf:type","sio:SIO_000614","iri"],
["this:$(pid)_$(uniqid)_Death_information_Attribute","rdf:type","obo:NCIT_C70810","iri"],

# Labels
["this:$(pid)_$(uniqid)_Status_Role","rdfs:label","Role: Patient for status recording","xsd:string"],
["this:$(pid)_$(uniqid)_Status_Process","rdfs:label","Process: Status recording process","xsd:string"],
["this:$(pid)_$(uniqid)_Status_Startdate","rdfs:label","Startdate: $(date)","xsd:string"],
["this:$(pid)_$(uniqid)_Status_Enddate","rdfs:label","Enddate: $(date)","xsd:string"],
["this:$(pid)_$(uniqid)_Status_Output","rdfs:label","Output type: $(status_label)","xsd:string"],
["this:$(pid)_$(uniqid)_Status_Attribute","rdfs:label","Attribute type: $(status_label)","xsd:string"],
["this:$(pid)_$(uniqid)_Death_information_Process","rdfs:label","Process: Death information recording process","xsd:string"],
["this:$(pid)_$(uniqid)_Death_information_Output","rdfs:label","Output type: Patient death information","xsd:string"],
["this:$(pid)_$(uniqid)_Death_information_Attribute","rdfs:label","Attribute type: Date of death","xsd:string"],

# Values
["this:$(pid)_$(uniqid)_ID","sio:SIO_000300","$(pid)","xsd:string"],
["this:$(pid)_$(uniqid)_Status_Output","sio:SIO_000300","$(status_label)","xsd:string"],
["this:$(pid)_$(uniqid)_Death_information_Output","sio:SIO_000300","$(death_date)","xsd:date"],
["this:$(pid)_$(uniqid)_Status_Startdate","sio:SIO_000300","$(date)","xsd:date"],
["this:$(pid)_$(uniqid)_Status_Enddate","sio:SIO_000300","$(date)","xsd:date"]]



config = dict(
  source_name = "source_cde_test",
  configuration = "ejp",    # Two options for this parameter:
                            # ejp: it defines CDE-in-a-Box references, being compatible with this workflow  
                            # csv: No workflow defined, set the source configuration for been used by CSV as data source
                            
  csv_name = "source_1" # parameter only needed in case you pick "csv" as configuration
)

yarrrml = EMB(config, prefixes,triplets)

test = yarrrml.transform_ShEx("this")
print(test)

# test2 = yarrrml.transform_YARRRML()
# print(test2)

test2 = yarrrml.transform_OBDA()
print(test2)