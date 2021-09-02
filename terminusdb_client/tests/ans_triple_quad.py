import pytest


@pytest.fixture(scope="module")
def triple_opt():
    return {
        "@type": "Optional",
        "query": {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "a"},
            "predicate": {"@type": "NodeValue", "node": "b"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "c"},
            },
        },
    }


@pytest.fixture(scope="module")
def quad_opt():
    return {
        "@type": "Optional",
        "query": {
            "@type": "Triple",
            "subject": {"@type": "NodeValue", "node": "a"},
            "predicate": {"@type": "NodeValue", "node": "b"},
            "object": {
                "@type": "Value",
                "data": {"@type": "xsd:string", "@value": "c"},
            },
            "graph": "d",
        },
    }
