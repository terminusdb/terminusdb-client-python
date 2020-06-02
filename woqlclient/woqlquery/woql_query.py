import re

from .woql_core import WOQLCore


class WOQLQuery(WOQLCore):
    def __init__(self, query=None):
        """defines the internal functions of the woql query object - the language API is defined in WOQLQuery

        Parameters
        ----------
        query json-ld query for initialisation"""
        super().__init__(query)

        # alias
        self.subsumption = self.sub
        self.equals = self.eq
        self.substring = self.substr
        self.update = self.update_object
        self.delete - self.delete_object
        self.read = self.read_object
        self.optional = self.opt
        self.idgenerator = self.idgen
        self.concatenate = self.concat
        self.typecast = self.cast

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
        new_json = WOQLQuery().json(self._cursor)
        for item in self._curser:
            del self._cursor[item]
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

    def comment(self, comment, subq):
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
        if type(queries[-1]) not in [bool, str, int, float] and hasattr(
            queries[-1], "json"
        ):
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
            new_json = WOQLQuery().json(self._cursor)
            for key in self._cursor:
                del self._cursor[key]
            queries = [new_json] + queries
        if queries and queries[0] == "woql:args":
            return ["woql:query_list"]
        self._cursor["@type"] = "woql:And"
        if "woql:query_list" not in self._cursor:
            self._cursor["woql:query_list"] = []
        for item in queries:
            index = len(self._cursor["woql:query_list"])
            onevar = self._gle(item, index)
            if (
                onevar["woql:query"]["@type"] == "woql:And"
                and onevar["woql:query"]["woql:query_list"]
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
        if self._cursor.get("@type") and self._cursor["@type"] != "woql:Or":
            new_json = WOQLQuery().json(self._cursor)
            for key in self._cursor:
                del self._cursor[key]
            queries = [new_json] + queries
        self._cursor["@type"] = "woql:Or"
        if "woql:query_list" not in self._cursor:
            self._cursor["woql:query_list"] = []
        for idx, item in enumerate(queries):
            onevar = self._qle(item, idx)
            self._cursor["woql:query_list"].append(onevar)
        return self

    def woql_from(self, graph_filter, query):
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

    def triple(self, sub, pred, obj):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Triple"
        self._cursor["woql:subject"] = self._clean_subject(sub)
        self._cursor["woql:predicate"] = self._clean_predicate(pred)
        self._cursor["woql:object"] = self._clean_object(obj)
        return self

    def quad(self, sub, pred, obj, graph):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        arguments = self.triple(sub, pred, obj)
        if sub and sub == "woql:args":
            return arguments.concat(["woql:graph_filter"])
        if not graph:
            return self._parameter_error(
                "Quad takes four parameters, the last should be a graph filter"
            )
        self._cursor["@type"] = "woql:Quad"
        self._cursor["woql:graph_filter"] = self._clean_graph(graph)
        return self

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
            return self.self._parameter_error("Equals takes two parameters")
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Equals"
        self._cursor["woql:left"] = self._clean_class(left)
        self._cursor["woql:right"] = self._clean_class(right)

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
        return self._wfroms(out_format)

    def get(self, as_vars, query_resource):
        """Takes an as structure"""
        if as_vars and as_vars == "woql:args":
            return ["woql:as_vars", "woql:query_resource"]
        self._cursor["@type"] = "woql:Get"
        if hasattr(as_vars, "json"):
            self._cursor["woql:as_vars"] = as_vars.json()
        else:
            self._cursor["woql:as_vars"] = WOQLQuery().woql_as(*as_vars).json()
        if query_resource:
            self._cursor["woql:query_resource"] = self._jobj(query_resource)
        else:
            self._cursor["woql:query_resource"] = {}
        self._cursor = self._cursor["woql:query_resource"]
        return self

    def put(self, as_vars, query_resource, query):
        """Takes an array of variables, an optional array of column names"""
        if as_vars and as_vars == "woql:args":
            return ["woql:as_vars", "woql:query", "woql:query_resource"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Put"
        if hasattr(as_vars, "json"):
            self._cursor["woql:as_vars"] = as_vars.json()
        else:
            self._cursor["woql:as_vars"] = WOQLQuery().woql_as(*as_vars).json()
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
        elif type(args[0]) in [float, str]:
            if len(args) > 2:
                map_type = args[2]
            else:
                map_type = False
            oasv = self._asv(args[0], args[1], type)
            self._query.append(oasv)
        elif type(args[0]) == dict:
            if hasattr(args[0], "json"):
                self._query.append(args[0].json)
            else:
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

    def remote(self, uri, opts):
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

    def delete_quad(self, subject, predicate, object_or_literal, graph):
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        triple_args = self.triple(subject, predicate, object_or_literal)
        if subject and subject == "woql:args":
            return triple_args.concat(["woql:graph"])
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
        self._clean_graph(graph)
        return self._updated()

    def when(self, query, consequent=None):
        if query and query == "woql:args":
            return ["woql:query", "woql:consequent"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:When"
        self._add_sub_query(query)
        if consequent:
            self._cursor["woql:consequent"] = self._jobj(consequent)
        else:
            self._cursor["woql:consequent"] = {}
        self._cursor = self._cursor["woql:consequent"]
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
        if hasattr(arith, "json"):
            self._cursor["woql:expression"] = arith.json()
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
        if len(new_args > 1):
            self._cursor = self._jobj(WOQLQuery().plus(*args))
        else:
            self._cursor["woql:second"] = self._arop(args[0])
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
            self._cursor["woql:second"] = self._arop(args[0])
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
            self._cursor["woql:second"] = self._arop(args[0])
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
            self._cursor["woql:second"] = self._arop(args[0])
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
            self._cursor["woql:second"] = self._arop(args[0])
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

    def opt(self, query):
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
        self._cursor["woql:base"] = self._clean_object(prefix)
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
                    slist2 = re.split(r"[^\w_]", slist[idx + 1])
                    x_var = slist2.pop(0)
                    nlist.push("v:" + x_var)
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

    def start(self, start, query):
        if start and start == "woql:args":
            return ["woql:start", "woql:query"]
        if self._cursor.get("@type"):
            self._wrap_cursor_with_and()
        self._cursor["@type"] = "woql:Start"
        self._cursor["woql:start"] = self._clean_object(start, "xsd:nonNegativeInteger")
        return self._add_sub_query(query)

    def limit(self, limit, query):
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

    def woql_not(self, query):
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

        if type(ordered_varlist[-1]) == dict and hasattr(ordered_varlist[-1], "json"):
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

    def group_by(self, gvarlist, groupedvar, output, groupquery):
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
