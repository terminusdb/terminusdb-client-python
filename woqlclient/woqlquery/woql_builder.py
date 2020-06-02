class TripleBuilder:
    """
    @file Triple Builder
        higher level composite queries - not language or api elements
        Class for enabling building of triples from pieces
        type is add_quad / remove_quad / add_triple / remove_triple
     """

    def __init__(self, _type=None, query=None, s=None, g=None):
        """
        what accumulation type are we
        """
        if _type is not None and _type.find(":") == -1:
            _type = "woql:" + _type
        self._type = _type
        self._cursor = query._cursor
        if s is not None:
            self._subject = s
        else:
            self._subject = False
        self._query = query
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

    def _add_po(self, p, o, g=None):
        if g is None:
            g = self.g
        newq = False
        if self._type == "woql:Triple":
            newq = WOQLQuery().triple(self._subject, p, o)
        elif self._type == "woql:AddTriple":
            newq = WOQLQuery().add_triple(self._subject, p, o)
        elif self._type == "woql:DeleteTriple":
            newq = WOQLQuery().delete_triple(self._subject, p, o)
        elif self._type == "woql:Quad":
            newq = WOQLQuery().quad(self._subject, p, o, g)
        elif self._type == "woql:AddQuad":
            newq = WOQLQuery().add_quad(self._subject, p, o, g)
        elif self._type == "woql:DeleteQuad":
            newq = WOQLQuery().delete_quad(self._subject, p, o, g)
        elif g is not None:
            newq = WOQLQuery().quad(self._subject, p, o, g)
        else:
            newq = WOQLQuery().triple(self._subject, p, o)
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
        os = self._subject
        self._subject += "_" + which
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
            cardcls = self._subject
            self._subject = od
            self._add_po("rdfs:subClassOf", cardcls)
        self._subject = os
        return self
