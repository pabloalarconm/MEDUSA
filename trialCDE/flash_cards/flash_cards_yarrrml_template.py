from embuilder.builder import EMB

prefixes = dict(
  rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#" ,
  rdfs = "http://www.w3.org/2000/01/rdf-schema#" ,
  ejprd_usecase_flash = "http://purl.org/ejp-rd/ontologies/2022/6/ejprd-usecase-flash#" ,
  xsd = "http://www.w3.org/2001/XMLSchema#",
  this = "http://my_example.com/ejprd/")


triplets = [

# Nodes
["this:$(uniqid)_User", "ejprd_usecase_flash:has_user_role", "this:$(uniqid)_Role","iri"],
["this:$(uniqid)_Role", "ejprd_usecase_flash:user_role_of", "this:$(uniqid)_User","iri"],
["this:$(uniqid)_Use_case", "ejprd_usecase_flash:use_case_of_user", "this:$(uniqid)_User","iri"],
["this:$(uniqid)_Use_case", "ejprd_usecase_flash:use_case_involves_specific_goal", "this:$(uniqid)_Specific_goal","iri"],
["this:$(uniqid)_Use_case", "ejprd_usecase_flash:such_that_I_can", "this:$(uniqid)_Contextual_goal","iri"],

#Types
["this:$(uniqid)_User", "rdf:type", "ejprd_usecase_flash:Clinical_doing_reseacrh","iri"],
["this:$(uniqid)_Role", "rdf:type", "ejprd_usecase_flash:Clinical_doing_reseacrh_role","iri"],
["this:$(uniqid)_Use_case", "rdf:type", "ejprd_usecase_flash:Use_case","iri"],
["this:$(uniqid)_Specific_goal", "rdf:type", "ejprd_usecase_flash:SpecificGoal","iri"],
["this:$(uniqid)_Contextual_goal", "rdf:type", "ejprd_usecase_flash:ContextualGoal","iri"],

# Labels
["this:$(uniqid)_User", "rdfs:label", "$(Name)","xsd:string"],
["this:$(uniqid)_Role", "rdfs:label", "$(As_a)","xsd:string"],
["this:$(uniqid)_Use_case", "rdfs:label", "$(Sum)","xsd:string"],
["this:$(uniqid)_Specific_goal", "rdfs:label", "$(such_that_I_can)","xsd:string"],
["this:$(uniqid)_Contextual_goal", "rdfs:label", "$(I_would_like_to)","xsd:string"]
]

config = dict(
  source_name = "source_cde_test",
  configuration = "ejp",   
  csv_name = "source_1",
  basicURI = "this"
)

builder = EMB(config, prefixes, triplets)
test = builder.transform_YARRRML()
# test = builder.transform_OBDA()
# test = builder.transform_ShEx()
# test = builder.transform_SPARQL()
print(test)