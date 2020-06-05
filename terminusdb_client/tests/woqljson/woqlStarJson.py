WoqlStar = {
    "@type": "woql:Limit",
    "woql:limit": {
        "@type": "woql:Datatype",
        "woql:datatype": {"@type": "xsd:nonNegativeInteger", "@value": 10},
    },
    "woql:query": {
        "@type": "woql:Triple",
        "woql:subject": {
            "@type": "woql:Variable",
            "woql:variable_name": {"@value": "Subject", "@type": "xsd:string"},
        },
        "woql:predicate": {
            "@type": "woql:Variable",
            "woql:variable_name": {"@value": "Predicate", "@type": "xsd:string"},
        },
        "woql:object": {
            "@type": "woql:Variable",
            "woql:variable_name": {"@value": "Object", "@type": "xsd:string"},
        },
    },
}
