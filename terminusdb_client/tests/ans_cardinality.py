import pytest


@pytest.fixture(scope="module")
def property_max():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {
                        "@type": "Value",
                        "node": "owl:DatatypeProperty",
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:range",
                    },
                    "object": {"@type": "Value", "node": "xsd:string"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:domain",
                    },
                    "object": {"@type": "Value", "node": "scm:A"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P_max"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {
                        "@type": "Value",
                        "node": "owl:Restriction",
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P_max"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "owl:onProperty",
                    },
                    "object": {"@type": "Value", "node": "scm:P"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P_max"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "owl:maxCardinality",
                    },
                    "object": {
                        "@type": "Value",
                        "data": {
                            "@value": 4,
                            "@type": "xsd:nonNegativeInteger",
                        },
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 6},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:A"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:subClassOf",
                    },
                    "object": {"@type": "Value", "node": "scm:P_max"},
                    "graph": "schema",
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def property_min():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {
                        "@type": "Value",
                        "node": "owl:DatatypeProperty",
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:range",
                    },
                    "object": {"@type": "Value", "node": "xsd:string"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:domain",
                    },
                    "object": {"@type": "Value", "node": "scm:A"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P_min"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {
                        "@type": "Value",
                        "node": "owl:Restriction",
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P_min"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "owl:onProperty",
                    },
                    "object": {"@type": "Value", "node": "scm:P"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P_min"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "owl:minCardinality",
                    },
                    "object": {
                        "@type": "Value",
                        "data": {
                            "@value": 2,
                            "@type": "xsd:nonNegativeInteger",
                        },
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 6},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:A"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:subClassOf",
                    },
                    "object": {"@type": "Value", "node": "scm:P_min"},
                    "graph": "schema",
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def property_cardinalty():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {
                        "@type": "Value",
                        "node": "owl:DatatypeProperty",
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:range",
                    },
                    "object": {"@type": "Value", "node": "xsd:string"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:P"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:domain",
                    },
                    "object": {"@type": "Value", "node": "scm:A"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "query": {
                    "@type": "AddQuad",
                    "subject": {
                        "@type": "NodeValue",
                        "node": "scm:P_cardinality",
                    },
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {
                        "@type": "Value",
                        "node": "owl:Restriction",
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "query": {
                    "@type": "AddQuad",
                    "subject": {
                        "@type": "NodeValue",
                        "node": "scm:P_cardinality",
                    },
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "owl:onProperty",
                    },
                    "object": {"@type": "Value", "node": "scm:P"},
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 5},
                "query": {
                    "@type": "AddQuad",
                    "subject": {
                        "@type": "NodeValue",
                        "node": "scm:P_cardinality",
                    },
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "owl:cardinality",
                    },
                    "object": {
                        "@type": "Value",
                        "data": {
                            "@value": 3,
                            "@type": "xsd:nonNegativeInteger",
                        },
                    },
                    "graph": "schema",
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 6},
                "query": {
                    "@type": "AddQuad",
                    "subject": {"@type": "NodeValue", "node": "scm:A"},
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:subClassOf",
                    },
                    "object": {
                        "@type": "Value",
                        "node": "scm:P_cardinality",
                    },
                    "graph": "schema",
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def chain_insert():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "query": {
                    "@type": "AddTriple",
                    "subject": {
                        "@type": "NodeValue",
                        "variable": "Node_ID",
                    },
                    "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                    "object": {
                        "@type": "Value",
                        "variable": "Type"
                    },
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "query": {
                    "@type": "AddTriple",
                    "subject": {
                        "@type": "NodeValue",
                        "variable": "Node_ID"
                    },
                    "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
                    "object": {
                        "@type": "Value",
                        "variable": "Label"
                    },
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 2},
                "query": {
                    "@type": "AddTriple",
                    "subject": {
                        "@type": "NodeValue",
                        "variable": "Node_ID"
                    },
                    "predicate": {
                        "@type": "NodeValue",
                        "node": "rdfs:comment",
                    },
                    "object": {
                        "@type": "Value",
                        "variable":  "Description"
                    },
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 3},
                "query": {
                    "@type": "AddTriple",
                    "subject": {
                        "@type": "NodeValue",
                        "variable":  "Node_ID",
                    },
                    "predicate": {"@type": "NodeValue", "node": "scm:prop"},
                    "object": {
                        "@type": "Value",
                        "variable": "Prop",
                    },
                },
            },
            {
                "@type": "QueryListElement",
                "index": {"@type": "xsd:nonNegativeInteger", "@value": 4},
                "query": {
                    "@type": "AddTriple",
                    "subject": {
                        "@type": "NodeValue",
                        "variable": "Node_ID",
                    },
                    "predicate": {"@type": "NodeValue", "node": "scm:prop"},
                    "object": {
                        "@type": "Value",
                        "variable": "Prop2",
                    },
                },
            },
            {
                "@type": "AddTriple",
                "subject": {
                    "@type": "NodeValue",
                    "variable": "Node_ID"
                },
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:subClassOf",
                },
                "object": {
                    "@type": "Value",
                    "node": "scm:myParentClass",
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def chain_doctype():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:MyDoc"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "node": "owl:Class"},
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:MyDoc"},
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:subClassOf",
                },
                "object": {
                    "@type": "Value",
                    "node": "terminus:Document",
                },
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:MyDoc"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "abc",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:MyDoc"},
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:comment",
                },
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "abcd",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {
                    "@type": "Value",
                    "node": "owl:DatatypeProperty",
                },
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:range"},
                "object": {"@type": "Value", "node": "xsd:dateTime"},
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop"},
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:domain",
                },
                "object": {"@type": "Value", "node": "scm:MyDoc"},
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "aaa",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop2"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {
                    "@type": "Value",
                    "node": "owl:DatatypeProperty",
                },
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop2"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:range"},
                "object": {"@type": "Value", "node": "xsd:integer"},
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop2"},
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:domain",
                },
                "object": {"@type": "Value", "node": "scm:MyDoc"},
                "graph": "schema",
            },
            {
                "@type": "AddQuad",
                "subject": {"@type": "NodeValue", "node": "scm:prop2"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "abe",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
        ],
    }
