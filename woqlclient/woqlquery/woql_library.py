class WOQLLibrary(g=None):
    def __init__(self):
        self.default_schema = g or "schema/main"

    def _get_all_documents(self):
        return self.woqlQuery().woql_and(
            self.woqlQuery().triple("v:Subject", "type", "v:Type"),
            self.woqlQuery().sub("terminus:Document", "v:Type"),
        )

    def _document_metadata(self, g):
        g = g or self.default_schema
        return self.woqlQuery().woql_and(
            self.woqlQuery().triple("v:ID", "rdf:type", "v:Class"),
            self.woqlQuery().sub("terminus:Document", "v:Class"),
            self.woqlQuery().opt().triple("v:ID", "label", "v:Label"),
            self.woqlQuery().opt().triple("v:ID", "comment", "v:Comment"),
            self.woqlQuery().opt().quad("v:Class", "label", "v:Type", g),
            self.woqlQuery().opt().quad("v:Class", "comment", "v:Type_Comment", g),
        )

    def _concrete_document_classes(self, g):
        g = g or self.default_schema
        return self.woqlQuery().woql_and(
            self.woqlQuery().sub("terminus:Document", "v:Class"),
            self.woqlQuery()
            .woql_not()
            .quad("v:Class", "terminus:tag", "terminus:abstract", g),
            self.woqlQuery().limit(1).opt().quad("v:Class", "label", "v:Label", g),
            self.woqlQuery().limit(1).opt().quad("v:Class", "comment", "v:Comment", g),
        )

    def _property_metadata(self, g):
        g = g or self.default_schema
        return self.woqlQuery().woql_and(
            self.woqlQuery().quad("v:Property", "type", "v:PropertyType", g),
            self.woqlQuery().woql_or(
                self.woqlQuery().eq("v:PropertyType", "owl:DatatypeProperty"),
                self.woqlQuery().eq("v:PropertyType", "owl:ObjectProperty"),
            ),
            self.woqlQuery().opt().quad("v:Property", "range", "v:Range", g),
            self.woqlQuery().opt().quad("v:Property", "type", "v:Type", g),
            self.woqlQuery().opt().quad("v:Property", "label", "v:Label", g),
            self.woqlQuery().opt().quad("v:Property", "comment", "v:Comment", g),
            self.woqlQuery().opt().quad("v:Property", "domain", "v:Domain", g),
        )

    def _element_metadata(self, g):
        g = g or self.default_schema
        return (
            self.woqlQuery()
            .select(
                "v:Element", "v:Label", "v:Comment", "v:Parents", "v:Domain", "v:Range"
            )
            .woql_and(
                self.woqlQuery().quad("v:Element", "type", "v:Type", g),
                self.woqlQuery()
                .opt()
                .quad("v:Element", "terminus:tag", "v:Abstract", g),
                self.woqlQuery().opt().quad("v:Element", "label", "v:Label", g),
                self.woqlQuery().opt().quad("v:Element", "comment", "v:Comment", g),
                self.woqlQuery()
                .opt()
                .group_by("v:Element", "v:Parent", "v:Parents")
                .woql_and(
                    self.woqlQuery().quad("v:Element", "subClassOf", "v:Parent", g)
                ),
                self.woqlQuery().opt().quad("v:Element", "domain", "v:Domain", g),
                self.woqlQuery().opt().quad("v:Element", "range", "v:Range", g),
            )
        )

    def _class_list(self, g):
        g = g or self.default_schema
        return (
            self.woqlQuery()
            .select(
                "v:Class",
                "v:Name",
                "v:Parents",
                "v:Children",
                "v:Description",
                "v:Abstract",
            )
            .woql_and(
                self.woqlQuery().quad("v:Class", "type", "owl:Class", g),
                self.woqlQuery().limit(1).opt().quad("v:Class", "label", "v:Name", g),
                self.woqlQuery()
                .limit(1)
                .opt()
                .quad("v:Class", "comment", "v:Description", g),
                self.woqlQuery().opt().quad("v:Class", "terminus:tag", "v:Abstract", g),
                self.woqlQuery()
                .opt()
                .group_by("v:Class", "v:Parent", "v:Parents")
                .woql_and(
                    self.woqlQuery().quad("v:Class", "subClassOf", "v:Parent", g),
                    self.woqlQuery().woql_or(
                        self.woqlQuery().eq("v:Parent", "terminus:Document"),
                        self.woqlQuery().quad("v:Parent", "type", "owl:Class", g),
                    ),
                ),
                self.woqlQuery()
                .opt()
                .group_by("v:Class", "v:Child", "v:Children")
                .woql_and(
                    self.woqlQuery().quad("v:Child", "subClassOf", "v:Class", g),
                    self.woqlQuery().quad("v:Child", "type", "owl:Class", g),
                ),
            )
        )

    def _get_data_of_class(self, chosen):
        return self.woqlQuery().woql_and(
            self.woqlQuery().triple("v:Subject", "type", chosen),
            self.woqlQuery().opt().triple("v:Subject", "v:Property", "v:Value"),
        )

    def _get_data_of_property(self, chosen):
        return self.woqlQuery().woql_and(
            self.woqlQuery().triple("v:Subject", chosen, "v:Value"),
            self.woqlQuery().opt().triple("v:Subject", "label", "v:Label"),
        )

    def _document_properties(self, doc_id, g):
        g = g or self.default_schema
        return self.woqlQuery().woql_and(
            self.woqlQuery().triple(doc_id, "v:Property", "v:Property_Value"),
            self.woqlQuery().opt().quad("v:Property", "label", "v:Property_Label", g),
            self.woqlQuery().opt().quad("v:Property", "type", "v:Property_Type", g),
        )

    def _get_document_connections(self, doc_id, g):
        g = g or self.default_schema
        return self.woqlQuery().woql_and(
            self.woqlQuery().eq("v:Docid", doc_id),
            self.woqlQuery().woql_or(
                self.woqlQuery().triple(doc_id, "v:Outgoing", "v:Entid"),
                self.woqlQuery().triple("v:Entid", "v:Incoming", doc_id),
            ),
            self.woqlQuery().triple("v:Entid", "type", "v:Enttype"),
            self.woqlQuery().sub("terminus:Document", "v:Enttype"),
            self.woqlQuery().opt().triple("v:Entid", "label", "v:Label"),
            self.woqlQuery().opt().quad("v:Enttype", "label", "v:Class_Label", g),
        )

    def _get_all_document_connections(self):
        return self.woqlQuery().woql_and(
            self.woqlQuery().sub("terminus:Document", "v:Enttype"),
            self.woqlQuery().triple("v:doc1", "type", "v:Enttype"),
            self.woqlQuery().triple("v:doc1", "v:Predicate", "v:doc2"),
            self.woqlQuery().triple("v:doc2", "type", "v:Enttype2"),
            self.woqlQuery().sub("terminus:Document", "v:Enttype2"),
            self.woqlQuery().opt().triple("v:doc1", "label", "v:Label1"),
            self.woqlQuery().opt().triple("v:doc2", "label", "v:Label2"),
            self.woqlQuery().woql_not().eq("v:doc1", "v:doc2"),
        )

    def _get_instance_meta(self, url, g):
        g = g or self.default_schema
        return self.woqlQuery().woql_and(
            self.woqlQuery().triple(url, "type", "v:InstanceType"),
            self.woqlQuery().opt().triple(url, "label", "v:InstanceLabel"),
            self.woqlQuery().opt().triple(url, "comment", "v:InstanceComment"),
            self.woqlQuery().opt().quad("v:InstanceType", "label", "v:ClassLabel", g),
        )

    def _simple_graph_query(self, g):
        g = g or self.default_schema
        return self.woqlQuery().woql_and(
            self.woqlQuery().triple("v:Source", "v:Edge", "v:Target"),
            self.woqlQuery().isa("v:Source", "v:Source_Class"),
            self.woqlQuery().sub("terminus:Document", "v:Source_Class"),
            self.woqlQuery().isa("v:Target", "v:Target_Class"),
            self.woqlQuery().sub("terminus:Document", "v:Target_Class"),
            self.woqlQuery().opt().triple("v:Source", "comment", "v:Source_Comment"),
            self.woqlQuery().opt().triple("v:Source", "label", "v:Source_Label"),
            self.woqlQuery().opt().quad("v:Source_Class", "label", "v:Source_Type", g),
            self.woqlQuery()
            .opt()
            .quad("v:Source_Class", "comment", "v:Source_Type_Comment", g),
            self.woqlQuery().opt().triple("v:Target", "label", "v:Target_Label"),
            self.woqlQuery().opt().triple("v:Target", "comment", "v:Target_Comment"),
            self.woqlQuery().opt().quad("v:Target_Class", "label", "v:Target_Type", g),
            self.woqlQuery()
            .opt()
            .quad("v:Target_Class", "comment", "v:Target_Type_Comment", g),
            self.woqlQuery().opt().quad("v:Edge", "label", "v:Edge_Type", g),
            self.woqlQuery().opt().quad("v:Edge", "comment", "v:Edge_Type_Comment", g),
        )

    def _get_capabilities(self, uid, dbid):
        # These are for the master database
        pattern = []
        if uid is not None:
            pattern.append(self.woqlQuery().idgen("doc:User", [uid], "v:UID"))
        if dbid is not None:
            pattern.append(self.woqlQuery().idgen("doc:", [dbid], "v:DBID"))
        pattern = pattern.concat(
            [
                self.woqlQuery().triple("v:UID", "terminus:authority", "v:CapID"),
                self.woqlQuery().triple(
                    "v:CapID", "terminus:authority_scope", "v:DBID"
                ),
                self.woqlQuery().triple("v:CapID", "terminus:action", "v:Action"),
            ]
        )
        return self.woqlQuery().woql_and(*pattern)

    def _create_capability(self, target, capabilities, prefix, vcap):
        prefix = prefix or "doc:"
        vcap = vcap or "v:Capability"
        if target.indexOf(":") == -1:
            vdb = "v:DB" + target
        else:
            vdb = "v:DB" + target.split(":")[1]
        capids = [target].concat(capabilities.sort())
        # make variable names have global scope;
        gens = [
            self.woqlQuery().unique(prefix + "Capability", capids, vcap),
            self.woqlQuery().idgen(prefix, [target], vdb),
            self.woqlQuery()
            .woql_not()
            .triple(vcap, "type", "terminus:DatabaseCapability"),
        ]
        writecap = [
            self.woqlQuery().add_triple(vcap, "type", "terminus:DatabaseCapability"),
            self.woqlQuery().add_triple(vcap, "terminus:authority_scope", vdb),
        ]
        for j in capabilities:
            writecap.append(
                self.woqlQuery().add_triple(vcap, "terminus:action", capabilities[j])
            )

        return (
            self.woqlQuery().when(self.woqlQuery().woql_and(*gens)).woql_and(*writecap)
        )
