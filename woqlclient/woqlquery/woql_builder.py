from .woql_core import WOQLCore
from .woql_schema import woqlSchema
from .woql_library import WOQLLibrary


def _star(self, Graph, Subj, Pred, Obj):
	Subj = Subj or "v:Subject"
	Pred = Pred or "v:Predicate"
	Obj = Obj  or  "v:Object"
	Graph = Graph or false;
	if Graph is not None:
		return self.quad(Subj, Pred, Obj, Graph)
	else:
		return self.triple(Subj, Pred, Obj);


def _lib(self):
    return self.WOQLLibrary()

#Internal Triple-builder functions which allow chaining of partial queries

def _abstract(self, graph, subj):
    if self.tripleBuilder is None:
        self.createTripleBuilder(subj)
    self.tripleBuilder.addPO("terminus:tag", "terminus:abstract", graph)
    return self

def _node(self, node, type):
    if self.tripleBuilder is None:
        self.createTripleBuilder(node, type)
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

def _property(self, proId, type):
    if self.tripleBuilder is None:
        self.createTripleBuilder()
    if self.adding_class is not None:
        part = self.findLastSubject(self.cursor)
        g = false
        if part is not None:
            gpart = part['woql:graph_filter'] or part['woql:graph']
        if gpart is not None:
            g = gpart["@value"]
        nq = self.WOQLSchema()._add_property(proId, type, g).domain(this.adding_class)
        combine = self.WOQLQuery().json(self.query)
        nwoql = self.WOQLQuery().woql_and(combine, nq)
        nwoql.adding_class = self.adding_class
        return nwoql.updated()
    else:
        proId = self.cleanPredicate(proId)
        self.tripleBuilder.addPO(proId, type)
    return self

def _insert(self, id, type, refGraph):
	type = self._cleanType(type, true)
	if refGraph is not None:
		return self._add_quad(id, "type", type, refGraph)
	return this._add_triple(id, "type", type)

def _insert_data (self, data, refGraph):
    if data.type and data.id:
        type = self._cleanType(data.type, true)
        self._insert(data.id, type, refGraph)
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
        self.createTripleBuilder()
    self.tripleBuilder.graph(g)
    return self

def _domain(self, d):
    if self.tripleBuilder is None:
        self.createTripleBuilder()
    d = self._cleanClass(d);
    self.tripleBuilder._addPO('rdfs:domain',d)
    return self

def _label(self, l, lang):
    if self.tripleBuilder is None:
        self.createTripleBuilder()
    self.tripleBuilder._label(l, lang)
    return self

def _description(self, c, lang):
    if self.tripleBuilder is None:
        self.createTripleBuilder()
    self.tripleBuilder._description(c, lang)
    return self

# Specifies that a new class should have parents class
# @param {array} parentList the list of parent class []

def _parent(self, *parentList):
    if self.tripleBuilder is None:
        self.createTripleBuilder()
    for i in parentList:
    	pn = self.cleanClass(parentList[i])
    	self.tripleBuilder._addPO('rdfs:subClassOf', pn)
    return self

def _max(self, m):
    if self.tripleBuilder is not None:
        self.tripleBuilder.card(m, "max")
    return self

def _cardinality(self, m):
    if self.tripleBuilder is not None:
        self.tripleBuilder.card(m, "cardinality")
    return this;

def _min(self, m):
    if self.tripleBuilder is not None:
        self.tripleBuilder.card(m, "min")
    return self;

def _createTripleBuilder(self, node, type):
	s = node
	t = type
	lastsubj = self.findLastSubject(self.cursor)
	g = false
	if lastsubj is not None:
		gobj = lastsubj["woql:graph_filter"] or lastsubj["woql:graph"]
        if gobj is not None:
            g = gobj["@value"]
        else:
            g = false
		s = lastsubj['woql:subject']
		t = type or lastsubj["@type"]
	if self.cursor["@type"] is not None:
		subq = self.WOQLQuery().json(self.cursor)
		if self.cursor["@type"] == "woql:And":
			newq = subq
		else:
			newq = self.WOQLQuery().woql_and(subq)
		nuj = newq.json()
		for k in self.cursor):
			delete(self.cursor[k])
		for i in nuj:
			self.cursor[i] = nuj[i]
	else:
		self.woql_and()
	self.tripleBuilder = self.TripleBuilder(t, this, s, g)


"""
@file Triple Builder
    higher level composite queries - not language or api elements
    Class for enabling building of triples from pieces
    type is add_quad / remove_quad / add_triple / remove_triple
 """

def TripleBuilder(self, type, query, s, g):
	#what accumulation type are we
    if type and type.indexOf(":") == -1:
        type = "woql:" + type
    self.type = type;
    self.cursor = query.cursor;
    if s is not None:
        self.subject = s
    else:
        self.subject = false
    self.query = query
    self.g = g;

def triple_builder_label(self, l, lang="en"):
	if l.substring(0, 2) == "v:":
		d = l
	else:
		d = {"@value": l, "@type": "xsd:string", "@language": lang }
	x = self._addPO('rdfs:label', d)
	return x

def triple_builder_graph(self, g):
	self.g = g

def triple_builder_description(self, c, lang="en"):
	if c.substring(0, 2) == "v:":
		d = c
	else:
		d = {"@value": c, "@type": "xsd:string", "@language": lang }
	return self._addPO('rdfs:comment', d);

def _addPO(self, p, o, g):
	g = g or self.g
	newq = false
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

def _getO(self, s, p):
	if self.cursor['@type'] == "woql:And":
        for i in self.cursor['query_list']:
			subq = self.cursor['query_list'][i]["woql:query"]
			if subq.query["woql:subject"] == s and subq.query["woql:predicate"] == p:
                return subq.query["woql:object"]
	return false

def _card(self, n, which):
	os = self.subject
	self.subject += "_" + which;
	self._addPO('rdf:type', "owl:Restriction");
	self._addPO("owl:onProperty", os)
    if which == "max":
        self._addPO("owl:maxCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"})
    elif which == "min":
        self._addPO("owl:minCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"})
    else:
        self._addPO("owl:cardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"})
	od = self._getO(os, "rdfs:domain");
	if od is not None:
		cardcls = self.subject
		self.subject = od
		self._addPO("rdfs:subClassOf", cardcls);
	self.subject = os;
	return self
