from woql_schema import WOQLSchema
from woql_library import WOQLLibrary


def _star(self, graph=None, subj=None, pred=None, obj=None):
    if subj is None:
        subj = "v:Subject"
    if pred is None:
        pred = "v:Predicate"
    if obj is None:
        obj = "v:Object"
    if graph is None:
        graph = False
    if graph is not None:
        return self.quad(subj, pred, obj, graph)
    else:
        return self.triple(subj, pred, obj)


def _lib(self):
    return WOQLLibrary()


def _abstract(self, graph, subj):
    """
    Internal Triple-builder functions which allow chaining of partial queries
    """
    if self.tripleBuilder is None:
        self._create_triple_builder(subj)
    self.tripleBuilder._addPO("terminus:tag", "terminus:abstract", graph)
    return self


def _node(self, node, node_type):
    if self.tripleBuilder is None:
        self._createTripleBuilder(node, node_type)
    self.tripleBuilder.subject = node
    return self


"""
Add a property at the current class/document

    @param {string} proId - property ID
    @param {string} type  - property type (range)
    @returns WOQLQuery object

    A range could be another class/document or an "xsd":"http://www.w3.org/2001/XMLSchema#" type
    like string|integer|datatime|nonNegativeInteger|positiveInteger etc ..
    (you don't need the prefix xsd for specific a type)
"""


def _property(self, pro_id, property_type):
    if self.tripleBuilder is None:
        self._createTripleBuilder()
    if self.adding_class is not None:
        part = self.findLastSubject(self.cursor)
        g = False
        if part is not None:
            gpart = part["woql:graph_filter"] or part["woql:graph"]
        if gpart is not None:
            g = gpart["@value"]
        nq = WOQLSchema()._add_property(pro_id, type, g).domain(self.adding_class)
        combine = self.WOQLQuery().json(self.query)
        nwoql = self.WOQLQuery().woql_and(combine, nq)
        nwoql.adding_class = self.adding_class
        return nwoql.updated()
    else:
        pro_id = self.cleanPredicate(pro_id)
        self.tripleBuilder.addPO(pro_id, property_type)
    return self


def _insert(self, insert_id, insert_type, ref_graph):
    insert_type = self._cleanType(insert_type, True)
    if ref_graph is not None:
        return self._add_quad(insert_id, "type", insert_type, ref_graph)
    return self._add_triple(insert_id, "type", insert_type)


def _insert_data(self, data, ref_graph):
    if data.type and data.id:
        data_type = self._cleanType(data.type, True)
        self._insert(data.id, data_type, ref_graph)
        if data.label is not None:
            self.label(data.label)
        if data.description is not None:
            self.description(data.description)
        for k in data:
            if ["id", "label", "type", "description"].indexOf(k) == -1:
                self.property(k, data[k])
    return self


def _graph(self, g):
    if self.tripleBuilder is None:
        self._createTripleBuilder()
    self.tripleBuilder.graph(g)
    return self


def _domain(self, d):
    if self.tripleBuilder is None:
        self._createTripleBuilder()
    d = self._cleanClass(d)
    self.tripleBuilder._addPO('rdfs:domain', d)
    return self


def _label(self, lan, lang):
    if self.tripleBuilder is None:
        self._createTripleBuilder()
    self.tripleBuilder._label(lan, lang)
    return self


def _description(self, c, lang):
    if self.tripleBuilder is None:
        self._createTripleBuilder()
    self.tripleBuilder._description(c, lang)
    return self


# Specifies that a new class should have parents class
# @param {array} parentList the list of parent class []


def _parent(self, *parent_list):
    if self.tripleBuilder is None:
        self._createTripleBuilder()
    for i in parent_list:
        pn = self._cleanClass(parent_list[i])
        self.tripleBuilder._addPO('rdfs:subClassOf', pn)
    return self


def _max(self, m):
    if self.tripleBuilder is not None:
        self.tripleBuilder.card(m, "max")
    return self


def _cardinality(self, m):
    if self.tripleBuilder is not None:
        self.tripleBuilder.card(m, "cardinality")
    return self



def _min(self, m):
    if self.tripleBuilder is not None:
        self.tripleBuilder.card(m, "min")
    return self


def _create_triple_builder(self, node, create_type):
    s = node
    t = create_type
    lastsubj = self.findLastSubject(self.cursor)
    g = False
    if lastsubj is not None:
        gobj = lastsubj["woql:graph_filter"] or lastsubj["woql:graph"]
        if gobj is not None:
            g = gobj["@value"]
        else:
            g = False
    s = lastsubj["woql:subject"]
    if create_type is not None:
        t = create_type
    else:
        t = lastsubj["@type"]
    if self.cursor["@type"] is not None:
        subq = self.WOQLQuery().json(self.cursor)
    if self.cursor["@type"] == "woql:And":
        newq = subq
    else:
        newq = self.WOQLQuery().woql_and(subq)
        nuj = newq.json()
    """
    for k in self.cursor: TODO take from ObjectFrame
        delete(self.cursor[k])
    """
    for i in nuj:
        self.cursor[i] = nuj[i]
    else:
        self.woql_and()
    self.tripleBuilder = self.TripleBuilder(t, self, s, g)


"""
@file Triple Builder
    higher level composite queries - not language or api elements
    Class for enabling building of triples from pieces
    type is add_quad / remove_quad / add_triple / remove_triple
 """


def triple_builder(self, triple_type, query, s, g):
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


def triple_builder_label(self, lab, lang="en"):
    if lab.substring(0, 2) == "v:":
        d = lab
    else:
        d = {"@value": lab, "@type": "xsd:string", "@language": lang}
    x = self._addPO('rdfs:label', d)
    return x


def triple_builder_graph(self, g):
    self.g = g


def triple_builder_description(self, c, lang="en"):
    if c.substring(0, 2) == "v:":
        d = c
    else:
        d = {"@value": c, "@type": "xsd:string", "@language": lang}
    return self._addPO('rdfs:comment', d)


def _add_po(self, p, o, g):
    g = g or self.g
    newq = False
    if self.type == "woql:Triple":
        newq = self.WOQLQuery()._triple(self.subject, p, o)
    elif self.type == "woql:AddTriple":
        newq = self.WOQLQuery()._add_triple(self.subject, p, o)
    elif self.type == "woql:DeleteTriple":
        newq = self.WOQLQuery()._delete_triple(self.subject, p, o)
    elif self.type == "woql:Quad":
        newq = self.WOQLQuery()._quad(self.subject, p, o, g)
    elif self.type == "woql:AddQuad":
        newq = self.WOQLQuery()._add_quad(self.subject, p, o, g)
    elif self.type == "woql:DeleteQuad":
        newq = self.WOQLQuery()._delete_quad(self.subject, p, o, g)
    elif g is not None:
        newq = self.WOQLQuery()._quad(self.subject, p, o, g)
    else:
        newq = self.WOQLQuery()._triple(self.subject, p, o)
    self._query.woql_and(newq)


def _get_o(self, s, p):
    if self.cursor['@type'] == "woql:And":
        for i in self.cursor['query_list']:
            subq = self.cursor['query_list'][i]["woql:query"]
            if subq.query["woql:subject"] == s and subq.query["woql:predicate"] == p:
                return subq.query["woql:object"]
    return False


def _card(self, n, which):
    os = self.subject
    self.subject += "_" + which
    self._addPO('rdf:type', "owl:Restriction")
    self._addPO("owl:onProperty", os)
    if which == "max":
        self._addPO(
            "owl:maxCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"}
        )
    elif which == "min":
        self._addPO(
            "owl:minCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"}
        )
    else:
        self._addPO("owl:cardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"})
    od = self._getO(os, "rdfs:domain")
    if od is not None:
        cardcls = self.subject
        self.subject = od
        self._addPO("rdfs:subClassOf", cardcls)
    self.subject = os
    return self
