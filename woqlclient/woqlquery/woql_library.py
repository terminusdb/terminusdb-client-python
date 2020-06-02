from .woql_query import WOQLQuery


class WOQLLibrary:
    def __init__(self):
        self.default_schema = "schema/main"

    def _get_all_documents(self):
        return WOQLQuery.woql_and(
            WOQLQuery.triple("v:Subject", "type", "v:Type"),
            WOQLQuery.sub("terminus:Document", "v:Type"),
        )

    def _document_metadata(self, g):
        g = g or self.default_schema
        return WOQLQuery.woql_and(
            WOQLQuery.triple("v:ID", "rdf:type", "v:Class"),
            WOQLQuery.sub("terminus:Document", "v:Class"),
            WOQLQuery.opt().triple("v:ID", "label", "v:Label"),
            WOQLQuery.opt().triple("v:ID", "comment", "v:Comment"),
            WOQLQuery.opt().quad("v:Class", "label", "v:Type", g),
            WOQLQuery.opt().quad("v:Class", "comment", "v:Type_Comment", g),
        )

    def _concrete_document_classes(self, g):
        g = g or self.default_schema
        return WOQLQuery.woql_and(
            WOQLQuery.sub("terminus:Document", "v:Class"),
            WOQLQuery.woql_not().quad(
                "v:Class", "terminus:tag", "terminus:abstract", g
            ),
            WOQLQuery.limit(1).opt().quad("v:Class", "label", "v:Label", g),
            WOQLQuery.limit(1).opt().quad("v:Class", "comment", "v:Comment", g),
        )

    def _property_metadata(self, g):
        g = g or self.default_schema
        return WOQLQuery.woql_and(
            WOQLQuery.quad("v:Property", "type", "v:PropertyType", g),
            WOQLQuery.woql_or(
                WOQLQuery.eq("v:PropertyType", "owl:DatatypeProperty"),
                WOQLQuery.eq("v:PropertyType", "owl:ObjectProperty"),
            ),
            WOQLQuery.opt().quad("v:Property", "range", "v:Range", g),
            WOQLQuery.opt().quad("v:Property", "type", "v:Type", g),
            WOQLQuery.opt().quad("v:Property", "label", "v:Label", g),
            WOQLQuery.opt().quad("v:Property", "comment", "v:Comment", g),
            WOQLQuery.opt().quad("v:Property", "domain", "v:Domain", g),
        )

    def _element_metadata(self, g):
        g = g or self.default_schema
        return WOQLQuery.select(
            "v:Element", "v:Label", "v:Comment", "v:Parents", "v:Domain", "v:Range"
        ).woql_and(
            WOQLQuery.quad("v:Element", "type", "v:Type", g),
            WOQLQuery.opt().quad("v:Element", "terminus:tag", "v:Abstract", g),
            WOQLQuery.opt().quad("v:Element", "label", "v:Label", g),
            WOQLQuery.opt().quad("v:Element", "comment", "v:Comment", g),
            WOQLQuery.opt()
            .group_by("v:Element", "v:Parent", "v:Parents")
            .woql_and(WOQLQuery.quad("v:Element", "subClassOf", "v:Parent", g)),
            WOQLQuery.opt().quad("v:Element", "domain", "v:Domain", g),
            WOQLQuery.opt().quad("v:Element", "range", "v:Range", g),
        )

    def _class_list(self, g):
        g = g or self.default_schema
        return WOQLQuery.select(
            "v:Class",
            "v:Name",
            "v:Parents",
            "v:Children",
            "v:Description",
            "v:Abstract",
        ).woql_and(
            WOQLQuery.quad("v:Class", "type", "owl:Class", g),
            WOQLQuery.limit(1).opt().quad("v:Class", "label", "v:Name", g),
            WOQLQuery.limit(1).opt().quad("v:Class", "comment", "v:Description", g),
            WOQLQuery.opt().quad("v:Class", "terminus:tag", "v:Abstract", g),
            WOQLQuery.opt()
            .group_by("v:Class", "v:Parent", "v:Parents")
            .woql_and(
                WOQLQuery.quad("v:Class", "subClassOf", "v:Parent", g),
                WOQLQuery.woql_or(
                    WOQLQuery.eq("v:Parent", "terminus:Document"),
                    WOQLQuery.quad("v:Parent", "type", "owl:Class", g),
                ),
            ),
            WOQLQuery.opt()
            .group_by("v:Class", "v:Child", "v:Children")
            .woql_and(
                WOQLQuery.quad("v:Child", "subClassOf", "v:Class", g),
                WOQLQuery.quad("v:Child", "type", "owl:Class", g),
            ),
        )

    def _get_data_of_class(self, chosen):
        return WOQLQuery.woql_and(
            WOQLQuery.triple("v:Subject", "type", chosen),
            WOQLQuery.opt().triple("v:Subject", "v:Property", "v:Value"),
        )

    def _get_data_of_property(self, chosen):
        return WOQLQuery.woql_and(
            WOQLQuery.triple("v:Subject", chosen, "v:Value"),
            WOQLQuery.opt().triple("v:Subject", "label", "v:Label"),
        )

    def _document_properties(self, doc_id, g):
        g = g or self.default_schema
        return WOQLQuery.woql_and(
            WOQLQuery.triple(doc_id, "v:Property", "v:Property_Value"),
            WOQLQuery.opt().quad("v:Property", "label", "v:Property_Label", g),
            WOQLQuery.opt().quad("v:Property", "type", "v:Property_Type", g),
        )

    def _get_document_connections(self, doc_id, g):
        g = g or self.default_schema
        return WOQLQuery.woql_and(
            WOQLQuery.eq("v:Docid", doc_id),
            WOQLQuery.woql_or(
                WOQLQuery.triple(doc_id, "v:Outgoing", "v:Entid"),
                WOQLQuery.triple("v:Entid", "v:Incoming", doc_id),
            ),
            WOQLQuery.triple("v:Entid", "type", "v:Enttype"),
            WOQLQuery.sub("terminus:Document", "v:Enttype"),
            WOQLQuery.opt().triple("v:Entid", "label", "v:Label"),
            WOQLQuery.opt().quad("v:Enttype", "label", "v:Class_Label", g),
        )

    def _get_all_document_connections(self):
        return WOQLQuery.woql_and(
            WOQLQuery.sub("terminus:Document", "v:Enttype"),
            WOQLQuery.triple("v:doc1", "type", "v:Enttype"),
            WOQLQuery.triple("v:doc1", "v:Predicate", "v:doc2"),
            WOQLQuery.triple("v:doc2", "type", "v:Enttype2"),
            WOQLQuery.sub("terminus:Document", "v:Enttype2"),
            WOQLQuery.opt().triple("v:doc1", "label", "v:Label1"),
            WOQLQuery.opt().triple("v:doc2", "label", "v:Label2"),
            WOQLQuery.woql_not().eq("v:doc1", "v:doc2"),
        )

    def _get_instance_meta(self, url, g):
        g = g or self.default_schema
        return WOQLQuery.woql_and(
            WOQLQuery.triple(url, "type", "v:InstanceType"),
            WOQLQuery.opt().triple(url, "label", "v:InstanceLabel"),
            WOQLQuery.opt().triple(url, "comment", "v:InstanceComment"),
            WOQLQuery.opt().quad("v:InstanceType", "label", "v:ClassLabel", g),
        )

    def _simple_graph_query(self, g):
        g = g or self.default_schema
        return WOQLQuery.woql_and(
            WOQLQuery.triple("v:Source", "v:Edge", "v:Target"),
            WOQLQuery.isa("v:Source", "v:Source_Class"),
            WOQLQuery.sub("terminus:Document", "v:Source_Class"),
            WOQLQuery.isa("v:Target", "v:Target_Class"),
            WOQLQuery.sub("terminus:Document", "v:Target_Class"),
            WOQLQuery.opt().triple("v:Source", "comment", "v:Source_Comment"),
            WOQLQuery.opt().triple("v:Source", "label", "v:Source_Label"),
            WOQLQuery.opt().quad("v:Source_Class", "label", "v:Source_Type", g),
            WOQLQuery.opt().quad(
                "v:Source_Class", "comment", "v:Source_Type_Comment", g
            ),
            WOQLQuery.opt().triple("v:Target", "label", "v:Target_Label"),
            WOQLQuery.opt().triple("v:Target", "comment", "v:Target_Comment"),
            WOQLQuery.opt().quad("v:Target_Class", "label", "v:Target_Type", g),
            WOQLQuery.opt().quad(
                "v:Target_Class", "comment", "v:Target_Type_Comment", g
            ),
            WOQLQuery.opt().quad("v:Edge", "label", "v:Edge_Type", g),
            WOQLQuery.opt().quad("v:Edge", "comment", "v:Edge_Type_Comment", g),
        )

    def _get_capabilities(self, uid, dbid):
        # These are for the master database
        pattern = []
        if uid is not None:
            pattern.append(WOQLQuery.idgen("doc:User", [uid], "v:UID"))
        if dbid is not None:
            pattern.append(WOQLQuery.idgen("doc:", [dbid], "v:DBID"))
        pattern = pattern.concat(
            [
                WOQLQuery.triple("v:UID", "terminus:authority", "v:CapID"),
                WOQLQuery.triple("v:CapID", "terminus:authority_scope", "v:DBID"),
                WOQLQuery.triple("v:CapID", "terminus:action", "v:Action"),
            ]
        )
        return WOQLQuery.woql_and(*pattern)

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
            WOQLQuery.unique(prefix + "Capability", capids, vcap),
            WOQLQuery.idgen(prefix, [target], vdb),
            WOQLQuery.woql_not().triple(vcap, "type", "terminus:DatabaseCapability"),
        ]
        writecap = [
            WOQLQuery.add_triple(vcap, "type", "terminus:DatabaseCapability"),
            WOQLQuery.add_triple(vcap, "terminus:authority_scope", vdb),
        ]
        for j in capabilities:
            writecap.append(
                WOQLQuery.add_triple(vcap, "terminus:action", capabilities[j])
            )

        return WOQLQuery.when(WOQLQuery.woql_and(*gens)).woql_and(*writecap)
