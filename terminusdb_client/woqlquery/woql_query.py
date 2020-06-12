import copy
import json
import pprint
import re

import terminusdb_client.woql_utils as utils

from .woql_core import _copy_dict, _tokenize, _tokens_to_json

pp = pprint.PrettyPrinter(indent=4)


class WOQLQuery:
    def __init__(self, query=None, graph="schema/main"):
        """defines the internal functions of the woql query object - the language API is defined in WOQLQuery

        Parameters
        ----------
        query: dict
               json-ld query for initialisation
        graph: str
               graph that this query is appled to, default to be schema/main"""
        if query:
            self._query = query
        else:
            self._query = {}
        self._cursor = self._query
        self._chain_ended = False
        self._contains_update = False
        self.adding_class = False
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

        # alias
        self.subsumption = self.sub
        self.equals = self.eq
        self.substring = self.substr
        self.update = self.update_object
        self.delete = self.delete_object
        self.read = self.read_object
        self.optional = self.opt
        self.idgenerator = self.idgen
        self.concatenate = self.concat
        self.typecast = self.cast

        # attribute for schema
        self._graph = graph
        self._adding_class = None

    # WOQLCore methods
    def _parameter_error(self, message):
        """Basic Error handling"""
        raise ValueError(message)

    def _add_sub_query(self, sub_query=None):
        """Internal library function which adds a subquery and sets the cursor"""
        if sub_query:
            self._cursor["woql:query"] = self._jobj(sub_query)
        else:
            nv = {}
            self._cursor["woql:query"] = nv
            self._cursor = nv
        return self

    def _contains_update_check(self, json=None):
        """Does this query contain an update"""
        if not json:
            json = self._query
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
        if hasattr(qobj, "to_dict"):
            return qobj.to_dict()
        if qobj is True:
            return {"@type": "woql:True"}
        return qobj

    def _asv(self, colname_or_index, vname, obj_type=None):
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

    def _wfrom(self, opts):
        """JSON LD Format Descriptor"""
        if opts and opts.get("format"):
            self._cursor["woql:format"] = {
                "@type": "woql:Format",
                "woql:format_type": {"@value": opts["format"], "@type": "xsd:string"},
            }
            if opts.get("format_header"):
                self._cursor["woql:format"]["woql:format_header"] = {
                    "@value": True,
                    "@type": "xsd:boolean",
                }
        return self

    def _arop(self, arg):
        """Wraps arithmetic operators in the appropriate json-ld"""
        if type(arg) == dict:
            if hasattr(arg, "to_dict"):
                return arg.to_dict()
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
            co_item["woql:index"] = self._jlt(idx, "xsd:nonNegativeInteger")
            vobj["woql:array_element"].append(co_item)
        return vobj

    def _wlist(self, wvar):
        # TODO: orig is Nonetype
        """takes input that can be either a string (variable name)
        or an array - each element of the array is a member of the list"""
        if type(wvar) == str:
            return self._expand_variable(wvar, True)
        if type(wvar) == list:
            ret = {"@type": "woql:Array", "woql:array_element": []}
            for idx, item in enumerate(wvar):
                co_item = self._clean_object(item)
                if type(co_item) == str:
                    co_item = {"node": co_item}
                co_item["@type"] = "woql:ArrayElement"
                co_item["woql:index"] = self._jlt(idx, "xsd:nonNegativeInteger")
                ret["woql:array_element"].append(co_item)
            return ret

    def _qle(self, query, idx):
        """Query List Element Constructor"""
        qobj = self._jobj(query)
        iqle = {
            "@type": "woql:QueryListElement",
            "woql:index": self._jlt(idx, "nonNegativeInteger"),
            "woql:query": qobj,
        }
        return iqle

    def _clean_subject(self, obj):
        """Transforms whatever is passed in as the subject into the appropriate json-ld for variable or id"""
        subj = False
        if type(obj) == dict:
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
        if type(predicate) == dict:
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

    def _clean_path_predicate(self, predicate=None):
        pred = False
        if predicate is not None:
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
            if self._looks_like_class(user_obj):
                return self._clean_class(user_obj)
            elif self._vocab and (user_obj in self._vocab):
                return self._clean_class(self._vocab[user_obj])
            else:
                obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) == float:
            if not target:
                target = "xsd:decimal"
            obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) == int:
            if not target:
                target = "xsd:integer"
            obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) == bool:
            if not target:
                target = "xsd:boolean"
            obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) == dict:
            if "@value" in user_obj:
                obj["woql:datatype"] = user_obj
            else:
                return user_obj
        else:
            obj["woql:datatype"] = self._jlt(str(user_obj))
        return obj

    def _looks_like_class(self, cstring):
        if ":" not in cstring:
            return False
        pref = cstring.split(":")[0]
        if pref == "v" or pref == "scm" or pref == "doc":
            return True
        if utils.STANDARD_URLS.get(pref):
            return True
        return False

    def _clean_graph(self, graph):
        """Transforms a graph filter or graph id into the proper json-ld form"""
        return {"@type": "xsd:string", "@value": graph}

    def _expand_variable(self, varname, always=False):
        """Transforms strings that start with v: into variable json-ld structures
        Parameters
        ----------
        varname : str
                  will be transformed if it starts with 'v:'
        always : bool
                 if True it will be transformed no matter it starts with 'v:' or not. Default to be False
        """
        if varname[:2] == "v:" or always:
            if varname[:2] == "v:":
                varname = varname[2:]
            return {
                "@type": "woql:Variable",
                "woql:variable_name": {"@value": varname, "@type": "xsd:string"},
            }
        else:
            return {"@type": "woql:Node", "woql:node": varname}

    def _clean_class(self, user_class=None, string_only=None):
        if type(user_class) != str:
            return ""
        if ":" not in user_class:
            if self._vocab and (user_class in self._vocab):
                user_class = self._vocab[user_class]
            else:
                user_class = "scm:" + user_class
        if string_only:
            return user_class
        else:
            return self._expand_variable(user_class)

    def _clean_type(self, user_type=None, string_only=None):
        return self._clean_class(user_type, string_only)

    def _default_context(self, db_iri):
        default = copy.copy(utils.STANDARD_URLS)
        default["scm"] = db_iri + "/schema#"
        default["doc"] = db_iri + "/data/"
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

    def execute(self, client, commit_msg=None):
        """Executes the query using the passed client to connect to a server"""
        if self._query.get("@context"):
            self._query["@context"] = client.conCapabilities._get_json_context()
        if commit_msg is None:
            return client.query(self)
        else:
            return client.query(self, commit_msg)

    def to_json(self):
        return self._json()

    def from_json(self, input_json):
        return self._json(input_json)

    def _json(self, input_json=None):
        """converts back and forward from json
        if the argument is present, the current query is set to it,
        if the argument is not present, the current json version of this query is returned"""
        if input_json:
            self.from_dict(json.loads(input_json))
            return self
        else:
            return json.dumps(self.to_dict(), sort_keys=True)

    def to_dict(self):
        return _copy_dict(self._query, True)

    def from_dict(self, dictdata):
        self._query = _copy_dict(dictdata)
        return self

    def _find_last_subject(self, json):
        """Finds the last woql element that has a woql:subject in it and returns the json for that
        used for triplebuilder to chain further calls - when they may be inside ands or ors or subqueries
        Parameters
        ----------
        json : dict
               dictionary that representing the query in josn-ld"""
        if "woql:query_list" in json:
            temp_json = copy.deepcopy(json["woql:query_list"])
            while len(temp_json) > 0:
                item = temp_json.pop()
                subitem = self._find_last_subject(item)
                if subitem:
                    return subitem
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

    def load_vocabulary(self, client):
        """Queries the schema graph and loads all the ids found there as vocabulary that can be used without prefixes
        ignoring blank node ids"""
        new_woql = WOQLQuery().quad("v:S", "v:P", "v:O", "schema/*")
        result = new_woql.execute(client)
        bindings = result.get("bindings", [])
        for each_result in bindings:
            for item in each_result:
                if type(item) == str:
                    spl = item.split(":")
                    if len(spl) == 2 and spl[1] and spl[0] != "_":
                        self._vocab[spl[0]] = spl[1]

    def _wrap_cursor_with_and(self):
        new_json = WOQLQuery().from_dict(self._cursor)
        self._cursor = {}
        self.woql_and(new_json, {})
        self._cursor = self._cursor["woql:query_list"][1]["woql:query"]

    def using(self, collection, subq):
        if collection and collection == "woql:args":
            return ["woql:collection", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Using"
        if not collection or type(collection) != str:
            return self._parameter_error(
                "The first parameter to using must be a Collection ID (string)"
            )
        self._cursor["woql:collection"] = self._jlt(collection)
        return self._add_sub_query(subq)

    def comment(self, comment, subq=None):
        if comment and comment == "woql:args":
            return ["woql:comment", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Comment"
        self._cursor["woql:comment"] = self._jlt(comment)
        return self._add_sub_query(subq)

    def select(self, *args):
        queries = list(args)
        if queries and queries[0] == "woql:args":
            return ["woql:variable_list", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Select"
        if not queries:
            return self._parameter_error(
                "Select must be given a list of variable names"
            )
        if hasattr(queries[-1], "to_dict"):
            embedquery = queries.pop()
        else:
            embedquery = False
        self._cursor["woql:variable_list"] = []
        for idx, item in enumerate(queries):
            onevar = self._varj(item)
            onevar["@type"] = "woql:VariableListElement"
            onevar["woql:index"] = self._jlt(idx, "nonNegativeInteger")
            self._cursor["woql:variable_list"].append(onevar)
        return self._add_sub_query(embedquery)

    def woql_and(self, *args):
        queries = list(args)
        if self._cursor.get("@type") and self._cursor["@type"] != "woql:And":
            new_json = WOQLQuery().from_dict(self._cursor)
            self._cursor.clear()
            queries = [new_json] + queries
        if queries and queries[0] == "woql:args":
            return ["woql:query_list"]
        self._cursor["@type"] = "woql:And"
        if "woql:query_list" not in self._cursor:
            self._cursor["woql:query_list"] = []
        for item in queries:
            index = len(self._cursor["woql:query_list"])
            onevar = self._qle(item, index)
            if (
                "woql:query" in onevar
                and "@type" in onevar["woql:query"]
                and "woql:query_list" in onevar["woql:query"]
                and onevar["woql:query"]["@type"] == "woql:And"
            ):
                for each in onevar["woql:query"]["woql:query_list"]:
                    qjson = each["woql:query"]
                    if qjson:
                        index = len(self._cursor["woql:query_list"])
                        subvar = self._qle(qjson, index)
                        self._cursor["woql:query_list"].append(subvar)
            else:
                self._cursor["woql:query_list"].append(onevar)
        return self

    def woql_or(self, *args):
        queries = list(args)
        if queries and queries[0] == "woql:args":
            return ["woql:query_list"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Or"
        if "woql:query_list" not in self._cursor:
            self._cursor["woql:query_list"] = []
        for idx, item in enumerate(queries):
            onevar = self._qle(item, idx)
            self._cursor["woql:query_list"].append(onevar)
        return self

    def woql_from(self, graph_filter, query=None):
        if graph_filter and graph_filter == "woql:args":
            return ["woql:graph_filter", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:From"
        if not graph_filter or type(graph_filter) != str:
            return self._parameter_error(
                "The first parameter to from must be a Graph Filter Expression (string)"
            )
        self._cursor["woql:graph_filter"] = self._jlt(graph_filter)
        return self._add_sub_query(query)

    def into(self, graph_descriptor, query):
        if graph_descriptor and graph_descriptor == "woql:args":
            return ["woql:graph", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Into"
        if not graph_descriptor or type(graph_descriptor) != str:
            return self._parameter_error(
                "The first parameter to from must be a Graph Filter Expression (string)"
            )
        self._cursor["woql:graph"] = self._jlt(graph_descriptor)
        return self._add_sub_query(query)

    def triple(self, sub, pred, obj, opt=False):
        if opt:
            return self.opt().triple(sub, pred, obj)
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Triple"
        self._cursor["woql:subject"] = self._clean_subject(sub)
        self._cursor["woql:predicate"] = self._clean_predicate(pred)
        self._cursor["woql:object"] = self._clean_object(obj)
        return self

    def quad(self, sub, pred, obj, graph, opt=False):
        if opt:
            return self.opt().quad(sub, pred, obj, graph)
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        arguments = self.triple(sub, pred, obj)
        if sub and sub == "woql:args":
            return arguments.append("woql:graph_filter")
        if not graph:
            return self._parameter_error(
                "Quad takes four parameters, the last should be a graph filter"
            )
        self._cursor["@type"] = "woql:Quad"
        self._cursor["woql:graph_filter"] = self._clean_graph(graph)
        return self

    def string(self, input_str):
        return {"@type": "xsd:string", "@value": input_str}

    def literal(self, input_val, input_type):
        if ":" not in input_type:
            input_type = "xsd:" + input_type
        return {"@type": input_type, "@value": input_val}

    def iri(self, varname):
        return {
            "@type": "woql:Node",
            "woql:node": varname,
        }

    def sub(self, parent, child):
        if parent and parent == "woql:args":
            return ["woql:parent", "woql:child"]
        if parent is None or child is None:
            return self._parameter_error("Subsumption takes two parameters, both URIs")
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Subsumption"
        self._cursor["woql:parent"] = self._clean_class(parent)
        self._cursor["woql:child"] = self._clean_class(child)
        return self

    def eq(self, left, right):
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if left is None or right is None:
            return self._parameter_error("Equals takes two parameters")
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Equals"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def substr(self, string, length, substring, before=0, after=0):
        if string and string == "woql:args":
            return [
                "woql:string",
                "woql:before",
                "woql:length",
                "woql:after",
                "woql:substring",
            ]
        if not substring:
            substring = length
            length = len(substring) + before
        if not string or not substring or type(substring) != type:
            return self._parameter_error(
                "Substr - the first and last parameters must be strings representing the full and substring variables / literals"
            )
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Substring"
        self._cursor["woql:string"] = self._clean_object(string)
        self._cursor["woql:before"] = self._clean_object(
            before, "xsd:nonNegativeInteger"
        )
        self._cursor["woql:length"] = self._clean_object(
            length, "xsd:nonNegativeInteger"
        )
        self._cursor["woql:after"] = self._clean_object(after, "xsd:nonNegativeInteger")
        self._cursor["woql:substring"] = self._clean_object(substring)
        return self

    def update_object(self, docjson):
        if docjson and docjson == "woql:args":
            return ["woql:document"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:UpdateObject"
        self._cursor["woql:document"] = docjson
        return self._updated()

    def delete_object(self, json_or_iri):
        if json_or_iri and json_or_iri == "woql:args":
            return ["woql:document"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:DeleteObject"
        self._cursor["woql:document_uri"] = json_or_iri
        return self._updated()

    def read_object(self, iri, output_var, out_format):
        if iri and iri == "woql:args":
            return ["woql:document"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:ReadObject"
        self._cursor["woql:document_uri"] = iri
        self._cursor["woql:document"] = self._expand_variable(output_var)
        return self._wfrom(out_format)

    def get(self, as_vars, query_resource=None):
        """Takes an as structure"""
        if as_vars and as_vars == "woql:args":
            return ["woql:as_vars", "woql:query_resource"]
        self._cursor["@type"] = "woql:Get"
        if hasattr(as_vars, "to_dict"):
            self._cursor["woql:as_vars"] = as_vars.to_dict()
        else:
            self._cursor["woql:as_vars"] = WOQLQuery().woql_as(*as_vars).to_dict()
        if query_resource:
            self._cursor["woql:query_resource"] = self._jobj(query_resource)
        else:
            self._cursor["woql:query_resource"] = {}
        self._cursor = self._cursor["woql:query_resource"]
        return self

    def put(self, as_vars, query_resource, query=None):
        """Takes an array of variables, an optional array of column names"""
        if as_vars and as_vars == "woql:args":
            return ["woql:as_vars", "woql:query", "woql:query_resource"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Put"
        if hasattr(as_vars, "to_dict"):
            self._cursor["woql:as_vars"] = as_vars.to_dict()
        else:
            self._cursor["woql:as_vars"] = WOQLQuery().woql_as(*as_vars).to_dict()
        if query_resource:
            self._cursor["woql:query_resource"] = self._jobj(query_resource)
        else:
            self._cursor["woql:query_resource"] = {}
        return self._add_sub_query(query)

    def woql_as(self, *args):
        if args and args[0] == "woql:args":
            return [["woql:indexed_as_var", "woql:named_as_var"]]
        if type(self._query) != list:
            self._query = []
        if type(args[0]) == list:
            for onemap in args:
                if type(onemap) == list and len(onemap) >= 2:
                    if len(onemap) == 2:
                        map_type = False
                    else:
                        map_type = onemap[2]
                    oasv = self._asv(onemap[0], onemap[1], map_type)
                    self._query.append(oasv)
        elif type(args[0]) in [int, str]:
            if len(args) > 2:
                map_type = args[2]
            else:
                map_type = False
            oasv = self._asv(args[0], args[1], map_type)
            self._query.append(oasv)
        elif hasattr(args[0], "to_dict"):
            self._query.append(args[0].to_dict())
        elif type(args[0]) == dict:
            self._query.append(args[0])
        return self

    def file(self, fpath, opts):
        if fpath and fpath == "woql:args":
            return ["woql:file", "woql:format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:FileResource"
        self._cursor["woql:file"] = fpath
        return self._wfrom(opts)

    def remote(self, uri, opts=None):
        if uri and uri == "woql:args":
            return ["woql:remote_uri", "woql:format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:RemoteResource"
        self._cursor["woql:remote_uri"] = {"@type": "xsd:anyURI", "@value": uri}
        return self._wfrom(opts)

    def post(self, fpath, opts):
        if fpath and fpath == "woql:args":
            return ["woql:file", "woql:format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:PostResource"
        self._cursor["woql:file"] = {"@type": "xsd:string", "@value": fpath}
        return self._wfrom(opts)

    def delete_triple(self, subject, predicate, object_or_literal):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        triple_args = self.triple(subject, predicate, object_or_literal)
        if subject and subject == "woql:args":
            return triple_args
        self._cursor["@type"] = "woql:DeleteTriple"
        return self._updated()

    def add_triple(self, subject, predicate, object_or_literal):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        triple_args = self.triple(subject, predicate, object_or_literal)
        if subject and subject == "woql:args":
            return triple_args
        self._cursor["@type"] = "woql:AddTriple"
        return self._updated()

    def delete_quad(self, subject, predicate, object_or_literal, graph=None):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        triple_args = self.triple(subject, predicate, object_or_literal)
        if subject and subject == "woql:args":
            return triple_args.append("woql:graph")
        if not graph:
            return self._parameter_error(
                "Delete Quad takes four parameters, the last should be a graph id"
            )
        self._cursor["@type"] = "woql:DeleteQuad"
        self._cursor["woql:graph"] = self._clean_graph(graph)
        return self._updated()

    def add_quad(self, subject, predicate, object_or_literal, graph):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        triple_args = self.triple(subject, predicate, object_or_literal)
        if subject and subject == "woql:args":
            return triple_args.concat(["woql:graph"])
        if not graph:
            return self._parameter_error(
                "Delete Quad takes four parameters, the last should be a graph id"
            )
        self._cursor["@type"] = "woql:AddQuad"
        self._cursor["woql:graph"] = self._clean_graph(graph)
        return self._updated()

    def when(self, query, consequent=None):
        if query and query == "woql:args":
            return ["woql:query", "woql:consequent"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:When"
        self._add_sub_query(query)
        if consequent:
            newv = self._jobj(consequent)
        else:
            newv = {}
        self._cursor["woql:consequent"] = newv
        self._cursor = newv
        return self

    def trim(self, untrimmed, trimmed):
        if untrimmed and untrimmed == "woql:args":
            return ["woql:untrimmed", "woql:trimmed"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Trim"
        self._cursor["woql:untrimmed"] = self._clean_object(untrimmed)
        self._cursor["woql:trimmed"] = self._clean_object(trimmed)
        return self

    def eval(self, arith, res):
        if arith and arith == "woql:args":
            return ["woql:expression", "woql:result"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Eval"
        if hasattr(arith, "to_dict"):
            self._cursor["woql:expression"] = arith.to_dict()
        else:
            self._cursor["woql:expression"] = arith
        self._cursor["woql:result"] = self._clean_object(res)
        return self

    def plus(self, *args):
        new_args = list(args)
        if new_args and new_args[0] == "woql:args":
            return ["woql:first", "woql:second"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Plus"
        self._cursor["woql:first"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor = self._jobj(WOQLQuery().plus(*new_args))
        else:
            self._cursor["woql:second"] = self._arop(new_args[0])
        return self

    def minus(self, *args):
        new_args = list(args)
        if new_args and new_args[0] == "woql:args":
            return ["woql:first", "woql:second"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Minus"
        self._cursor["woql:first"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["woql:second"] = self._jobj(WOQLQuery().minus(*new_args))
        else:
            self._cursor["woql:second"] = self._arop(new_args[0])
        return self

    def times(self, *args):
        new_args = list(args)
        if new_args and new_args[0] == "woql:args":
            return ["woql:first", "woql:second"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Times"
        self._cursor["woql:first"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["woql:second"] = self._jobj(WOQLQuery().times(*new_args))
        else:
            self._cursor["woql:second"] = self._arop(new_args[0])
        return self

    def divide(self, *args):
        new_args = list(args)
        if new_args and new_args[0] == "woql:args":
            return ["woql:first", "woql:second"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Divide"
        self._cursor["woql:first"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["woql:second"] = self._jobj(WOQLQuery().divide(*new_args))
        else:
            self._cursor["woql:second"] = self._arop(new_args[0])
        return self

    def div(self, *args):
        new_args = list(args)
        if new_args and new_args[0] == "woql:args":
            return ["woql:first", "woql:second"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Div"
        self._cursor["woql:first"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["woql:second"] = self._jobj(WOQLQuery().div(*new_args))
        else:
            self._cursor["woql:second"] = self._arop(new_args[0])
        return self

    def exp(self, first, second):
        if first and first == "woql:args":
            return ["woql:first", "woql:second"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Exp"
        self._cursor["woql:first"] = self._arop(first)
        self._cursor["woql:second"] = self._arop(second)
        return self

    def floor(self, user_input):
        if user_input and user_input == "woql:args":
            return ["woql:argument"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Floor"
        self._cursor["woql:argument"] = self._arop(user_input)
        return self

    def isa(self, element, of_type):
        if element and element == "woql:args":
            return ["woql:element", "woql:of_type"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:IsA"
        self._cursor["woql:element"] = self._clean_subject(element)
        self._cursor["woql:of_type"] = self._clean_class(of_type)
        return self

    def like(self, left, right, dist):
        if left and left == "woql:args":
            return ["woql:left", "woql:right", "woql:like_similarity"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Like"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        if dist:
            self._cursor["woql:like_similarity"] = self._clean_object(
                dist, "xsd:decimal"
            )
        return self

    def less(self, left, right):
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Less"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def greater(self, left, right):
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Greater"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def opt(self, query=None):
        if query and query == "woql:args":
            return ["woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Optional"
        self._add_sub_query(query)
        return self

    def unique(self, prefix, key_list, uri):
        if prefix and prefix == "woql:args":
            return ["woql:base", "woql:key_list", "woql:uri"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Unique"
        self._cursor["woql:base"] = self._clean_object(prefix)
        self._cursor["woql:key_list"] = self._vlist(key_list)
        self._cursor["woql:uri"] = self._clean_class(uri)
        return self

    def idgen(self, prefix, input_var_list, output_var):
        if prefix and prefix == "woql:args":
            return ["woql:base", "woql:key_list", "woql:uri"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:IDGenerator"
        self._cursor["woql:base"] = self._clean_object(self.string(prefix))
        self._cursor["woql:key_list"] = self._vlist(input_var_list)
        self._cursor["woql:uri"] = self._clean_class(output_var)
        return self

    def upper(self, left, right):
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Upper"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def lower(self, left, right):
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Lower"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def pad(self, user_input, pad, length, output):
        if user_input and user_input == "woql:args":
            return [
                "woql:pad_string",
                "woql:pad_char",
                "woql:pad_times",
                "woql:pad_result",
            ]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Pad"
        self._cursor["woql:pad_string"] = self._clean_object(user_input)
        self._cursor["woql:pad_char"] = self._clean_object(pad)
        self._cursor["woql:pad_times"] = self._clean_object(length, "xsd:integer")
        self._cursor["woql:pad_result"] = self._clean_object(output)
        return self

    def split(self, user_input, glue, output):
        if user_input and user_input == "woql:args":
            return ["woql:split_string", "woql:split_pattern", "woql:split_list"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Split"
        self._cursor["woql:split_string"] = self._clean_object(user_input)
        self._cursor["woql:split_pattern"] = self._clean_object(glue)
        self._cursor["woql:split_list"] = self._wlist(output)
        return self

    def member(self, member, mem_list):
        if member and member == "woql:args":
            return ["woql:member", "woql:member_list"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Member"
        self._cursor["woql:member"] = self._clean_object(member)
        self._cursor["woql:member_list"] = self._wlist(mem_list)
        return self

    def concat(self, concat_list, result):
        if concat_list and concat_list == "woql:args":
            return ["woql:concat_list", "woql:concatenated"]
        if type(concat_list) == str:
            slist = re.split("(v:)", concat_list)
            nlist = []
            if slist[0]:
                nlist.append(slist[0])
            for idx, item in enumerate(slist):
                if item and item == "v:":
                    slist2 = re.split(r"([^\w_])", slist[idx + 1])
                    x_var = slist2.pop(0)
                    nlist.append("v:" + x_var)
                    rest = "".join(slist2)
                    if rest:
                        nlist.append(rest)
            concat_list = nlist
        if type(concat_list) == list:
            if self._cursor.get("@type"):
                self._wrap_cursor_with_and()
            self._cursor["@type"] = "woql:Concatenate"
            self._cursor["woql:concat_list"] = self._wlist(concat_list)
            self._cursor["woql:concatenated"] = self._clean_object(result)
        return self

    def join(self, user_input, glue, output):
        if user_input and user_input == "woql:args":
            return ["woql:join_list", "woql:join_separator", "woql:join"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Join"
        self._cursor["woql:join_list"] = self._wlist(user_input)
        self._cursor["woql:join_separator"] = self._clean_object(glue)
        self._cursor["woql:join"] = self._clean_object(output)
        return self

    def sum(self, user_input, output):
        if user_input and user_input == "woql:args":
            return ["woql:sum_list", "woql:sum"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Sum"
        self._cursor["woql:sum_list"] = self._wlist(user_input)
        self._cursor["woql:sum"] = self._clean_object(output)
        return self

    def start(self, start, query=None):
        if start and start == "woql:args":
            return ["woql:start", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Start"
        self._cursor["woql:start"] = self._clean_object(start, "xsd:nonNegativeInteger")
        return self._add_sub_query(query)

    def limit(self, limit, query=None):
        if limit and limit == "woql:args":
            return ["woql:limit", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Limit"
        self._cursor["woql:limit"] = self._clean_object(limit, "xsd:nonNegativeInteger")
        return self._add_sub_query(query)

    def re(self, pattern, reg_str, reg_list):
        if pattern and pattern == "woql:args":
            return ["woql:pattern", "woql:regexp_string", "woql:regexp_list"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Regexp"
        self._cursor["woql:pattern"] = self._clean_object(pattern)
        self._cursor["woql:regexp_string"] = self._clean_object(reg_str)
        self._cursor["woql:regexp_list"] = self._wlist(reg_list)
        return self

    def length(self, var_list, var_len):
        if var_list and var_list == "woql:args":
            return ["woql:length_list", "woql:length"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Length"
        self._cursor["woql:length_list"] = self._vlist(var_list)
        if type(var_len) == float:
            self._cursor["woql:length"] = self._clean_object(
                var_len, "xsd:nonNegativeInteger"
            )
        elif type(var_len) == str:
            self._cursor["woql:length"] = self._varj(var_len)
        return self

    def woql_not(self, query=None):
        if query and query == "woql:args":
            return ["woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Not"
        return self._add_sub_query(query)

    def cast(self, val, user_type, result):
        if val and val == "woql:args":
            return ["woql:typecast_value", "woql:typecast_type", "woql:typecast_result"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Typecast"
        self._cursor["woql:typecast_value"] = self._clean_object(val)
        self._cursor["woql:typecast_type"] = self._clean_object(user_type)
        self._cursor["woql:typecast_result"] = self._clean_object(result)
        return self

    def order_by(self, *args):
        ordered_varlist = list(args)
        if ordered_varlist and ordered_varlist == "woql:args":
            return ["woql:variable_ordering", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:OrderBy"
        self._cursor["woql:variable_ordering"] = []

        if not ordered_varlist or len(ordered_varlist) == 0:
            return self._parameter_error(
                "Order by must be passed at least one variables to order the query"
            )

        if type(ordered_varlist[-1]) == dict and hasattr(
            ordered_varlist[-1], "to_dict"
        ):
            embedquery = ordered_varlist.pop()
        else:
            embedquery = False
        for idx, item in enumerate(ordered_varlist):
            if type(item) == str:
                obj = {
                    "@type": "woql:VariableOrdering",
                    "woql:index": self._jlt(idx, "xsd:nonNegativeInteger"),
                }
                cmds = item.split(" ")
                if len(cmds) > 1 and cmds[1].strip().lower() == "asc":
                    obj["woql:ascending"] = self._jlt(True, "xsd:boolean")
                varname = cmds[0].strip()
                obj["woql:variable"] = self._varj(varname)
                self._cursor["woql:variable_ordering"].append(obj)
            else:
                self._cursor["woql:variable_ordering"].append(ordered_varlist[idx])
        return self._add_sub_query(embedquery)

    def group_by(self, gvarlist, groupedvar, output, groupquery=None):
        if gvarlist and gvarlist == "woql:args":
            return [
                "woql:variable_list",
                "woql:group_var",
                "woql:grouped",
                "woql:query",
            ]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:GroupBy"
        self._cursor["woql:group_by"] = []
        if type(gvarlist) == str:
            gvarlist = [gvarlist]
        for idx, item in enumerate(gvarlist):
            onevar = self._varj(item)
            onevar["@type"] = "woql:VariableListElement"
            onevar["woql:index"] = self._jlt(idx, "nonNegativeInteger")
            self._cursor["woql:group_by"].append(onevar)
        self._cursor["woql:group_template"] = []
        if type(groupedvar) == str:
            groupedvar = [groupedvar]
        for idx, item in enumerate(groupedvar):
            onevar = self._varj(item)
            onevar["@type"] = "woql:VariableListElement"
            onevar["woql:index"] = self._jlt(idx, "nonNegativeInteger")
            self._cursor["woql:group_template"].append(onevar)
        self._cursor["woql:grouped"] = self._varj(output)
        return self._add_sub_query(groupquery)

    def true(self, subject, pattern, obj, path):
        if subject and subject == "woql:args":
            return ["woql:subject", "woql:path_pattern", "woql:object", "woql:path"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Path"
        self._cursor["woql:subject"] = self._clean_subject(subject)
        if type(pattern) == str:
            pattern = self._compile_path_pattern(pattern)
        self._cursor["woql:path_pattern"] = pattern
        self._cursor["woql:object"] = self._clean_object(obj)
        self._cursor["woql:path"] = self._varj(path)
        return self

    def size(self, graph, size):
        if graph and graph == "woql:args":
            return ["woql:resource", "woql:size"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Size"
        self._cursor["woql:resource"] = self._clean_graph(graph)
        self._cursor["woql:size"] = self._varj(size)
        return self

    def triple_count(self, graph, triple_count):
        if graph and graph == "woql:args":
            return ["woql:resource", "woql:triple_count"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:TripleCount"
        self._cursor["woql:resource"] = self._clean_graph(graph)
        self._cursor["woql:triple_count"] = self._varj(triple_count)
        return self

    def star(self, graph=None, subj=None, pred=None, obj=None):
        if subj is None:
            subj = "v:Subject"
        if pred is None:
            pred = "v:Predicate"
        if obj is None:
            obj = "v:Object"
        if graph is None:
            graph = False
        if graph:
            return self.quad(subj, pred, obj, graph)
        else:
            return self.triple(subj, pred, obj)

    def lib(self):
        # return WOQLLibrary()
        pass

    def abstract(self, graph=None, subj=None):
        """
        Internal Triple-builder functions which allow chaining of partial queries
        """
        if not self._triple_builder:
            self._create_triple_builder(subj)
        self._triple_builder._add_po("terminus:tag", "terminus:abstract", graph)
        return self

    def node(self, node, node_type=None):
        if not self._triple_builder:
            self._create_triple_builder(node, node_type)
        self._triple_builder._subject = node
        return self

    def property(self, pro_id, property_type, label=None, description=None):
        """
        Add a property at the current class/document

        A range could be another class/document or an "xsd":"http://www.w3.org/2001/XMLSchema#" type
        like string|integer|datatime|nonNegativeInteger|positiveInteger etc ..
        (you don't need the prefix xsd for specific a type)

        Parameters
        ----------
        pro_id : str
                 property ID
        property_type : str
                        property type (range)
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if label is None and description is None:
            if not self._triple_builder:
                self._create_triple_builder()
            if self._adding_class:
                part = self._find_last_subject(self._cursor)
                g = False
                if part:
                    gpart = (
                        part["woql:graph_filter"]
                        if part.get("woql:graph_filter")
                        else part["woql:graph"]
                    )
                if gpart:
                    g = gpart["@value"]
                nq = (
                    WOQLQuery()
                    .add_property(pro_id, property_type, g)
                    .domain(self._adding_class)
                )
                combine = WOQLQuery().from_dict(self._query)
                nwoql = WOQLQuery().woql_and(combine, nq)
                nwoql._adding_class = self._adding_class
                return nwoql._updated()
            else:
                pro_id = self._clean_predicate(pro_id)
                self._triple_builder._add_po(pro_id, property_type)
            return self
        else:
            result_obj = self.property(pro_id, property_type)
            if label:
                result_obj = result_obj.label(label)
            if description:
                result_obj = result_obj.description(description)
            return result_obj

    def insert(
        self, insert_id, insert_type, ref_graph=None, label=None, description=None
    ):
        if label is None and description is None:
            insert_type = self._clean_type(insert_type, True)
            if ref_graph:
                return self.add_quad(insert_id, "type", insert_type, ref_graph)
            return self.add_triple(insert_id, "type", insert_type)
        else:
            result_obj = self.insert(insert_id, insert_type, ref_graph)
            if label:
                result_obj = result_obj.label(label)
            if description:
                result_obj = result_obj.description(description)
            return result_obj

    def insert_data(self, data, ref_graph):
        if data.get("type") and data.get("id"):
            data_type = self._clean_type(data["type"], True)
            self.insert(data["id"], data_type, ref_graph)
            if data.get("label"):
                self.label(data["label"])
            if data.get("description"):
                self.description(data["description"])
            for k in data:
                if k not in ["id", "label", "type", "description"]:
                    self.property(k, data[k])
        return self

    def graph(self, g):
        if not self._triple_builder:
            self._create_triple_builder()
        self._triple_builder.graph(g)
        return self

    def domain(self, d):
        if not self._triple_builder:
            self._create_triple_builder()
        d = self._clean_class(d)
        self._triple_builder._add_po("rdfs:domain", d)
        return self

    def label(self, lan, lang="en"):
        if not self._triple_builder:
            self._create_triple_builder()
        self._triple_builder.label(lan, lang)
        return self

    def description(self, c, lang="en"):
        if not self._triple_builder:
            self._create_triple_builder()
        self._triple_builder.description(c, lang)
        return self

    def parent(self, *parent_list):
        """Specifies that a new class should have parents class
        param {array} parentList the list of parent class []
        """
        if not self._triple_builder:
            self._create_triple_builder()
        for ipl in parent_list:
            pn = self._clean_class(ipl)
            self._triple_builder._add_po("rdfs:subClassOf", pn)
        return self

    def max(self, m):
        if self._triple_builder:
            self._triple_builder.card(m, "max")
        return self

    def cardinality(self, m):
        if self._triple_builder:
            self._triple_builder.card(m, "cardinality")
        return self

    def min(self, m):
        if self._triple_builder:
            self._triple_builder.card(m, "min")
        return self

    def _create_triple_builder(self, node=None, user_type=None):
        s = node
        t = user_type
        lastsubj = self._find_last_subject(self._cursor)
        g = False
        if lastsubj:
            gobj = (
                lastsubj["woql:graph_filter"]
                if lastsubj.get("woql:graph_filter")
                else lastsubj.get("woql:graph")
            )
            g = gobj["@value"] if gobj else False
            s = lastsubj["woql:subject"]
            t = user_type if user_type else lastsubj["@type"]
        if "@type" in self._cursor:
            subq = WOQLQuery().from_dict(self._cursor)
            if self._cursor["@type"] == "woql:And":
                newq = subq
            else:
                newq = WOQLQuery().woql_and(subq)
            nuj = newq.to_dict()
            self._cursor.clear()
            for i in nuj:
                self._cursor[i] = nuj[i]
        else:
            self.woql_and()
        self._triple_builder = TripleBuilder(t, self, s, g)

    def add_class(self, c, graph=None):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        if not graph:
            graph = self._graph
        if c:
            c = self._clean_class(c, True)
            self._adding_class = c
            self.add_quad(c, "rdf:type", "owl:Class", graph)
        return self

    def insert_class_data(self, data, ref_graph):
        """Adds a bunch of class data in one go
        """
        if data.get("id"):
            self.add_class(data["id"], ref_graph)
            if data.get("label"):
                self.label(data["label"])
            if data.get("description"):
                self.description(data["description"])
            if data.get("parent"):
                if not isinstance(data["parent"], list):
                    data["parent"] = [data["parent"]]
                self.parent(*data["parent"])
            for k in data:
                if k not in ["id", "label", "description", "parent"]:
                    data[k]["domain"] = data["id"]
                    self.insert_property_data(data[k], ref_graph)
        return self

    def doctype_data(self, data, ref_graph):
        if not data.get("parent"):
            data["parent"] = []
        if not isinstance(data["parent"], list):
            data["parent"] = [data["parent"]]
        data["parent"].append("Document")
        return self.insert_class_data(data, ref_graph)

    def insert_property_data(self, data, ref_graph):
        if data.get("id"):
            self.add_property(data["id"], ref_graph)
            if data.get("label"):
                self.label(data["label"])
            if data.get("description"):
                self.description(data["description"])
            if data.get("domain"):
                self.domain(data["domain"])
            if data.get("max"):
                self.max(data["max"])
            if data.get("min"):
                self.min(data["min"])
            if data.get("cardinality"):
                self.cardinality(data["cardinality"])
        return self

    def delete_class(self, c, graph=None):
        if not graph:
            graph = self._graph
        ap = WOQLQuery()
        if c:
            c = ap._clean_class(c, True)
            ap.woql_and(
                WOQLQuery().delete_quad(c, "v:Outgoing", "v:Value", graph),
                WOQLQuery().opt().delete_quad("v:Other", "v:Incoming", c, graph),
            )
            ap._updated()
        return ap

    def add_property(self, p, t, graph=None):
        if not graph:
            graph = self._graph
        ap = WOQLQuery()
        t = ap._clean_type(t, True) if t else "xsd:string"
        if p:
            p = ap._clean_path_predicate(p)
            # TODO: cleaning
            if utils.is_data_type(t):
                ap.woql_and(
                    WOQLQuery().add_quad(p, "rdf:type", "owl:DatatypeProperty", graph),
                    WOQLQuery().add_quad(p, "rdfs:range", t, graph),
                )
            else:
                ap.woql_and(
                    WOQLQuery().add_quad(p, "rdf:type", "owl:ObjectProperty", graph),
                    WOQLQuery().add_quad(p, "rdfs:range", t, graph),
                )
            ap._updated()
        return ap

    def delete_property(self, p, graph=None):
        if not graph:
            graph = self._graph
        ap = WOQLQuery()
        if p:
            p = ap._clean_path_predicate(p)
            ap.woql_and(
                WOQLQuery().delete_quad(p, "v:All", "v:Al2", graph),
                WOQLQuery().delete_quad("v:Al3", "v:Al4", p, graph),
            )
            ap._updated()
        return ap

    def box_classes(self, classes, excepts, prefix=None, graph=None):
        if not graph:
            graph = self._graph
        if not prefix:
            prefix = "scm:"
        subs = []
        for i in classes:
            subs.append(WOQLQuery().sub(classes[i], "v:Cid"))
        nsubs = []
        for i in excepts:
            nsubs.append(WOQLQuery().woql_not().sub(excepts[i], "v:Cid"))
        idgens = [
            WOQLQuery().re("#(.)(.*)", "v:Cid", ["v:AllB", "v:FirstB", "v:RestB"]),
            WOQLQuery().lower("v:FirstB", "v:Lower"),
            WOQLQuery().concat(["v:Lower", "v:RestB"], "v:Propname"),
            WOQLQuery().concat(["Scoped", "v:FirstB", "v:RestB"], "v:Cname"),
            WOQLQuery().idgen(prefix, ["v:Cname"], "v:ClassID"),
            WOQLQuery().idgen(prefix, ["v:Propname"], "v:PropID"),
        ]
        woql_filter = WOQLQuery().woql_and(
            WOQLQuery().quad("v:Cid", "rdf:type", "owl:Class", graph),
            WOQLQuery().woql_not().node("v:Cid").abstract(graph),
            WOQLQuery().woql_and(*idgens),
            WOQLQuery().quad("v:Cid", "label", "v:Label", graph),
            WOQLQuery().concat("Box Class generated for class v:Cid", "v:CDesc", graph),
            WOQLQuery().concat(
                "Box Property generated to link box v:ClassID to class v:Cid",
                "v:PDesc",
                graph,
            ),
        )
        if len(subs):
            if len(subs) == 1:
                woql_filter.woql_and(subs[0])
            else:
                woql_filter.woql_and(WOQLQuery().woql_or(*subs))
        if len(nsubs):
            woql_filter.woql_and(WOQLQuery().woql_and(*nsubs))
        cls = (
            WOQLQuery(graph=graph)
            .add_class("v:ClassID")
            .label("v:Label")
            .description("v:CDesc")
        )
        prop = (
            WOQLQuery(graph=graph)
            .add_property("v:PropID", "v:Cid")
            .label("v:Label")
            .description("v:PDesc")
            .domain("v:ClassID")
        )
        nq = WOQLQuery.when(woql_filter).woql_and(cls, prop)
        return nq._updated()

    def generate_choice_list(
        self,
        cls=None,
        clslabel=None,
        clsdesc=None,
        choices=None,
        graph=None,
        parent=None,
    ):
        if not graph:
            graph = self._graph
        clist = []
        if ":" not in cls:
            listid = "_:" + cls
        else:
            listid = "_:" + cls.split(":")[1]
        lastid = listid
        wq = WOQLQuery().add_class(cls, graph).label(clslabel)
        if clsdesc:
            wq.description(clsdesc)
        if parent:
            wq.parent(parent)
        confs = [wq]
        for i in choices:
            if not choices[i]:
                continue
            if type(choices[i]) == list:
                chid = choices[i][0]
                clab = choices[i][1]
                desc = choices[i][2] if len(choices[i]) >= 3 else False
            else:
                chid = choices[i]
                clab = utils.label_from_url(chid)
                desc = False
            cq = WOQLQuery().insert(chid, cls, graph).label(clab)
            if desc:
                cq.description(desc)
            confs.append(cq)
            if i < len(choices) - 1:
                nextid = listid + "_" + i
            else:
                nextid = "rdf:nil"
            clist.append(WOQLQuery().add_quad(lastid, "rdf:first", chid, graph))
            clist.append(WOQLQuery().add_quad(lastid, "rdf:rest", nextid, graph))
            lastid = nextid
        oneof = WOQLQuery().woql_and(
            WOQLQuery().add_quad(cls, "owl:oneOf", listid, graph), *clist
        )
        return WOQLQuery().woql_and(*confs, oneof)

    def libs(self, libs, parent, graph, prefix):
        bits = []
        if "xdd" in libs:
            bits.append(self._load_xdd(graph))
            if "box" in libs:
                bits.append(self._load_xdd_boxes(parent, graph, prefix))
                bits.append(self._load_xsd_boxes(parent, graph, prefix))
        elif "box" in libs:
            bits.append(self._load_xsd_boxes(parent, graph, prefix))
        if len(bits) > 1:
            return WOQLQuery().woql_and(*bits)
        return bits[0]

    def _load_xdd(self, graph=None):
        if not graph:
            graph = self._graph
        return WOQLQuery().woql_and(
            # geograhpic datatypes
            self.add_datatype(
                "xdd:coordinate",
                "Coordinate",
                "A latitude / longitude pair making up a coordinate, encoded as: [lat,long]",
                graph,
            ),
            self.add_datatype(
                "xdd:coordinatePolygon",
                "Coordinate Polygon",
                "A JSON list of [[lat,long]] coordinates forming a closed polygon.",
                graph,
            ),
            self.add_datatype(
                "xdd:coordinatePolyline",
                "Coordinate Polyline",
                "A JSON list of [[lat,long]] coordinates.",
                graph,
            ),
            # uncertainty range datatypes
            self.add_datatype(
                "xdd:dateRange",
                "Date Range",
                "A date (YYYY-MM-DD) or an uncertain date range [YYYY-MM-DD1,YYYY-MM-DD2]. "
                + "Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            self.add_datatype(
                "xdd:decimalRange",
                "Decimal Range",
                "Either a decimal value (e.g. 23.34) or an uncertain range of decimal values "
                + "(e.g.[23.4, 4.143]. Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            self.add_datatype(
                "xdd:integerRange",
                "Integer Range",
                "Either an integer (e.g. 30) or an uncertain range of integers [28,30]. "
                + "Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            self.add_datatype(
                "xdd:gYearRange",
                "Year Range",
                "A year (e.g. 1999) or an uncertain range of years: (e.g. [1999,2001])."
                + "Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            # string refinement datatypes
            self.add_datatype("xdd:email", "Email", "A valid email address", graph),
            self.add_datatype("xdd:html", "HTML", "A string with embedded HTML", graph),
            self.add_datatype("xdd:json", "JSON", "A JSON encoded string", graph),
            self.add_datatype("xdd:url", "URL", "A valid http(s) URL", graph),
        )

    def add_datatype(self, d_id, label, descr, graph=None):
        if not graph:
            graph = self._graph
        # utility function for creating a datatype in woql
        dt = WOQLQuery().insert(d_id, "rdfs:Datatype", graph).label(label)
        if descr:
            dt.description(descr)
        return dt

    def _load_xsd_boxes(self, parent, graph, prefix):
        # Loads box classes for all of the useful xsd classes the format is to generate the box classes for xsd:anyGivenType
        # as class(prefix:AnyGivenType) -> property(prefix:anyGivenType) -> datatype(xsd:anyGivenType)
        return WOQLQuery().woql_and(
            self.box_datatype(
                "xsd:anySimpleType",
                "Any Simple Type",
                "Any basic data type such as string or integer. An xsd:anySimpleType value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:string",
                "String",
                "Any text or sequence of characters",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:boolean",
                "Boolean",
                "A true or false value. An xsd:boolean value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:decimal",
                "Decimal",
                "A decimal number. An xsd:decimal value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:double",
                "Double",
                "A double-precision decimal number. An xsd:double value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:float",
                "Float",
                "A floating-point number. An xsd:float value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:time",
                "Time",
                "A time. An xsd:time value. hh:mm:ss.ssss",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:date",
                "Date",
                "A date. An xsd:date value. YYYY-MM-DD",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:dateTime",
                "Date Time",
                "A date and time. An xsd:dateTime value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:dateTimeStamp",
                "Date-Time Stamp",
                "An xsd:dateTimeStamp value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:gYear",
                "Year",
                " A particular 4 digit year YYYY - negative years are BCE.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:gMonth",
                "Month",
                "A particular month. An xsd:gMonth value. --MM",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:gDay",
                "Day",
                "A particular day. An xsd:gDay value. ---DD",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:gYearMonth",
                "Year / Month",
                "A year and a month. An xsd:gYearMonth value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:gMonthDay",
                "Month / Day",
                "A month and a day. An xsd:gMonthDay value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:duration",
                "Duration",
                "A period of time. An xsd:duration value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:yearMonthDuration",
                "Year / Month Duration",
                "A duration measured in years and months. An xsd:yearMonthDuration value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:dayTimeDuration",
                "Day / Time Duration",
                "A duration measured in days and time. An xsd:dayTimeDuration value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:byte", "Byte", "An xsd:byte value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:short", "Short", "An xsd:short value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:integer",
                "Integer",
                "A simple number. An xsd:integer value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:long", "Long", "An xsd:long value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:unsignedByte",
                "Unsigned Byte",
                "An xsd:unsignedByte value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:unsignedInt",
                "Unsigned Integer",
                "An xsd:unsignedInt value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:unsignedLong",
                "Unsigned Long Integer",
                "An xsd:unsignedLong value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:positiveInteger",
                "Positive Integer",
                "A simple number greater than 0. An xsd:positiveInteger value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:nonNegativeInteger",
                "Non-Negative Integer",
                "A simple number that can't be less than 0. An xsd:nonNegativeInteger value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:negativeInteger",
                "Negative Integer",
                "A negative integer. An xsd:negativeInteger value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:nonPositiveInteger",
                "Non-Positive Integer",
                "A number less than or equal to zero. An xsd:nonPositiveInteger value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:base64Binary",
                "Base 64 Binary",
                "An xsd:base64Binary value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:anyURI",
                "Any URI",
                "Any URl. An xsd:anyURI value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:language",
                "Language",
                "A natural language identifier as defined by by [RFC 3066] . An xsd:language value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:normalizedString",
                "Normalized String",
                "An xsd:normalizedString value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:token", "Token", "An xsd:token value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:NMTOKEN", "NMTOKEN", "An xsd:NMTOKEN value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:Name", "Name", "An xsd:Name value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:NCName", "NCName", "An xsd:NCName value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:NOTATION",
                "NOTATION",
                "An xsd:NOTATION value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xsd:QName", "QName", "An xsd:QName value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:ID", "ID", "An xsd:ID value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:IDREF", "IDREF", "An xsd:IDREF value.", parent, graph, prefix
            ),
            self.box_datatype(
                "xsd:ENTITY", "ENTITY", "An xsd:ENTITY value.", parent, graph, prefix
            ),
        )

    def _load_xdd_boxes(self, parent, graph, prefix):
        # Generates a query to create box classes for all of the xdd datatypes. the format is to generate the box classes for xdd:anyGivenType
        # as class(prefix:AnyGivenType) -> property(prefix:anyGivenType) -> datatype(xdd:anyGivenType)
        return WOQLQuery().woql_and(
            self.box_datatype(
                "xdd:coordinate",
                "Coordinate",
                "A particular location on the surface of the earth, defined by latitude and longitude . An xdd:coordinate value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xdd:coordinatePolygon",
                "Geographic Area",
                "A shape on a map which defines an area. within the defined set of coordinates   An xdd:coordinatePolygon value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xdd:coordinatePolyline",
                "Coordinate Path",
                "A set of coordinates forming a line on a map, representing a route. An xdd:coordinatePolyline value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype("xdd:url", "URL", "A valid url.", parent, graph, prefix),
            self.box_datatype(
                "xdd:email", "Email", "A valid email address.", parent, graph, prefix
            ),
            self.box_datatype(
                "xdd:html", "HTML", "A safe HTML string", parent, graph, prefix
            ),
            self.box_datatype("xdd:json", "JSON", "A JSON Encoded String"),
            self.box_datatype(
                "xdd:gYearRange",
                "Year",
                "A 4-digit year, YYYY, or if uncertain, a range of years. An xdd:gYearRange value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xdd:integerRange",
                "Integer",
                "A simple number or range of numbers. An xdd:integerRange value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xdd:decimalRange",
                "Decimal Number",
                "A decimal value or, if uncertain, a range of decimal values. An xdd:decimalRange value.",
                parent,
                graph,
                prefix,
            ),
            self.box_datatype(
                "xdd:dateRange",
                "Date Range",
                "A date or a range of dates YYYY-MM-DD",
                parent,
                graph,
                prefix,
            ),
        )

    def box_datatype(
        self,
        datatype=None,
        label=None,
        descr=None,
        parent=None,
        graph=None,
        prefix=None,
    ):
        # utility function for boxing a datatype in woql
        # format is (predicate) prefix:datatype (domain) prefix:Datatype (range) xsd:datatype
        if not graph:
            graph = self._graph
        prefix = prefix if prefix else "scm:"
        ext = datatype.split(":")[1]
        box_class_id = prefix + ext[0].upper() + ext[1:]
        box_prop_id = prefix + ext[0].lower() + ext[1:]
        box_class = self.add_class(box_class_id, graph).label(label)
        box_class.description("Boxed Class for " + datatype)
        if parent:
            box_class.parent(parent)
        box_prop = (
            self.add_property(box_prop_id, datatype, graph)
            .label(label)
            .domain(box_class_id)
        )
        if descr:
            box_prop.description(descr)
        return WOQLQuery().woql_and(box_class, box_prop)

    def doctype(self, user_type, graph=None, label=None, description=None):
        if label is None and description is None:
            return WOQLQuery().add_class(user_type, graph).parent("Document")

        result_obj = WOQLQuery().doctype(user_type, graph)
        if isinstance(label, str) and label:
            result_obj = result_obj.label(label)
        if isinstance(description, str) and description:
            result_obj = result_obj.description(description)
        return result_obj


class TripleBuilder:
    """Triple Builder

    higher level composite queries - not language or api elements
    Class for enabling building of triples from pieces
    type is add_quad / remove_quad / add_triple / remove_triple
     """

    def __init__(self, ops_type=None, query=None, s=None, g=None):
        """
        what accumulation type are we
        """
        if ops_type and ops_type.find(":") == -1:
            ops_type = "woql:" + ops_type
        self._type = ops_type
        self._cursor = query._cursor
        if s:
            self._subject = s
        else:
            self._subject = False
        self._parent_query = query
        self._graph = g

    def label(self, lab, lang="en"):
        if lab[:2] == "v:":
            d = lab
        else:
            d = {"@value": lab, "@type": "xsd:string", "@language": lang}
        x = self._add_po("rdfs:label", d)
        return x

    def graph(self, g):
        self._graph = g

    def description(self, c, lang=None):
        if not lang:
            lang = "en"
        if c[:2] == "v:":
            d = c
        else:
            d = {"@value": c, "@type": "xsd:string", "@language": lang}
        x = self._add_po("rdfs:comment", d)
        return x

    def _add_po(self, p, o, g=None):
        if not g:
            g = self._graph
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
        elif g:
            newq = WOQLQuery().quad(self._subject, p, o, g)
        else:
            newq = WOQLQuery().triple(self._subject, p, o)
        return self._parent_query.woql_and(newq)

    def _get_o(self, s, p):
        if self._cursor["@type"] == "woql:And":
            for item in self._cursor["query_list"]:
                subq = item["woql:query"]
                if (
                    subq._parent_query["woql:subject"] == s
                    and subq._parent_query["woql:predicate"] == p
                ):
                    return subq._parent_query["woql:object"]
        return False

    def card(self, n, which):
        # need to generate a new id for the cardinality object
        # and point it at the property in question via the onProperty function
        prop = self._subject
        if isinstance(prop, dict):
            if prop.get("node"):
                prop = prop["node"]
            else:
                return False
        newid = str(prop) + str(which)
        self._query.woql_and(
            WOQLQuery()
            .add_quad(newid, "type", "owl:Restriction", self._graph)
            .add_quad(newid, "owl:onProperty", self._subject, self._graph)
        )
        if which == "max":
            self._query.woql_and().add_quad(
                newid,
                "owl:maxCardinality",
                {"@value": n, "@type": "xsd:nonNegativeInteger"},
                self._graph,
            )
        elif which == "min":
            self._query.woql_and().add_quad(
                newid,
                "owl:minCardinality",
                {"@value": n, "@type": "xsd:nonNegativeInteger"},
                self._graph,
            )
        else:
            self._query.woql_and().add_quad(
                newid,
                "owl:cardinality",
                {"@value": n, "@type": "xsd:nonNegativeInteger"},
                self._graph,
            )
        # then make the domain of the property into a subclass of the restriction
        od = self._get_o(prop, "rdfs:domain")
        if od:
            self._query.woql_and().add_quad(od, "subClassOf", newid, self._graph)
        return self
