import pytest


@pytest.fixture(scope="module")
def insert_without():
    return {
        "@type": "woql:AddTriple",
        "woql:subject": {
            "@type": "woql:Variable",
            "woql:variable_name": {"@value": "Bike_URL", "@type": "xsd:string"},
        },
        "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
        "woql:object": {"@type": "woql:Node", "woql:node": "scm:Bicycle"},
    }


@pytest.fixture(scope="module")
def insert_with_des():
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
                            "@value": "Bike_URL",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdf:type"},
                    "woql:object": {"@type": "woql:Node", "woql:node": "scm:Bicycle"},
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
                            "@value": "Bike_URL",
                            "@type": "xsd:string",
                        },
                    },
                    "woql:predicate": {"@type": "woql:Node", "woql:node": "rdfs:label"},
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {
                            "@value": "Bike_Label",
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
                            "@value": "Bike_URL",
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
                            "@value": "Bike_Des",
                            "@type": "xsd:string",
                        },
                    },
                },
            },
        ],
    }
