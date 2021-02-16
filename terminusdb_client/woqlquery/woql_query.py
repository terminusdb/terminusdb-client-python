import copy
import datetime as dt
import json

# import pprint
import re

import terminusdb_client.woql_utils as utils

from .woql_core import _copy_dict, _tokenize, _tokens_to_json

# pp = pprint.PrettyPrinter(indent=4)


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
        self._triple_builder_context = {}
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

    def __add__(self, other):
        """Creates a logical AND with the argument passed, for WOQLQueries.

        Parameters
        ----------
        other : WOQLQuery object

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return WOQLQuery().woql_and(self, other)

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
        if not isinstance(json, dict):
            return False
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
        if type(varb) is str:
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
        if type(colname_or_index) is int:
            asvar["@type"] = "woql:IndexedAsVar"
            asvar["woql:index"] = self._jlt(colname_or_index, "xsd:nonNegativeInteger")
        elif type(colname_or_index) is str:
            asvar["@type"] = "woql:NamedAsVar"
            asvar["woql:identifier"] = self._jlt(colname_or_index)
        if vname[:2] == "v:":
            vname = vname[2:]
        asvar["woql:variable_name"] = {"@type": "xsd:string", "@value": vname}
        if obj_type:
            asvar["woql:var_type"] = obj_type
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
        if type(arg) is dict:
            if hasattr(arg, "to_dict"):
                return arg.to_dict()
            else:
                return arg
        var = self._clean_object(arg, "xsd:decimal")
        return var

    def _vlist(self, target_list):
        """Wraps value lists in the appropriate json-ld"""
        vobj = {"@type": "woql:Array", "woql:array_element": []}
        if type(target_list) is str:
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
        if type(wvar) is str:
            return self._expand_variable(wvar, True)
        if type(wvar) is list:
            ret = {"@type": "woql:Array", "woql:array_element": []}
            for idx, item in enumerate(wvar):
                co_item = self._clean_object(item)
                if type(co_item) is str:
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
        if type(obj) is dict:
            return obj
        elif type(obj) is str:
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
        if type(predicate) is dict:
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
        if type(user_obj) is str:
            if self._looks_like_class(user_obj):
                return self._clean_class(user_obj)
            elif self._vocab and (user_obj in self._vocab):
                return self._clean_class(self._vocab[user_obj])
            else:
                obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) is float:
            if not target:
                target = "xsd:decimal"
            obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) is int:
            if not target:
                target = "xsd:integer"
            obj["woql:datatype"] = self._jlt(user_obj, target)
        elif type(user_obj) is bool:
            if not target:
                target = "xsd:boolean"
            obj["woql:datatype"] = self._jlt(user_obj, target)
        elif isinstance(user_obj, dt.date):
            if not target:
                target = "xsd:dateTime"
            obj["woql:datatype"] = self._jlt(user_obj.isoformat(), target)
        elif type(user_obj) is dict:
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
        if (
            pref == "v"
            or pref == "scm"
            or pref == "doc"
            or pref == "terminusdb"
            or pref == "http"
            or pref == "https"
        ):
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
            "boolean": "xsd:boolean",
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

    def execute(self, client, commit_msg=None, file_dict=None):
        """Executes the query using the passed client to connect to a server

        Parameters
        ----------
        client: WOQLClient object
            client that provide connection to the database for the query to execute.
        commit_msg: str
            optional, commit message for this query. Recommended for query that carrries an update.
        file_dict:
            File dictionary to be associated with post name => filename, for multipart POST

        """
        if commit_msg is None:
            return client.query(self, file_dict=file_dict)
        else:
            return client.query(self, commit_msg, file_dict=file_dict)

    def to_json(self):
        """Dumps the JSON-LD format of the query in a json string"""
        return self._json()

    def from_json(self, input_json):
        """Set a query from a JSON-LD json string"""
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
        """Give the dictionary that represents the query in JSON-LD format."""
        return _copy_dict(self._query, True)

    def from_dict(self, dictdata):
        """Set a query from a dictionary that represents the query in JSON-LD format."""
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
            for item in json["woql:query_list"][::-1]:
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

    def _find_last_property(self, json):
        """Finds the last woql property that has a woql:subject in it and returns the json for that
        used for triplebuilder to chain further calls - when they may be inside ands or ors or subqueries

        Parameters
        ----------
        json : dict
               dictionary that representing the query in josn-ld"""
        if "woql:query_list" in json:
            for item in json["woql:query_list"][::-1]:
                subitem = self._find_last_property(item)
                if subitem:
                    return subitem
        if "woql:query" in json:
            item = self._find_last_property(json["woql:query"])
            if item:
                return item
        if "woql:subject" in json and self._is_property_triple(
            json.get("woql:predicate"), json.get("woql:object")
        ):
            return json
        return False

    def _is_property_triple(self, pred, obj):
        if isinstance(pred, dict):
            p = pred.get("woql:node")
        else:
            p = pred
        if isinstance(obj, dict):
            o = obj.get("woql:node")
        else:
            o = obj
        if o == "owl:ObjectProperty" or o == "owl:DatatypeProperty":
            return True
        if p == "rdfs:domain" or p == "rdfs:range":
            return True
        return False

    def _compile_path_pattern(self, pat):
        """Turns a textual path pattern into a JSON-LD description"""
        toks = _tokenize(pat)
        if toks:
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
                if type(item) is str:
                    spl = item.split(":")
                    if len(spl) == 2 and spl[1] and spl[0] != "_":
                        self._vocab[spl[0]] = spl[1]

    def _wrap_cursor_with_and(self):
        if self._cursor.get("@type") == "woql:And" and self._cursor.get(
            "woql:query_list"
        ):
            next_item = len(self._cursor.get("woql:query_list"))
            self.woql_and({})
            self._cursor = self._cursor["woql:query_list"][next_item]["woql:query"]
        else:
            new_json = WOQLQuery().from_dict(self._cursor)
            self._cursor.clear()
            self.woql_and(new_json, {})
            self._cursor = self._cursor["woql:query_list"][1]["woql:query"]

    def using(self, collection, subq=None):
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
        self._cursor["@context"] = "/api/prefixes/" + collection
        return self._add_sub_query(subq)

    def comment(self, comment, subq=None):
        """Adds a text comment to a query - can also be used to wrap any part of a query to turn it off

        Parameters
        ----------
        comment : str
            text comment
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if comment and comment == "woql:args":
            return ["woql:comment", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Comment"
        self._cursor["woql:comment"] = self._jlt(comment)
        return self._add_sub_query(subq)

    def select(self, *args):
        """Filters the query so that only the variables included in [V1...Vn] are returned in the bindings

        Parameters
        ----------
        args
            only these variables are returned

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        """Select the set of variables that the result will return"""
        queries = list(args)
        if queries and queries[0] == "woql:args":
            return ["woql:variable_list", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Select"
        if queries != [] and not queries:
            return self._parameter_error(
                "Select must be given a list of variable names"
            )
        if queries == []:
            embedquery = False
        elif hasattr(queries[-1], "to_dict"):
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

    def distinct(self, *args):
        """Ensures that the solutions for the variables [V1...Vn] are distinct

        Parameters
        ----------
        args
            The variables to make distinct

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        """Select the set of variables that the result will return"""
        queries = list(args)
        if queries and queries[0] == "woql:args":
            return ["woql:variable_list", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Distinct"
        if queries != [] and not queries:
            return self._parameter_error(
                "Distinct must be given a list of variable names"
            )
        if queries == []:
            embedquery = False
        elif hasattr(queries[-1], "to_dict"):
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
        """Creates a logical AND of the arguments
        Commonly used to combine WOQLQueries.

        Parameters
        ----------
        args : WOQLQuery objects
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Creates a logical OR of the arguments

        Parameters
        ----------
        args : WOQLQuery objects

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Specifies the database URL that will be the default database for the enclosed query

        Parameters
        ----------
        graph_filter : str
            url of the database
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Sets the current output graph for writing output to.

        Parameters
        ----------
        graph_descriptor : str
            output graph
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Creates a triple pattern matching rule for the triple [S, P, O] (Subject, Predicate, Object)

        Parameters
        ----------
        sub : str
            Subject
        pred : str
            Predicate
        obj : str
            Object
        opt : bool
            weather or not this triple is optional, default to be False

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if opt:
            return self.opt().triple(sub, pred, obj)
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Triple"
        self._cursor["woql:subject"] = self._clean_subject(sub)
        self._cursor["woql:predicate"] = self._clean_predicate(pred)
        self._cursor["woql:object"] = self._clean_object(obj)
        return self

    def added_triple(self, sub, pred, obj, opt=False):
        """Creates a triple pattern matching rule for the triple [S, P, O] (Subject, Predicate, Object) added to the current commit.

        Parameters
        ----------
        sub : str
            Subject
        pred : str
            Predicate
        obj : str
            Object
        opt : bool
            weather or not this triple is optional, default to be False

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if opt:
            return self.opt().triple(sub, pred, obj)
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:AddedTriple"
        self._cursor["woql:subject"] = self._clean_subject(sub)
        self._cursor["woql:predicate"] = self._clean_predicate(pred)
        self._cursor["woql:object"] = self._clean_object(obj)
        return self

    def removed_triple(self, sub, pred, obj, opt=False):
        """Creates a triple pattern matching rule for the triple [S, P, O] (Subject, Predicate, Object) added to the current commit.

        Parameters
        ----------
        sub : str
            Subject
        pred : str
            Predicate
        obj : str
            Object
        opt : bool
            weather or not this triple is optional, default to be False

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if opt:
            return self.opt().triple(sub, pred, obj)
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:RemovedTriple"
        self._cursor["woql:subject"] = self._clean_subject(sub)
        self._cursor["woql:predicate"] = self._clean_predicate(pred)
        self._cursor["woql:object"] = self._clean_object(obj)
        return self

    def quad(self, sub, pred, obj, graph, opt=False):
        """Creates a pattern matching rule for the quad [S, P, O, G] (Subject, Predicate, Object, Graph)

        Parameters
        ----------
        sub : str
            Subject
        pre : str
            Predicate
        obj : str
            Object
        gra : str
            Graph
        opt : bool
            weather or not this quad is optional, default to be False

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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

    def added_quad(self, sub, pred, obj, graph, opt=False):
        """Creates a pattern matching rule for the quad [S, P, O, G] (Subject, Predicate, Object, Graph) added to the current commit.

        Parameters
        ----------
        sub : str
            Subject
        pre : str
            Predicate
        obj : str
            Object
        gra : str
            Graph
        opt : bool
            weather or not this quad is optional, default to be False

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        self._cursor["@type"] = "woql:AddedQuad"
        self._cursor["woql:graph_filter"] = self._clean_graph(graph)
        return self

    def removed_quad(self, sub, pred, obj, graph, opt=False):
        """Creates a pattern matching rule for the quad [S, P, O, G] (Subject, Predicate, Object, Graph) added to the current commit.

        Parameters
        ----------
        sub : str
            Subject
        pre : str
            Predicate
        obj : str
            Object
        gra : str
            Graph
        opt : bool
            weather or not this quad is optional, default to be False

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        self._cursor["@type"] = "woql:RemovedQuad"
        self._cursor["woql:graph_filter"] = self._clean_graph(graph)
        return self

    def string(self, input_str):
        """Transforms the given string into the proper json-ld form

        Parameters
        ----------
        input_str : str
            the given input string

        Returns
        -------
        dict
        """
        return {"@type": "xsd:string", "@value": input_str}

    def boolean(self, input_bool):
        """Transforms the given bool object into the proper json-ld form

        Parameters
        ----------
        input_bool : bool
            the given input string

        Returns
        -------
        dict
        """
        if input_bool:
            return {"@type": "xsd:boolean", "@value": True}
        else:
            return {"@type": "xsd:boolean", "@value": False}

    def datetime(self, input_obj):
        """Transforms the given datetime object into the proper json-ld form

        Parameters
        ----------
        input_obj : str
            the given input dateTime object

        Returns
        -------
        dict
        """
        if isinstance(input_obj, dt.date):
            return {"@type": "xsd:dateTime", "@value": input_obj.isoformat()}
        elif isinstance(input_obj, str):
            return {"@type": "xsd:dateTime", "@value": input_obj}
        else:
            raise ValueError("Input need to be either string or a datetime object.")

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
        """Returns true if child is a sub-class of parent, according to the current DB schema

        Parameters
        ----------
        parent : str
            the parent class to be checked
        child : str, optional
            the child class to be checked

        Returns
        -------
        bool
        """
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
        """Matches if a is equal to b
        Parameters
        ----------
        left : str
            object in the graph
        right : str
            object in the graph
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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

    def read_object(self, iri, output_var):
        if iri and iri == "woql:args":
            return ["woql:document"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:ReadObject"
        self._cursor["woql:document_uri"] = iri
        self._cursor["woql:document"] = self._expand_variable(output_var)
        return self

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

    def put(self, as_vars, query, query_resource=None):
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
        self._cursor["woql:query"] = self._jobj(query)
        if query_resource:
            self._cursor["woql:query_resource"] = self._jobj(query_resource)
        else:
            self._cursor["woql:query_resource"] = {}
        return self

    def woql_as(self, *args):
        if args and args[0] == "woql:args":
            return [["woql:indexed_as_var", "woql:named_as_var"]]
        if type(self._query) is not list:
            self._query = []
        if type(args[0]) is list:
            if len(args) == 1:
                for i, onemap in enumerate(args[0]):
                    iasv = self._asv(i, onemap)
                    self._query.append(iasv)
            else:
                for onemap in args:
                    if type(onemap) is list and len(onemap) >= 2:
                        if len(onemap) == 2:
                            map_type = False
                        else:
                            map_type = onemap[2]
                        oasv = self._asv(onemap[0], onemap[1], map_type)
                        self._query.append(oasv)
        elif type(args[0]) in [int, str]:
            if len(args) > 2 and type(args[2]) is str:
                oasv = self._asv(args[0], args[1], args[2])
            elif len(args) > 1 and type(args[1]) is str:
                if args[1][:4] == "xsd:" or args[1][:4] == "xdd:":
                    oasv = self._asv(len(self._query), args[0], args[1])
                else:
                    oasv = self._asv(args[0], args[1])
            else:
                oasv = self._asv(len(self._query), args[0])
            self._query.append(oasv)
        elif hasattr(args[0], "to_dict"):
            self._query.append(args[0].to_dict())
        elif type(args[0]) is dict:
            self._query.append(args[0])
        return self

    def file(self, fpath, opts=None):
        """Provides details of a file source in a JSON format that includes a URL property

        Parameters
        ----------
        fpath : dict
            file data source in a JSON format
        opts : input options
            optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        Example
        -------
        To load a local csv file:
        >>> WOQLQuery().file("/app/local_files/my.csv")
        See Also
        --------
        remote
            If your csv file is a uri then use :meth:`.remote` instead of `.file`.
        """
        if opts is None:
            opts = []
        if fpath and fpath == "woql:args":
            return ["woql:file", "woql:format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:FileResource"
        self._cursor["woql:file"] = fpath
        return self._wfrom(opts)

    def once(self, query=None):
        """Obtains only one result from subquery

        Parameters
        ----------
        query : WOQLQuery object, optional

        Returns
        ----------
        WOQLQuery object
            query object that can be chained and/or executed
        """
        if query and query == "woql:args":
            return ["woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Once"
        return self._add_sub_query(query)

    def remote(self, uri, opts=None):
        """Provides details of a remote data source in a JSON format that includes a URL property

        Parameters
        ----------
        uri : str
            remote data source
        opts : input options
            optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        Examples
        --------
        >>> csv = WOQLQuery().get(
        ...     WOQLQuery().woql_as("Start station", "v:Start_Station").
        ...     woql_as("End station", "v:End_Station").
        ...     woql_as("Start date", "v:Start_Time").
        ...     woql_as("End date", "v:End_Time").
        ...     woql_as("Duration", "v:Duration").
        ...     woql_as("Start station number", "v:Start_ID").
        ...     woql_as("End station number", "v:End_ID").
        ...     woql_as("Bike number", "v:Bike").
        ...     woql_as("Member type", "v:Member_Type")
        ... ).remote("https://terminusdb.com/t/data/bike_tutorial.csv")
        See Also
        --------
        file
            If your csv file is local then use :meth:`.file` instead of `.remote`.
        """
        if uri and uri == "woql:args":
            return ["woql:remote_uri", "woql:format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:RemoteResource"
        self._cursor["woql:remote_uri"] = {"@type": "xsd:anyURI", "@value": uri}
        return self._wfrom(opts)

    def post(self, fpath, opts=None):
        if fpath and fpath == "woql:args":
            return ["woql:file", "woql:format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:PostResource"
        self._cursor["woql:file"] = {"@type": "xsd:string", "@value": fpath}
        return self._wfrom(opts)

    def delete_triple(self, subject, predicate, object_or_literal):
        """Deletes any triples that match the rule [subject, predicate, object]

        Parameters
        ----------
        subject : str
            Subject
        predicate : str
            Predicate
        object_or_literal : str
            Object or Literal

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        Examples
        --------
        This example deletes the comment triple of a particular value from the document
        identified by doc:X:
        >>> update = WOQLQuery().delete_triple("doc:X", "comment", "my comment")
        >>> qry = WOQLQuery().when(True, update)
        >>> client.update(qry.json(), 'MyDatabaseId')
        Note that only triples matching the particular object value will be deleted.
        To delete all triples matching this predicate, (regardless of value) we use a
        when clause, and introduce a variable ``v:any`` which will bind to any value
        for this subject and predicate combination:
        >>> when = WOQLQuery().triple('doc:X', 'comment', 'v:any')
        >>> update = WOQLQuery().delete_triple('doc:X', 'comment', 'v:any')
        >>> qry = WOQLQuery().when(when, update)
        >>> client.update(qry.json(), 'MyDatabaseId')
        """
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        triple_args = self.triple(subject, predicate, object_or_literal)
        if subject and subject == "woql:args":
            return triple_args
        self._cursor["@type"] = "woql:DeleteTriple"
        return self._updated()

    def add_triple(self, subject, predicate, object_or_literal):
        """Adds triples according to the the pattern [subject, predicate, object]

        Parameters
        ----------
        subject : str
            Subject
        predicate : str
            Predicate
        object_or_literal : str
            Object or Literal

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute

        Examples
        --------
        This example adds a triple for a comment predicate and a certain value to the document identified by doc:X:
        >>> update = WOQLQuery().add_triple("doc:X", "comment", "my comment")
        >>> qry = WOQLQuery().when(True, update)
        >>> client.update(qry.json(), 'MyDatabaseId')

        Notes
        --------
        To update an existing triple, it is not just a case of calling `add_triple` again.
        One needs to delete the previous triple first.
        Otherwise two triples with the same predicate but different object values will be present.

        See Also
        --------
        delete_triple
        add_quad
        """
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        triple_args = self.triple(subject, predicate, object_or_literal)
        if subject and subject == "woql:args":
            return triple_args
        self._cursor["@type"] = "woql:AddTriple"
        return self._updated()

    def update_triple(self, subject, predicate, new_object):
        return self.woql_and(
            WOQLQuery().opt(
                WOQLQuery()
                .triple(subject, predicate, "v:AnyObject")
                .delete_triple(subject, predicate, "v:AnyObject")
                .woql_not()
                .triple(subject, predicate, new_object)
            ),
            WOQLQuery().add_triple(subject, predicate, new_object),
        )

    def delete_quad(self, subject, predicate, object_or_literal, graph=None):
        """Deletes any quads that match the rule [subject, predicate, object, graph]

        Parameters
        ----------
        subject : str
            Subject
        predicate : str
            Predicate
        object_or_literal : str
            Object or Literal
        graph : str
            Graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Adds quads according to the pattern [subject, predicate, object, graph]

        Parameters
        ----------
        subject : str
            Subject
        predicate : str
            Predicate
        object_or_literal : str
            Object or Literal
        graph : str
            Graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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

    def update_quad(self, subject, predicate, new_object, graph):
        return self.woql_and(
            WOQLQuery().opt(
                WOQLQuery()
                .quad(subject, predicate, "v:AnyObject", graph)
                .delete_quad(subject, predicate, "v:AnyObject", graph)
                .woql_not()
                .quad(subject, predicate, new_object, graph)
            ),
            WOQLQuery().add_quad(subject, predicate, new_object, graph),
        )

    def when(self, query, consequent=None):
        """When the sub-query in Condition is met, the Update query is executed

        Parameters
        ----------
        query : WOQLQuery object or bool
        consequent : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute

        Notes
        -----
        Functions which take a query as an argument advance the cursor to make the chaining of queries fall
        into the corrent place in the encompassing json
        """
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
        """A trimmed version of untrimmed (with leading and trailing whitespace removed) is copied into trimmed

        Parameters
        ----------
        untrimmed : str
            original string
        trimmed : str
            WOQL varible storing the result string

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if untrimmed and untrimmed == "woql:args":
            return ["woql:untrimmed", "woql:trimmed"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Trim"
        self._cursor["woql:untrimmed"] = self._clean_object(untrimmed)
        self._cursor["woql:trimmed"] = self._clean_object(trimmed)
        return self

    def eval(self, arith, res):
        """Evaluates the Arithmetic Expression Arith and copies the output to variable V

        Parameters
        ----------
        arith : WOQLQuery or dict
            query or JSON-LD representing the query
        res : str
            output variable

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Adds numbers N1...Nn together

        Parameters
        ----------
        args : int or float
            numbers to add together

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Adds numbers N1...Nn together

        Parameters
        ----------
        args : int or float
            numbers to add together

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Multiplies numbers N1...Nn together

        Parameters
        ----------
        args : int or float
            numbers to be multiplied

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Divides numbers N1...Nn by each other left, to right precedence

        Parameters
        ----------
        args : int or float
            numbers to be divided

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Division - integer division - args are divided left to right

        Parameters
        ----------
        args : int or float
            numbers for division

        Returns
        -------
        WOQLQuery
            query object that can be chained and/or execute
        """
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
        """Raises A to the power of B

        Parameters
        ----------
        first : int or float
            base number
        second : int or float
            power of

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if first and first == "woql:args":
            return ["woql:first", "woql:second"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Exp"
        self._cursor["woql:first"] = self._arop(first)
        self._cursor["woql:second"] = self._arop(second)
        return self

    def floor(self, user_input):
        """The floor function of a real number x denotes the greatest integer less than or equal to x.

        Parameters
        ----------
        user_input : int or float
            number whose floor needs to be calculated

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if user_input and user_input == "woql:args":
            return ["woql:argument"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Floor"
        self._cursor["woql:argument"] = self._arop(user_input)
        return self

    def isa(self, element, of_type):
        """Matches if element is a member of a certain type, according to the current state of the DB

        Parameters
        ----------
        element : str
            element to be checked
        of_type : str
            type to be checked

        Returns
        -------
        bool
        """
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
        """Compares the value of v1 against v2 and returns true if v1 is less than v2

        Parameters
        ----------
        left : str
            first variable to compare
        right : str
            second variable to compare

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Less"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def greater(self, left, right):
        """Compares the value of v1 against v2 and returns true if v1 is greater than v2

        Parameters
        ----------
        left : str
            first variable to compare
        right : str
            second variable to compare

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Greater"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def opt(self, query=None):
        """The Query in the Optional argument is specified as optional

        Parameters
        ----------
        query : WOQLQuery object

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute

        Examples
        -------
        >>> WOQLQuery().woql_and(WOQLQuery().
        ... triple('v:MandatorySubject','v:MandatoryObject', 'v:MandatoryValue'),
        ... WOQLQuery.opt(WOQLQuery().triple('v:OptionalS', 'v:OptionalObject',
        ... 'v:OptionalValue'))
        ... )
        """
        if query and query == "woql:args":
            return ["woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Optional"
        self._add_sub_query(query)
        return self

    def unique(self, prefix, key_list, uri):
        """Generates an ID for a node as a function of the passed VariableList with a specific prefix (URL base). If the values of the passed variables are the same, the output will be the same

        Parameters
        ----------
        prefix : str
            prefix for the id
        key_list : str
            variable to generate id for
        uri : str
            the variable to hold the id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Generates an ID for a node as a function of the passed VariableList with a specific prefix (URL base). If the values of the passed variables are the same, the output will be the same

        Parameters
        ----------
        prefix : str
            prefix for the id
        input_var_list : str or list
            variable to generate id for
        output_var : str
            the variable to hold the id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if prefix and prefix == "woql:args":
            return ["woql:base", "woql:key_list", "woql:uri"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:IDGenerator"
        self._cursor["woql:base"] = self._clean_object(self.iri(prefix))
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
        """Changes a string to lower-case - input is in u, output in l

        Parameters
        ----------
        left : str
            input string
        right : str
            stores output

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if left and left == "woql:args":
            return ["woql:left", "woql:right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Lower"
        self._cursor["woql:left"] = self._clean_object(left)
        self._cursor["woql:right"] = self._clean_object(right)
        return self

    def pad(self, user_input, pad, length, output):
        """
        Pads out the string input to be exactly len long by appending the pad character pad to form output

        Parameters
        ----------
        user_input : str
            input string
        pad : str
            padding character(s)
        length :  int
            length to pad
        output : str
            stores output

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Splits a variable apart (input) into a list of variables (output) by separating the strings together with separator

        Parameters
        ----------
        user_input : str
            input string or WOQL variable "v:"
        glue : str
            character string to separate string into list
        output : str
            WOQL variable that stores output list

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Iterates through a list and returns a value for each member

        Parameters
        ----------
        member : str
            a WOQL variable representing an element of the list
        mem_list : str
            a WOQL list variable

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if member and member == "woql:args":
            return ["woql:member", "woql:member_list"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Member"
        self._cursor["woql:member"] = self._clean_object(member)
        self._cursor["woql:member_list"] = self._wlist(mem_list)
        return self

    def concat(self, concat_list, result):
        """Concatenates the list of variables into a string and saves the result in v

        Parameters
        ----------
        concat_list : list
            list of variables to concatenate
        result : str
            saves the results

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if concat_list and concat_list == "woql:args":
            return ["woql:concat_list", "woql:concatenated"]
        if type(concat_list) is str:
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
        if type(concat_list) is list:
            if self._cursor.get("@type"):
                self._wrap_cursor_with_and()
            self._cursor["@type"] = "woql:Concatenate"
            self._cursor["woql:concat_list"] = self._wlist(concat_list)
            self._cursor["woql:concatenated"] = self._clean_object(result)
        return self

    def join(self, user_input, glue, output):
        """
        Joins a list variable together (input) into a string variable (output) by glueing the strings together with glue

        Parameters
        ----------
        user_input : list
            a list of variables
        glue :  str
            jioining character(s)
        output : str
            variable that sotres output

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """
        Joins a list variable containing numbers together (input) into a single number
        containing the sum.

        Parameters
        ----------
        user_input : list
            a variable containing a list of numbers
        output : str
            a variable that stores the output

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if user_input and user_input == "woql:args":
            return ["woql:sum_list", "woql:sum"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Sum"
        self._cursor["woql:sum_list"] = self._wlist(user_input)
        self._cursor["woql:sum"] = self._clean_object(output)
        return self

    def start(self, start, query=None):
        """Specifies that the start of the query returned

        Parameters
        ----------
        start : int
            index of the frist result got returned
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if start and start == "woql:args":
            return ["woql:start", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Start"
        self._cursor["woql:start"] = self._clean_object(start, "xsd:nonNegativeInteger")
        return self._add_sub_query(query)

    def limit(self, limit, query=None):
        """Specifies that only the first Number of rows will be returned

        Parameters
        ----------
        limit : int
            number of maximum results returned
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if limit and limit == "woql:args":
            return ["woql:limit", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Limit"
        self._cursor["woql:limit"] = self._clean_object(limit, "xsd:nonNegativeInteger")
        return self._add_sub_query(query)

    def re(self, pattern, reg_str, reg_list):
        """Regular Expression Call
        p is a regex pattern (.*) using normal regular expression syntax, the only unusual thing is that special characters have to be escaped twice, s is the string to be matched and m is a list of matches:
        e.g. WOQL.re("(.).*", "hello", ["v:All", "v:Sub"])

        Parameters
        ----------
        pattern : str
            regex pattern
        reg_str : str
            string to be matched
        reg_list : str or list or dict
            store list of matches

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        if type(var_len) is float:
            self._cursor["woql:length"] = self._clean_object(
                var_len, "xsd:nonNegativeInteger"
            )
        elif type(var_len) is str:
            self._cursor["woql:length"] = self._varj(var_len)
        return self

    def woql_not(self, query=None):
        """Creates a logical NOT of the arguments

        Parameters
        ----------
        query : WOQLQuery object, optional

        Returns
        ----------
        WOQLQuery object
            query object that can be chained and/or executed
        """
        if query and query == "woql:args":
            return ["woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Not"
        return self._add_sub_query(query)

    def immediately(self, query=None):
        """Immediately runs side-effects without backtracking

        Parameters
        ----------
        query : WOQLQuery object, optional

        Returns
        ----------
        WOQLQuery object
            query object that can be chained and/or executed
        """
        if query and query == "woql:args":
            return ["woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Immediately"
        return self._add_sub_query(query)

    def count(self, countvar, query=None):
        """Counds the number of solutions in the given query

        Parameters
        ----------
        result : A variable or non-negative integer with the count
        query : The query from which to count the number of results

        Returns
        ----------
        WOQLQuery object
           query object that can be chained and/or executed
        """
        if countvar and countvar == "woql:args":
            return ["woql:count", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Count"
        self._cursor["woql:count"] = self._clean_object(countvar)
        return self._add_sub_query(query)

    def cast(self, val, user_type, result):
        """Changes the type of va to type and saves the return in vb

        Parameters
        ----------
        val : str
            original variable
        user_type : str
            type to be changed
        rsult: str
            save the return variable

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if val and val == "woql:args":
            return ["woql:typecast_value", "woql:typecast_type", "woql:typecast_result"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Typecast"
        self._cursor["woql:typecast_value"] = self._clean_object(val)
        self._cursor["woql:typecast_type"] = self._clean_object(user_type)
        self._cursor["woql:typecast_result"] = self._clean_object(result)
        return self

    def type_of(self, value, vtype):
        if value and value == "woql:args":
            return ["woql:value", "woql:type"]
        if not value or not vtype:
            return self._parameter_error("type_of takes two parameters, both values")
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:TypeOf"
        self._cursor["woql:value"] = self._clean_object(value)
        self._cursor["woql:type"] = self._clean_object(vtype)
        return self

    def order_by(self, *args, order="asc"):
        """
        Orders the results by the list of variables including in gvarlist, asc_or_desc is a WOQL.asc or WOQ.desc list of variables

        Parameters
        ----------
        gvarlist : list or dict of WOQLQuery().asc or WOQLQuery().desc objects
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute

        Examples
        -------
        Examples of 3 different usage patterns of order argument
            >>> test1 = WOQLQuery().select("v:Time").using("_commits").woql_and(
            ...        WOQLQuery().order_by("v:Time", order="asc").triple("v:A", "ref:commit_timestamp", "v:Time")
            ... )
            >>> test2 = WOQLQuery().select("v:Time", "v:Message").using("_commits").woql_and(
            ...     WOQLQuery().order_by("v:Time", "v:Message", order={"v:Time": "desc", "v:Message": "asc"}).woql_and(
            ...         WOQLQuery().triple("v:A", "ref:commit_timestamp", "v:Time"),
            ...         WOQLQuery().triple("v:A", "ref:commit_message", "v:Message")
            ...     )
            ... )
            >>> test3 = WOQLQuery().select("v:Time", "v:Message").using("_commits").woql_and(
            ...     WOQLQuery().order_by("v:Time", "v:Message", order=["desc", "asc"]).woql_and(
            ...         WOQLQuery().triple("v:A", "ref:commit_timestamp", "v:Time"),
            ...         WOQLQuery().triple("v:A", "ref:commit_message", "v:Message")
            ...     )
            ... )
        """

        ordered_varlist = list(args)
        if ordered_varlist and ordered_varlist == "woql:args":
            return ["woql:variable_ordering", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:OrderBy"
        self._cursor["woql:variable_ordering"] = []

        if not ordered_varlist or len(ordered_varlist) == 0:
            return self._parameter_error(
                "Order by must be passed at least one variable to order the query"
            )

        if type(ordered_varlist[-1]) is dict and hasattr(
            ordered_varlist[-1], "to_dict"
        ):
            embedquery = ordered_varlist.pop()
        else:
            embedquery = False
        # if not isinstance(data["parent"], list):
        if isinstance(order, list):
            if len(args) != len(order):
                return self._parameter_error(
                    "Order array must be same length as variable array"
                )

        for idx, item in enumerate(ordered_varlist):
            if type(item) is str:
                obj = {
                    "@type": "woql:VariableOrdering",
                    "woql:index": self._jlt(idx, "xsd:nonNegativeInteger"),
                }
                if isinstance(order, str):
                    iorder = order
                if isinstance(order, list):
                    iorder = order[idx]
                    if iorder is None:
                        iorder = "asc"
                if isinstance(order, dict):
                    iorder = order.get(item)
                    if iorder is None:
                        iorder = "asc"
                if iorder == "desc":
                    obj["woql:ascending"] = self._jlt(False, "xsd:boolean")
                else:
                    obj["woql:ascending"] = self._jlt(True, "xsd:boolean")
                obj["woql:variable"] = self._varj(item)
                self._cursor["woql:variable_ordering"].append(obj)
            else:
                self._cursor["woql:variable_ordering"].append(ordered_varlist[idx])
        return self._add_sub_query(embedquery)

    def group_by(self, gvarlist, groupedvar, output, groupquery=None):
        """
        Groups the results of groupquery together by the list of variables gvarlist, using the variable groupedvar as a grouping and saves the result into variable output.

        Parameters
        ----------
        gvarlist : list or dict or WOQLQuery object
            list of variables to group
        groupedvar : list or str
            grouping template variable(s)
        output : str, optional
            output variable
        groupquery : dict, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if gvarlist and gvarlist == "woql:args":
            return [
                "woql:group_by",
                "woql:group_template",
                "woql:grouped",
                "woql:query",
            ]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:GroupBy"
        self._cursor["woql:group_by"] = []
        if type(gvarlist) is str:
            gvarlist = [gvarlist]
        for idx, item in enumerate(gvarlist):
            onevar = self._varj(item)
            onevar["@type"] = "woql:VariableListElement"
            onevar["woql:index"] = self._jlt(idx, "nonNegativeInteger")
            self._cursor["woql:group_by"].append(onevar)
        if type(groupedvar) is str:
            self._cursor["woql:group_template"] = self._varj(groupedvar)
        else:
            self._cursor["woql:group_template"] = []
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

    def path(self, subject, pattern, obj, path):
        """
        Create a path object constructed by the rules specified with pattern.

        Parameters
        ----------
        subject : str
            a woql subject, the node that the path started
        pattern : str
            a pattern which specified the edges the path is consisted of.
            It uses pattern construction syntax such as:
            * '(scm:edge1, scm:edge2)+' for repeated pattern,
            * 'scm:edge1|scm:edge2' for 'or' pattern,
            * '<scm:edge' for reverse pattern, and
            * '(scm:edge1)[n,m] for pattern between n and m times'
        obj : str
            a woql object, the node that the path ended
        path: str
            output variable

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if subject and subject == "woql:args":
            return ["woql:subject", "woql:path_pattern", "woql:object", "woql:path"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Path"
        self._cursor["woql:subject"] = self._clean_subject(subject)
        if type(pattern) is str:
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
        """
        Selects everything as triples in the graph identified by GraphIRI into variables Subj, Pred, Obj - by default they are "v:Subject", "v:Predicate", "v:Object"

        Parameters
        ----------
        GraphIRI : str
            graphIRI
        Subj : str, optional
            target subject
        Pred : str, optional
            target predicate
        Obj : str, optional
            target object

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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

    def all(self, subj=None, pred=None, obj=None, graph=None):
        return self.star(subj=subj, pred=pred, obj=obj, graph=graph)

    def lib(self):
        # return WOQLLibrary()
        pass

    def abstract(self, graph=None, subj=None):
        """
        Internal Triple-builder functions which allow chaining of partial queries
        """
        return self._add_partial(subj, "terminus:tag", "terminus:abstract", graph)

    def node(self, node, node_type=None):
        """
        Selects nodes with the ID NodeID as the subject of subsequent sub-queries. The second argument PatternType specifies what type of sub-queries are being constructed, options are: triple, quad, update_triple, update_quad, delete_triple, delete_quad

        Parameters
        ----------
        node : str
            node to be selected
        node_type : str
            pattern type, optional (default is triple)

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if node_type == "add_quad":
            node_type = "AddQuad"
        elif node_type == "delete_quad":
            node_type = "DeleteQuad"
        elif node_type == "add_triple":
            node_type = "AddTriple"
        elif node_type == "delete_triple":
            node_type = "DeleteTriple"
        elif node_type == "quad":
            node_type = "Quad"
        elif node_type == "triple":
            node_type = "Triple"
        if ":" not in node_type:
            node_type = "woql:" + node_type
        ctxt = {"subject": node}
        if node_type is not None:
            ctxt["action"] = node_type
        self._set_context(ctxt)
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
            if self._adding_class() is not None:
                part = self._find_last_subject(self._cursor)
                if part:
                    gpart = (
                        part["woql:graph_filter"]
                        if part.get("woql:graph_filter")
                        else part["woql:graph"]
                    )
                else:
                    gpart = None
                if gpart:
                    gpart["@value"]
                nprop = (
                    WOQLQuery()
                    .add_property(pro_id, property_type)
                    .domain(self._adding_class())
                )
                self.woql_and(nprop)
            else:
                self._add_partial(None, pro_id, property_type)
            return self
        else:
            self.property(pro_id, property_type)
            if label:
                self.label(label)
            if description:
                self.description(description)
            return self

    def insert(
        self, insert_id, insert_type, ref_graph=None, label=None, description=None
    ):
        """Inserts a new node of a specified type in a graph

        Parameters
        ----------
        insert_id : str
            ID of the node to be inserted
        insert_type : str
            The rdf type of the node. This should be defined in your schema.
        ref_graph : str, optional
            target graph
        label : str, optional
            label for the insert object
        description : str, optional
            description for the insert object

        Returns
        -------
        WOQLQuery object
            a query object that can be chained and/or execute

        Notes
        --------
        If graph parameter is None then this is a shorthand for calling :meth:`add_triple` with
        rdf:type as predicate: ``.add_triple(subject, 'rdf:type', type).``
        Otherwise :meth:`add_quad` will be called.
        It will yield a json object like follows: ``{'add_triple': ['doc:subject', 'rdf:type', 'scm:type']}``

        Examples
        --------
        >>> update = WOQLQuery().insert("Dog", "scm:Animal").label('Dog')
        >>> qry = WOQLQuery().when(True, update)
        >>> client.update(qry.json(), 'MyDatabaseId')

        See Also
        --------
        add_triple
        add_quad
        """
        if label is None and description is None:
            insert_type = self._clean_type(insert_type, True)
            if ref_graph:
                self.add_quad(insert_id, "type", insert_type, ref_graph)
            else:
                self.add_triple(insert_id, "type", insert_type)
        else:
            self.insert(insert_id, insert_type, ref_graph)
            if label:
                self.label(label)
            if description:
                self.description(description)
        return self

    def insert_data(self, data, ref_graph):
        """Creates a new node of the specified type in a graph, with description and label.

        Parameters
        ----------
        data : dict
            dictionary with id, label, description attributes.
        ref_graph : str
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """Used to specify that the rest of the query should use the graph g in calls to add_quad, quad, etc
        Parameters
        ----------
        g : str
            target graph
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self._set_context({"graph": g})

    def domain(self, d):
        """Specifies the domain of a new property
        Parameters
        ----------
        d : str
            target domain
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        d = self._clean_class(d)
        return self._add_partial(None, "rdfs:domain", d)

    def label(self, lab, lang="en"):
        """Depending on context, either adds a label match to a triple/quad or adds a label create to add_quad, add_triple
        The triple/quad that will get created will be for the rdfs:label predicate.
        Parameters
        ----------
        lan : str
            label to add
        lang : str, optional
            language, default is English "en"
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if lab[:2] == "v:":
            d = lab
        else:
            d = {"@value": lab, "@type": "xsd:string", "@language": lang}
        return self._add_partial(None, "rdfs:label", d)

    def description(self, desc, lang="en"):
        """Adds or matches a rdfs:comment field in a query
        Parameters
        ----------
        c : str
            description to be added
        lang : str, optional
            language, default is English "en"
        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if desc[:2] == "v:":
            d = desc
        else:
            d = {"@value": desc, "@type": "xsd:string", "@language": lang}
        return self._add_partial(None, "rdfs:comment", d)

    def parent(self, *args):
        """Specifies that a new class should have parents listed in *args - (short hand for (a, rdfs:subClassOf b)

        Parameters
        ----------
        args : list
            parent classes

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        for ipl in args:
            pn = self._clean_class(ipl)
            self._add_partial(None, "rdfs:subClassOf", pn)
        return self

    def max(self, m):
        """Sets the maximum cardinality for a property to m

        Parameters
        ----------
        m : int
            maximum cardinality

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self._card(m, "max")
        return self

    def cardinality(self, m):
        """Sets the cardinality of a property to be precisely m

        Parameters
        ----------
        m : int
            cardinality

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self._card(m, "cardinality")
        return self

    def min(self, m):
        """Sets the minimum cardinality for a property to m

        Parameters
        ----------
        m : int
            minimum cardinality

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self._card(m, "min")
        return self

    def _card(self, n, which):
        ctxt = self._triple_builder_context
        s = ctxt.get("subject")
        g = ctxt.get("graph")
        lastsubj = self._find_last_subject(self._cursor)
        if lastsubj is not None and s is None:
            s = lastsubj.get("woql:subject")
        if type(s) is dict:
            s = s.get("woql:node")
        else:
            return
        if lastsubj is not None and g is None:
            gobj = lastsubj.get("woql:graph_filter")
            if gobj is None:
                gobj = lastsubj.get("woql:graph")
            if gobj is not None:
                g = gobj.get("@value")
        newid = s + "_" + which
        self.woql_and(
            WOQLQuery().add_quad(newid, "type", "owl:Restriction", g),
            WOQLQuery().add_quad(newid, "owl:onProperty", s, g),
        )
        if which == "max":
            self.woql_and(
                WOQLQuery().add_quad(
                    newid,
                    "owl:maxCardinality",
                    WOQLQuery().literal(n, "xsd:nonNegativeInteger"),
                    g,
                )
            )
        elif which == "min":
            self.woql_and(
                WOQLQuery().add_quad(
                    newid,
                    "owl:minCardinality",
                    WOQLQuery().literal(n, "xsd:nonNegativeInteger"),
                    g,
                )
            )
        else:
            self.woql_and(
                WOQLQuery().add_quad(
                    newid,
                    "owl:cardinality",
                    WOQLQuery().literal(n, "xsd:nonNegativeInteger"),
                    g,
                )
            )

        od = self._get_object(s, "rdfs:domain")
        if od is not None:
            self.woql_and(WOQLQuery().add_quad(od, "rdfs:subClassOf", newid, g))
        return self

    def _get_object(self, s, p):
        if self._cursor.get("@type") == "woql:And":
            for item in self._cursor["woql:query_list"]:
                subq = item.get("woql:query")
                if self._same_entry(subq.get("woql:subject"), s) and self._same_entry(
                    subq.get("woql:predicate"), p
                ):
                    return subq.get("woql:object")
        return None

    def _same_entry(self, a, b):
        """
        A function to check the given two objects, which can be of different types (str, dict), are equal or not.
        When both the passed objects are dicts, deep comparison is done to check for the equality.

        Parameters
        ----------
        a : str or dict
        b : str or dict

        Returns
        -------
        bool
        """
        if a == b:
            return True
        elif type(a) is dict and type(b) is str:
            return self._string_matches_object(b, a)
        elif type(b) is dict and type(a) is str:
            return self._string_matches_object(a, b)
        elif type(a) is dict and type(b) is dict:
            for k in a:
                if b.get(k) != a.get(k):
                    return False
            for j in b:
                if b.get(j) != a.get(j):
                    return False
            return True

    def _string_matches_object(self, s, obj):
        """
        A function to check if the given string is present in the passed dict or not.

        Parameters
        ----------
        s : str
        obj : dict

        Returns
        -------
        bool
        """
        n = obj.get("woql:node")
        if n is not None:
            return s == n
        v = obj.get("@value")
        if v is not None:
            return s == v
        vn = obj.get("woql:variable_name")
        if vn is not None:
            return s == "v:" + vn
        return False

    def _add_partial(self, s, p, o, g=None):
        ctxt = self._triple_builder_context
        if s is None:
            s = ctxt.get("subject")
        if g is None:
            g = ctxt.get("graph")
        lastsubj = self._find_last_subject(self._cursor)
        if s is None and lastsubj:
            s = lastsubj.get("woql:subject")
        t = ctxt.get("action")
        if t is None:
            t = lastsubj.get("@type")
        if g is None and lastsubj:
            gobj = lastsubj.get("woql:graph_filter")
            if gobj is None:
                gobj = lastsubj.get("woql:graph")
            if gobj is not None:
                g = gobj.get("@value")
        if g is None:
            g = "schema/main"

        if t == "woql:AddTriple":
            self.woql_and(WOQLQuery().add_triple(s, p, o))
        elif t == "woql:DeleteTriple":
            self.woql_and(WOQLQuery().delete_triple(s, p, o))
        elif t == "woql:AddQuad":
            self.woql_and(WOQLQuery().add_quad(s, p, o, g))
        elif t == "woql:DeleteQuad":
            self.woql_and(WOQLQuery().delete_quad(s, p, o, g))
        elif t == "woql:Quad":
            self.woql_and(WOQLQuery().quad(s, p, o, g))
        else:
            self.woql_and(WOQLQuery().triple(s, p, o))
        return self

    def _adding_class(self, string_only=False):
        ac = self._triple_builder_context.get("adding_class")
        if ac and string_only and type(ac) is dict:
            return ac.get("woql:node")
        return ac

    def _set_adding_class(self, c):
        self._triple_builder_context["adding_class"] = c
        return self

    def _set_context(self, ctxt):
        for i in ctxt.keys():
            self._triple_builder_context[i] = ctxt[i]
        return self

    def add_class(self, c, graph=None):
        """Generates a new Class with the given ClassID and writes it to the DB schema

        Parameters
        ----------
        classid : str
            class to be added
        graph : str, optional
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if not graph:
            graph = self._graph
        if c:
            c = self._clean_class(c, True)
            self.add_quad(c, "rdf:type", "owl:Class", graph)
            self._set_adding_class(c)
        return self

    def insert_class_data(self, data, ref_graph):
        """Adds a bunch of class data in one go"""
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

    def insert_doctype_data(self, data, ref_graph):
        if not data.get("parent"):
            data["parent"] = []
        if not isinstance(data["parent"], list):
            data["parent"] = [data["parent"]]
        data["parent"].append("Document")
        return self.insert_class_data(data, ref_graph)

    def insert_property_data(self, data, ref_graph):
        """A function to insert the passed property data

        Parameters
        ----------
        data : str
            class to be deleted
        ref_graph : str
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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

    def delete_class(self, classid, graph=None):
        """Deletes the Class with the passed ID form the schema (and all references to it)

        Parameters
        ----------
        classid : str
            class to be deleted
        graph : str, optional
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if not graph:
            graph = self._graph
        ap = WOQLQuery()
        if classid:
            classid = ap._clean_class(classid, True)
            ap.woql_and(
                WOQLQuery().delete_quad(classid, "v:Outgoing", "v:Value", graph),
                WOQLQuery().opt().delete_quad("v:Other", "v:Incoming", classid, graph),
            )
            ap._updated()
        return ap

    def add_property(self, p, t, graph=None):
        """Generates a new Property with the given PropertyID and a range of type PropType and writes it to the DB schema

        Parameters
        ----------
        p : str
            property id to be added
        t : str
            type of the proerty
        graph : str, optional
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if not graph:
            graph = self._graph
        t = self._clean_type(t, True) if t else "xsd:string"
        if p:
            p = self._clean_path_predicate(p)
            # TODO: cleaning
            if utils.is_data_type(t):
                self.woql_and(
                    WOQLQuery().add_quad(p, "rdf:type", "owl:DatatypeProperty", graph),
                    WOQLQuery().add_quad(p, "rdfs:range", t, graph),
                )
            else:
                self.woql_and(
                    WOQLQuery().add_quad(p, "rdf:type", "owl:ObjectProperty", graph),
                    WOQLQuery().add_quad(p, "rdfs:range", t, graph),
                )
            self._updated()
        return self

    def delete_property(self, p, graph=None):
        """Deletes the property with the passed ID from the schema (and all references to it)

        Parameters
        ----------
        p : str
            property id to be deleted
        graph : str
            target graph ,optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        for i in classes.keys():
            subs.append(WOQLQuery().sub(classes[i], "v:Cid"))
        nsubs = []
        for i in excepts.keys():
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
            WOQLQuery().concat("Box Class generated for class v:Cid", "v:CDesc"),
            WOQLQuery().concat(
                "Box Property generated to link box v:ClassID to class v:Cid", "v:PDesc"
            ),
        )
        if subs:
            if len(subs) == 1:
                woql_filter.woql_and(subs[0])
            else:
                woql_filter.woql_and(WOQLQuery().woql_or(*subs))
        if nsubs:
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
        nq = WOQLQuery().when(woql_filter).woql_and(cls, prop)
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
            if type(choices[i]) is list:
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
        """
        A function to generate a query for all of the xdd datatypes.

        Parameters
        ----------
        graph : str, optional
            Graph

        Returns
        -------
        WOQLQuery object
            a query object that can be chained and/or execute
        """
        if not graph:
            graph = self._graph
        return WOQLQuery().woql_and(
            # geographic datatypes
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
        """
        A utility function for creating a datatype in woql.

        Parameters
        ----------
        d_id : str
            the datatype id
        label : str
            label for the datatype
        descr : str
            description for the datatype
        graph : str, optional
            Graph

        Returns
        -------
        WOQLQuery object
            a query object that can be chained and/or execute
        """
        if not graph:
            graph = self._graph
        dt = WOQLQuery().insert(d_id, "rdfs:Datatype", graph).label(label)
        if descr:
            dt.description(descr)
        return dt

    def _load_xsd_boxes(self, parent, graph, prefix):
        """
        A function to load box classes for all of the useful xsd classes.
        The format is to generate the box classes for xsd:anyGivenType as:
         class(prefix:AnyGivenType) -> property(prefix:anyGivenType) -> datatype(xsd:anyGivenType)

        Parameters
        ----------
        parent : str, optional
            the parent class of the box_class
        graph : str, optional
            Graph
        prefix : str, optional
            prefix for the box_class_id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """ A function to generate a query to create box classes for all of the xdd datatypes.
        The format is to generate the box classes for xdd:anyGivenType as:
         class(prefix:AnyGivenType) -> property(prefix:anyGivenType) -> datatype(xdd:anyGivenType)

        Parameters
        ----------
        parent : str, optional
            the parent class of the box_class
        graph : str, optional
            Graph
        prefix : str, optional
            prefix for the box_class_id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
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
        """A utility function for boxing a datatype in woql.
        The format is (predicate) prefix:datatype (domain) prefix:Datatype (range) xsd:datatype.

        Parameters
        ----------
        datatype : str, optional
            the datatype
        label : str, optional
            label for the data type
        descr : str, optional
            description for the datatype
        parent : str, optional
            the parent class of the box_class
        graph : str, optional
            Graph
        prefix : str, optional
            prefix for the box_class_id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """

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
        """Creates a new document class in the schema - equivalent to: add_quad(type, "rdf:type", "owl:Class", graph), add_quad(type, subclassof, tcs:Document, graph)

        Parameters
        ----------
        user_type : str
            type of the document
        graph : str, optional
            target graph
        label : str, optional
            label for the doctype
        description : str, optional
            description for the doctype

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if label is None and description is None:
            return WOQLQuery().add_class(user_type, graph).parent("Document")

        result_obj = WOQLQuery().doctype(user_type, graph)
        if isinstance(label, str) and label:
            result_obj = result_obj.label(label)
        if isinstance(description, str) and description:
            result_obj = result_obj.description(description)
        return result_obj

    def vars(self, *args):
        """Generate variables to be used in WOQLQueries
        Parameters
        ----------
        args
            string arguments
        Returns
        -------
        tuple/string
            args prefixed with "v:"
        """
        vars_tuple = tuple(f"v:{arg}" for arg in args)
        if len(vars_tuple) == 1:
            vars_tuple = vars_tuple[0]
        return vars_tuple
