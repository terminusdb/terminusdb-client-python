import pytest


@pytest.fixture(scope="module")
def doctype_without():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "owl:Class"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                    "woql:object": {
                        "@type": "woql:Node",
                        "woql:node": "terminus:Document",
                    },
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:subClassOf",
                    },
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
                },
            },
        ],
    }


@pytest.fixture(scope="module")
def doctype_with_label():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "Station Object",
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
def doctype_with_des():
    return {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:AddQuad",
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "Station Object",
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
                    "woql:subject": {"@type": "woql:Node", "woql:node": "scm:Station"},
                    "woql:predicate": {
                        "@type": "woql:Node",
                        "woql:node": "rdfs:comment",
                    },
                    "woql:object": {
                        "@type": "woql:Datatype",
                        "woql:datatype": {
                            "@value": "A bike station object.",
                            "@type": "xsd:string",
                            "@language": "en",
                        },
                    },
                    "woql:graph": {"@type": "xsd:string", "@value": "schema/main"},
                },
            },
        ],
    }
