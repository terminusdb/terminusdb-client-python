import pytest


@pytest.fixture(scope="module")
def doctype_without():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "AddTriple",
                "graph": "schema",
                "object": {"@type": "NodeValue", "node": "owl:Class"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "subject": {"@type": "Value", "node": "Station"},
            },
            {
                "@type": "AddTriple",
                "graph": "schema",
                "object": {
                    "@type": "NodeValue",
                    "node": "terminus:Document",
                },
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:subClassOf",
                },
                "subject": {"@type": "Value", "node": "Station"},
            },
        ],
    }


@pytest.fixture(scope="module")
def doctype_with_label():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "Station"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "node": "owl:Class"},
                "graph": "schema",
            },
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "Station"},
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
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "Station"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "Station Object",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
        ],
    }


@pytest.fixture(scope="module")
def doctype_with_des():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "Station"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "node": "owl:Class"},
                "graph": "schema",
            },
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "Station"},
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
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "Station"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "Station Object",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "node": "Station"},
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:comment",
                },
                "object": {
                    "@type": "Value",
                    "data": {
                        "@value": "A bike station object.",
                        "@type": "xsd:string",
                        "@language": "en",
                    },
                },
                "graph": "schema",
            },
        ],
    }
