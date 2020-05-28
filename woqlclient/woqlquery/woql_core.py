import copy

import woql_utils as utils


class WOQLCore:
    def __init__(self, query=None):
        """defines the internal functions of the woql query object - the language API is defined in WOQLQuery

        Parameters
        ----------
        query json-ld query for initialisation"""
        self._query = query if query else {}
        self._errors = []
        self._cursor = self._query
        selt._chain_ended = False
        self._contains_update = False
        # operators which preserve global paging
        self._paging_transitive_properties = [
            "select",
            "from",
            "start",
            "when",
            "opt",
            "limit",
        ]
        self._update_operators = [
            "woql:AddTriple",
            "woql:DeleteTriple",
            "woql:AddQuad",
            "woql:DeleteQuad",
            "woql:DeleteObject",
            "woql:UpdateObject",
        ]

        self._vocab = self._load_default_vocabulary()

        self._triple_builder = False
        return self

    def _parameter_error(self, message):
        """Basic Error handling"""
        self._errors.append({"type": self._cursor["@type"], "message": message})
        return self

    def _has_errors(self):
        return len(self._errors) > 0

    def _add_sub_query(self, sub_query=None):
        """Internal library function which adds a subquery and sets the cursor"""
        if sub_query:
            self._cursor["woql:query"] = self._jobj(sub_query)
        else:
            self._cursor["woql:query"] = {}
            self.curson = {}
        return self

    def _contains_update_check(self, json=None):
        """Does this query contain an update"""
        if not json:
            json = self.query
        if json["@type"] in self._update_operators:
            return True
        if json.get("woql:consequent") and self._contains_update_check(
            json["woql:consequent"]
        ):
            return True
        if json.get("woql:query"):
            return self._contains_update_check(json["woql:query"])
        if json.get("woql:query_list"):
            for item in json["woql:query_list"]:
                if self._contains_update_check(item):
                    return True
        return False

    def _updated(self):
        """Called to inidicate that this query will cause an update to the DB"""
        self._contains_update = True
        return self

    # A bunch of internal functions for formatting values for JSON-LD translation

    def _jlt(self, val, val_type):
        """Wraps the passed value in a json-ld literal carriage"""
        if not val_type:
            val_type = "xsd:string"
        elif ":" not in val_type:
            val_type = "xsd:" + val_type
        return {"@type": val_type, "@value": val}

    def _varj(self, verb):
        if varb[:2] == "v:":
            varb = varb[2:]
        if type(varb) == str:
            return {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": varb, "@type": "xsd:string"},
            }
        return varb

    def _jobj(self, qobj):
        """Transforms a javascript representation of a query into a json object if needs be"""
        if hasattr(qobj, "json"):
            return qonj.json()
        if qobj is True:
            return {"@type": "woql:True"}
        return qobj

    def _asv(self, colname_or_index, vname, obj_type):
        """Wraps the elements of an AS variable in the appropriate json-ld"""
        asvar = {}
        if type(colname_or_index) == int:
            asvar["@type"] = "woql:IndexedAsVar"
            asvar["woql:index"] = self._jlt(colname_or_index, "xsd:nonNegativeInteger")
        elif type(colname_or_index) == str:
            asvar["@type"] = "woql:NamedAsVar"
            asvar["woql:identifier"] = self._jlt(colname_or_index)
        if vname[:2] == "v:":
            vname = vname[2:]
        asvar["woql:variable_name"] = {"@type": "xsd:string", "@value": vname}
        if obj_type:
            asvar["woql:var_type"] = self._jlt(obj_type, "xsd:anyURI")
        return asvar

    def _add_asv(self, cursor, asv):
        """Adds a variable to a json-ld as variable list"""
        if asv["@type"] == "woql:IndexedAsVar":
            if not cursor["woql:indexed_as_var"]:
                cursor["woql:indexed_as_var"] = []
                cursor["woql:indexed_as_var"].append(asv)
        else:
            if not cursor["woql:named_as_var"]:
                cursor["woql:named_as_var"] = []
                cursor["woql:named_as_var"].append(asv)

    def _wfroms(self, opts):
        """JSON LD Format Descriptor"""
        if opts and opts.format:
            self._cursor["woql:format"] = {
                "@type": "woql:Format",
                "woql:format_type": {"@value": opts.format, "@type": "xsd:string"},
            }
        if opts.format_header:
            self._cursor["woql:format"]["woql:format_header"] = {
                "@value": true,
                "@type": "xsd:boolean",
            }
        return self

    def _arop(self, arg):
        """Wraps arithmetic operators in the appropriate json-ld"""
        if type(arg) not in [bool, str, int, float, NoneType]:
            if hasattr(arg, "json"):
                return arg.json()
            else:
                return arg
        var = self._clean_object(arg, "xsd:decimal")
        var["@type"] = "woql:ArithmeticValue"
        return var

    def _vlist(self, target_list):
        """Wraps value lists in the appropriate json-ld"""
        vobj = {"@type": "woql:Array", "woql:array_element": []}
        if type(target_list) == str:
            target_list = [target_list]
        for idx, item in enumerate(target_list):
            co_item = self._clean_object(item)
            co_item["@type"] = "woql:ArrayElement"
            co_item["woql:index"] = self._jlt(idx, "xsd:nonNegativeInteger`")
            vobj["woql:array_element"].append(co_item)
        return vobj

    def _wlist(self, wvar):
        """takes input that can be either a string (variable name)
        or an array - each element of the array is a member of the list"""
        if type(wvar) == str:
            self._expand_variable(wvar, True)
        if type(wvar) == list:
            ret = {"@type": "woql:Array", "woql:array_element": []}
            for idx, item in enumerate(wvar):
                co_item = self._clean_object(item)
                if type(co_item) == str:
                    co_item = {"node": co_item}
                    co_item["@type"] = "woql:ArrayElement"
                    co_item["woql:index"] = self._jlt(idx, "xsd:nonNegativeInteger`")
                    ret["woql:array_element"].append(co_item)
        return ret

    def _qle(self, query, idx):
        """Query List Element Constructor"""
        qobj = self._jobj(query)
        return {
            "@type": "woql:QueryListElement",
            "woql:index": self._jlt(idx, "nonNegativeInteger"),
            "woql:query": qobj,
        }

    def _clean_object(self, obj):
        """Transforms whatever is passed in as the subject into the appropriate json-ld for variable or id"""
        subj = False
        if type(obj) not in [bool, str, int, float, NoneType]:
            return obj
        elif type(obj) == str:
            if ":" in obj:
                subj = obj
            elif self._vocab and (obj in self._vocab):
                subj = self._vocab[obj]
            else:
                subj = "doc:" + obj
            return self._expand_variable(subj)
        self._parameter_error("Subject must be a URI string")
        return str(obj)

    def _clean_predicate(self, predicate):
        """Transforms whatever is passed in as the predicate (id or variable) into the appropriate json-ld form """
        pred = False
        if type(predicate) not in [bool, str, int, float, NoneType]:
            return predicate
        if type(predicate) != str:
            self._parameter_error("Predicate must be a URI string")
            return str(predicate)
        if ":" in predicate:
            pred = predicate
        elif self._vocab and (predicate in self._vocab):
            pred = self._vocab[predicate]
        else:
            pred = "scm:" + predicate
        return self._expand_variable(predicate)

    def _clean_path_predicate(self, predicate):
        pred = False
        if ":" in predicate:
            pred = predicate
        elif self._vocab and (predicate in self._vocab):
            pred = self._vocab[predicate]
        else:
            pred = "scm:" + predicate
        return pred

    def _clean_object(self, object, target):
        """Transforms whatever is passed in as the object of a triple into the appropriate json-ld form (variable, literal or id)"""
        obj = {"@type": "woql:Datatype"}
        if type(object) == str:
            if ":" in object:
                return self._clean_class(object)
            elif self._vocab and (object in self._vocab):
                return self._clean_class(self._vocab[object])
            else:
                obj["woql:datatype"] = self._jlt(object, target)
        elif type(object) == float:
            if not target:
                target = "xsd:decimal"
            obj["woql:datatype"] = self._jlt(object, target)
        elif type(object) not in [bool, str, int, float, NoneType]:
            if "@value" in object:
                obj["woql:datatype"] = object
            else:
                return object
        return obj

    def _clean_graph(self, graph):
        """Transforms a graph filter or graph id into the proper json-ld form"""
        return {"@type": "xsd:string", "@value": graph}

    def _expand_variable(self, varname, always):
        """Transforms strings that start with v: into variable json-ld structures
        @param varname - will be transformed if it starts with v:"""
        if varname[:2] == "v:" or always:
            if varname[:2] == "v:":
                varname = varname[2:]
            return {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": varname, "@type": "xsd:string"},
            }
        else:
            return {"@type": "woql:Node", "woql:node": varname}

    def _clean_class(self, user_class, string_only):
        if type(user_class) != str:
            return ""
        if ":" in user_class:
            if self._vocab and (user_class in self._vocab):
                user_class = self._vocab[user_class]
            else:
                user_class = "scm:" + user_class
        if string_only:
            return user_class
        else:
            return self._expand_variable(user_class)

    def _clean_type(self, user_type, string_only):
        return _clean_class(user_type, string_only)

    def _default_context(self, db_iri):
        default = copy.copy(utils.STANDARD_URLS)
        default["scm"] = db_iri + "/schema#"
        default["doc"] = db_iri + "/document/"
        default["db"] = db_iri + "/"
        return default

    def _get_context(self, query=None):
        """Retrieves the value of the current json-ld context"""
        if not query:
            query = self._query
        for prop in query:
            if prop in self._paging_transitive_properties:
                native_query = query[prop][1]
                native_context = selt._get_context(native_query)
                if native_context:
                    return native_context

    def _context(self, current_context):
        """Retrieves the value of the current json-ld context"""
        self._cursor["@context"] = current_context

    def _load_default_vocabulary(self):
        """vocabulary elements that can be used without prefixes in woql.py queries"""
        return {
            "type": "rdf:type",
            "label": "rdfs:label",
            "Class": "owl:Class",
            "DatatypeProperty": "owl:DatatypeProperty",
            "ObjectProperty": "owl:ObjectProperty",
            "Document": "terminus:Document",
            "abstract": "terminus:Document",
            "comment": "rdfs:comment",
            "range": "rdfs:range",
            "domain": "rdfs:domain",
            "subClassOf": "rdfs:subClassOf",
            "string": "xsd:string",
            "integer": "xsd:integer",
            "decimal": "xsd:decimal",
            "email": "xdd:email",
            "json": "xdd:json",
            "dateTime": "xsd:dateTime",
            "date": "xsd:date",
            "coordinate": "xdd:coordinate",
            "line": "xdd:coordinatePolyline",
            "polygon": "xdd:coordinatePolygon",
        }

    @property
    def _vocabulary(self, vocab):
        """Provides the query with a 'vocabulary' a list of well known predicates that can be used without prefixes mapping: id: prefix:id ..."""
        return self._vocab

    @_vocabulary.setter
    def _vocabulary(self, vocab):
        self._vocab = vocab

    def load_vocabulary(self, client):
        # define in woql_query
        pass

    def execute(self, client, commit_msg):
        if self.query.get("@context"):
            self.query["@context"] = client.connection
        # TODO, check how to get the connection
