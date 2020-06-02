class TripleBuilder:
    """
    @file Triple Builder
        higher level composite queries - not language or api elements
        Class for enabling building of triples from pieces
        type is add_quad / remove_quad / add_triple / remove_triple
     """

    def __init__(self, triple_type, query, s, g):
        """
        what accumulation type are we
        """
        if triple_type and triple_type.indexOf(":") == -1:
            triple_type = "woql:" + type
        self.type = triple_type
        self.cursor = query.cursor
        if s is not None:
            self.subject = s
        else:
            self.subject = False
        self.query = query
        self.g = g

    def label(self, lab, lang="en"):
        if lab[:2] == "v:":
            d = lab
        else:
            d = {"@value": lab, "@type": "xsd:string", "@language": lang}
        x = self._add_po("rdfs:label", d)
        return x

    def graph(self, g):
        self.g = g

    def description(self, c, lang="en"):
        if c[:2] == "v:":
            d = c
        else:
            d = {"@value": c, "@type": "xsd:string", "@language": lang}
        return self._addPO("rdfs:comment", d)

    def _add_po(self, p, o, g):
        g = g or self.g
        newq = False
        if self.type == "woql:Triple":
            newq = self.WOQLQuery().triple(self.subject, p, o)
        elif self.type == "woql:AddTriple":
            newq = self.WOQLQuery().add_triple(self.subject, p, o)
        elif self.type == "woql:DeleteTriple":
            newq = self.WOQLQuery().delete_triple(self.subject, p, o)
        elif self.type == "woql:Quad":
            newq = self.WOQLQuery().quad(self.subject, p, o, g)
        elif self.type == "woql:AddQuad":
            newq = self.WOQLQuery().add_quad(self.subject, p, o, g)
        elif self.type == "woql:DeleteQuad":
            newq = self.WOQLQuery().delete_quad(self.subject, p, o, g)
        elif g is not None:
            newq = self.WOQLQuery().quad(self.subject, p, o, g)
        else:
            newq = self.WOQLQuery().triple(self.subject, p, o)
        self._query.woql_and(newq)

    def _get_o(self, s, p):
        if self._cursor["@type"] == "woql:And":
            for i in self._cursor["query_list"]:
                subq = self._cursor["query_list"][i]["woql:query"]
                if (
                    subq._query["woql:subject"] == s
                    and subq._query["woql:predicate"] == p
                ):
                    return subq._query["woql:object"]
        return False

    def card(self, n, which):
        os = self.subject
        self.subject += "_" + which
        self._add_po("rdf:type", "owl:Restriction")
        self._add_po("owl:onProperty", os)
        if which == "max":
            self._add_po(
                "owl:maxCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"}
            )
        elif which == "min":
            self._add_po(
                "owl:minCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"}
            )
        else:
            self._add_po(
                "owl:cardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"}
            )
        od = self._get_o(os, "rdfs:domain")
        if od is not None:
            cardcls = self.subject
            self.subject = od
            self._add_po("rdfs:subClassOf", cardcls)
        self.subject = os
        return self
