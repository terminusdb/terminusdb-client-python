import copy
import datetime as dt
import json

# import pprint
import re

import terminusdb_client.woql_utils as utils

from .woql_core import _copy_dict, _tokenize, _tokens_to_json

# pp = pprint.PrettyPrinter(indent=4)

BLOCK_SCOPE = [
    "select",
    "from",
    "start",
    "when",
    "opt",
    "limit",
]
UPDATE_OPERATORS = [
    "AddTriple",
    "DeleteTriple",
    "AddQuad",
    "DeleteQuad",
    "DeleteObject",
    "UpdateObject",
]

SHORT_NAME_MAPPING = {
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
        self._vocab = SHORT_NAME_MAPPING

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

    def __and__(self, other):
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

    def __or__(self, other):
        """Creates a logical OR with the argument passed, for WOQLQueries.

        Parameters
        ----------
        other : WOQLQuery object

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return WOQLQuery().woql_or(self, other)

    # WOQLCore methods
    # def _parameter_error(self, message):
    #     """Basic Error handling"""
    #     raise ValueError(message)

    def _add_sub_query(self, sub_query=None):
        """Internal library function which adds a subquery and sets the cursor"""
        if sub_query:
            self._cursor["query"] = self._coerce_to_dict(sub_query)
        else:
            initial_object = {}
            self._cursor["query"] = initial_object
            self._cursor = initial_object
        return self

    def _contains_update_check(self, json=None):
        """Does this query contain an update"""
        if not json:
            json = self._query
        if not isinstance(json, dict):
            return False
        if json["@type"] in self._update_operators:
            return True
        if json.get("consequent") and self._contains_update_check(
            json["consequent"]
        ):
            return True
        if json.get("query"):
            return self._contains_update_check(json["query"])
        if json.get("and"):
            for item in json["and"]:
                if self._contains_update_check(item):
                    return True
        if json.get("or"):
            for item in json["or"]:
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
                "@type": "Value",
                "variable_name": varb
            }
        return varb

    def _coerce_to_dict(self, qobj):
        """Transforms a object representation of a query into a dictionary object if needs be"""
        if hasattr(qobj, "to_dict"):
            return qobj.to_dict()
        if qobj is True:
            return {"@type": "True"}
        return qobj

    def _raw_var(varb):
        if varb[:2] == "v:":
            return varb[2:]
        return varb

    def _raw_var_list(vl):
        ret = []
        for v in vl:
            ret.append(self._raw_var(v))
        return ret

    def _data_list(self, wvar):
        # TODO: orig is Nonetype
        """takes input that can be either a string (variable name)
        or an array - each element of the array is a member of the list"""
        if type(wvar) is str:
            return self._expand_data_variable(wvar, True)
        if type(wvar) is list:
            ret = []
            for item in wvar:
                co_item = self._clean_data_value(item)
                ret.append(co_item)
            return ret

    def _asv(self, colname_or_index, vname, obj_type=None):
        """Wraps the elements of an AS variable in the appropriate json-ld"""
        asvar = {}
        if type(colname_or_index) is int:
            asvar["@type"] = "Column"
            asvar["indicator"] = {"@type" : "Indicator", "index" : column_or_index}
        elif type(colname_or_index) is str:
            asvar["@type"] = "Column"
            asvar["indicator"] = {"@type" : "Indicator", "name" : column_or_index}
        if vname[:2] == "v:":
            vname = vname[2:]
        asvar["variable"] = vname
        if obj_type:
            asvar["type"] = obj_type
        return asvar

    def _wfrom(self, opts):
        """JSON LD Format Descriptor"""
        if opts and opts.get("format"):
            self._cursor["format"] = {
                "@type": "Format",
                "format_type": {"@value": opts["format"], "@type": "xsd:string"},
            }
            if opts.get("format_header"):
                self._cursor["format"]["format_header"] = {
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
        vl = []
        for item in target_list:
            v = self._expand_value_variable(item)
            vl.append(v)
        return vl

    def _data_value_list(self, target_list):
        dvl = []
        for item in target_list:
            o = self.clean_data_value(item)
            dvl.append(o)
        return dvl

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
        raise ValueError("Subject must be a URI string")

    def _clean_predicate(self, predicate):
        """Transforms whatever is passed in as the predicate (id or variable) into the appropriate json-ld form """
        pred = False
        if type(predicate) is dict:
            return predicate
        if type(predicate) != str:
            raise ValueError("Predicate must be a URI string")
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
        obj = {"@type": "Value"}
        if type(user_obj) is str:
            if user_obj[:2] == "v:":
                return self.expand_value_variable(o)
            else:
                obj["node"] = user_obj
        elif type(user_obj) is float:
            if not target:
                target = "xsd:decimal"
            obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is int:
            if not target:
                target = "xsd:integer"
            obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is bool:
            if not target:
                target = "xsd:boolean"
            obj["data"] = self._jlt(user_obj, target)
        elif isinstance(user_obj, dt.date):
            if not target:
                target = "xsd:dateTime"
            obj["data"] = self._jlt(user_obj.isoformat(), target)
        elif type(user_obj) is dict:
            if "@value" in user_obj:
                obj["data"] = user_obj
            else:
                return user_obj
        else:
            obj["data"] = self._jlt(str(user_obj))
        return obj

    def _clean_data_value(self, user_obj, target=None):
        """Transforms whatever is passed in as the object of a triple into the appropriate json-ld form (variable, literal or id)"""
        obj = {"@type": "DataValue"}
        if type(user_obj) is str:
            if user_obj[:2] == "v:":
                return self.expand_data_variable(o)
            else:
                obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is float:
            if not target:
                target = "xsd:decimal"
            obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is int:
            if not target:
                target = "xsd:integer"
            obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is bool:
            if not target:
                target = "xsd:boolean"
            obj["data"] = self._jlt(user_obj, target)
        elif isinstance(user_obj, dt.date):
            if not target:
                target = "xsd:dateTime"
            obj["data"] = self._jlt(user_obj.isoformat(), target)
        elif type(user_obj) is dict:
            if "@value" in user_obj:
                obj["data"] = user_obj
            else:
                return user_obj
        else:
            obj["data"] = self._jlt(str(user_obj))
        return obj

    def _clean_arithmetic_value(self, user_obj, target=None):
        """Transforms whatever is passed in as the object of a triple into the appropriate json-ld form (variable, literal or id)"""
        obj = {"@type": "ArithmeticValue"}
        if type(user_obj) is str:
            if user_obj[:2] == "v:":
                return self.expand_data_variable(o)
            else:
                obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is float:
            if not target:
                target = "xsd:decimal"
            obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is int:
            if not target:
                target = "xsd:integer"
            obj["data"] = self._jlt(user_obj, target)
        elif type(user_obj) is bool:
            if not target:
                target = "xsd:boolean"
            obj["data"] = self._jlt(user_obj, target)
        elif isinstance(user_obj, dt.date):
            if not target:
                target = "xsd:dateTime"
            obj["data"] = self._jlt(user_obj.isoformat(), target)
        elif type(user_obj) is dict:
            if "@value" in user_obj:
                obj["data"] = user_obj
            else:
                return user_obj
        else:
            obj["data"] = self._jlt(str(user_obj))
        return obj

    def _clean_node_value(self, user_obj, target=None):
        """Transforms whatever is passed in as the object of a triple into the appropriate json-ld form (variable, literal or id)"""
        obj = {"@type": "NodeValue"}
        if type(user_obj) is str:
            if user_obj[:2] == "v:":
                return self.expand_node_variable(o)
            else:
                obj["node"] = user_obj
        elif type(user_obj) is dict:
            return user_obj
        else:
            obj["node"] = user_obj
        return obj

    def _clean_graph(self, graph):
        """Transforms a graph filter by doing nothing"""
        return graph

    def _expand_variable(self, varname, target_type, always=False):
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
                "@type": target_type,
                "variable": varname
            }
        else:
            return {"@type": target_type, "node": varname}

    def _expand_value_variable(self,varname,always=False):
        return self._expand_variable(varname,'Value',always)

    def _expand_node_variable(self,varname,always=False):
        return self._expand_variable(varname,'NodeValue',always)

    def _expand_data_variable(self,varname,always=False):
        return self._expand_variable(varname,'DataValue',always)

    def _expand_arithmetic_variable(self,varname,always=False):
        return self._expand_variable(varname,'ArithmeticValue',always)

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
        """Finds the last woql element that has a subject in it and returns the json for that
        used for triplebuilder to chain further calls - when they may be inside ands or ors or subqueries

        Parameters
        ----------
        json : dict
               dictionary that representing the query in josn-ld"""
        if "and" in json:
            for item in json["and"][::-1]:
                subitem = self._find_last_subject(item)
                if subitem:
                    return subitem
        if "or" in json:
            for item in json["or"][::-1]:
                subitem = self._find_last_subject(item)
                if subitem:
                    return subitem

        if "query" in json:
            item = self._find_last_subject(json["query"])
            if item:
                return item
        if "subject" in json:
            return json
        return False

    def _find_last_property(self, json):
        """Finds the last woql property that has a subject in it and returns the json for that
        used for triplebuilder to chain further calls - when they may be inside ands or ors or subqueries

        Parameters
        ----------
        json : dict
               dictionary that representing the query in josn-ld"""
        if "and" in json:
            for item in json["and"][::-1]:
                subitem = self._find_last_property(item)
                if subitem:
                    return subitem
        if "or" in json:
            for item in json["or"][::-1]:
                subitem = self._find_last_property(item)
                if subitem:
                    return subitem

        if "query" in json:
            item = self._find_last_property(json["query"])
            if item:
                return item
        if "subject" in json and self._is_property_triple(
            json.get("predicate"), json.get("object")
        ):
            return json
        return False

    def _is_property_triple(self, pred, obj):
        if isinstance(pred, dict):
            p = pred.get("node")
        else:
            p = pred
        if isinstance(obj, dict):
            o = obj.get("node")
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
            raise ValueError("Pattern error - could not be parsed " + pat)

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
        if self._cursor.get("@type") == "And" and self._cursor.get(
            "and"
        ):
            next_item = len(self._cursor.get("and"))
            self.woql_and({})
            self._cursor = self._cursor["and"][next_item]
        else:
            new_json = WOQLQuery().from_dict(self._cursor)
            self._cursor.clear()
            self.woql_and(new_json, {})
            self._cursor = self._cursor["and"][1]

    def using(self, collection, subq=None):
        if collection and collection == "args":
            return ["collection", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Using"
        if not collection or type(collection) != str:
            raise ValueError(
                "The first parameter to using must be a Collection ID (string)"
            )
        self._cursor["collection"] = collection
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
        if comment and comment == "args":
            return ["comment", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Comment"
        self._cursor["comment"] = self._jlt(comment)
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
        if queries and queries[0] == "args":
            return ["variables", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Select"
        if queries != [] and not queries:
            raise ValueError("Select must be given a list of variable names")
        if queries == []:
            embedquery = False
        elif hasattr(queries[-1], "to_dict"):
            embedquery = queries.pop()
        else:
            embedquery = False
        self._cursor["variables"] = self.raw_var_list(queries)
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
        if queries and queries[0] == "args":
            return ["variable_list", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Distinct"
        if queries != [] and not queries:
            raise ValueError("Distinct must be given a list of variable names")
        if queries == []:
            embedquery = False
        elif hasattr(queries[-1], "to_dict"):
            embedquery = queries.pop()
        else:
            embedquery = False
        self._cursor["variable_list"] = self.raw_var_list(queries)
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
        if self._cursor.get("@type") and self._cursor["@type"] != "And":
            new_json = WOQLQuery().from_dict(self._cursor)
            self._cursor.clear()
            queries = [new_json] + queries
        if queries and queries[0] == "args":
            return ["query_list"]
        self._cursor["@type"] = "And"
        if "query_list" not in self._cursor:
            self._cursor["query_list"] = []
        for item in queries:
            index = len(self._cursor["and"])
            onevar = self._coerce_to_dict(item)
            if (
                onevar["@type"] == "And"
                and onevar['and']
            ):
                for each in onevar["and"]:
                    if each:
                        subvar = self._corce_to_dict(each)
                        self._cursor["and"].append(subvar)
            else:
                self._cursor["and"].append(onevar)
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
        if queries and queries[0] == "args":
            return ["or"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Or"
        if "or" not in self._cursor:
            self._cursor["or"] = []
        for item in queries:
            onevar = self._corce_to_dict(item)
            self._cursor["or"].append(onevar)
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
        if graph_filter and graph_filter == "args":
            return ["graph_filter", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "From"
        if not graph_filter or type(graph_filter) != str:
            raise ValueError(
                "The first parameter to from must be a Graph Filter Expression (string)"
            )
        self._cursor["graph_filter"] = graph_filter
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
        if graph_descriptor and graph_descriptor == "args":
            return ["graph", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Into"
        if not graph_descriptor or type(graph_descriptor) != str:
            raise ValueError(
                "The first parameter to from must be a Graph Filter Expression (string)"
            )
        self._cursor["graph"] = graph_descriptor
        return self._add_sub_query(query)

    def triple(self, sub, pred, obj, opt=False):
        """Creates a triple pattern matching rule for the triple [S, P, O] (Subject, Predicate, Object)

        Parameters
        ----------
        sub : str
            Subject, has to be a node (URI)
        pred : str
            Predicate, can be variable (prefix with "v:") or node
        obj : str
            Object, can be variable or node or value
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
        self._cursor["@type"] = "Triple"
        self._cursor["subject"] = self._clean_subject(sub)
        self._cursor["predicate"] = self._clean_predicate(pred)
        self._cursor["object"] = self._clean_object(obj)
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
        self._cursor["@type"] = "AddedTriple"
        self._cursor["subject"] = self._clean_subject(sub)
        self._cursor["predicate"] = self._clean_predicate(pred)
        self._cursor["object"] = self._clean_object(obj)
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
        self._cursor["@type"] = "RemovedTriple"
        self._cursor["subject"] = self._clean_subject(sub)
        self._cursor["predicate"] = self._clean_predicate(pred)
        self._cursor["object"] = self._clean_object(obj)
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
        if sub and sub == "args":
            return arguments.append("graph_filter")
        if not graph:
            raise ValueError(
                "Quad takes four parameters, the last should be a graph filter"
            )
        self._cursor["@type"] = "Triple"
        self._cursor["graph_filter"] = self._clean_graph(graph)
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
        if sub and sub == "args":
            return arguments.append("graph_filter")
        if not graph:
            raise ValueError(
                "Quad takes four parameters, the last should be a graph filter"
            )
        self._cursor["@type"] = "AddedTriple"
        self._cursor["graph_filter"] = self._clean_graph(graph)
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
        if sub and sub == "args":
            return arguments.append("graph_filter")
        if not graph:
            raise ValueError(
                "Quad takes four parameters, the last should be a graph filter"
            )
        self._cursor["@type"] = "DeletedTriple"
        self._cursor["graph_filter"] = self._clean_graph(graph)
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
            "@type": "NodeValue",
            "node": varname,
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
        if parent and parent == "args":
            return ["parent", "child"]
        if parent is None or child is None:
            raise ValueError("Subsumption takes two parameters, both URIs")
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Subsumption"
        self._cursor["parent"] = self._clean_node_value(parent)
        self._cursor["child"] = self._clean_node_value(child)
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
        if left and left == "args":
            return ["left", "right"]
        if left is None or right is None:
            raise ValueError("Equals takes two parameters")
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Equals"
        self._cursor["left"] = self._clean_object(left)
        self._cursor["right"] = self._clean_object(right)
        return self

    def substr(self, string, length, substring, before=0, after=0):
        if string and string == "args":
            return [
                "string",
                "before",
                "length",
                "after",
                "substring",
            ]
        if not substring:
            substring = length
            length = len(substring) + before
        if not string or not substring or type(substring) != type:
            raise ValueError(
                "Substr - the first and last parameters must be strings representing the full and substring variables / literals"
            )
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Substring"
        self._cursor["string"] = self._clean_data_value(string, "xsd:string")
        self._cursor["before"] = self._clean_data_value(
            before, "xsd:nonNegativeInteger"
        )
        self._cursor["length"] = self._clean_data_value(
            length, "xsd:nonNegativeInteger"
        )
        self._cursor["after"] = self._clean_data_value(after, "xsd:nonNegativeInteger")
        self._cursor["substring"] = self._clean_datat_value(substring, "xsd:string")
        return self

    def update_object(self, docjson):
        if docjson and docjson == "args":
            return ["document"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "UpdateObject"
        if isinstance(input_obj, str):
            doc = self.expand_value(input_obj)
        else:
            doc = input_obj
        self._cursor["document"] = doc
        return self._updated()

    def delete_object(self, json_or_iri):
        if json_or_iri and json_or_iri == "args":
            return ["document"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "DeleteObject"
        self._cursor["document_uri"] = this.clean_node_value(json_or_iri)
        return self._updated()

    def read_object(self, iri, output_var):
        if iri and iri == "args":
            return ["document"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "ReadObject"
        self._cursor["document_uri"] = iri
        self._cursor["document"] = self._expand_variable(output_var)
        return self

    def get(self, as_vars, query_resource=None):
        """Takes an as structure"""
        if as_vars and as_vars == "args":
            return ["columns", "resource"]
        self._cursor["@type"] = "Get"
        if hasattr(as_vars, "to_dict"):
            self._cursor["columns"] = as_vars.to_dict()
        else:
            self._cursor["columns"] = WOQLQuery().woql_as(*as_vars).to_dict()
        if query_resource:
            self._cursor["resource"] = self._coerce_to_dict(query_resource)
        else:
            self._cursor["resource"] = {}
        self._cursor = self._cursor["resource"]
        return self

    def put(self, as_vars, query, query_resource=None):
        """Takes an array of variables, an optional array of column names"""
        if as_vars and as_vars == "args":
            return ["columns", "query", "resource"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Put"
        if hasattr(as_vars, "to_dict"):
            self._cursor["columns"] = as_vars.to_dict()
        else:
            self._cursor["columns"] = WOQLQuery().woql_as(*as_vars).to_dict()
        self._cursor["query"] = self._coerce_to_dict(query)
        if query_resource:
            self._cursor["resource"] = self._coerce_to_dict(query_resource)
        else:
            self._cursor["resource"] = {}
        return self

    def woql_as(self, *args):
        if args and args[0] == "args":
            return [["indexed_as_var", "named_as_var"]]
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
        if fpath and fpath == "args":
            return ["source", "format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "QueryResource"
        fpath['@type'] = 'Source'
        self._cursor["source"] = fpath
        self._cursor["format"] = "csv"
        if opts:
            self._cursor["options"] = opts
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
        if query and query == "args":
            return ["query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Once"
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
        if uri and uri == "args":
            return ["remote_uri", "format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "QueryResource"
        uri['@type'] = 'Source'
        self._cursor['source'] = uri
        self._cursor['format'] = "csv"
        if opts:
            self._cursor['options'] = opts
        return self

    def post(self, fpath, opts=None):
        if fpath and fpath == "args":
            return ["file", "format"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "QueryResource"
        fpath['@type'] = 'Source'
        self._cursor['source'] = fpath
        self._cursor['format'] = "csv"
        if opts:
            self._cursor['options'] = opts
        return self

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
        if subject and subject == "args":
            return triple_args
        self._cursor["@type"] = "DeleteTriple"
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
        if subject and subject == "args":
            return triple_args
        self._cursor["@type"] = "AddTriple"
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
        if subject and subject == "args":
            return triple_args.append("graph")
        if not graph:
            raise ValueError(
                "Delete Quad takes four parameters, the last should be a graph id"
            )
        self._cursor["@type"] = "DeleteTriple"
        self._cursor["graph"] = self._clean_graph(graph)
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
        if subject and subject == "args":
            return triple_args.concat(["graph"])
        if not graph:
            raise ValueError(
                "Delete Quad takes four parameters, the last should be a graph id"
            )
        self._cursor["@type"] = "AddTriple"
        self._cursor["graph"] = self._clean_graph(graph)
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
        if untrimmed and untrimmed == "args":
            return ["untrimmed", "trimmed"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Trim"
        self._cursor["untrimmed"] = self._clean_data_value(untrimmed)
        self._cursor["trimmed"] = self._clean_data_value(trimmed)
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
        if arith and arith == "args":
            return ["expression", "result"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Eval"
        if hasattr(arith, "to_dict"):
            self._cursor["expression"] = arith.to_dict()
        else:
            self._cursor["expression"] = arith
        self._cursor["result"] = self._clean_arithmetic_value(res)
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
        if new_args and new_args[0] == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Plus"
        self._cursor["left"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor = self._coerce_to_dict(WOQLQuery().plus(*new_args))
        else:
            self._cursor["right"] = self._arop(new_args[0])
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
        if new_args and new_args[0] == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Minus"
        self._cursor["left"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["right"] = self._coerce_to_dict(
                WOQLQuery().minus(*new_args)
            )
        else:
            self._cursor["right"] = self._arop(new_args[0])
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
        if new_args and new_args[0] == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Times"
        self._cursor["left"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["right"] = self._coerce_to_dict(
                WOQLQuery().times(*new_args)
            )
        else:
            self._cursor["right"] = self._arop(new_args[0])
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
        if new_args and new_args[0] == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Divide"
        self._cursor["left"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["right"] = self._coerce_to_dict(
                WOQLQuery().divide(*new_args)
            )
        else:
            self._cursor["right"] = self._arop(new_args[0])
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
        if new_args and new_args[0] == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Div"
        self._cursor["left"] = self._arop(new_args.pop(0))
        if len(new_args) > 1:
            self._cursor["right"] = self._coerce_to_dict(
                WOQLQuery().div(*new_args)
            )
        else:
            self._cursor["right"] = self._arop(new_args[0])
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
        if first and first == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Exp"
        self._cursor["left"] = self._arop(first)
        self._cursor["right"] = self._arop(second)
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
        if user_input and user_input == "args":
            return ["argument"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Floor"
        self._cursor["argument"] = self._arop(user_input)
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
        if element and element == "args":
            return ["element", "of_type"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "IsA"
        self._cursor["element"] = self._clean_node_value(element)
        self._cursor["of_type"] = self._clean_node_value(of_type)
        return self

    def like(self, left, right, dist):
        if left and left == "args":
            return ["left", "right", "like_similarity"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Like"
        self._cursor["left"] = self._clean_data_value(left, 'xsd:string')
        self._cursor["right"] = self._clean_data_value(right, 'xsd:string')
        if dist:
            self._cursor["like_similarity"] = self._clean_object(
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
        if left and left == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Less"
        self._cursor["left"] = self._clean_object(left)
        self._cursor["right"] = self._clean_object(right)
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
        if left and left == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Greater"
        self._cursor["left"] = self._clean_object(left)
        self._cursor["right"] = self._clean_object(right)
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
        if query and query == "args":
            return ["query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Optional"
        self._add_sub_query(query)
        return self

    def unique(self, prefix, key_list, uri):
        """Generates an ID for a node as a function of the passed VariableList with a specific prefix (URL base)(A.K.A Hashing) If the values of the passed variables are the same, the output will be the same

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

        Examples
        -------
        >>> WOQLQuery().unique("https://base.url",["page","1"],"v:obj_id").execute(client)
        {'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': ['obj_id'], 'bindings': [{'obj_id': 'https://base.urlacd150a6885f609532931d89844070b1'}], 'deletes': 0, 'inserts': 0, 'transaction_retry_count': 0}
        """
        if prefix and prefix == "args":
            return ["base", "key_list", "uri"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Unique"
        self._cursor["base"] = self._clean_object(prefix)
        self._cursor["key_list"] = self._data_list(key_list)
        self._cursor["uri"] = self._clean_nod_value(uri)
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

        Examples
        -------
        >>> WOQLQuery().idgen("https://base.url",["page","1"],"v:obj_id").execute(client)
        {'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': ['obj_id'], 'bindings': [{'obj_id': 'https://base.url_page_1'}], 'deletes': 0, 'inserts': 0, 'transaction_retry_count': 0}
        """
        if prefix and prefix == "args":
            return ["base", "key_list", "uri"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "LexicalKey"
        self._cursor["base"] = self._clean_data_value(self.iri(prefix))
        self._cursor["key_list"] = self._clean_object(input_var_list)
        self._cursor["uri"] = self._clean_data_value(output_var)
        return self

    def random_idgen(self, prefix, key_list, uri):
        """Randomly generates an ID and appends to the end of the key_list.

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

        Examples
        -------
        >>> WOQLQuery().random_idgen("https://base.url",["page","1"],"v:obj_id").execute(client)
        {'@type': 'api:WoqlResponse', 'api:status': 'api:success', 'api:variable_names': ['obj_id'], 'bindings': [{'obj_id': 'http://base.url_page_1_rv1mfa59ekisdutnxx6zdt2fkockgah'}], 'deletes': 0, 'inserts': 0, 'transaction_retry_count': 0}
        """
        if prefix and prefix == "args":
            return ["base", "key_list", "uri"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "RandomIDGenerator"
        self._cursor["base"] = self._clean_object(prefix)
        self._cursor["key_list"] = self._vlist(key_list)
        self._cursor["uri"] = self._clean_node_value(uri)
        return self

    def upper(self, left, right):
        if left and left == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Upper"
        self._cursor["left"] = self._clean_object(left)
        self._cursor["right"] = self._clean_object(right)
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
        if left and left == "args":
            return ["left", "right"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Lower"
        self._cursor["left"] = self._clean_object(left)
        self._cursor["right"] = self._clean_object(right)
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
        if user_input and user_input == "args":
            return [
                "pad_string",
                "pad_char",
                "pad_times",
                "pad_result",
            ]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Pad"
        self._cursor["pad_string"] = self._clean_object(user_input)
        self._cursor["pad_char"] = self._clean_object(pad)
        self._cursor["pad_times"] = self._clean_object(length, "xsd:integer")
        self._cursor["pad_result"] = self._clean_object(output)
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
        if user_input and user_input == "args":
            return ["split_string", "split_pattern", "split_list"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Split"
        self._cursor["split_string"] = self._clean_object(user_input)
        self._cursor["split_pattern"] = self._clean_object(glue)
        self._cursor["split_list"] = self._data_list(output)
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
        if member and member == "args":
            return ["member", "member_list"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Member"
        self._cursor["member"] = self._clean_object(member)
        self._cursor["member_list"] = self._data_list(mem_list)
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
        if concat_list and concat_list == "args":
            return ["concat_list", "concatenated"]
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
            self._cursor["@type"] = "Concatenate"
            self._cursor["concat_list"] = self._data_list(concat_list)
            self._cursor["concatenated"] = self._clean_object(result)
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
        if user_input and user_input == "args":
            return ["join_list", "join_separator", "join"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Join"
        self._cursor["join_list"] = self._data_list(user_input)
        self._cursor["join_separator"] = self._clean_object(glue)
        self._cursor["join"] = self._clean_object(output)
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
        if user_input and user_input == "args":
            return ["sum_list", "sum"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Sum"
        self._cursor["sum_list"] = self._data_list(user_input)
        self._cursor["sum"] = self._clean_object(output)
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
        if start and start == "args":
            return ["start", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Start"
        self._cursor["start"] = self._clean_object(start, "xsd:nonNegativeInteger")
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
        if limit and limit == "args":
            return ["limit", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Limit"
        self._cursor["limit"] = self._clean_object(limit, "xsd:nonNegativeInteger")
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
        if pattern and pattern == "args":
            return ["pattern", "string", "result"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Regexp"
        self._cursor["pattern"] = self._clean_data_value(pattern, 'xsd:string')
        self._cursor["string"] = self._clean_data_value(reg_str, 'xsd:string')
        self._cursor["result"] = self._data_list(reg_list)
        return self

    def length(self, var_list, var_len):
        if var_list and var_list == "args":
            return ["list", "length"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Length"
        self._cursor["list"] = self._clean_data_list(var_list)
        if type(var_len) is float:
            self._cursor["length"] = self._clean_object(
                var_len, "xsd:nonNegativeInteger"
            )
        elif type(var_len) is str:
            self._cursor["length"] = self._varj(var_len)
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
        if query and query == "args":
            return ["query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Not"
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
        if query and query == "args":
            return ["query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Immediately"
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
        if countvar and countvar == "args":
            return ["count", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Count"
        self._cursor["count"] = self._clean_object(countvar)
        return self._add_sub_query(query)

    def cast(self, val, user_type, result, literal_type=None):
        """Changes the type of va to type and saves the return in vb

        Parameters
        ----------
        val : str
            original variable
        user_type : str
            type to be changed
        result: str
            save the return variable
        literal_type: str, optional
            literal type of`val`, can be used to treat `val` as a literal rather than an object or variable in the WOQL query.
            If literal type is "owl:Thing" or "node", `val` will be treated as object in the graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if literal_type is not None:
            if literal_type == "owl:Thing" or literal_type == "node":
                return self.cast(self.iri(val), user_type, result)
            else:
                return self.cast(self.literal(val, literal_type), user_type, result)
        if val and val == "args":
            return ["typecast_value", "typecast_type", "typecast_result"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Typecast"
        self._cursor["value"] = self._clean_object(val)
        self._cursor["type"] = self._clean_node_value(user_type)
        self._cursor["result"] = self._clean_object(result)
        return self

    def type_of(self, value, vtype):
        if value and value == "args":
            return ["value", "type"]
        if not value or not vtype:
            raise ValueError("type_of takes two parameters, both values")
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "TypeOf"
        self._cursor["value"] = self._clean_object(value)
        self._cursor["type"] = self._clean_node_value(vtype)
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
        if ordered_varlist and ordered_varlist == "args":
            return ["ordering", "query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "OrderBy"
        self._cursor["ordering"] = []

        if not ordered_varlist or len(ordered_varlist) == 0:
            raise ValueError(
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
                raise ValueError("Order array must be same length as variable array")

        for item in ordered_varlist:
            if type(item) is str:
                obj = {
                    "@type": "OrderTemplate",
                    "variable" : self._raw_var(item),
                    "order": "asc"
                }
                self._cursor["ordering"].append(obj)
            else:
                self._cursor["ordering"].append(item)
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
        if gvarlist and gvarlist == "args":
            return [
                "group_by",
                "template",
                "grouped",
                "query",
            ]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "GroupBy"
        if type(gvarlist) is str:
            gvarlist = [gvarlist]
        self._cursor["group_by"] = self._raw_var_list(gvarlist)
        if type(groupedvar) is str:
            groupedvar = [groupedvar]
        self._cursor["template"] = self._raw_var_list(groupedvar)
        self._cursor["grouped"] = self._varj(output)
        return self._add_sub_query(groupquery)

    def true(self):
        self._cursor["@type"] = "True"
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
        if subject and subject == "args":
            return ["subject", "path_pattern", "object", "path"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Path"
        self._cursor["subject"] = self._clean_subject(subject)
        if type(pattern) is str:
            pattern = self._compile_path_pattern(pattern)
        self._cursor["pattern"] = pattern
        self._cursor["object"] = self._clean_object(obj)
        self._cursor["path"] = self._varj(path)
        return self

    def size(self, graph, size):
        if graph and graph == "args":
            return ["resource", "size"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "Size"
        self._cursor["resource"] = self._clean_graph(graph)
        self._cursor["size"] = self._varj(size)
        return self

    def triple_count(self, graph, triple_count):
        if graph and graph == "args":
            return ["resource", "triple_count"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "TripleCount"
        self._cursor["resource"] = self._clean_graph(graph)
        self._cursor["triple_count"] = self._varj(triple_count)
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
            node_type = "" + node_type
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
                        part["graph_filter"]
                        if part.get("graph_filter")
                        else part["graph"]
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
            self._add_partial(None, "rdfs:subClassOf", ipl)
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
            s = lastsubj.get("subject")
        if type(s) is dict:
            s = s.get("node")
        else:
            return
        if lastsubj is not None and g is None:
            gobj = lastsubj.get("graph_filter")
            if gobj is None:
                gobj = lastsubj.get("graph")
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
        if self._cursor.get("@type") == "And":
            for item in self._cursor["query_list"]:
                subq = item.get("query")
                if self._same_entry(subq.get("subject"), s) and self._same_entry(
                    subq.get("predicate"), p
                ):
                    return subq.get("object")
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
        n = obj.get("node")
        if n is not None:
            return s == n
        v = obj.get("@value")
        if v is not None:
            return s == v
        vn = obj.get("variable_name")
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
            s = lastsubj.get("subject")
        t = ctxt.get("action")
        if t is None:
            t = lastsubj.get("@type")
        if g is None and lastsubj:
            gobj = lastsubj.get("graph_filter")
            if gobj is None:
                gobj = lastsubj.get("graph")
            if gobj is not None:
                g = gobj.get("@value")
        if g is None:
            g = "schema/main"

        if t == "AddTriple":
            self.woql_and(WOQLQuery().add_triple(s, p, o))
        elif t == "DeleteTriple":
            self.woql_and(WOQLQuery().delete_triple(s, p, o))
        elif t == "AddQuad":
            self.woql_and(WOQLQuery().add_quad(s, p, o, g))
        elif t == "DeleteQuad":
            self.woql_and(WOQLQuery().delete_quad(s, p, o, g))
        elif t == "Quad":
            self.woql_and(WOQLQuery().quad(s, p, o, g))
        else:
            self.woql_and(WOQLQuery().triple(s, p, o))
        return self

    def _adding_class(self, string_only=False):
        ac = self._triple_builder_context.get("adding_class")
        if ac and string_only and type(ac) is dict:
            return ac.get("node")
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
        t = t if t else "xsd:string"
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
        cls: str,
        clslabel="",
        clsdesc="",
        choices=None,
        graph="schema",
        parent=None,
    ):
        clist = []
        if ":" not in cls:
            listid = "_:" + cls
        else:
            listid = "_:" + cls.split(":")[1]
        lastid = listid
        if not clslabel:
            clslabel = cls
        wq = WOQLQuery().add_class(cls, graph).label(clslabel)
        if clsdesc:
            wq.description(clsdesc)
        if parent:
            wq.parent(parent)
        confs = [wq]
        if choices is None:
            choices = []
        for i, choice in enumerate(choices):
            if not choice:
                continue
            if type(choice) is list:
                chid = choice[0]
                clab = choice[1]
                desc = choice[2] if len(choice) >= 3 else False
            else:
                chid = choice
                clab = utils.label_from_url(chid)
                desc = False
            cq = WOQLQuery().insert(chid, cls, graph).label(clab)
            if desc:
                cq.description(desc)
            confs.append(cq)
            if i < len(choices) - 1:
                nextid = listid + "_" + str(i)
            else:
                nextid = "rdf:nil"
            clist.append(
                WOQLQuery().add_quad(lastid, "rdf:first", WOQLQuery().iri(chid), graph)
            )
            clist.append(
                WOQLQuery().add_quad(lastid, "rdf:rest", WOQLQuery().iri(nextid), graph)
            )
            lastid = nextid
        oneof = WOQLQuery().woql_and(
            WOQLQuery().add_quad(cls, "owl:oneOf", WOQLQuery().iri(listid), graph),
            *clist,
        )
        result = WOQLQuery().woql_and(*confs, oneof)
        if result._cursor.get("@context") is None:
            result._context({"_": "_:"})
        return result

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
        """A function to generate a query to create box classes for all of the xdd datatypes.
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
