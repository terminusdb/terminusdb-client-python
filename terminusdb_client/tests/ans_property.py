import pytest


@pytest.fixture(scope="module")
def property_without():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "owl:Class"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "terminus:Document",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "owl:DatatypeProperty",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:range"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "xsd:dateTime"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def property_with_des():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "owl:Class"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "terminus:Document",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "owl:DatatypeProperty",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:range"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "xsd:dateTime"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "Journey Duration",
                            "@type": "xsd:string",
                            "@language": "en",
                        },
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 6},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Duration"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:comment",
                    },
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "Journey duration in minutes.",
                            "@type": "xsd:string",
                            "@language": "en",
                        },
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def obj_property_without():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "owl:Class"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "terminus:Document",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {
                        "@type": "woql:Node",
                        "woql:node": "scm:start_station",
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "owl:ObjectProperty",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {
                        "@type": "woql:Node",
                        "woql:node": "scm:start_station",
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:range"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:Station"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {
                        "@type": "woql:Node",
                        "woql:node": "scm:start_station",
                    },
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:Journey"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }
