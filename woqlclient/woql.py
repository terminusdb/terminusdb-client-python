"""
  The WOQL Query object implements the WOQL language via the fluent style
"""

import sys
import re
from copy import copy
from .utils import Utils

STANDARD_URLS = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'tcs': 'http://terminusdb.com/schema/tcs#',
    'tbs': 'http://terminusdb.com/schema/tbs#',
    'xdd': 'http://terminusdb.com/schema/xdd#',
    'v': 'http://terminusdb.com/woql/variable/',
    'terminus': 'http://terminusdb.com/schema/terminus#',
    'vio': 'http://terminusdb.com/schema/vio#',
    'docs': 'http://terminusdb.com/schema/documentation#'
}

class WOQLQuery:
    """Creates a new Empty Query object
    """

    def __init__(self,query=None):
        self.query = query if query else {}
        self.cursor = self.query
        self.chain_ended = False
        self.contains_update = False
        # operators which preserve global paging
        self.paging_transitive_properties = ['select', 'from', 'start', 'when', 'opt', 'limit']
        self.vocab = self._load_default_vocabulary()
        # object used to accumulate triples from fragments to support usage like node("x").label("y")
        self.tripleBuilder = False
        self.adding_class = False
        self._clean_class = self._clean_type = self._clean_predicate
        self.relationship = self.entity
        self.cast = self.typecast

    def isLiteralType(self, t):
        if t:
            pref = t.split(":")
            if (pref[0] == "xdd" or pref[0] == "xsd"):
                return True
        return False

    def get(self, arr1, arr2=None, target=None):
        """Imports the Target Resource to the variables defined in Map

        Takes an array of variables, an optional array of column names

        Parameters
        ----------
        arr1 : WQOLQuery object or list
            If WQOLQuery, arr2 will replace the target. If list, its column names of the source csv
        arr2 : list or str
            List, if arr1 is list and it will take the variable names for the input. Str, if arr1 is WQOLQuery, it will be the target
        target : str, target of the source data, optional
            Used only if arr1 and arr2 is list

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if hasattr(arr1, 'json'):
            map = arr1.json()
            target = arr2;
        else:
            map = self._build_as_clauses(arr1, arr2);

        if target:
            if hasattr(target, 'json'):
                target = target.json()
            self.cursor['get'] = [map, target];
        else:
            self.cursor['get'] = [map, {}];
            self.cursor = self.cursor["get"][1];
        return self

    def woql_with(self, gid, remq, subq=None):
        """Reads source into a temporary in-memory graph and runs the query on it.

        Parameters
        ----------
        gid : str
            graph id
        remq : WOQLQuery object
        subq : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if hasattr(remq, 'json'):
            remq = remq.json()
        if subq is not None:
            if hasattr(subq, 'json'):
                subq = subq.json()
            self.cursor['with'] = [gid, remq, subq]
        else:
            self.cursor['with'] = [gid, remq, {}]
            self.cursor = self.cursor["with"][2]

        return self

    def _build_as_clauses(self, vars=None, cols=None):
        clauses = []
        def check_vars_cols(obj):
            return obj and \
                   isinstance(obj, (list, dict, WOQLQuery)) and \
                   len(obj)
        if check_vars_cols(vars):
            for i in range(len(vars)):
                v = vars[i]
                if check_vars_cols(cols):
                    c = cols[i]
                    if type(c) == str:
                        c = {"@value": c}
                    clauses.append({'as': [c, v]})
                else:
                    if hasattr(a, 'as') or ('as' in a):
                        clauses.append(v)
                    else:
                        clauses.append({'as': [v]})
        return clauses

    def typecast(self, va, type, vb):
        """Changes the type of va to type and saves the return in vb

        Parameters
        ----------
        va : str
            original variable
        type : str
            type to be changed
        vb : str
            save the return variable

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['typecast'] = [va, type, vb];
        return self

    def insert(self, node, type, graph=None):
        """Insert a node with a specific type in a graph

        Parameters
        ----------
        node : str
            node to be insert
        type : str
            type of the node
        graph : str, optional
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if graph is not None:
            return WOQLQuery().add_quad(node, "rdf:type", WOQLQuery()._clean_type(type), graph)
        else:
            return WOQLQuery().add_triple(node, "rdf:type", WOQLQuery()._clean_type(type))

    def doctype(self, type, graph=None):
        """Creates a new document class in the schema - equivalent to: add_quad(type, "rdf:type", "owl:Class", graph), add_quad(type, subclassof, tcs:Document, graph)

        Parameters
        ----------
        type : str
            type of the docuemnt
        graph : str, optional
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return WOQLQuery().add_class(type, graph).parent("Document")

    def length(self, va, vb):
        """Calculates the length of the value in va and stores it in vb

        Parameters
        ----------
        va : str
            value to calculate length
        vb : str
            stores result

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['length'] = [va, vb];
        return self

    def remote(self, json, opts=None):
        """Provides details of a remote data source in a JSON format that includes a URL property

        Parameters
        ----------
        json : dict
            remote data source in a JSON format
        opts : imput options, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if opts is not None:
            self.cursor['remote'] = [json, opts]
        self.cursor['remote'] = [json];
        return self

    def file(self, json, opts=None):
        """Provides details of a file source in a JSON format that includes a URL property

        Parameters
        ----------
        json : dict
            remote data source in a JSON format
        opts : imput options, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if opts is not None:
            self.cursor['file'] = [json, opts]
        self.cursor['file'] = [json];
        return self

    # WOQL.group_by = function(gvarlist, groupedvar, groupquery, output){    return new WOQLQuery().group_by(gvarlist, groupedvar, groupquery, output); }

    def group_by(self, gvarlist, groupedvar, groupquery, output=None):
        """
        Groups the results of groupquery together by the list of variables gvarlist, using the variable groupedvar as a grouping and saves the result into variable output.

        Parameters
        ----------
        gvarlist : list or dict or WOQLQuery object
            list of variables to group
        groupedvar : list or str
            grouping variable(s)
        groupquery : WOQLQuery object
        output : str, optional
            output variable

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        args = []
        self.cursor['group_by'] = args
        if hasattr(gvarlist, 'json'):
            args.append(gvarlist.json())

        if 'list' in gvarlist:
            args.append(gvarlist)
        else:
            args.append({'list': gvarlist})

        if type(groupedvar) == list:
            ng = Utils.addNamespacesToVariables(groupedvar)
            groupedvar = {"list": ng}
        elif type(groupedvar) == str:
            groupedvar = Utils.addNamespacesToVariable(groupedvar)

        args.append(groupedvar)

        if output:
            if hasattr(groupquery, 'json'):
                groupquery = groupquery.json()
            args.append(groupquery)
        else:
            output = groupquery
            sq = {}
            self.cursor = sq
            args.append(sq)

        args.append(Utils.addNamespacesToVariable(output))

        return self

    def order_by(self, gvarlist, asc_or_desc=None, query=None):
        """
        Orders the results by the list of variables including in gvarlist, asc_or_desc is a WOQL.asc or WOQ.desc list of variables

        Parameters
        ----------
        gvarlist : list or dict or WOQLQuery object
            list of variables to order
        asc_or_desc : WOQLQuery object
            WOQL.asc or WOQ.desc, optional, default is asc
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        ordering = gvarlist
        if hasattr(gvarlist, 'json'):
            ordering = gvarlist.json()
        if type(ordering) not in [list, dict]:
            ordering = [ordering]
        if type(ordering) == list:
            vars = Utils.addNamespacesToVariables(ordering)
            if asc_or_desc is None:
                asc_or_desc = "asc"
            ordering = {}
            ordering[asc_or_desc] = vars
        self._advance_cursor("order_by", ordering)
        if query is not None:
            self.cursor = query.json() if hasattr(query, 'json') else query
        return self

    def asc(self, varlist_or_var):
        """Orders the list by ascending order

        Parameters
        ----------
        varlist_or_var : list or str
            list of variables to order

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if type(varlist_or_var) != list:
            varlist_or_var = [varlist_or_var]
        self.cursor["asc"] = varlist_or_var
        return self

    def desc(self, varlist_or_var):
        """Orders the list by descending value

        Parameters
        ----------
        varlist_or_var : list or str
            list of variables to order

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if type(varlist_or_var) != list:
            varlist_or_var = [varlist_or_var]
        self.cursor["desc"] = varlist_or_var
        return self

    def idgen(self, prefix, vari, type, mode=None):
        """Generates an ID for a node as a function of the passed VariableList with a specific prefix (URL base). If the values of the passed variables are the same, the output will be the same

        Parameters
        ----------
        prefix : str
            prefix for the id
        vari : str
            variable to generate id for
        type : str
            the variable to hold the id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['idgen'] = [prefix]
        if hasattr(vari, 'json'):
            self.cursor['idgen'].append(vari.json())
        elif hasattr(vari, 'list') or ('list' in vari):
            self.cursor['idgen'].append(vari)
        else:
            self.cursor['idgen'].append({"list": vari})

        if mode:
            self.cursor['idgen'].append(mode)

        self.cursor['idgen'].append(type)
        return self

    def unique(self, prefix, vari, type):
        """Generates an ID for a node as a function of the passed VariableList with a specific prefix (URL base). If the values of the passed variables are the same, the output will be the same

        Parameters
        ----------
        prefix : str
            prefix for the id
        vari : str
            variable to generate id for
        type : str
            the variable to hold the id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['unique'] = [prefix]
        if hasattr(vari, 'json'):
            self.cursor['unique'].append(vari.json())
        elif hasattr(vari, 'list') or ('list' in vari):
            self.cursor['unique'].append(vari)
        else:
            self.cursor['unique'].append({"list": vari})

        self.cursor['unique'].append(type)
        return self

    def re(self, p, s, m):
        """Regular Expression Call

        p is a regex pattern (.*) using normal regular expression syntax, the only unusual thing is that special characters have to be escaped twice, s is the string to be matched and m is a list of matches:
        e.g. WOQL.re("(.).*", "hello", ["v:All", "v:Sub"])

        Parameters
        ----------
        p : str
            regex pattern
        s : str
            string to be matched
        m : str or list or dict
            store list of matches

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if type(p) == str:
            if p[:2] != 'v:':
                p = {"@value" : p, "@type": "xsd:string"}

        if type(s) == str:
            if s[:2] != 'v:':
                s = {"@value" : s, "@type": "xsd:string"}

        if type(m) == str:
            m = [m]

        if (type(m) != dict) or ('list' not in m):
            m = {'list': m}

        self.cursor['re'] = [p, s, m]
        return self

    def concat(self, list, v):
        """Concatenates the list of variables into a string and saves the result in v

        Parameters
        ----------
        list : list
            list of variables to concatenate
        v : str
            saves the results

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if type(list) == str:
            nlist = re.split('(v:[\w_]+)\\b', list)
            for i in range(1,len(nlist)):
                if (nlist[i-1][len(nlist[i-1])-1:] == "v") and \
                   (nlist[i][:1] == ":"):
                   nlist[i-1] = nlist[i-1][:len(nlist[i-1])-1]
                   nlist[i] = nlist[i][1:]
        elif 'list' in list:
            nlist = list['list']
        elif isinstance(list, (list, dict, WOQLQuery)):
            nlist = list
        args = []
        for item in nlist:
            if (not item):
                continue
            if type(item) == str:
                if item[:2] == "v:":
                    args.append(item)
                else:
                    nvalue = {"@value": item, "@type": "xsd:string"}
                    args.append(nvalue)
            elif item:
                args.append(nlist[i])

        if v.find(":") == -1:
            v = "v:" + v

        self.cursor['concat'] = [{'list': args}, v]
        return self

    def lower(self, u, l):
        """Changes a string to lower-case - input is in u, output in l

        Parameters
        ----------
        u : str
            input string
        l : str
            stores output

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['lower'] = [u, l]
        return self

    def pad(self, input, pad, len, output):
        """
        Pads out the string input to be exactly len long by appending the pad character pad to form output

        Parameters
        ----------
        input : str
            input string
        pad : str
            padding character(s)
        len :  int
            length to pad
        output : str
            stores output

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['pad'] = [input, pad, len, output]
        return self

    def join(self, input, glue, output):
        """
        Joins a list variable together (input) into a string variable (output) by glueing the strings together with glue

        Parameters
        ----------
        input : list
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
        self.cursor['join'] = [input, glue, output]
        return self

    def less(self, v1, v2):
        """Compares the value of v1 against v2 and returns true if v1 is less than v2

        Parameters
        ----------
        v1 : str
            first variable to compare
        v2 : str
            second variable to compare

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['less'] = [v1, v2]
        return self

    def greater(self, v1, v2):
        """Compares the value of v1 against v2 and returns true if v1 is greater than v2

        Parameters
        ----------
        v1 : str
            first variable to compare
        v2 : str
            second variable to compare

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['greaters'] = [v1, v2]
        return self

    def list(self, *args):
        """Create a list of variables for WOQL

        Parameters
        ----------
        args
            variables to be put in the list

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['list'] = list(args)
        return self

    def json(self, json=None):
        """Generates a WOQLQuery object from the passed WOQL JSON

        json version of query for passing to api

        Parameters
        ----------
        json : dict
            JSON-LD object, optional

        Returns
        -------
        dict
            JSON-LD format of the WOQL query
        """
        if json:
            self.query = json
            return self
        return self.query

    def when(self, Query, Update=None):
        """When the sub-query in Condition is met, the Update query is executed

        Parameters
        ----------
        Query : WOQLQuery object or bool
        Update : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute

        Notes
        -----
        Functions which take a query as an argument advance the cursor to make the chaining of queries fall
        into the corrent place in the encompassing json
        """
        if type(Query) == bool:
            if Query:
                self.cursor["when"] = [{"true": []}, {}]
            else:
                self.cursor["when"] = [{"false": []}, {}]
        else:
            q =  Query.json() if hasattr(Query,'json') else Query
            self.cursor['when'] = [q, {}]

        if Update:
            upd = Update.json() if hasattr(Update,'json') else Update
            self.cursor["when"][1] = upd

        self.cursor = self.cursor["when"][1]
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
        """
        if query:
            q = query.json() if callable(query.json) else query
            self.cursor["opt"] = [q]
        else:
            self.cursor['opt'] = [{}]
            self.cursor = self.cursor["opt"][0]
        return self

    def woql_from(self, dburl, query=None):
        """Specifies the database URL that will be the default database for the enclosed query

        Parameters
        ----------
        dburl : str
            url of the database
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self._advance_cursor("from", dburl)
        if query:
            self.cursor = query.json() if hasattr(query,'json') else query
        return self

    def into(self, dburl, query=None):
        """Sets the current output graph for writing output to.

        Parameters
        ----------
        dburl : str
            output graph
        query : WOQLQuery object, optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self._advance_cursor("into", dburl)
        if query:
            self.cursor = query.json() if hasattr(query,'json') else query
        return self

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
        self._advance_cursor("limit", limit)
        if query:
            self.cursor = query.json() if hasattr(query,'json') else query
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
        self._advance_cursor("start", start)
        if query:
            self.cursor = query.json()
        return self

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

        self.cursor['select'] = list(args)
        index = len(args)
        if isinstance(self.cursor['select'][index-1], (list, dict, WOQLQuery)):
            self.cursor['select'][index-1] = self.cursor['select'][index-1].json()
        else:
            self.cursor['select'].append({})
            self.cursor = self.cursor['select'][index]
        return self

    def woql_and(self, *args):
        """Creates a logical AND of the arguments

        Parameters
        ----------
        args : WOQLQuery objects

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if not hasattr(self.cursor,'and'):
            self.cursor['and'] = []
        for item in args:
            if item.contains_update:
                self.contains_update = True
            self.cursor['and'].append(item.json())
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
        if not hasattr(self.cursor,'or'):
            self.cursor['or'] = []
        for item in args:
            if item.contains_update:
                self.contains_update = True
            if hasattr(item,'or'):
                nquery = item.json()
            else:
                nquery = item
            if hasattr(nquery,'or'):
                self.cursor['and'] = self.cursor['or'] + nquery['or']
            else:
                self.cursor['or'].append(item.json())
        return self

    def woql_not(self, query=None):
        """Creates a logical NOT of the arguments

        Parameters
        ----------
        query : WOQLQuery object, optional

        Returns
        ----------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if query:
            if query.contains_update:
                self.contains_update = True
            query = query.json() if hasattr(query,'json') else query
            self.cursor['not'] = [query]
        else:
            self.cursor['not'] = [{}]
            self.cursor = self.cursor['not'][0]
        return self

    def triple(self, sub, pre, obj):
        """Creates a triple pattern matching rule for the triple [S, P, O] (Subject, Predicate, Object)

        Parameters
        ----------
        sub : str
            Subject
        pre : str
            Predicate
        obj : str
            Object

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor["triple"] = [self._clean_subject(sub),self._clean_predicate(pre),self._clean_object(obj)]
        return self._chainable("triple", self._clean_subject(sub))

    def quad(self, sub, pre, obj, gra):
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

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor["quad"] = [self._clean_subject(sub),
                                self._clean_predicate(pre),
                                self._clean_object(obj),
                                self._clean_graph(gra)]
        return self._chainable("quad", self._clean_subject(sub))


    def eq(self, a, b):
        """Matches if a is equal to b

        Parameters
        ----------
        a : str
            object in the graph
        b : str
            object in the graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor["eq"] = [self._clean_object(a),self._clean_object(b)];
        return self._last()

    def sub(self, a, b=None):
        """Returns true if ClassA is a sub-class of ClassB, according to the current DB schema

        Parameters
        ----------
        a : str
            classA
        b : str, optional
            classB

        Returns
        -------
        bool
        """
        if (not b) and self.tripleBuilder:
            self.tripleBuilder.sub(self._clean_class(a))
            return self
        self.cursor["sub"] = [self._clean_class(a),self._clean_class(b)]
        return self._last("sub", a)

    def comment(self, val=None):
        """Adds a text comment to a query - can also be used to wrap any part of a query to turn it off

        Parameters
        ----------
        val : str
            text comment

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """

        if val and hasattr(val, 'json'):
            self.cursor['comment'] = [val.json()]
        elif type(val) == str:
            self.cursor['comment'] = [{"@value": val, "@language": "en"}]
        elif isinstance(val, (list, dict, WOQLQuery)):
            if len(val):
                self.cursor['comment'] = val
            else:
                self.cursor['comment'] = [val]
        else:
            self.cursor['comment'] = []

        last_index = len(self.cursor['comment'])
        self.cursor['comment'].append({})
        self.cursor = self.cursor['comment'][last_index]
        return self

    def abstract(self, varname=None):
        """
        If no argument is set, this is used to specify that a new class is abstract. If used with an argument, a triple check for class abstraction is added and the result is saved in varname

        Parameters
        ----------
        varname : str, optional
            result of class abstraction

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if varname:
            return self.quad(varname, "tcs:tag", "tcs:abstract", "db:schema")
        elif self.tripleBuilder:
            self.tripleBuilder.abstract()
        return self

    def isa(self, a, b=None):
        """Matches if Instance is a member of Class, according to the current state of the DB

        Parameters
        ----------
        a : str
            classA
        b : str, optional
            classB

        Returns
        -------
        bool
        """
        if (not b) and self.tripleBuilder:
            self.tripleBuilder.isa(self._clean_class(a))
            return self

        if b:
            self.cursor["isa"] = [self._clean_class(a),self._clean_class(b)]
            return self._chainable("isa", a)

    def trim(self, string, variable):
        """A trimmed version of StringA (with leading and trailing whitespace removed) is copied into VariableA

        Parameters
        ----------
        string : str
            StringA
        variable : str
            VariableA

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['trim'] = [string, variable]
        return self._chainable('trim', variable)

    def eval(self, arith, v):
        """Evaluates the Arithmetic Expression Arith and copies the output to variable V

        Parameters
        ----------
        arith : WOQLQuery or dict
            query or JSON-LD representing the query
        v : str
            output variable

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if hasattr(arith, 'json'):
            arith = arith.json()
        self.cursor['eval'] = [arith, v]
        return self._chainable('eval', v)


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
        self.cursor['plus'] = []
        for item in args:
            self.cursor['plus'].append(item.json() if hasattr(item,'json') else item)
        return self._last()

    def minus(self, *args):
        """Subtracts Numbers N1..Nn

        Parameters
        ----------
        args : int or float
            numbers to be subtracted

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['minus'] = []
        for item in args:
            self.cursor['minus'].append(item.json() if hasattr(item,'json') else item)
        return self._last()

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
        self.cursor['times'] = []
        for item in args:
            self.cursor['times'].append(item.json() if hasattr(item,'json') else item)
        return self._last()

    def divide(self, *args):
        """Divides numbers N1...Nn by each other left, to right precedence

        Parameters
        ----------
        args : int or float
            numbers to tbe divided

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['divide'] = []
        for item in args:
            self.cursor['divide'].append(item.json() if hasattr(item,'json') else item)
        return self._last()

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
        self.cursor['div'] = []
        for item in args:
            self.cursor['div'].append(item.json() if hasattr(item,'json') else item)
        return self._last()

    def exp(self, a, b):
        """Raises A to the power of B

        Parameters
        ----------
        a : int or float
        b : int or float

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if hasattr(a, 'json'):
            a = a.json()
        if hasattr(b, 'json'):
            b = b.json()

        self.cursor['exp'] = [a, b]
        return self._last()

    def delete(self, JSON_or_IRI):
        """Deletes a node identified by an IRI or a JSON-LD document

        Parameters
        ----------
        JSON_or_IRI : str
            IRI or a JSON-LD document

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.cursor['delete'] = [JSON_or_IRI]
        return self._last_update()

    def delete_triple(self, subject, predicate, object_or_literal):
        """Deletes any triples that match the rule [S,P,O]

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
        """
        self.cursor['delete_triple'] = [self._clean_subject(subject),
                                        self._clean_predicate(predicate),
                                        self._clean_object(object_or_literal)]
        return self._chainable_update('delete_triple', subject)

    def add_triple(self, subject, predicate, object_or_literal):
        """Adds triples according to the the pattern [S,P,O]

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
        """
        self.cursor['add_triple'] = [self._clean_subject(subject),
                                    self._clean_predicate(predicate),
                                    self._clean_object(object_or_literal)]
        return self._chainable_update('add_triple', subject)

    def delete_quad(self, subject, predicate, object_or_literal, graph):
        """Deletes any quads that match the rule [S, P, O, G] (Subject, Predicate, Object, Graph)

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
        self.cursor['delete_quad'] =[self._clean_subject(subject),
                                    self._clean_predicate(predicate),
                                    self._clean_object(object_or_literal),
                                    self._clean_graph(graph)]
        return self._chainable_update('delete_quad', subject)

    def add_quad(self, subject, predicate, object_or_literal, graph):
        """Adds quads according to the the pattern [S,P,O]

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
        self.cursor['add_quad'] =[self._clean_subject(subject),
                                    self._clean_predicate(predicate),
                                    self._clean_object(object_or_literal),
                                    self._clean_graph(graph)]
        return self._chainable_update('add_quad', subject)

    # Schema manipulation shorthand

    def add_class(self, c=None, graph=None):
        """Generates a new Class with the given ClassID and writes it to the DB schema

        Parameters
        ----------
        c : str
            class to be added
        graph : str, optional
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if c:
            graph = self.clean_graph(graph) if graph else "db:schema"
            self.adding_class = c
            c = "scm:" + c if c.find(":") == -1 else c
            self.add_quad(c, "rdf:type", "owl:Class", graph)
        return self

    def delete_class(self, c=None, graph=None):
        """Deletes the Class with the passed ID form the schema (and all references to it)

        Parameters
        ----------
        c : str
            class to be deleted
        graph : str, optional
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if c:
            graph = self._clean_graph(graph) if graph else "db:schema"
            c = "scm:" + c if c.find(":") == -1 else c

            return self.woql_and(WOQLQuery().delete_quad(c, "v:All", "v:Al2", graph),
                            WOQLQuery().opt().delete_quad("v:Al3", "v:Al4", c, graph))
        return self

    def add_property(self, p=None, t=None, g=None):
        """Generates a new Property with the given PropertyID and a range of type PropType and writes it to the DB schema

        Parameters
        ----------
        p : str
            property id to be added
        t : str
            type of the proerty
        g : str
            target graph ,optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if not t:
            t = "xsd:string"
        if p:
            graph = self._clean_graph(g) if g else "db:schema"
            p = "scm:" + p if p.find(":") == -1 else p
            t = self._clean_type(t) if t.find(":") == -1 else t
            tc = self.cursor
            pref = t.split(":")
            if (pref[0] is not None) and (pref[0] == "xdd" or pref[0] == "xsd"):
                self.woql_and(WOQLQuery().add_quad(p, "rdf:type", "owl:DatatypeProperty", graph),
                         WOQLQuery().add_quad(p, "rdfs:range", t, graph))
            else:
                self.woql_and(WOQLQuery().add_quad(p, "rdf:type", "owl:ObjectProperty", graph),
                         WOQLQuery().add_quad(p, "rdfs:range", t, graph))
        return self._chainable_update("add_quad", p)

    def delete_property(self, p=None, graph=None):
        """Deletes the property with the passed ID from the schema (and all references to it)

        Parameters
        ----------
        p : str
            property id to be deleted
        g : str
            target graph ,optional

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if p:
            graph = self._clean_graph(graph) if graph else "db:schema"
            p = "scm:" + p if p.find(":") == -1 else p
            return self.woql_and(WOQLQuery().delete_quad(p, "v:All", "v:Al2", graph),
                            WOQLQuery().delete_quad("v:Al3", "v:Al4", p, graph))
        return self

    # Language elements that cannot be invoked from the top level and therefore are not exposed in the WOQL api

    def woql_as(self, a=None, b=None):
        """Imports the value identified by Source to a Target variable

        Parameters
        ----------
        a : str
            Source
        b : str
            Target

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if a is None:
            return

        if not hasattr(self, 'asArray'):
            self.asArray = True
            self.query = []

        if b is not None:
            if b.find(":") == -1:
                b = "v:" + b
            if isinstance(a, (list, dict, WOQLQuery)):
                val = a
            else:
                val = { "@value" : a}
            self.query.append({'as': [val, b]})
        else:
            if a.find(":") == -1:
                a = "v:" + a
            self.query.append({'as': [a]})

        return self

    # WOQL API

    def node(self, node, type=None):
        """
        Selects nodes with the ID NodeID as the subject of subsequent sub-queries. The second argument PatternType specifies what type of sub-queries are being constructed, options are: triple, quad, update_triple, update_quad, delete_triple, delete_quad

        Parameters
        ----------
        node : str
            node to be selected
        type : str
            pattern type, optional (default is triple)

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if not type:
            type = "triple"
        self.tripleBuilder = TripleBuilder(type, self.cursor, node)
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
        g = self._clean_graph(g)
        if hasattr(self,'type'):
            t = "quad" if self.type == "triple" else False
            if self.type == "add_triple":
                t = "add_quad"
            if self.type == "delete_triple":
                t = "delete_quad"
        if not self.tripleBuilder:
            self.tripleBuilder = TripleBuilder(t, self.cursor)
        self.tripleBuilder.graph(g)
        return self

    def label(self, l, lang=None):
        """Depending on context, either adds a label match to a triple/quad or adds a label create to add_quad, add_triple

        Parameters
        ----------
        l : str
            label to add
        lang : str, optional
            language

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if self.tripleBuilder:
            self.tripleBuilder.label(l, lang)
        return self

    def description(self, c, lang=None):
        """Adds or matches a rdfs:comment field in a query

        Parameters
        ----------
        c : str
            description to be added
        lang : str, optional
            language

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if self.tripleBuilder:
            self.tripleBuilder.description(c, lang)
        return self

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
        if self.tripleBuilder:
            self.tripleBuilder.addPO('rdfs:domain',d)
        return self

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
        if self.tripleBuilder:
            for item in args:
                pn = self._clean_class(item)
                self.tripleBuilder.addPO('rdfs:subClassOf', pn)
        return self

    def entity(self):
        """Adds or matches a subclass relationship to tcs:Entity class

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.parent("tcs:Entity")

    def property(self, p, val):
        """Specifies that property p should have value val

        Parameters
        ----------
        p : str
            property
        val : str
            value

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if self.tripleBuilder:
            if(self.adding_class):
                nwoql = WOQLQuery().add_property(p, val).\
                domain(self.adding_class)
                nwoql.query["and"].append(self.json())
                nwoql.adding_class = self.adding_class
                return nwoql
            p = self._clean_predicate(p)
            self.tripleBuilder.addPO(p, val)
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
        if self.tripleBuilder:
            self.tripleBuilder.card(m, "max")
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
        if self.tripleBuilder:
            self.tripleBuilder.card(m, "cardinality")
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
        if self.tripleBuilder:
            self.tripleBuilder.card(m, "min")
        return self

    def star(self, GraphIRI=None, Subj=None, Pred=None, Obj=None):
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

        Subj = self._clean_subject(Subj) if Subj else "v:Subject"
        Pred = self._clean_predicate(Pred) if Pred else "v:Predicate"
        Obj = self._clean_object(Obj) if Obj else "v:Object"
        GraphIRI = self._clean_graph(GraphIRI) if GraphIRI else False

        if GraphIRI:
            return self.quad(Subj, Pred, Obj, GraphIRI)
        else:
            return self.triple(Subj, Pred, Obj)

    def get_everything(self, GraphIRI=None):
        """Retrieves all triples from the graph in question as (v:Subject, v:Predicate, v:Object)

        Parameters
        ----------
        GraphIRI : str
            target graph

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if GraphIRI:
            GraphIRI = self._clean_graph(GraphIRI)
            return self.quad("v:Subject", "v:Predicate", "v:Object", GraphIRI)
        else:
            self.triple("v:Subject", "v:Predicate", "v:Object")

    def get_all_documents(self):
        """Retrieves document id (v:Document) and type (v:Type) of all documents

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                    WOQLQuery().triple("v:Subject", "rdf:type", "v:Type"),
                    WOQLQuery().sub("v:Type", "tcs:Document")
                    )

    def document_metadata(self):
        """
        Retrieves meta-data about all documents, document id, label, comment (v:ID, v:Label, v:Comment), document class id, label and comment (v:Class, v:Type, v:Type_Comment),

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().triple("v:ID", "rdf:type", "v:Class"),
                WOQLQuery().sub("v:Class", "tcs:Document"),
                WOQLQuery().opt().triple("v:ID", "rdfs:label", "v:Label"),
                WOQLQuery().opt().triple("v:ID", "rdfs:comment", "v:Comment"),
                WOQLQuery().opt().quad("v:Class", "rdfs:label", "v:Type", "db:schema"),
                WOQLQuery().opt().quad("v:Class", "rdfs:comment", "v:Type_Comment", "db:schema")
                )

    def concrete_document_classes(self):
        """Retrieves all instances and their meta-data (v:Class, v:Label, v:Comment) of concrete document classes

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().sub("v:Class", "tcs:Document"),
                WOQLQuery().woql_not().abstract("v:Class"),
                WOQLQuery().opt().quad("v:Class", "rdfs:label", "v:Label", "db:schema"),
                WOQLQuery().opt().quad("v:Class", "rdfs:comment", "v:Comment", "db:schema")
                )

    def property_metadata(self):
        """Retrieves all meta-data about each property (v:Property, v:Type, v:Range, v:Domain, v:Label, v:Comment)


        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().woql_or(
                    WOQLQuery().quad("v:Property", "rdf:type", "owl:DatatypeProperty", "db:schema"),
                    WOQLQuery().quad("v:Property", "rdf:type", "owl:ObjectProperty", "db:schema")
                ),
                WOQLQuery().opt().quad("v:Property", "rdfs:range", "v:Range", "db:schema"),
                WOQLQuery().opt().quad("v:Property", "rdf:type", "v:Type", "db:schema"),
                WOQLQuery().opt().quad("v:Property", "rdfs:label", "v:Label", "db:schema"),
                WOQLQuery().opt().quad("v:Property", "rdfs:comment", "v:Comment", "db:schema"),
                WOQLQuery().opt().quad("v:Property", "rdfs:domain", "v:Domain", "db:schema")
                )

    def element_metadata(self):
        """
        Retrieves meta-data about all elements in the schema (v:Element, v:Parent, v:Type, v:Range, v:Domain, v:Label, v:Comment, v:Abstract)

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().quad("v:Element", "rdf:type", "v:Type", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "tcs:tag", "v:Abstract", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "rdfs:label", "v:Label", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "rdfs:comment", "v:Comment", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "rdfs:subClassOf", "v:Parent", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "rdfs:domain", "v:Domain", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "rdfs:range", "v:Range", "db:schema")
                )

    def class_metadata(self):
        """Retrieves meta-data about all the classes in the schema (v:Element, v:Label, v:Comment, v:Abstract)

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().quad("v:Element", "rdf:type", "owl:Class", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "rdfs:label", "v:Label", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "rdfs:comment", "v:Comment", "db:schema"),
                WOQLQuery().opt().quad("v:Element", "tcs:tag", "v:Abstract", "db:schema")
                )

    def get_data_of_class(self, chosen):
        """Retrieves all triples that have a subject of the passed class (v:Document, v:Property, v:Value)

        Parameters
        ----------
        chosen : str
            chosen class

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().triple("v:Subject", "rdf:type", chosen),
                WOQLQuery().opt().triple("v:Subject", "v:Property", "v:Value")
                )

    def get_data_of_property(self, chosen):
        """Retrieves all triples that use the passed predicate along with the predicate's label (v:Document, v:Value, v:Label)

        Parameters
        ----------
        chosen : str
            chosen predicate

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().triple("v:Subject", chosen, "v:Value"),
                WOQLQuery().opt().triple("v:Subject", "rdfs:label", "v:Label")
                )

    def document_properties(self, id):
        """
        Retrieves all properties of a given document, along with their labels, values and type (v:Property, v:Property_Value, v:Property_Label, v:Property_Type)

        Parameters
        ----------
        id : str
            document id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().triple(id, "v:Property", "v:Property_Value"),
                WOQLQuery().opt().quad("v:Property", "rdfs:label", "v:Property_Label", "db:schema"),
                WOQLQuery().opt().quad("v:Property", "rdf:type", "v:Property_Type", "db:schema")
                )

    def get_document_connections(self, id):
        """
        Retrieve all links between the passed document and other documents (v:Entid, v:Outgoing, v:Incoming, v:Enttype, v:Label, v:Class_Label)

        Parameters
        ----------
        id : str
            document id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().eq("v:Docid", id),
                WOQLQuery().woql_or(
                    WOQLQuery().triple(id, "v:Outgoing", "v:Entid"),
                    WOQLQuery().triple("v:Entid", "v:Incoming", id)
                ),
                WOQLQuery().isa("v:Entid", "v:Enttype"),
                WOQLQuery().sub("v:Enttype", "tcs:Document"),
                WOQLQuery().opt().triple("v:Entid", "rdfs:label", "v:Label"),
                WOQLQuery().opt().quad("v:Enttype", "rdfs:label", "v:Class_Label", "db:schema")
                )

    def get_instance_meta(self, id):
        """
        Retrieve basic meta-data for a given object (v:InstanceType, v:InstanceLabel, v:InstanceComment, v:ClassLabel)

        Parameters
        ----------
        id : str
            document id

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().triple(id, "rdf:type", "v:InstanceType"),
                WOQLQuery().opt().triple(id, "rdfs:label", "v:InstanceLabel"),
                WOQLQuery().opt().triple(id, "rdfs:comment", "v:InstanceComment"),
                WOQLQuery().opt().quad("v:InstanceType", "rdfs:label", "v:ClassLabel", "db:schema")
                )

    def simple_graph_query(self):
        """
        Create a graph query with pattern (v:Source, v:Edge, v:Target), with meta-data for each element (v:Source_Class, v:Source_Label , v:Source_Comment, v:Source_Type, v:Source_Type_Comment, v:Target_Class, v:Target_Label , v:Target_Comment, v:Target_Type, v:Target_Class_Comment, v:Target_Label , v:Edge_Type_Comment, v:Edge_Type)

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.woql_and(
                WOQLQuery().triple("v:Source", "v:Edge", "v:Target"),
                WOQLQuery().isa("v:Source", "v:Source_Class"),
                WOQLQuery().sub("v:Source_Class", "tcs:Document"),
                WOQLQuery().isa("v:Target", "v:Target_Class"),
                WOQLQuery().sub("v:Target_Class", "tcs:Document"),
                WOQLQuery().opt().triple("v:Source", "rdfs:label", "v:Source_Label"),
                WOQLQuery().opt().triple("v:Source", "rdfs:comment", "v:Source_Comment"),
                WOQLQuery().opt().quad("v:Source_Class", "rdfs:label", "v:Source_Type", "db:schema"),
                WOQLQuery().opt().quad("v:Source_Class", "rdfs:comment", "v:Source_Type_Comment", "db:schema"),
                WOQLQuery().opt().triple("v:Target", "rdfs:label", "v:Target_Label"),
                WOQLQuery().opt().triple("v:Target", "rdfs:comment", "v:Target_Comment"),
                WOQLQuery().opt().quad("v:Target_Class", "rdfs:label", "v:Target_Type", "db:schema"),
                WOQLQuery().opt().quad("v:Target_Class", "rdfs:comment", "v:Target_Type_Comment", "db:schema"),
                WOQLQuery().opt().quad("v:Edge", "rdfs:label", "v:Edge_Type", "db:schema"),
                WOQLQuery().opt().quad("v:Edge", "rdfs:comment", "v:Edge_Type_Comment", "db:schema")
                )

    def get_vocabulary(self):
        """Returns the vocabulary at play - a list of all properties and classes in the schema

        Returns
        -------
        dict
        """
        return self.vocab

    def set_vocabulary(self, vocab):
        """
        Provides the query with a 'vocabulary' a list of well known predicates that can be used without prefixes mapping: id: prefix:id ...

        Parameters
        ----------
        vocab : dict
            JSON object where the indices are non-prefixed string and the values are the corresponding prefixed strings: {type: "rdf:type"...}

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self.vocab = vocab

    def load_vocabulary(self, client):
        """Loads the entirety of the current schema graph as a vocabulary - allows all valid schema URLs to be used without prefixes.

        Queries the schema graph and loads all the ids found there as vocabulary that can be used without prefixes.

        It ignoring blank node ids.

        Parameters
        ----------
        client : WOQLClient object

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        nw = WOQLQuery().quad("v:S", "v:P", "v:O", "db:schema")
        result = nw.execute(client)
        if (result and 'bindings' in result) and (len(result['bindings']) > 0):
            for item in result['bindings']:
                for key in item:
                    value = item[key]
                    if type(value) == str:
                        val_spl = value.split(":")
                        if len(val_spl)==2 and val_spl[1] and val_spl[0]!='_':
                            self.vocab[val_spl[0]] = val_spl[1]

    def get_limit(self):
        """Returns the current limit value

        Returns
        -------
        int
        """
        return self._get_paging_property("limit")

    def set_limit(self, l):
        """Sets the limit to N

        Parameters
        ----------
        l : int
            limit to set

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self._set_paging_property("limit", l)

    def is_paged(self, q=None):
        """True if the query was paged (i.e. had a limit set)

        Parameters
        ----------
        q : WOQLQuery object

        Returns
        -------
        bool
        """
        if q is None:
            q = self.query
        for prop in q:
            if prop == "limit":
                return True
            elif prop in self.paging_transitive_properties:
                return self.is_paged(q[prop][len(q[prop])-1])
        return False

    def get_page(self):
        """Returns the current page number as an offset from the current page size (limit)

        Returns
        -------
        int
        """
        if self.is_paged():
            psize = self.get_limit()
            if self.has_start():
                s = self.get_start()
                return ((s // psize) + 1)
            else:
                return 1
        else:
            return False

    def set_page(self, pagenum):
        """Sets the page to page number N (where N is an integer)

        Parameters
        ----------
        pagenum : int
            page number to set

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        pstart = (self.get_limit() * (pagenum - 1))
        if self.has_start():
            self._set_start(pstart)
        else:
            self.add_start(pstart)
        return self

    def next_page(self):
        """Increments the page number

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.set_page(self.get_page() + 1)

    def first_page(self):
        """Sets the page number to the first page

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        return self.set_page(1)

    def previous_page(self):
        """Decrements the page number if it is currently ≥ 1

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        npage = self.get_page() - 1
        if npage > 0:
            self.set_page(npage)
        return self

    def set_page_size(self, size):
        """Sets the page size (limit)

        Parameters
        ----------
        size : int
            size of the page

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        self._set_paging_property("limit", size)
        if self.has_start():
            self._set_start(0)
        else:
            self.add_start(0)
        return self

    def has_select(self):
        """Returns true if the query contains a select clause

        Returns
        -------
        bool
        """
        return bool(self._get_paging_property("select"))

    def get_select_variables(self, q=None):
        """Returns list of the variables specified as part of the select clause

        Parameters
        ----------
        q : WOQLQuery object, optional

        Returns
        -------
        list
        """
        if q is None:
            q = self.query
        for prop in q:
            if prop == "select":
                vars = q[prop][:len(q[prop])-1]
                return vars
            elif prop in self.paging_transitive_properties:
                val = self.get_select_variables(q[prop][len(q[prop])-1])
                if val is not None:
                    return val

    def has_start(self):
        """Check if the query have a start value set

        Returns
        -------
        bool
        """
        result = self._get_paging_property("start")
        return result is not None

    def get_start(self):
        """Returns the current start value (result offset)

        Returns
        -------
        int
        """
        return self._get_paging_property("start");

    def _set_start(self, start):
        """Internal function for setting a start value for an already built query
        """
        return self._set_paging_property("start", start)

    def add_start(self, s):
        """Sets the start value (result offset)

        Parameters
        ----------
        s : int
            start index

        Returns
        -------
        WOQLQuery object
            query object that can be chained and/or execute
        """
        if self.has_start():
            self._set_start(s)
        else:
            nq = {'start': [s, self.query]}
            self.query = nq
        return self

    def _get_paging_property(self, pageprop, q=None):
        """Internal function for interogating formed query
        Returns the value of one of the 'paging' related properties (limit, start,...)
        """
        if q is None:
            q = self.query
        for prop in q:
            if prop == pageprop:
                return q[prop][0]
            elif prop in self.paging_transitive_properties:
                val = self._get_paging_property(pageprop, q[prop][len(q[prop])-1])
                if val is not None:
                    return val

    def _set_paging_property(self, pageprop, val, q=None):
        """Internal function for changing paging properties (start, limit) of already built queries
        Sets the value of one of the paging_transitive_properties properties"""
        if q is None:
            q = self.query
        for prop in q:
            if prop == pageprop:
                q[prop][0] = val
            elif prop in self.paging_transitive_properties:
                self._set_paging_property(pageprop, val, q[prop][len(q[prop])-1])
        return self


    def get_context(self, q=None):
        """Retrieves the value of the current json-ld context

        Parameters
        ----------
        q : WOQLQuery object, optional

        Returns
        -------
        dict
        """
        if q is None:
            q = self.query
        for prop in q:
            if prop == "@context":
                return q[prop]
            if prop in self.paging_transitive_properties:
                nc = self.get_context(q[prop][1])
            if nc:
                return nc

    def context(self, c):
        """Specifies the query context as a JSON-LD context (prefix → value)

        Parameters
        ----------
        c : dict
            context
        """
        self.cursor['@context'] = c

    #Internal State Control Functions
    #Not part of public API -

    def _default_context(self, DB_IRI):
        result = copy(STANDARD_URLS)
        result['scm'] = DB_IRI + "/schema#"
        result['doc'] = DB_IRI + "/document/"
        result['db'] = DB_IRI + "/"
        return result

    def _load_default_vocabulary(self):
        vocab = {}
        vocab['type'] = "rdf:type"
        vocab['label'] = "rdfs:label"
        vocab['Class'] = "owl:Class"
        vocab['DatatypeProperty'] = "owl:DatatypeProperty"
        vocab['ObjectProperty'] = "owl:ObjectProperty"
        vocab['Entity'] = "tcs:Entity"
        vocab['Document'] = "tcs:Document"
        vocab['Relationship'] = "tcs:Relationship"
        vocab['temporality'] = "tcs:temporality"
        vocab['geotemporality'] = "tcs:geotemporality"
        vocab['geography'] = "tcs:geography"
        vocab['abstract'] = "tcs:abstract"
        vocab['comment'] = "rdfs:comment"
        vocab['range'] = "rdfs:range"
        vocab['domain'] = "rdfs:domain"
        vocab['subClassOf'] = "rdfs:subClassOf"
        vocab['string'] = "xsd:string"
        vocab['integer'] = "xsd:integer"
        vocab['decimal'] = "xsd:decimal"
        vocab['email'] = "xdd:email"
        vocab['json'] = "xdd:json"
        vocab['dateTime'] = "xsd:dateTime"
        vocab['date'] = "xsd:date"
        vocab['coordinate'] = "xdd:coordinate"
        vocab['line'] = "xdd:coordinatePolyline"
        vocab['polygon'] = "xdd:coordinatePolygon"
        return vocab

    def _advance_cursor(self, action, value):
        """Advances internal cursor to support chaining of calls: limit(50).start(50). rather than (limit, [50, (start, [50, (lisp-style (encapsulation)))))"""
        self.cursor[action] = [value]
        self.cursor[action].append({})
        self.cursor = self.cursor[action][1]

    def _clean_subject(self, s):
        if type(s) != str or s.find(":") != -1:
            return s
        if self.vocab and (s in self.vocab):
            return self.vocab[s]
        return "doc:" + s

    def _clean_predicate(self, p):
        if p.find(":") != -1:
            return p
        if self.vocab and (p in self.vocab):
            return self.vocab[p]
        return "scm:" + p

    def _clean_graph(self, g):
        if g.find(":") != -1:
            return g
        if self.vocab and (g in self.vocab):
            return self.vocab[g]
        return "db:" + g

    def _clean_object(self, o):
        if type(o) != str or o.find(":") != -1:
            return o
        if self.vocab and (o in self.vocab):
            return self.vocab[o]
        return { "@value": o, "@language": "en"}

    def _last(self, call=None, subject=None):
        """Called to indicate that this is the last call in constructing a complete woql query object"""
        self.chain_ended = True
        return self

    def _last_update(self):
        """Called to indicate that this is the last call that is chainable - for example triple pattern matching.."""
        self._last()
        return self

    def _chainable(self, call, subj):
        """Called to indicate internally that this is a chainable update - by setting the subject and call of the Triple Builder object which is used to build further triples"""
        self.tripleBuilder = TripleBuilder(call, self.cursor, self._clean_subject(subj))
        self._last()
        return self

    def _chainable_update(self, call, subj):
        """Called to indicate internally that this is a chainable update - by setting the subject and call of the Triple Builder object which is used to build further triples"""
        self.tripleBuilder = TripleBuilder(call, self.cursor, self._clean_subject(subj))
        return self._last_update()

    def _is_chainable(self, operator, lastArg=None):
        """Determines whether a given operator can have a chained query as its last argument"""
        non_chaining_operators = ["and", "or", "remote", "file", "re"]
        if (lastArg is not None and type(lastArg) == dict and
            '@value' not in lastArg and
            '@type' not in lastArg and
            'value' not in lastArg
            ):
            for op in non_chaining_operators:
                if op in operator:
                    return False
            return True
        else:
            return False

    def execute(self, client):
        """Executes the query using the passed client to connect to a server

        Parameters
        ----------
        client : woqlClient
        """
        if "@context" not in self.query:
            self.query['@context'] = self._default_context(client.conConfig.dbURL())
        json = self.json()
        if self.contains_update:
            return client.select(json)
            #return client.update(json)
        else:
            return client.select(json)


class TripleBuilder:
    """
    * higher level composite queries - not language or api elements
    * Class for enabling building of triples from pieces
    * type is add_quad / remove_quad / add_triple / remove_triple
    """

    def __init__(self, type=None, cursor=None, s=None):
        self.type = type
        self.cursor = cursor
        self.subject = s if s else False
        self.g = False

        self.sub = self.isa

    def label(self, l, lang=None):
        if not lang:
            lang = "en"
        if l[:2] == "v:":
            d = l
        else:
            d = {"@value": l, "@language": lang }
        x = self.addPO('rdfs:label', d)
        return x

    def description(self, l, lang=None):
        if not lang:
            lang = "en"
        if l[:2] == "v:":
            d = l
        else:
            d = {"@value": l, "@language": lang }
        x = self.addPO('rdfs:comment', d)
        return x

    def addPO(self, p, o, g=None):
        if self.type:
            if self.type == "isa" or self.type == "sub":
                ttype = "triple"
            else:
                ttype = self.type
        else:
            ttype = "triple"
        #“In the basket are %s and %s” % (x,y)

        evstr = " %s (\"%s\" , \"%s\" , " % (ttype, self.subject, p)
        #ttype + "(\"" + self.subject + "\", " + p + "\", "
        if type(o) == str:
            evstr += "'" + o + "'"
        elif isinstance(o, (list, dict, WOQLQuery)):
            evstr += str(o)
        else:
            evstr += o

        if ttype[-4:] == "quad" or self.g:
            if not g:
                g = self.g if self.g else "db:schema"
            evstr += ", \"%s\" " % (g)
            #', "' + g + '"'
        evstr += ")"
        try:
            unit = eval("WOQLQuery()." + evstr)
            return self.add_entry(unit)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            return self

    def getO(self, s, p):
        if "and" in self.cursor:
            for item in self.cursor['and']:
                clause = item
                key = list(clause.keys())[0]
                if clause[key][0] == s and \
                   clause[key][1] == p and \
                   clause[key][2] :
                    return clause[key][2]
        elif self.cursor.keys():
            clause = self.cursor
            key = list(clause.keys())[0]
            if clause[key][0] == s and \
               clause[key][1] == p and \
               clause[key][2] :
                return clause[key][2]

        return False

    def add_entry(self, unit):
        if self.type in self.cursor:
            next = {}
            next[self.type] = self.cursor[self.type]
            self.cursor['and'] = [next]
            del self.cursor[self.type]

        if 'and' in self.cursor:
            self.cursor['and'].append(unit.json())
        else:
            j = unit.json()
            if self.type in j:
                self.cursor[self.type] = j[self.type]
            else:
                print(j)
        return self

    def card(self, n, which):
        os = self.subject
        self.subject += "_" + which
        self.addPO('rdf:type', "owl:Restriction")
        self.addPO("owl:onProperty", os)
        if which == "max":
            self.addPO("owl:maxCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"})
        elif which == "min":
            self.addPO("owl:minCardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"})
        else:
            self.addPO("owl:cardinality", {"@value": n, "@type": "xsd:nonNegativeInteger"})

        od = self.getO(os, "rdfs:domain")
        if od:
            cardcls = self.subject
            self.subject = od
            self.addPO("rdfs:subClassOf", cardcls)
        self.subject = os
        return self

    def isa(self, a):
        unit = WOQLQuery.isa(self.subject, a)
        self.add_entry(unit)

    def graph(self, g):
        self.g = g

    def abstract(self):
        return self.addPO('tcs:tag', "tcs:abstract")

"""

Methods that has not been impremented
====================================

# Pretty print need logic for translate to WOQLpy

    def pretty_print(self, indent, show_context, q=None, fluent=None):
        if not hasattr(self, 'indent'):
            self.indent = indent
        if q is None:
            q = self.query
        string = ""
        newlining_operators = ["get", "from", "into"]
        for operator in q:
            # ignore context in pretty print
            if (operator == "@context"):
                if (show_context):
                    c = self._get_context()
                    if c:
                        string += "@context: " + str(c) + "\n"
                continue
            # statement starts differently depending on indent and whether it is fluent style or regular function style
            string += self._get_woql_prelude(operator, fluent, indent - self.indent)
            val = q[operator]
            if self._is_chainable(operator, val[val.length-1]):
                # all arguments up until the last are regular function arguments
                string += self._unclean_arguments(operator,  val.slice(0, val.length-1), indent, show_context)
                if newlining_operators not in operator:
                    # some fluent function calls demand a linebreak..
                    string += "\n" + (" " * (indent-this.indent))
                # recursive call to query included in tail
                string += self.pretty_print(indent, show_context, val[val.length-1], true)
            else:
                # non chainable operators all live inside the function call parameters
                string += this._unclean_arguments(operator, val, indent, show_context)
        # remove any trailing dots in the chain (only exist in incompletely specified queries)
        if (string[-1] == "."):
            string = string[:-1];
        return string

    def _get_woql_prelude(self, operator, fluent, inline):
        Gets the starting characters for a WOQL query - varies depending on how the query is invoked and how indented it is
        # TODO: should follow WOQLpy syntex not js syntex
        if operator in ["true" or "false"]:
            return operator
        if fluent:
            return "." + operator
        if inline:
            return "\n" + " " * (inline) + "WOQL." + operator
        else:
            return "WOQL." + operator

/**
 * Transforms arguments to WOQL functions from the internal (clean) version, to the WOQL.js human-friendly version
 */
WOQLQuery.prototype.uncleanArguments = function(operator, args, indent, show_context){
    str = '(';
    const args_take_newlines = ["and", "or"];
    if(this.hasShortcut(operator, args)){
    return this.getShortcut(args, indent);
    }
    else {
    for(var i = 0; i<args.length; i++){
    if(this.argIsSubQuery(operator, args[i], i)){
    str += this.prettyPrint(indent + this.indent, show_context, args[i], false);
    }
    else if(operator == "get" && i == 0){ // weird one, needs special casing
    str += "\n" + nspaces(indent-this.indent) + "WOQL";
    for(var j = 0; j < args[0].length; j++){
    var myas = (args[0][j].as ? args[0][j].as : args[0][j]);
    var lhs = myas[0];
    var rhs = myas[1];
    if(typeof lhs == "object" && lhs['@value']){
    lhs = lhs['@value'];
    }
    if(typeof lhs == "object") {
    lhs = JSON.stringify(lhs);
    }
    else {
    lhs = '"' + lhs + '"'
    }
    str += '.as(' + lhs;
    if(rhs) str += ', "' + rhs + '"';
    str += ")";
    str += "\n" + nspaces(indent);
    }
    }
    else {
    str += this.uncleanArgument(operator, args[i], i, args);
    }
    if(i < args.length -1) str +=  ',';
    }
    }
    if(args_take_newlines.indexOf(operator) != -1){
    str += "\n" + nspaces(indent-this.indent);
    }
    str += ")";
    return str;
}


/**
 * Passed as arguments: 1) the operator (and, triple, not, opt, etc)
 * 2) the value of the argument
 * 3) the index (position) of the argument.
 */
WOQLQuery.prototype.uncleanArgument = function(operator, val, index, allArgs){
    //numeric values go out untouched...
    const numeric_operators = ["limit", "start", "eval", "plus", "minus", "times", "divide", "exp", "div"];
    if(operator == "isa"){
    val = (index == 0 ? this.unclean(val, 'subject') : this.unclean(val, 'class'));
    }
    else if(operator == "sub"){
    val = this.unclean(val, 'class');
    }
    else if(["select"].indexOf(operator) != -1){
    if(val.substring(0, 2) == "v:") val = val.substring(2);
    }
    else if(["quad", "add_quad", "delete_quad", "add_triple", "delete_triple", "triple"].indexOf(operator) != -1){
    switch(index){
    case 0: val = this.unclean(val, "subject"); break;
    case 1: val = this.unclean(val, "predicate"); break;
    case 2: val = this.unclean(val, "object"); break;
    case 3: val = this.unclean(val, "graph"); break;
    }
    }
    if(typeof val == "object"){
    if(operator == "concat" && index == 0){
    var cstr = "";
    if(val.list){
    for(var i = 0 ; i<val.list.length; i++){
    if(val.list[i]['@value']) cstr += val.list[i]['@value'];
    else cstr += val.list[i];
    }
    }
    var oval = '"' + cstr + '"';
    }
    else {
    var oval = this.unclean_objectArgument(operator, val, index);
    }
    return oval;
    }
    //else if(numeric_operators.indexOf(operator) !== -1){
    //    return val;
    //}
    if(typeof val == "string"){
    return '"' + val + '"';
    }
    return val;
}

WOQLQuery.prototype.unclean_objectArgument = function(operator, val, index){
    if(val['@value'] && (val['@language'] || (val['@type'] && val['@type'] == "xsd:string"))) return '"' + val['@value'] + '"';
    if(val['@value'] && (val['@type'] && val['@type'] == "xsd:integer")) return val['@value'];
    if(val['list']) {
    var nstr = "[";
    for(var i = 0 ; i<val['list'].length; i++){
    if(typeof val['list'][i] == "object"){
    nstr += this.unclean_objectArgument("list", val['list'][i], i);
    }
    else {
    nstr += '"' + val['list'][i] + '"';
    }
    if(i < val['list'].length-1){
    nstr += ",";
    }
    }
    nstr += "]";
    return nstr;
    }
    return JSON.stringify(val);
}

WOQLQuery.prototype.argIsSubQuery = function(operator, arg, index){
    const squery_operators = ["and", "or", "when", "not", "opt", "exp", "minus", "div", "divide", "plus", "multiply"];
    if(squery_operators.indexOf(operator) !== -1){
    if(arg && typeof arg != "object") return false;
    return true;
    }
    if(operator == "group_by" && index == 2) return true;
    else return false;
}

/**
 * Goes from the properly prefixed clean internal version of a variable to the WOQL.js unprefixed form
 */
WOQLQuery.prototype.unclean = function(s, part){
    if(typeof s != "string") return s;
    if(s.indexOf(":") == -1) return s;
    if(s.substring(0,4) == "http") return s;
    var suff = s.split(":")[1];
    if(this.vocab && this.vocab[suff] && this.vocab[suff] == s){
    return suff;
    }
    if(!part) return s;
    if(part == "subject" && (s.split(":")[0] == "doc")) return suff;
    if(part == "class" && (s.split(":")[0] == "scm")) return suff;
    if(part == "predicate" && (s.split(":")[0] == "scm")) return suff;
    if(part == "type" && (s.split(":")[0] == "scm")) return suff;
    if(part == "graph" && (s.split(":")[0] == "db")) return suff;
    return s;
}

WOQLQuery.prototype.hasShortcut = function(operator, args, indent, show_context){
    if(operator == "true") return true;
}

WOQLQuery.prototype.getShortcut = function(operator, args, indent, show_context){
    if(operator == "true") return true;
}

function nspaces(n){
    let spaces = "";
    for(var i = 0; i<n; i++){
    spaces += " ";
    }
    return spaces;
}

WOQLQuery.prototype.printLine = function(indent, clauses){
    return "(\n" + nspaces(indent) + "WOQL." + clauses.join(",\n"+ nspaces(indent) + "WOQL.") + "\n" + nspaces(indent - this.indent) + ")";
}

"""
