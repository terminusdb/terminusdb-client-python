from .woql_query import WOQLQuery


class WOQLLib:
    def __init__(self, mode=None):
        if mode is None:
            self._mode = "query"
        else:
            self._mode = mode
        self._user_variables = []
        self._user_values = []
        self._default_variables = []
        self._parameters = []
        self._default_schema_resource = "schema/main"
        self._default_commit_resource = "_commits"
        self._default_meta_resource = "_meta"
        self._masterdb_resource = "terminus"
        self._masterdb_doc = "terminus://terminus/data"
        self._empty = ""

    def classes(self, values, variables, schema_resource=None):
        if schema_resource is not None:
            graph = schema_resource
        else:
            graph = self._default_schema_resource
        self._default_variables = [
            "Class ID",
            "Class Name",
            "Description",
            "Parents",
            "Children",
            "Abstract",
            "Parent",
            "Child",
        ]
        if variables:
            self._set_user_variables(variables)
        select_vars = self._get_varlist()[:6]
        qpattern = (
            WOQLQuery()
            .select(*select_vars)
            .woql_and(
                WOQLQuery().quad(self._varn("Class ID"), "type", "owl:Class", graph),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().quad(
                        self._varn("Class ID"),
                        "comment",
                        self._varn("Description"),
                        graph,
                    ),
                    WOQLQuery().eq(self._varn("Description"), self._empty),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().quad(
                        self._varn("Class ID"), "label", self._varn("Class Name"), graph
                    ),
                    WOQLQuery().eq(self._varn("Class Name"), ""),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery()
                    .quad(
                        self._varn("Class ID"),
                        "terminus:tag",
                        "terminus:abstract",
                        graph,
                    )
                    .eq(self._varn("Abstract"), "Yes"),
                    WOQLQuery().eq(self._varn("Abstract"), "No"),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery()
                    .group_by(
                        self._varn("Class ID"),
                        self._varn("Parent"),
                        self._varn("Parents"),
                    )
                    .woql_and(
                        WOQLQuery().quad(
                            self._varn("Class ID"),
                            "subClassOf",
                            self._varn("Parent"),
                            graph,
                        ),
                        WOQLQuery().woql_or(
                            WOQLQuery().eq(self._varn("Parent"), self._docroot()),
                            WOQLQuery().quad(
                                self._varn("Parent"), "type", "owl:Class", graph
                            ),
                        ),
                    ),
                    WOQLQuery().eq(self._varn("Parents"), ""),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery()
                    .group_by(
                        self._varn("Class ID"),
                        self._varn("Child"),
                        self._varn("Children"),
                    )
                    .woql_and(
                        WOQLQuery().quad(
                            self._varn("Child"),
                            "subClassOf",
                            self._varn("Class ID"),
                            graph,
                        ),
                        WOQLQuery().quad(
                            self._varn("Child"), "type", "owl:Class", graph
                        ),
                    ),
                    WOQLQuery().eq(self._varn("Children"), ""),
                ),
            )
        )
        return self._add_constraints(qpattern, values)

    def property(self, values, variables, schema_resource=None):
        if schema_resource is not None:
            graph = schema_resource
        else:
            graph = self._default_schema_resource
        self._default_variables = [
            "Property ID",
            "Property Name",
            "Property Domain",
            "Property Type",
            "Property Range",
            "Property Description",
            "OWL Type",
        ]
        if variables:
            self._set_user_variables(variables)
        select_vars = self._get_varlist[:6]
        qpattern = (
            WOQLQuery()
            .select(*select_vars)
            .woql_and(
                WOQLQuery()
                .quad(self._varn("Property ID"), "type", self._varn("OWL Type"), graph)
                .quad(
                    self._varn("Property ID"),
                    "domain",
                    self._varn("Property Domain"),
                    graph,
                )
                .quad(
                    self._varn("Property ID"),
                    "range",
                    self._varn("Property Range"),
                    graph,
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery()
                    .eq(self._varn("OWL Type"), "owl:DatatypeProperty")
                    .eq(self._varn("Property Type"), "Data"),
                    WOQLQuery()
                    .eq(self._varn("OWL Type"), "owl:ObjectProperty")
                    .eq(self._varn("Property Type"), "Object"),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().quad(
                        self._varn("Property ID"),
                        "label",
                        self._varn("Property Name"),
                        graph,
                    ),
                    WOQLQuery().eq(self._varn("Property Name"), ""),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().quad(
                        self._varn("Property ID"),
                        "comment",
                        self._varn("Property Description"),
                        graph,
                    ),
                    WOQLQuery().eq(self._varn("Property Description"), ""),
                ),
            )
        )
        return self._add_constraints(qpattern, values)

    def graphs(self, values, variables, cresource=None):
        if cresource is not None:
            pass
        else:
            self._default_commit_resource
        self._default_variables = [
            "Graph ID",
            "Graph Type",
            "Branch ID",
            "Commit ID",
            "Graph IRI",
            "Branch IRI",
            "Commit IRI",
        ]
        if variables:
            self._set_user_variables(variables)
        woql = WOQLQuery().woql_and(
            WOQLQuery().triple(
                self._varn("Graph IRI"), "ref:graph_name", self._varn("Graph ID")
            ),
            WOQLQuery().woql_or(
                WOQLQuery()
                .triple(
                    self._varn("Commit IRI"), "ref:instance", self._varn("Graph IRI")
                )
                .eq(self._varn("Graph Type"), "instance"),
                WOQLQuery()
                .triple(self._varn("Commit IRI"), "ref:schema", self._varn("Graph IRI"))
                .eq(self._varn("Graph Type"), "schema"),
                WOQLQuery()
                .triple(
                    self._varn("Commit IRI"), "ref:inference", self._varn("Graph IRI")
                )
                .eq(self._varn("Graph Type"), "inference"),
            ),
            WOQLQuery().triple(
                self._varn("Commit IRI"), "ref:commit_id", self._varn("Commit ID")
            ),
            WOQLQuery()
            .limit(1)
            .woql_or(
                WOQLQuery()
                .triple(
                    self._varn("Branch IRI"), "ref:ref_commit", self._varn("Commit IRI")
                )
                .triple(
                    self._varn("Branch IRI"), "ref:branch_name", self._varn("Branch ID")
                ),
                WOQLQuery()
                .eq(self._varn("Branch IRI"), "")
                .eq(self._varn("Branch ID"), ""),
            ),
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(cresource, compiled)
