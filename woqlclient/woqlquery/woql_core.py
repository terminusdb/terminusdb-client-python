import copy

import woqlclient.woql_utils as utils

# helper functions


def _get_clause_and_remainder(pat):
    """Breaks a graph pattern up into two parts - the next clause, and the remainder of the string
    @param {string} pat - graph pattern fragment
    """
    pat = pat.strip()
    opening = 1
    # if there is a parentheses, we treat it as a clause and go to the end
    if pat[0] == "(":
        for idx, char in enumerate(pat[1:]):
            if char == "(":
                opening += 1
            elif char == ")":
                pass
            if opening == 0:
                rem = pat[idx + 1 :].strip()
                if rem:
                    return [pat[1:idx], rem]
                return _get_clause_and_remainder(pat[1:idx])
                # whole thing surrounded by parentheses, strip them out and reparse
        return []
    if pat[0] == "+" or pat[0] == "," or pat[0] == "|":
        ret = [pat[0]]
        if pat[1:]:
            ret.append(pat[1:])
        return ret
    if pat[0] == "{":
        close_idx = pat.find("}") + 1
        ret = [pat[:close_idx]]
        if pat[close_idx:]:
            ret.append(pat[close_idx:])
        return ret
    for idx, char in enumerate(pat[1:]):
        if char in [",", "|", "+", "{"]:
            return [pat[:idx], pat[idx:]]
    return [pat]


def _tokenize(pat):
    """Tokenizes the pattern into a sequence of tokens which may be clauses or operators"""
    parts = _get_clause_and_remainder(pat)
    seq = []
    while len(parts) == 2:
        seq.append(parts[0])
        parts = _get_clause_and_remainder(parts[1])
    seq.append(parts[0])
    return seq


def _tokens_to_json(seq, query):
    """Turns a sequence of tokens into the appropriate JSON-LD
    @param {Array} seq
    @param {*} q"""
    if len(seq) == 1:  # may need to be further tokenized
        ntoks = _tokenize(seq[0])
        if len(ntoks) == 1:
            tok = ntoks[0].strip()
            if tok == "*":
                path_pred = "owl:topObjectProperty"
            else:
                path_pred = query._clean_path_predicate(tok)
            return {
                "@type": "woql:PathPredicate",
                "woql:path_predicate": {"@id": path_pred},
            }
        else:
            return _tokens_to_json(ntoks, query)
    elif "|" in seq:  # binds most loosely
        left = seq[: seq.index("|")]
        right = seq[seq.index("|") + 1 :]
        return {
            "@type": "woql:PathOr",
            "woql:path_left": _tokens_to_json(left, query),
            "woql:path_right": _tokens_to_json(right, query),
        }
    elif "," in seq:  # binds tighter
        first = seq[: seq.index(",")]
        second = seq[seq.index(",") + 1 :]
        return {
            "@type": "woql:PathSequence",
            "woql:path_first": _tokens_to_json(first, query),
            "woql:path_second": _tokens_to_json(second, query),
        }
    elif seq[1] == "+":  # binds tightest of all
        return {
            "@type": "woql:PathPlus",
            "woql:path_pattern": _tokens_to_json([seq[0]], query),
        }
    elif seq[1][0] == "{":  # binds tightest of all
        meat = seq[1][1:-1].split(",")
        return {
            "@type": "woql:PathTimes",
            "woql:path_minimum": {"@type": "xsd:positiveInteger", "@value": meat[0]},
            "woql:path_maximum": {"@type": "xsd:positiveInteger", "@value": meat[1]},
            "woql:path_pattern": _tokens_to_json([seq[0]], query),
        }
    else:
        query._parameter_error("Pattern error - could not be parsed " + seq[0])
        return {
            "@type": "woql:PathPredicate",
            "rdfs:label": "failed to parse query " + seq[0],
        }


def _copy_json(orig, rollup=None):
    if type(orig) == list:
        return orig
    if rollup:
        if orig["@type"] in ["woql:And", "woql:Or"]:
            if not orig.get("woql:query_list") or not len(orig["woql:query_list"]):
                return {}
            if len(orig["woql:query_list"]) == 1:
                return _copy_json(orig["woql:query_list"][0]["woql:query"], rollup)
        if "woql:query" in orig and orig["@type"] != "woql:Comment":
            if not orig["woql:query"].get("@type"):
                return {}
        if "woql:consequent" in orig:
            if not orig["woql:consequent"].get("@type"):
                return {}
    nuj = {}
    for key, part in orig.items():
        if type(part) == list:
            nupart = []
            for item in part:
                if type(item) not in [bool, str, int, float]:
                    sub = _copy_json(item, rollup)
                    if not sub or not utils.empty(sub):
                        nupart.append(sub)
                else:
                    nupart = nupart.append(item)
            nuj[key] = nupart
        elif type(part) not in [bool, str, int, float]:
            query = _copy_json(part, rollup)
            if not query or not utils.empty(query):
                nuj[key] = query
        else:
            nuj[key] = part
    return nuj


class WOQLCore:
    def __init__(self, query=None):
        """defines the internal functions of the woql query object - the language API is defined in WOQLQuery

        Parameters
        ----------
        query json-ld query for initialisation"""
        if query:
            self._query = query
        else:
            self._query = {}
        self._errors = []
        self._cursor = self._query
        self._chain_ended = False
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

    def _jlt(self, val, val_type=None):
        """Wraps the passed value in a json-ld literal carriage"""
        if not val_type:
            val_type = "xsd:string"
        elif ":" not in val_type:
            val_type = "xsd:" + val_type
        return {"@type": val_type, "@value": val}

    def _varj(self, varb):
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
            return qobj.json()
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
                "@value": True,
                "@type": "xsd:boolean",
            }
        return self

    def _arop(self, arg):
        """Wraps arithmetic operators in the appropriate json-ld"""
        if type(arg) not in [bool, str, int, float]:
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

    def _clean_subject(self, obj):
        """Transforms whatever is passed in as the subject into the appropriate json-ld for variable or id"""
        subj = False
        if type(obj) not in [bool, str, int, float]:
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
        if type(predicate) not in [bool, str, int, float]:
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
        return self._expand_variable(pred)

    def _clean_path_predicate(self, predicate):
        pred = False
        if ":" in predicate:
            pred = predicate
        elif self._vocab and (predicate in self._vocab):
            pred = self._vocab[predicate]
        else:
            pred = "scm:" + predicate
        return pred

    def _clean_object(self, user_obj, target=None):
        """Transforms whatever is passed in as the object of a triple into the appropriate json-ld form (variable, literal or id)"""
        obj = {"@type": "woql:Datatype"}
        if type(user_obj) == str:
            if ":" in user_obj:
                return self._clean_class(user_obj)
            elif self._vocab and (user_obj in self._vocab):
                return self._clean_class(self._vocab[user_obj])
            else:
                obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) == float:
            if not target:
                target = "xsd:decimal"
            obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) not in [bool, str, int, float]:
            if "@value" in user_obj:
                obj["woql:datatype"] = user_obj
            else:
                return user_obj
        return obj

    def _clean_graph(self, graph):
        """Transforms a graph filter or graph id into the proper json-ld form"""
        return {"@type": "xsd:string", "@value": graph}

    def _expand_variable(self, varname, always=False):
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

    def _clean_class(self, user_class, string_only=False):
        print(" i am in cean class")
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
        return self._clean_class(user_type, string_only)

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
                native_context = self._get_context(native_query)
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
        """Executes the query using the passed client to connect to a server"""
        if self.query.get("@context"):
            self.query["@context"] = client.conCapabilities._get_json_context()
        self._query["@context"]["woql"] = "http://terminusdb.com/schema/woql#"
        # for owl:oneOf choice lists
        self._query["@context"]["_"] = "_:"
        return client.query(self, commit_msg)

    def json(self, json=None):
        """converts back and forward from json
        if the argument is present, the current query is set to it,
        if the argument is not present, the current json version of this query is returned"""
        if json:
            self._query = _copy_json(json)
            return self
        return _copy_json(self._query, True)

    def _wrap_cursor_with_and(self):
        # define in woql_query
        pass

    def _find_last_subject(self, json):
        """Finds the last woql element that has a woql:subject in it and returns the json for that
        used for triplebuilder to chain further calls - when they may be inside ands or ors or subqueries
        @param {object} json"""
        if "woql:query_list" in json:
            temp_json = copy.copy(json["woql:query_list"])
            while len(temp_json) > 0:
                item = temp_json.pop()
                if self._find_last_subject(item):
                    return item
        if "woql:query" in json:
            item = self._find_last_subject(json["woql:query"])
            if item:
                return item
        if "woql:subject" in json:
            return json
        return False

    def _compile_path_pattern(self, pat):
        """Turns a textual path pattern into a JSON-LD description"""
        toks = _tokenize(pat)
        if toks and len(toks):
            return _tokens_to_json(toks, self)
        else:
            self._parameter_error("Pattern error - could not be parsed " + pat)
