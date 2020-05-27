from ..utils import UTILS

"""
    The WOQL Schema Class provides pre-built WOQL queries for schema manipulation
    a) adding and deleting classes and properties
    b) loading datatype libraries
    c) boxing classes
"""


class WOQLSchema(g):

    def __init__(self):
        self.graph = g or "schema/main"

    def  WOQLQuery(self, query = {}):
        """
           TODO workaround for WOQLQuery
        """
        return query

    def _add_class(self, c, graph = self.graph):
    	ap = self.WOQLQuery()
    	if c is not None:
    		c = ap._cleanClass(c, true)
    		ap.adding_class = c
    		ap._add_quad(c,"rdf:type","owl:Class",graph)
    	return ap

    def _insert_class_data(self, data, refGraph):
        """
            Adds a bunch of class data in one go
        """
        ap = self.WOQLQuery()
        if data.id is not None:
            c = ap._cleanClass(data.id, true)
            ap = self.WOQLSchema().add_class(c, refGraph)
            if data.label is not None:
                ap.label(data.label)
            if data.description is not None:
                ap.description(data.description)
            if data.parent is not None:
                if not isinstance(data.parent, list):
                    data.parent = [data.parent]
                    """ap.parent(...data.parent) TODO"""
            for k in data:
                if ["id", "label", "description", "parent"].indexOf(k) == -1:
                    ap._insert_property_data(k, data[k], refGraph)
        return ap

    def _doctype_data(self, data, refGraph):
        if data.parent is None:
            data.parent = []
        if not isinstance(data.parent, list):
            data.parent = [data.parent]
        data.parent.append("Document")
        return self._insert_class_data(data, refGraph)

    def _insert_property_data(self, data, graph):
        ap = self.WOQLQuery()
        if data.id is not None:
            c = ap.cleanClass(data.id, true)
            ap._add_class(c, refGraph)
            if data.label is not None:
                ap.label(data.label)
            if data.description is not None:
                ap.description(data.description)
            if data.parent is not None:
                if not instance(data.parent, list):
                    data.parent = [data.parent]
                    """ap.parent(...data.parent) TODO"""
            for k in data:
                if ["id", "label", "description", "parent"].indexOf(k) == -1:
                   ap.insert_property_data(k, data[k], refGraph)
        return ap

    def _add_property(Self, p, t, graph=self.graph):
        ap = self.WOQLQuery()
        t = ap._cleanType(t, true) if t is not None else "xsd:string"
        if p is not None:
    		p = ap._cleanPathPredicate(p)
    		if UTILS.TypeHelper.isDatatype(t) is not None:
    		    ap.and(
    				self.WOQLQuery().add_quad(p, "rdf:type", "owl:DatatypeProperty", graph),
    				self.WOQLQuery().add_quad(p, "rdfs:range", t, graph)
    			)
    		else:
    			ap.and(
    				self.WOQLQuery().add_quad(p, "rdf:type", "owl:ObjectProperty", graph),
    				self.WOQLQuery().add_quad(p, "rdfs:range", t, graph)
    			)
    		ap._updated()
    	return ap
