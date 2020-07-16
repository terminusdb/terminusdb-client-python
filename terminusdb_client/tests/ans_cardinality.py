import pytest


@pytest.fixture(scope="module")
def property_max():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
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
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:range",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "xsd:string"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:A"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P_max"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "owl:Restriction",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P_max"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "owl:onProperty",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P_max"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "owl:maxCardinality",
                    },
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": 4,
                            "@type": "xsd:nonNegativeInteger",
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:A"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:P_max"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def property_min():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
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
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:range",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "xsd:string"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:A"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P_min"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "owl:Restriction",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P_min"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "owl:onProperty",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P_min"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "owl:minCardinality",
                    },
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": 2,
                            "@type": "xsd:nonNegativeInteger",
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:A"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:P_min"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def property_cardinalty():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
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
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:range",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "xsd:string"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:A"},
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
                        "woql:node": "scm:P_cardinality",
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "owl:Restriction",
                    },
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
                        "woql:node": "scm:P_cardinality",
                    },
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "owl:onProperty",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:P"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {
                        "@type": "woql:Node",
                        "woql:node": "scm:P_cardinality",
                    },
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "owl:cardinality",
                    },
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": 3,
                            "@type": "xsd:nonNegativeInteger",
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:A"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "scm:P_cardinality",
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def chain_insert():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddTriple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Node_ID",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "Type", "@type": "xsd:string"},
                    },
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddTriple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Node_ID",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Label",
                            "@type": "xsd:string",
                        },
                    },
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "woql:query": {
                    "@type": "woql:AddTriple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Node_ID",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:comment",
                    },
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Description",
                            "@type": "xsd:string",
                        },
                    },
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "woql:query": {
                    "@type": "woql:AddTriple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Node_ID",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:prop"},
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "Prop", "@type": "xsd:string"},
                    },
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "woql:query": {
                    "@type": "woql:AddTriple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Node_ID",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:prop"},
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Prop2",
                            "@type": "xsd:string",
                        },
                    },
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "woql:query": {
                    "@type": "woql:AddTriple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Node_ID",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "scm:myParentClass",
                    },
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def chain_doctype():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:MyDoc"},
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:MyDoc"},
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:MyDoc"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "abc",
                            "@type": "xsd:string",
                            "@language": "en",
                        },
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:MyDoc"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:comment",
                    },
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "abcd",
                            "@type": "xsd:string",
                            "@language": "en",
                        },
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop"},
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
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:range"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "xsd:dateTime"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 6},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:MyDoc"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 7},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "aaa",
                            "@type": "xsd:string",
                            "@language": "en",
                        },
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 8},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop2"},
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
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 9},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop2"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:range"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "xsd:integer"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 10},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop2"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:domain",
                    },
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:MyDoc"},
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 11},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:prop2"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "abe",
                            "@type": "xsd:string",
                            "@language": "en",
                        },
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }
