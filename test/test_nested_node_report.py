"""\
Test that nested node graphs are included in the sh:detail section of the validation report
TODO: Extend test to have nodes of nodes, etc. See nesting is working properly.
"""

from cgi import test
from pyshacl import validate
from rdflib import Graph

shacl_file = '''\
# prefix: ex

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
#
ex:vfd_basic a sh:NodeShape;
    sh:targetClass brick:VFD ;
    # list node shapes to use
    sh:node
        ex:vfd_relationships,
        ex:vfd_points_min,
        ex:deep_nest_0
    .


# COMPONENT SHAPES. These do not have a target...they need the parent to work...
#
ex:vfd_relationships a sh:NodeShape;
    sh:property ex:vfd_partOf .

ex:vfd_points_min a sh:NodeShape;
    # VFD has the minimum set of points
    sh:property ex:point_run_status .

# Triple nested shape
ex:deep_nest_0 a sh:NodeShape ;
    sh:node ex:deep_nest_1 .

ex:deep_nest_1 a sh:NodeShape ;
    sh:property ex:deep_nest_property_1 ;
    sh:node ex:deep_nest_2 ;
    .

ex:deep_nest_2 a sh:NodeShape ;
    sh:property ex:deep_nest_property_2
    .

# PROPERTY SHAPES
#
ex:vfd_partOf a sh:PropertyShape ;
    sh:path brick:isPartOf ;
    sh:or (
        [ sh:class brick:Fan ]
        [ sh:class brick:Pump ]
    ) .

ex:point_run_status a sh:PropertyShape ;
    sh:message "Entity does not have a run status point defined" ;
    sh:path brick:hasPoint ;
    sh:qualifiedMinCount 1 ;
    sh:qualifiedValueShapesDisjoint true ;
    sh:qualifiedValueShape [
        sh:class brick:On_Off_Status
    ]
    .

ex:deep_nest_property_1 a sh:PropertyShape ;
    sh:path brick:isPartOf ;
    sh:class brick:Fan .

ex:deep_nest_property_2 a sh:PropertyShape ;
    sh:path brick:isPartOf ;
    sh:class brick:Fan .
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

brick:VFD a owl:Class .
brick:Fan a owl:Class .
brick:AHU a owl:Class .

## RELATIONSHIPS
brick:isPartOf a owl:ObjectProperty .
brick:isPointOf a owl:ObjectProperty .

## POINTS
brick:On_Off_Status a owl:Class .
brick:Frequency_Sensor a owl:Class .


# SET MODEL
# ===============================

# points
ex:s_run_status a brick:On_Off_Status .

## This should pass
ex:f1 a brick:Fan .
ex:vfd1 a brick:VFD ;
    brick:isPartOf ex:f1 ;
    brick:hasPoint ex:s_run_status .

# THIS SHOULD FAIL, missing min points
ex:f2 a brick:Fan .
ex:vfd2 a brick:VFD ;
    brick:isPartOf ex:f2 ;
    brick:hasPoint brick:Frequency_Sensor.

# THIS SHOULD FAIL, incorrect parent
ex:ahu0 a brick:AHU .
ex:vfd3 a brick:VFD ;
    brick:isPartOf ex:ahu0 ;
    brick:hasPoint ex:s_run_status .

ex:ahu1 a brick:AHU .
ex:vfd4 a brick:VFD ;
    brick:isPartOf ex:ahu1 ;
    brick:hasPoint ex:s_run_status .
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
