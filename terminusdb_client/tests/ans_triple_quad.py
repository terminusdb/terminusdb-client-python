import pytest


@pytest.fixture(scope="module")
def triple_opt():
    return {
        "@type": "woql:Optional",
        "woql:query": {
            "@type": "woql:Triple",
            "woql:subject": {"@type": "woql:Node", "woql:node": "doc:a"},
            "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:b"},
            "woql:object": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:string", "@value": "c"},
            },
        },
    }


@pytest.fixture(scope="module")
def quad_opt():
    return {
        "@type": "woql:Optional",
        "woql:query": {
            "@type": "woql:Quad",
            "woql:subject": {"@type": "woql:Node", "woql:node": "doc:a"},
            "woql:predicate": {"@type": "woql:Node", "woql:node": "scm:b"},
            "woql:object": {
                "@type": "woql:Datatype",
                "woql:datatype": {"@type": "xsd:string", "@value": "c"},
            },
            "woql:graph_filter": {"@type": "xsd:string", "@value": "d"},
        },
    }
