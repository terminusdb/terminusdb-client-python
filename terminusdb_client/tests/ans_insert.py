import pytest


@pytest.fixture(scope="module")
def insert_without():
    return {
        "@type": "AddTriple",
        "subject": {
            "@type": "NodeValue",
            "variable": "Bike_URL",
        },
        "predicate": {"@type": "NodeValue", "node": "rdf:type"},
        "object": {"@type": "Value", "node": "Bicycle"},
    }


@pytest.fixture(scope="module")
def insert_with_des():
    return {
        "@type": "And",
        "and": [
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "variable": "Bike_URL"},
                "predicate": {"@type": "NodeValue", "node": "rdf:type"},
                "object": {"@type": "Value", "node": "Bicycle"},
            },
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "variable": "Bike_URL"},
                "predicate": {"@type": "NodeValue", "node": "rdfs:label"},
                "object": {"@type": "Value", "variable": "Bike_Label"},
            },
            {
                "@type": "AddTriple",
                "subject": {"@type": "NodeValue", "variable": "Bike_URL"},
                "predicate": {
                    "@type": "NodeValue",
                    "node": "rdfs:comment",
                },
                "object": {
                    "@type": "Value",
                    "variable": "Bike_Des",
                },
            },
        ],
    }
