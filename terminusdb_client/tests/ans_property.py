# import pytest
#
#
# @pytest.fixture(scope="module")
# def property_without():
#     return {
#         "@type": "And",
#         "and": [
#              {
#                  "@type": "AddTriple",
#                  "subject": {"@type": "NodeValue", "node": "Journey"},
#                  "predicate": {"@type": "NodeValue", "node": "rdf:type"},
#                  "object": {"@type": "Value", "node": "owl:Class"},
#                  "graph": "schema",
#             },
#             {
#                 "@type": "AddTriple",
#                 "subject": {"@type": "NodeValue", "node": "Journey"},
#                 "predicate": {
#                     "@type": "NodeValue",
#                     "node": "rdfs:subClassOf",
#                 },
#                 "object": {
#                     "@type": "Value",
#                     "node": "terminus:Document",
#                 },
#                 "graph": "schema",
#             },
#             {
#                 "@type": "AddTriple",
#                 "subject": {"@type": "NodeValue", "node": "Duration"},
#                 "predicate": {"@type": "NodeValue", "node": "rdf:type"},
#                 "object": {
#                     "@type": "Value",
#                     "node": "owl:DatatypeProperty",
#                 },
#                 "graph": "schema",
#             },
#             {
#                 "@type": "AddTriple",
#                 "subject": {"@type": "NodeValue", "node": "Duration"},
#                 "predicate": {"@type": "NodeValue", "node": "rdfs:range"},
#                 "object": {"@type": "Value", "node": "xsd:dateTime"},
#                 "graph": "schema",
#             },
#             {
#                 "@type": "AddTriple",
#                 "subject": {"@type": "NodeValue", "node": "Duration"},
#                 "predicate": {
#                     "@type": "NodeValue",
#                     "node": "rdfs:domain",
#                 },
#                 "object": {"@type": "Value", "node": "Journey"},
#                 "graph": "schema",
#             },
#         ],
#     }
#
#
# @pytest.fixture(scope="module")
# def property_with_des():
#     return {
#         "@type": "And",
#         "and": [
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Journey"},
#                     "predicate": {"@type": "NodeValue", "node": "rdf:type"},
#                     "object": {"@type": "Value", "node": "owl:Class"},
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Journey"},
#                     "predicate": {
#                         "@type": "NodeValue",
#                         "node": "rdfs:subClassOf",
#                     },
#                     "object": {
#                         "@type": "Value",
#                         "node": "terminus:Document",
#                     },
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Duration"},
#                     "predicate": {"@type": "NodeValue", "node": "rdf:type"},
#                     "object": {
#                         "@type": "Value",
#                         "node": "owl:DatatypeProperty",
#                     },
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Duration"},
#                     "predicate": {"@type": "NodeValue", "node": "rdfs:range"},
#                     "object": {"@type": "Value", "node": "xsd:dateTime"},
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Duration"},
#                     "predicate": {
#                         "@type": "NodeValue",
#                         "node": "rdfs:domain",
#                     },
#                     "object": {"@type": "Value", "node": "Journey"},
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Duration"},
#                     "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
#                     "object": {
#                         "@type": "Value",
#                         "data": {
#                             "@value": "Journey Duration",
#                             "@type": "xsd:string",
#                             "@language": "en",
#                         },
#                     },
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "Value", "node": "Duration"},
#                     "predicate": {
#                         "@type": "NodeValue",
#                         "node": "rdfs:comment",
#                     },
#                     "object": {
#                         "@type": "Value",
#                         "data": {
#                             "@value": "Journey duration in minutes.",
#                             "@type": "xsd:string",
#                             "@language": "en",
#                         },
#                     },
#                     "graph": "schema",
#             },
#         ],
#     }
#
#
# @pytest.fixture(scope="module")
# def obj_property_without():
#     return {
#         "@type": "And",
#         "and": [
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Journey"},
#                     "predicate": {"@type": "NodeValue", "node": "rdf:type"},
#                     "object": {"@type": "Value", "node": "owl:Class"},
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {"@type": "NodeValue", "node": "Journey"},
#                     "predicate": {
#                         "@type": "NodeValue",
#                         "node": "rdfs:subClassOf",
#                     },
#                     "object": {
#                         "@type": "Value",
#                         "node": "terminus:Document",
#                     },
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {
#                         "@type": "NodeValue",
#                         "node": "start_station",
#                     },
#                     "predicate": {"@type": "NodeValue", "node": "rdf:type"},
#                     "object": {
#                         "@type": "Value",
#                         "node": "owl:ObjectProperty",
#                     },
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {
#                         "@type": "NodeValue",
#                         "node": "start_station",
#                     },
#                     "predicate": {"@type": "NodeValue", "node": "rdfs:range"},
#                     "object": {"@type": "Value", "node": "Station"},
#                     "graph": "schema",
#             },
#             {
#                     "@type": "AddTriple",
#                     "subject": {
#                         "@type": "NodeValue",
#                         "node": "start_station",
#                     },
#                     "predicate": {
#                         "@type": "NodeValue",
#                         "node": "rdfs:domain",
#                     },
#                     "object": {"@type": "Value", "node": "Journey"},
#                     "graph": "schema",
#             },
#         ],
#     }
