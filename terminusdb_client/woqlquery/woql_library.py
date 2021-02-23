from .woql_query import WOQLQuery


class WOQLLib:

    """Patterns to help getting the most useful information from schema graphs"""

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

    def classes(self, values=None, variables=None, schema_resource=None):
        """General Patten 1: Classes"""
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

    def property(self, values=None, variables=None, schema_resource=None):
        """General Pattern 2: Properties"""
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
        select_vars = self._get_varlist()[:6]
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

    def graphs(self, values=None, variables=None, cresource=None):
        """General Pattern 3: Graphs
        Retrieves information about the graphs in existence at any commit (and whether the commit is the head of a branch)"""
        if cresource is None:
            cresource = self._default_commit_resource
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

    def branches(self, values=None, variables=None, cresource=None):
        """General Pattern 4: Retrieves Branches, Their ID, Head Commit ID, Head Commit Time
        (if present, new branches have no commits)"""
        if cresource is None:
            cresource = self._default_commit_resource
        self._default_variables = [
            "Branch ID",
            "Time",
            "Commit ID",
            "Branch IRI",
            "Commit IRI",
        ]
        if variables:
            self._set_user_variables(variables)
        woql = (
            WOQLQuery()
            .triple(
                self._varn("Branch IRI"), "ref:branch_name", self._varn("Branch ID")
            )
            .opt()
            .triple(
                self._varn("Branch IRI"), "ref:ref_commit", self._varn("Commit IRI")
            )
            .triple(self._varn("Commit IRI"), "ref:commit_id", self._varn("Commit ID"))
            .triple(
                self._varn("Commit IRI"), "ref:commit_timestamp", self._varn("Time")
            )
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(cresource, compiled)

    def objects(self, values=None, variables=None):
        """General Pattern 5: Objects - just a list of object ids and their types"""
        self._default_variables = ["Object Type", "Object ID"]
        if variables:
            self._set_user_variables(variables)
        qpattern = WOQLQuery().triple(
            self._varn("Object ID"), "type", self._varn("Object Type")
        )
        return self._add_constraints(qpattern, values)

    def property_values(self, values=None, variables=None):
        """General Pattern 6: Full Object Properties"""
        self._default_variables = [
            "Object ID",
            "Property ID",
            "Property Value",
            "Value ID",
            "Value Class",
            "Any Class",
        ]
        if variables:
            self._set_user_variables(variables)
        select_vars = self._get_varlist()[:5]
        qpattern = (
            WOQLQuery()
            .select(*select_vars)
            .woql_or(
                WOQLQuery()
                .triple(
                    self._varn("Object ID"),
                    self._varn("Property ID"),
                    self._varn("Value ID"),
                )
                .triple(self._varn("Value ID"), "type", self._varn("Value Class"))
                .read_object(self._varn("Value ID"), self._varn("Property Value"))
                .comment(
                    "If the value of the property has a type, that means it is an object property and we retrieve the full object as the property value",
                ),
                WOQLQuery()
                .triple(
                    self._varn("Object ID"),
                    self._varn("Property ID"),
                    self._varn("Property Value"),
                )
                .woql_not()
                .triple(self._varn("Property Value"), "type", self._varn("Any Class"))
                .comment(
                    "If the value of the property has no type, that means it is a datatype property and we retrieve the datatype value as usual",
                ),
            )
        )

        return self._add_constraints(qpattern, values)

    def object_metadata(self, values=None, variables=None, schema_resource=None):
        """General Pattern 7: Object Metadata"""
        if schema_resource is not None:
            graph = schema_resource
        else:
            graph = self._default_schema_resource
        self._default_variables = [
            "Object ID",
            "Name",
            "Description",
            "Type ID",
            "Type Name",
            "Type Description",
        ]
        if variables:
            self._set_user_variables(variables)
        qpattern = (
            WOQLQuery()
            .triple(self._varn("Object ID"), "type", self._varn("Type ID"))
            .woql_and(
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().triple(
                        self._varn("Object ID"), "label", self._varn("Name")
                    ),
                    WOQLQuery().eq(self._varn("Name"), self._empty),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().triple(
                        self._varn("Object ID"), "comment", self._varn("Description")
                    ),
                    WOQLQuery().eq(self._varn("Description"), self._empty),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().quad(
                        self._varn("Type ID"), "label", self._varn("Type Name"), graph
                    ),
                    WOQLQuery().eq(self._varn("Type Name"), self._empty),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().quad(
                        self._varn("Type ID"),
                        "comment",
                        self._varn("Type Description"),
                        graph,
                    ),
                    WOQLQuery().eq(self._varn("Type Description"), self._empty),
                ),
            )
            .comment(
                "Returns an object(s) with its id, name and descriptions, and the object type, type id and type description",
            )
        )
        return self._add_constraints(qpattern, values)

    def property_metadata(self, values=None, variables=None, schema_resource=None):
        """General Pattern 8: Value Metadata"""
        if schema_resource is not None:
            graph = schema_resource
        else:
            graph = self._default_schema_resource
        self._default_variables = [
            "Object ID",
            "Property ID",
            "Property Name",
            "Property Value",
            "Property Description",
        ]
        if variables:
            self._set_user_variables(variables)
        qpattern = (
            WOQLQuery()
            .triple(
                self._varn("Object ID"),
                self._varn("Property ID"),
                self._varn("Property Value"),
            )
            .limit(1)
            .woql_or(
                WOQLQuery().quad(
                    self._varn("Property ID"),
                    "label",
                    self._varn("Property Name"),
                    graph,
                ),
                WOQLQuery().eq(self._varn("Property Name"), self._empty),
            )
            .limit(1)
            .woql_or(
                WOQLQuery().quad(
                    self._varn("Property ID"),
                    "comment",
                    self._varn("Property Description"),
                    graph,
                ),
                WOQLQuery().eq(self._varn("Property Description"), self._empty),
            )
            .comment(
                "Returns a property and its value and the basic metadata associated with the property (name, id, description)",
            )
        )
        return self._add_constraints(qpattern, values)

    def commits(self, values=None, variables=None, cresource=None):
        """General Pattern 9: Commits"""
        if cresource is None:
            cresource = self._default_commit_resource
        self._default_variables = [
            "Commit ID",
            "Commit IRI",
            "Time",
            "Author",
            "Message",
            "Parent ID",
            "Parent IRI",
            "Children",
            "Child ID",
            "Child IRI",
            "Branch IRI",
            "Branch ID",
        ]
        if variables:
            self._set_user_variables(variables)
        qpattern = (
            WOQLQuery()
            .triple(self._varn("Commit IRI"), "ref:commit_id", self._varn("Commit ID"))
            .triple(
                self._varn("Commit IRI"), "ref:commit_timestamp", self._varn("Time")
            )
            .limit(1)
            .woql_or(
                WOQLQuery().triple(
                    self._varn("Commit IRI"), "ref:commit_author", self._varn("Author")
                ),
                WOQLQuery().eq(self._varn("Author"), self._empty),
            )
            .limit(1)
            .woql_or(
                WOQLQuery().triple(
                    self._varn("Commit IRI"),
                    "ref:commit_message",
                    self._varn("Message"),
                ),
                WOQLQuery().eq(self._varn("Message"), self._empty),
            )
            .limit(1)
            .woql_or(
                WOQLQuery()
                .triple(
                    self._varn("Commit IRI"),
                    "ref:commit_parent",
                    self._varn("Parent IRI"),
                )
                .triple(
                    self._varn("Parent IRI"), "ref:commit_id", self._varn("Parent ID")
                ),
                WOQLQuery()
                .eq(self._varn("Parent IRI"), self._empty)
                .eq(self._varn("Parent ID"), self._empty),
            )
            .limit(1)
            .woql_or(
                WOQLQuery()
                .select(self._varn("Children"))
                .group_by(
                    [self._varn("Commit IRI"), self._varn("Child IRI")],
                    self._varn("Child ID"),
                    self._varn("Children"),
                )
                .triple(
                    self._varn("Child IRI"),
                    "ref:commit_parent",
                    self._varn("Commit IRI"),
                )
                .triple(
                    self._varn("Child IRI"), "ref:commit_id", self._varn("Child ID")
                ),
                WOQLQuery().eq(self._varn("Children"), self._empty),
            )
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
                .eq(self._varn("Branch IRI"), self._empty)
                .eq(self._varn("Branch ID"), self._empty),
            )
        )
        compiled = self._add_constraints(qpattern, values)
        return WOQLQuery().using(cresource, compiled)

    def commit_chain(self, values=None, variables=None, cresource=None):
        """General Pattern 10: Commit Chain"""
        if cresource is None:
            cresource = self._default_commit_resource
        self._default_variables = ["Head IRI", "Tail IRI", "Path"]
        if variables:
            self._set_user_variables(variables)
        woql = WOQLQuery().path(
            self._varn("Head IRI"),
            "ref:commit_parent+",
            self._varn("Tail IRI"),
            self._varn("Path"),
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(cresource, compiled)

    def repos(self, values, variables=None, cresource=None):
        """General Pattern 11: Repositories"""
        if cresource is None:
            cresource = self._default_commit_resource
        self._default_variables = [
            "Repository IRI",
            "Repository Name",
            "Repository Type",
            "Remote URL",
            "Repository Head IRI",
        ]
        if variables:
            self._set_user_variables(variables)
        woql = WOQLQuery().woql_and(
            WOQLQuery()
            .triple(
                self._varn("Repository IRI"),
                "repo:repository_name",
                self._varn("Repository Name"),
            )
            .triple(self._varn("Repository IRI"), "type", self._varn("Repository Type"))
            .triple(
                self._varn("Repository IRI"),
                "repo:repository_head",
                self._varn("Repository Head IRI"),
            )
            .woql_or(
                WOQLQuery().eq(self._varn("Repository Type"), "repo:Local"),
                WOQLQuery()
                .eq(self._varn("Repository Type"), "repo:Remote")
                .triple(
                    self._varn("Repository IRI"),
                    "repo:remote_url",
                    self._varn("Remote URL"),
                ),
            )
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(cresource, compiled)

    def dbs(self, values=None, variables=None):
        """General Pattern 12: dbs"""
        self._default_variables = [
            "DB Name",
            "DB ID",
            "Account",
            "Resource Name",
            "Description",
            "Allow Origin",
            "DB IRI",
            "DB x",
        ]
        if variables:
            self._set_user_variables(variables)
        woql = WOQLQuery().woql_and(
            WOQLQuery()
            .triple(self._varn("DB IRI"), "type", "terminus:Database")
            .triple(
                self._varn("DB IRI"),
                "terminus:resource_name",
                self._varn("Resource Name"),
            )
            .triple(
                self._varn("DB IRI"),
                "terminus:allow_origin",
                self._varn("Allow Origin"),
            )
            .split(
                self._varn("Resource Name"),
                "\\|",
                [self._varn("Account"), self._varn("DB ID")],
            )
            .woql_and(
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().triple(
                        self._varn("DB IRI"), "label", self._varn("DB Name")
                    ),
                    WOQLQuery().eq(self._varn("DB Name"), self._empty),
                ),
                WOQLQuery()
                .limit(1)
                .woql_or(
                    WOQLQuery().triple(
                        self._varn("DB IRI"), "comment", self._varn("Description")
                    ),
                    WOQLQuery().eq(self._varn("Description"), self._empty),
                ),
            )
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(self.masterdb_resource, compiled)

    def users(self, values=None, variables=None):
        """General Pattern 13: users"""
        self._default_variables = [
            "User ID",
            "User Name",
            "Commit Log ID",
            "User Notes",
            "Capabilities",
            "User IRI",
            "Capability IRI",
        ]
        if variables:
            self._set_user_variables(variables)
        select_vars = self._get_varlist()[:6]

        woql = (
            WOQLQuery()
            .select(*select_vars)
            .woql_and(
                WOQLQuery()
                .triple(self._varn("User IRI"), "type", "terminus:User")
                .triple(
                    self._varn("User IRI"), "terminus:agent_name", self._varn("User ID")
                )
                .woql_and(
                    WOQLQuery()
                    .limit(1)
                    .woql_or(
                        WOQLQuery().triple(
                            self._varn("User IRI"), "label", self._varn("User Name")
                        ),
                        WOQLQuery().eq(self._varn("User Name"), self._empty),
                    ),
                    WOQLQuery()
                    .limit(1)
                    .woql_or(
                        WOQLQuery().triple(
                            self._varn("User IRI"),
                            "terminus:commit_log_id",
                            self._varn("Commit Log ID"),
                        ),
                        WOQLQuery().eq(self._varn("Commit Log ID"), self._empty),
                    ),
                    WOQLQuery()
                    .limit(1)
                    .woql_or(
                        WOQLQuery().triple(
                            self._varn("User IRI"), "comment", self._varn("User Notes")
                        ),
                        WOQLQuery().eq(self._varn("User Notes"), self._empty),
                    ),
                    WOQLQuery()
                    .limit(1)
                    .woql_or(
                        WOQLQuery()
                        .group_by(
                            self._varn("User IRI"),
                            self._varn("Capability IRI"),
                            self._varn("Capabilities"),
                        )
                        .triple(
                            self._varn("User IRI"),
                            "terminus:authority",
                            self._varn("Capability IRI"),
                        ),
                        WOQLQuery().eq(self._varn("Capabilities"), self._empty),
                    ),
                )
            )
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(self.masterdb_resource, compiled)

    def capabilities(self, values=None, variables=None):
        """General Pattern 14: capabilities"""
        self._default_variables = [
            "Capability Name",
            "Capability Type",
            "Capability Description",
            "Capability IRI",
            "Access IRI",
            "Permissions",
            "Resources",
            "Permission ID",
            "Resource ID",
        ]
        if variables:
            self._set_user_variables(variables)
        # select_vars = self._get_varlist()[:7]
        woql = WOQLQuery().woql_and(
            WOQLQuery()
            .triple(self._varn("Capability IRI"), "type", self._varn("Capability Type"))
            .sub("terminus:Capability", self._varn("Capability Type")),
            WOQLQuery()
            .limit(1)
            .woql_or(
                WOQLQuery().triple(
                    self._varn("Capability IRI"), "label", self._varn("Capability Name")
                ),
                WOQLQuery().eq(self._varn("Capability Name"), self.empty),
            ),
            WOQLQuery()
            .limit(1)
            .woql_or(
                WOQLQuery().triple(
                    self._varn("Capability IRI"),
                    "comment",
                    self._varn("Capability Description"),
                ),
                WOQLQuery().eq(self._varn("Capability Description"), self.empty),
            ),
            WOQLQuery()
            .triple(
                self._varn("Capability IRI"),
                "terminus:access",
                self._varn("Access IRI"),
            )
            .group_by(
                self._varn("Access IRI"),
                self._varn("Permission ID"),
                self._varn("Permissions"),
            )
            .triple(
                self._varn("Access IRI"), "terminus:action", self._varn("Permission ID")
            ),
            WOQLQuery()
            .triple(
                self._varn("Capability IRI"),
                "terminus:access",
                self._varn("Access IRI"),
            )
            .group_by(
                self._varn("Access IRI"),
                self._varn("Resource ID"),
                self._varn("Resources"),
            )
            .triple(
                self._varn("Access IRI"),
                "terminus:authority_scope",
                self._varn("Resource ID"),
            ),
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(self._masterdb_resource, compiled)

    def add_user(self, user_id, values, variables=None):
        doc = self.masterdb_doc
        self.default_variables = [
            "User Name",
            "User Commit ID",
            "Notes",
            "Password",
            "User ID",
            "User IRI",
        ]
        if variables:
            self._set_user_variables(variables)
        query = (
            WOQLQuery()
            .idgen(doc + "User", user_id, self._varn("User IRI"))
            .add_triple(self._varn("User IRI"), "type", "terminus:User")
            .add_triple(self._varn("User IRI"), "terminus:agent_name", user_id)
            .add_triple(self._varn("User IRI"), "label", self._varn("User Name"))
            # .add_triple(self._varn('User IRI'), 'terminus:password', self._varn('Password'))
            .add_triple(
                self._varn("User IRI"),
                "terminus:commit_log_id",
                self._varn("User Commit ID"),
            )
            .add_triple(self._varn("User IRI"), "comment", self._varn("Notes"))
        )
        woql = self._add_constraints(query, values)
        return WOQLQuery().using(self._masterdb_resource, woql)

    def add_capability(self, user_id, label=None, description=None):
        query = WOQLQuery().add_triple(id, "type", "terminus:Capability")
        if label:
            query.add_triple(user_id, "label", label)
        if description:
            query.add_triple(user_id, "comment", description)
        return WOQLQuery().using(self.masterdb_resource, query)

    def add_access(self, accid, permissions, resources, label=None, description=None):
        query = WOQLQuery()
        if not accid:
            accid = "v:Access IRI"
            query.when(
                WOQLQuery().idgen("doc:Access", [permissions.concat(resources)], accid)
            )
        query.add_triple(accid, "type", "terminus:Access")
        for item in permissions:
            query.add_triple(accid, "terminus:action", item)
        for item in resources:
            query.add_triple(accid, "terminus:authority_scope", item)
        if label:
            query.add_triple(accid, "label", label)
        if description:
            query.add_triple(accid, "comment", description)
        return WOQLQuery().using(self.masterdb_resource, query)

    def grant_access(self, capiri, acciri):
        query = WOQLQuery().add_triple(capiri, "terminus:access", acciri)
        return WOQLQuery().using(self.masterdb_resource, query)

    def grant_capability(self, uid, capiri, uiri=None):
        if uiri is None:
            uiri = "v:User IRI"
        query = (
            WOQLQuery()
            .when(WOQLQuery().triple(uiri, "terminus:agent_name", uid))
            .add_triple(uiri, "terminus:authority", capiri)
        )
        return WOQLQuery().using(self.masterdb_resource, query)

    def revoke_capability(self, uid, capiri, uiri=None):
        if uiri is None:
            uiri = "v:User IRI"
        query = (
            WOQLQuery()
            .when(WOQLQuery().triple(uiri, "terminus:agent_name", uid))
            .delete_triple(uiri, "terminus:authority", capiri)
        )
        return WOQLQuery().using(self.masterdb_resource, query)

    def prefixes(self, values, variables=None, cresource=None):
        if cresource is None:
            cresource = self._default_commit_resource
        self.default_variables = ["Prefix", "URI", "Prefix Pair IRI"]
        if variables:
            self._set_user_variables(variables)
        query = (
            WOQLQuery()
            .triple(
                "ref:default_prefixes", "ref:prefix_pair", self._varn("Prefix Pair IRI")
            )
            .triple(self._varn("Prefix Pair IRI"), "ref:prefix_uri", self._varn("URI"))
            .triple(self._varn("Prefix Pair IRI"), "ref:prefix", self._varn("Prefix"))
        )
        woql = self._add_constraints(query, values)
        return WOQLQuery().using(cresource, woql)

    def insert_prefix(self, values, variables=None, cresource=None):
        if cresource is None:
            cresource = self._default_commit_resource
        self.default_variables = ["Prefix Pair IRI"]
        if variables:
            self._set_user_variables(variables)
        query = (
            WOQLQuery()
            .using(cresource)
            .idgen("doc:PrefixPair", values, self._varn("Prefix Pair IRI"))
            .add_triple(
                "ref:default_prefixes", "ref:prefix_pair", self._varn("Prefix Pair IRI")
            )
            .insert(self._varn("Prefix Pair IRI"), "ref:PrefixPair")
            .property("ref:prefix", values[0])
            .property("ref:prefix_uri", values[1])
        )
        return query

    def document_classes(self, values, variables=None, graph_resource=None):
        pattern = self.classes(values, variables, graph_resource)
        return self._add_doctype_constraint(pattern, self._varn("Class ID"))

    def user_capabilities(self, values, variables=None):
        self.capabilities(False, variables)  # load default variables
        self._default_variables.append("User IRI")
        self.default_variables.append("User ID")
        if variables:
            self._set_user_variables(variables)
        constraint = (
            WOQLQuery()
            .triple(
                self._varn("User IRI"), "terminus:agent_name", self._varn("User ID")
            )
            .triple(
                self._varn("User IRI"),
                "terminus:authority",
                self._varn("Capability IRI"),
            )
        )
        return WOQLLib().capabilities(constraint, variables)

    def commit_chain_full(self, values, graph_resource=None):
        if graph_resource is None:
            cresource = self._default_commit_resource
        else:
            cresource = graph_resource
        woql = WOQLQuery().woql_or(
            WOQLQuery().woql_and(
                WOQLLib().commit_chain(None, ["Commit IRI"]), WOQLLib().commits()
            ),
            WOQLQuery().woql_and(
                WOQLLib().commit_chain(None, ["Head IRI", "Commit IRI"]),
                WOQLLib().commits(),
            ),
        )
        compiled = self._add_constraints(woql, values)
        return WOQLQuery().using(cresource, compiled)

    def concrete_document_classes(self, values, variables=None, graph_resource=None):
        pattern = self.document_classes(values, variables, graph_resource)
        if graph_resource is None:
            graph = self._default_schema_resource
        else:
            graph = graph_resource
        return self._add_constraint(
            pattern,
            WOQLQuery()
            .woql_not()
            .quad(
                self._varn("Document IRI"), "terminus:tag", "terminus:abstract", graph
            )
            .comment("Does not match document class(es) marked as abstract"),
        )

    def document_metadata(self, values, variables=None, graph_resource=None):
        if not variables:
            variables = []
        pattern = self.object_metadata(values, variables, graph_resource)
        return self._add_doctype_constraint(pattern, self._varn("Type ID"))

    def documents(self, values, variables=None):
        if not variables:
            variables = ["Document Type", "Document ID"]
        pattern = self.objects(values, variables)
        return self._add_constraints(pattern, values)

    def first_commit(self):
        pattern = self.commits()
        noparent = (
            WOQLQuery()
            .using("_commits")
            .woql_and(
                WOQLQuery().triple(
                    self._varn("Any Commit IRI"),
                    "ref:commit_id",
                    self._varn("Commit ID"),
                ),
                WOQLQuery()
                .woql_not()
                .triple(
                    self._varn("Any Commit IRI"),
                    "ref:commit_parent",
                    self._varn("Parent IRI"),
                ),
            )
        )
        return self._add_constraint(pattern, noparent)

    def get_commit_from_now(self, step=1):
        return (
            WOQLQuery()
            .using("_commits")
            .path(
                "v:commit",
                f"ref:commit_parent{{{step},{step}}}",
                "v:target_commit",
                "v:path",
            )
            .triple("v:branch", "ref:branch_name", "main")
            .triple("v:branch", "ref:ref_commit", "v:commit")
            .triple("v:target_commit", "ref:commit_id", "v:cid")
        )

    def get_current_commit(self):
        return (
            WOQLQuery()
            .using("_commits")
            .triple("v:branch", "ref:branch_name", "main")
            .triple("v:branch", "ref:ref_commit", "v:commit")
        )

    def _add_constraints(self, pattern, vals):
        if not vals:
            return pattern
        if isinstance(vals, list):
            nq = WOQLQuery()
            for idx, item in enumerate(vals):
                if item is not None:
                    nq.woql_and(WOQLQuery().eq(item, self._var(idx)))
            return self._add_constraint(pattern, nq)
        elif hasattr(vals, "json"):
            return self._add_constraint(pattern, vals)
        elif isinstance(vals, dict):
            myvars = self._get_varlist()
            nq = WOQLQuery()
            for key, item in vals.items():
                if key in myvars:
                    nq.woql_and(WOQLQuery().eq(item), self._var(myvars.index(key)))
            return self._add_constraint(pattern, nq)
        else:
            return self._add_constraint(pattern, WOQLQuery().eq(self._var(0), vals))

    def _add_constraint(self, qpattern, woql):
        amalgamated = WOQLQuery().woql_and(woql, qpattern)
        return amalgamated

    def _var(self, idx):
        if idx >= len(self._user_variables):
            vname = self._default_variables[idx]
        else:
            vname = self._user_variables[idx]
        return "v:" + vname

    def _varn(self, default_varname):
        return self._var(self._default_variables.index(default_varname))

    def _get_varlist(self):
        varlist = []
        for idx, item in enumerate(self._default_variables):
            if idx < len(self._user_variables) and self._user_variables[idx]:
                varlist.append(self._user_variables[idx])
            else:
                varlist.append(item)
        return varlist

    def _get_meta(self, query):
        meta = {
            "variables": self._get_varlist(),
            "default_variables": self.default_variables,
            "query": query.to_dict(),
        }
        if self._user_variables:
            meta._user_variables = self._user_variables
        if self._user_values:
            meta._user_values = self._user_value
        return meta

    def _docroot(self):
        return "terminus:Document"

    def _add_doctype_constraint(self, pattern, varname):
        self._add_constraint(
            pattern,
            WOQLQuery()
            .sub(self._docroot(), varname)
            .comment("Only matches classes subsumed by terminus:Document class"),
        )
