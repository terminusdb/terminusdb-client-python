WoqlExtra = {
    "chainAndJson": {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:Triple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "A", "@type": "xsd:string"},
                    },
                    "woql:predicate": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "B", "@type": "xsd:string"},
                    },
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "C", "@type": "xsd:string"},
                    },
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:Triple",
                    "woql:subject": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "D", "@type": "xsd:string"},
                    },
                    "woql:predicate": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "E", "@type": "xsd:string"},
                    },
                    "woql:object": {
                        "@type": "woql:Variable",
                        "woql:variable_name": {"@value": "F", "@type": "xsd:string"},
                    },
                },
            },
        ],
    },
    "usingJson": {
        "@type": "woql:Using",
        "@context": "/api/prefixes/userName/dbName/local/commit/commitID",
        "woql:collection": {
            "@type": "xsd:string",
            "@value": "userName/dbName/local/commit/commitID",
        },
        "woql:query": {
            "@type": "woql:Triple",
            "woql:subject": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "A", "@type": "xsd:string"},
            },
            "woql:predicate": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "B", "@type": "xsd:string"},
            },
            "woql:object": {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": "C", "@type": "xsd:string"},
            },
        },
    },
    "multiUsingJson": {
        "@type": "woql:And",
        "woql:query_list": [
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 0},
                "woql:query": {
                    "@type": "woql:Using",
                    "@context": "/api/prefixes/admin/dbName/local/commit/commitID_1",
                    "woql:collection": {
                        "@type": "xsd:string",
                        "@value": "admin/dbName/local/commit/commitID_1",
                    },
                    "woql:query": {
                        "@type": "woql:Triple",
                        "woql:subject": {
                            "@type": "woql:Variable",
                            "woql:variable_name": {
                                "@value": "A",
                                "@type": "xsd:string",
                            },
                        },
                        "woql:predicate": {
                            "@type": "woql:Variable",
                            "woql:variable_name": {
                                "@value": "B",
                                "@type": "xsd:string",
                            },
                        },
                        "woql:object": {
                            "@type": "woql:Variable",
                            "woql:variable_name": {
                                "@value": "C",
                                "@type": "xsd:string",
                            },
                        },
                    },
                },
            },
            {
                "@type": "woql:QueryListElement",
                "woql:index": {"@type": "xsd:nonNegativeInteger", "@value": 1},
                "woql:query": {
                    "@type": "woql:Using",
                    "@context": "/api/prefixes/admin/dbName/local/commit/commitID_2",
                    "woql:collection": {
                        "@type": "xsd:string",
                        "@value": "admin/dbName/local/commit/commitID_2",
                    },
                    "woql:query": {
                        "@type": "woql:Not",
                        "woql:query": {
                            "@type": "woql:Triple",
                            "woql:subject": {
                                "@type": "woql:Variable",
                                "woql:variable_name": {
                                    "@value": "A",
                                    "@type": "xsd:string",
                                },
                            },
                            "woql:predicate": {
                                "@type": "woql:Variable",
                                "woql:variable_name": {
                                    "@value": "B",
                                    "@type": "xsd:string",
                                },
                            },
                            "woql:object": {
                                "@type": "woql:Variable",
                                "woql:variable_name": {
                                    "@value": "C",
                                    "@type": "xsd:string",
                                },
                            },
                        },
                    },
                },
            },
        ],
    },
}
