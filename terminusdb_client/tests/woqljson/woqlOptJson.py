WoqlOpt = {
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
