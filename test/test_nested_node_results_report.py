"""\
Test that nested node graphs only return a single result in results report for each node with a target
"""

from cgi import test
from pyshacl import validate
from rdflib import Graph

shacl_file = '''\

@prefix ex: <http://datashapes.org/shasf/tests/expression/nested_node_report.test.shacl#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix switch: <https://switchautomation.com/schemas/BrickExtension#> .

<http://datashapes.org/shasf/tests/expression/nested_node_report.test.shacl>
  rdf:type owl:Ontology ;
  rdfs:label "Test of nested node graph reporting" ;
.

# BASE SHAPE
# This is the only shape with an explicit (or implicit) target declaration
#
ex:base_shape a sh:NodeShape;
    sh:targetClass brick:Target_Class ;
    sh:message "Parent message" ;
    # list node shapes to use
    sh:node
        ex:unnested_node_shape,
        ex:nested_node_shape_2_lvl0, 
        ex:nested_node_shape_2_lvl1 .


# COMPONENT SHAPES. These do not have a target declaration...they need the parent to work...
#

# Unnested
ex:unnested_node_shape a sh:NodeShape;
    sh:message "Unnested node" ;
    sh:property ex:test_property .

ex:nested_node_shape_2_lvl0 a sh:NodeShape;
    sh:message "Nested node 2 lvl 0" ;
    sh:node ex:nested_node_shape_2_lvl1 .
    
ex:nested_node_shape_2_lvl1 a sh:NodeShape ;
    sh:node ex:nested_node_shape_2_lvl2 .

ex:nested_node_shape_2_lvl2 a sh:NodeShape ;
    sh:property ex:test_property .


# use same test in all nodes for consistency
ex:test_property a sh:PropertyShape ;
    sh:message "Entity does not have Part_Class part" ;
    sh:minCount 1 ;
    sh:path brick:hasPart ;
    sh:class brick:Part_Class .
'''

data_graph = '''
# prefix: ex

@prefix ex: <http://datashapes.org/shasf/tests/expression/nested_node_report.test.shacl#> .
@prefix brick: <https://brickschema.org/schema/Brick#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .


# SET ONTOLOGY
# ===============================

brick:Target_Class a owl:Class .
brick:Part_Class a owl:Class .

brick:hasPart a owl:ObjectProperty .

# SET MODEL
# ===============================

ex:test_part a brick:Part_Class .

ex:test_entity_success a brick:Target_Class ;
    brick:hasPart ex:test_part .

ex:test_entity_fail a brick:Target_Class .

'''

def test_nested_node_report():
    d = Graph().parse(data=data_graph, format="turtle")
    s = Graph().parse(data=shacl_file, format="turtle")
    conforms, report, message = validate(d, shacl_graph=s, debug=False)
    print(message)
    print(report.serialize(format="longturtle"))
    assert not conforms

if __name__ == "__main__":
    exit(test_nested_node_report())
