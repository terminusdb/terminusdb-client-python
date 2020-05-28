
class WOQLLibrary(g):

    def __init__(self):
        self.default_schema = g or "schema/main"

    def WOQLQuery(self, query={}):
        """
           TODO workaround for WOQLQuery
        """
        return query

    def  _getAllDocuments(self):
        return self.WOQLQuery().woql_and(
    		self.WOQLQuery().triple("v:Subject", "type", "v:Type"),
    		self.WOQLQuery().sub("terminus:Document", "v:Type")
    	)

    def _documentMetadata(self, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().triple("v:ID", "rdf:type", "v:Class"),
    		self.WOQLQuery().sub("terminus:Document", "v:Class"),
    		self.WOQLQuery().opt().triple("v:ID", "label", "v:Label"),
    		self.WOQLQuery().opt().triple("v:ID", "comment", "v:Comment"),
    		self.WOQLQuery().opt().quad("v:Class", "label", "v:Type", g),
    		self.WOQLQuery().opt().quad("v:Class", "comment", "v:Type_Comment", g)
    	)

    def _concreteDocumentClasses(self, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().sub("terminus:Document", "v:Class"),
            self.WOQLQuery().woql_not().quad("v:Class", "terminus:tag", "terminus:abstract", g),
            self.WOQLQuery().limit(1).opt().quad("v:Class", "label", "v:Label", g),
    		self.WOQLQuery().limit(1).opt().quad("v:Class", "comment", "v:Comment", g)
    	)

    def _propertyMetadata(self, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().woql_and(
            self.WOQLQuery().quad("v:Property", "type", "v:PropertyType", g),
    		self.WOQLQuery().woql_or(
    			self.WOQLQuery().eq("v:PropertyType", "owl:DatatypeProperty"),
    			self.WOQLQuery().eq("v:PropertyType", "owl:ObjectProperty")
    		),
    		self.WOQLQuery().opt().quad("v:Property", "range", "v:Range", g),
    		self.WOQLQuery().opt().quad("v:Property", "type", "v:Type", g),
    		self.WOQLQuery().opt().quad("v:Property", "label", "v:Label", g),
    		self.WOQLQuery().opt().quad("v:Property", "comment", "v:Comment", g),
    		self.WOQLQuery().opt().quad("v:Property", "domain", "v:Domain", g)
    	)


    def _elementMetadata(self, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().select("v:Element", "v:Label", "v:Comment", "v:Parents", "v:Domain", "v:Range").woql_and(
    		self.WOQLQuery().quad("v:Element", "type", "v:Type", g),
    		self.WOQLQuery().opt().quad("v:Element", "terminus:tag", "v:Abstract", g),
    		self.WOQLQuery().opt().quad("v:Element", "label", "v:Label", g),
    		self.WOQLQuery().opt().quad("v:Element", "comment", "v:Comment", g),
            self.WOQLQuery().opt().group_by("v:Element", "v:Parent", "v:Parents").woql_and(
                self.WOQLQuery().quad("v:Element", "subClassOf", "v:Parent", g)
            ),
    		self.WOQLQuery().opt().quad("v:Element", "domain", "v:Domain", g),
    		self.WOQLQuery().opt().quad("v:Element", "range", "v:Range", g)
    	)

    def _classList(self, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().select("v:Class", "v:Name", "v:Parents", "v:Children", "v:Description", "v:Abstract").woql_and(
    		self.WOQLQuery().quad("v:Class", "type", "owl:Class", g),
    		self.WOQLQuery().limit(1).opt().quad("v:Class", "label", "v:Name", g),
    		self.WOQLQuery().limit(1).opt().quad("v:Class", "comment", "v:Description", g),
    		self.WOQLQuery().opt().quad("v:Class", "terminus:tag", "v:Abstract", g),
    		self.WOQLQuery().opt().group_by("v:Class", "v:Parent", "v:Parents").woql_and(
                self.WOQLQuery().quad("v:Class", "subClassOf", "v:Parent", g),
                self.WOQLQuery().woql_or(
                    self.WOQLQuery().eq("v:Parent", "terminus:Document"),
                    self.WOQLQuery().quad("v:Parent", "type", "owl:Class", g),
                )
            ),
    		self.WOQLQuery().opt().group_by("v:Class", "v:Child", "v:Children").woql_and(
                self.WOQLQuery().quad("v:Child", "subClassOf", "v:Class", g),
                self.WOQLQuery().quad("v:Child", "type", "owl:Class", g)
            )
    	)

    def _getDataOfClass(self, chosen):
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().triple("v:Subject", "type", chosen),
    		self.WOQLQuery().opt().triple("v:Subject", "v:Property", "v:Value")
    	)

    def _getDataOfProperty(self, chosen):
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().triple("v:Subject", chosen, "v:Value"),
    		self.WOQLQuery().opt().triple("v:Subject", "label", "v:Label")
    	)

    def _documentProperties(self, id, g):
    	g = g or this.default_schema
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().triple(id, "v:Property", "v:Property_Value"),
    		self.WOQLQuery().opt().quad("v:Property", "label", "v:Property_Label", g),
    		self.WOQLQuery().opt().quad("v:Property", "type", "v:Property_Type", g)
    	)

    def _getDocumentConnections(self, id, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().eq("v:Docid", id),
    		self.WOQLQuery().woql_or(
    			self.WOQLQuery().triple(id, "v:Outgoing", "v:Entid"),
    			self.WOQLQuery().triple("v:Entid", "v:Incoming", id)
    		),
    		self.WOQLQuery().triple("v:Entid", "type", "v:Enttype"),
    		self.WOQLQuery().sub("terminus:Document", "v:Enttype"),
    		self.WOQLQuery().opt().triple("v:Entid", "label", "v:Label"),
    		self.WOQLQuery().opt().quad("v:Enttype", "label", "v:Class_Label", g)
    	)

    def _getAllDocumentConnections(self):
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().sub("terminus:Document", "v:Enttype"),
    		self.WOQLQuery().triple("v:doc1", "type", "v:Enttype"),
    		self.WOQLQuery().triple("v:doc1", "v:Predicate", "v:doc2"),
    		self.WOQLQuery().triple("v:doc2", "type", "v:Enttype2"),
    		self.WOQLQuery().sub("terminus:Document", "v:Enttype2"),
    		self.WOQLQuery().opt().triple("v:doc1", "label", "v:Label1"),
    		self.WOQLQuery().opt().triple("v:doc2", "label", "v:Label2"),
    		self.WOQLQuery().woql_not().eq("v:doc1", "v:doc2")
    	)

    def _getInstanceMeta(self, url, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().woql_and(
    		self.WOQLQuery().triple(url, "type", "v:InstanceType"),
    		self.WOQLQuery().opt().triple(url, "label", "v:InstanceLabel"),
    		self.WOQLQuery().opt().triple(url, "comment", "v:InstanceComment"),
    		self.WOQLQuery().opt().quad("v:InstanceType", "label", "v:ClassLabel", g)
    	)

    def _simpleGraphQuery(self, g):
    	g = g or self.default_schema
    	return self.WOQLQuery().woql_and(
    	    self.WOQLQuery().triple("v:Source", "v:Edge", "v:Target"),
    	    self.WOQLQuery().isa("v:Source", "v:Source_Class"),
    	    self.WOQLQuery().sub("terminus:Document", "v:Source_Class"),
    	    self.WOQLQuery().isa("v:Target", "v:Target_Class"),
    	    self.WOQLQuery().sub("terminus:Document", "v:Target_Class"),
    	    self.WOQLQuery().opt().triple("v:Source", "comment", "v:Source_Comment"),
            self.WOQLQuery().opt().triple("v:Source", "label", "v:Source_Label"),
    	    self.WOQLQuery().opt().quad("v:Source_Class", "label", "v:Source_Type", g),
    	    self.WOQLQuery().opt().quad("v:Source_Class", "comment", "v:Source_Type_Comment", g),
    	    self.WOQLQuery().opt().triple("v:Target", "label", "v:Target_Label"),
    	    self.WOQLQuery().opt().triple("v:Target", "comment", "v:Target_Comment"),
    	    self.WOQLQuery().opt().quad("v:Target_Class", "label", "v:Target_Type", g),
    	    self.WOQLQuery().opt().quad("v:Target_Class", "comment", "v:Target_Type_Comment", g),
    	    self.WOQLQuery().opt().quad("v:Edge", "label", "v:Edge_Type", g),
    	    self.WOQLQuery().opt().quad("v:Edge", "comment", "v:Edge_Type_Comment", g)
    	)

    def _getCapabilities(self,uid, dbid):
        #These are for the master database
        pattern = []
        if uid is not None:
            pattern.append(
                self.WOQLQuery().idgen("doc:User", [uid], "v:UID")
            )
        if dbid is not None:
            pattern.append(
                self.WOQLQuery().idgen("doc:", [dbid], "v:DBID")
            )
        pattern = pattern.concat([
            self.WOQLQuery().triple("v:UID", "terminus:authority", "v:CapID"),
            self.WOQLQuery().triple("v:CapID", "terminus:authority_scope", "v:DBID"),
            self.WOQLQuery().triple("v:CapID", "terminus:action", "v:Action")
        ])
        return self.WOQLQuery().woql_and(*pattern)

    def _createCapability(self, target, capabilities, prefix, vcap):
    	prefix = prefix or "doc:"
    	vcap = vcap or "v:Capability"
        if target.indexOf(":") == -1:
            vdb = "v:DB" + target
        else:
            vdb = "v:DB" + target.split(":")[1]
    	capids = [target].concat(capabilities.sort());
        #make variable names have global scope;
        gens = [
    		self.WOQLQuery().unique(prefix+"Capability", capids, vcap),
    		self.WOQLQuery().idgen(prefix, [target], vdb),
    		self.WOQLQuery().woql_not().triple(vcap, "type", "terminus:DatabaseCapability")
    	]
    	writecap = [
    		self.WOQLQuery().add_triple(vcap, "type", "terminus:DatabaseCapability"),
    		self.WOQLQuery().add_triple(vcap, "terminus:authority_scope", vdb),
    	]
        for j in capabilities:
    		writecap.append(self.WOQLQuery().add_triple(vcap, "terminus:action", capabilities[j]))

        return  self.WOQLQuery().when(self.WOQLQuery().woql_and(*gens)).woql_and(*writecap)
