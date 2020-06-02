import woql_utils as utils

from .woqlQuery import woqlQuery


"""
    The WOQL Schema Class provides pre-built WOQL queries for schema manipulation
    a) adding and deleting classes and properties
    b) loading datatype libraries
    c) boxing classes
"""


class WOQLSchema(g):
    def __init__(self):
        self.graph = g or "schema/main"

    def _add_class(self, c, graph=None):
        graph = self.graph
        ap = self.woqlQuery()
        if c is not None:
            c = ap._cleanClass(c, True)
            ap.adding_class = c
            ap._add_quad(c, "rdf:type", "owl:Class", graph)
        return ap

    def _insert_class_data(self, data, ref_graph):
        """
            Adds a bunch of class data in one go
        """
        ap = self.woqlQuery()
        if data.id is not None:
            c = ap._cleanClass(data.id, True)
            ap = self.WOQLSchema().add_class(c, ref_graph)
            if data.label is not None:
                ap.label(data.label)
            if data.description is not None:
                ap.description(data.description)
            if data.parent is not None:
                if not isinstance(data.parent, list):
                    data.parent = [data.parent]
                    """ap.parent(...data.parent) TODO"""
            for k in data:
                if ["id", "label", "description", "parent"].indexOf(k) == -1:
                    ap._insert_property_data(k, data[k], ref_graph)
        return ap

    def _doctype_data(self, data, ref_graph):
        if data.parent is None:
            data.parent = []
        if not isinstance(data.parent, list):
            data.parent = [data.parent]
        data.parent.append("Document")
        return self._insert_class_data(data, ref_graph)

    def _insert_property_data(self, data, ref_graph):
        ap = self.woqlQuery()
        if data.id is not None:
            c = ap._cleanClass(data.id, True)
            ap._add_class(c, ref_graph)
            if data.label is not None:
                ap.label(data.label)
            if data.description is not None:
                ap.description(data.description)
            if data.parent is not None:
                if not isinstance(data.parent, list):
                    data.parent = [data.parent]
                    """ap.parent(...data.parent) TODO"""
            for k in data:
                if ["id", "label", "description", "parent"].indexOf(k) == -1:
                    ap.insert_property_data(k, data[k], ref_graph)
        return ap

    def delete_class(self, c, graph=self.graph):
        ap = self.woqlQuery()
        if c is not None:
            c = ap.cleanClass(c, True)
            # TODO: cleaning
            # ap.woql_and(
            #     self.woqlQuery().delete_quad(c, "v:Outgoing", "v:Value", graph),
            #     self.woqlQuery().opt().delete_quad("v:Other", "v:Incoming", c, graph)
            # )
            # ap.updated()
        return ap

    def _insert_property_data(self, data, graph):
        ap = self.woqlQuery()
        if data.id is not None:
            p = ap._cleanPathPredicate(data.id)
            t = ap._cleanType(data.range, True) if t is not None else "xsd:string"
            ap._add_property(p, t, graph)
            if data.label is not None:
                ap.label(data.label)
            if data.description is not None:
                ap.description(data.description)
            if data.domain is not None:
                ap.domain(data.domain)
            if data.max is not None:
                ap.max(data.max)
            if data.min is not None:
                ap.min(data.min)
                ap.cardinality(data.cardinality)
        return ap

    def _add_property(self, p, t, graph=None):
        if graph is None:
            graph = self.graph
        ap = self.woqlQuery()
        t = ap._cleanType(t, True) if t is not None else "xsd:string"
        if p is not None:
            p = ap._cleanPathPredicate(p)
            # TODO: cleaning
            if utils.type_helper.isDatatype(t) is not None:
                ap.woql_and(
                    self.woqlQuery().add_quad(
                        p, "rdf:type", "owl:DatatypeProperty", graph
                    ),
                    self.woqlQuery().add_quad(p, "rdfs:range", t, graph),
                )
            else:
                ap.woql_and(
                    self.woqlQuery().add_quad(
                        p, "rdf:type", "owl:ObjectProperty", graph
                    ),
                    self.woqlQuery().add_quad(p, "rdfs:range", t, graph),
                )
            ap._updated()
        return ap

    def _delete_property(self, p, graph=None):
        if graph is None:
            graph = self.graph
        ap = self.woqlQuery()
        if p is not None:
            p = ap.cleanPathPredicate(p)
            # TODO: cleaning
            ap.woql_and(
                self.woqlQuery().delete_quad(p, "v:All", "v:Al2", graph),
                self.woqlQuery().delete_quad("v:Al3", "v:Al4", p, graph),
            )
            ap.updated()
        return ap

    def _box_classes(self, prefix, classes, excepts, graph=None):
        if graph is None:
            graph = self.graph
        prefix = prefix or "scm:"
        subs = []
        for i in classes:
            subs.append(self.woqlQuery().sub(classes[i], "v:Cid"))
        nsubs = []
        for i in excepts:
            nsubs.append(self.woqlQuery().woql_not().sub(excepts[i], "v:Cid"))
        idgens = [
            self.woqlQuery().re("#(.)(.*)", "v:Cid", ["v:AllB", "v:FirstB", "v:RestB"]),
            self.woqlQuery().lower("v:FirstB", "v:Lower"),
            self.woqlQuery().concat(["v:Lower", "v:RestB"], "v:Propname"),
            self.woqlQuery().concat(["Scoped", "v:FirstB", "v:RestB"], "v:Cname"),
            self.woqlQuery().idgen(prefix, ["v:Cname"], "v:ClassID"),
            self.woqlQuery().idgen(prefix, ["v:Propname"], "v:PropID"),
        ]
        woql_filter = self.woqlQuery().woql_and(
            self.woqlQuery().quad("v:Cid", "rdf:type", "owl:Class", graph),
            self.woqlQuery().woql_not().node("v:Cid").abstract(graph),
            self.woqlQuery().woql_and(*idgens),
            self.woqlQuery().quad("v:Cid", "label", "v:Label", graph),
            self.woqlQuery().concat(
                "Box Class generated for class v:Cid", "v:CDesc", graph
            ),
            self.woqlQuery().concat(
                "Box Property generated to link box v:ClassID to class v:Cid",
                "v:PDesc",
                graph,
            ),
        )
        if len(subs):
            if len(subs) == 1:
                woql_filter.woql_and(subs[0])
            else:
                woql_filter.woql_and(self.woqlQuery().woql_or(*subs))
        if nsubs.len():
            woql_filter.woql_and(woqlQuery().woql_and(*nsubs))
        cls = (
            self.WOQLSchema(graph)
            .add_class("v:ClassID")
            .label("v:Label")
            .description("v:CDesc")
        )
        prop = (
            self.WOQLSchema(graph)
            .add_property("v:PropID", "v:Cid")
            .label("v:Label")
            .description("v:PDesc")
            .domain("v:ClassID")
        )
        nq = self.woqlQuery().when(woql_filter).woql_and(cls, prop)
        return nq._updated()

    def _generate_choice_list(
        self,
        cls=None,
        clslabel=None,
        clsdesc=None,
        choices=[],
        graph=None,
        parent=None,
    ):
        if graph is None:
            graph = self.graph
        clist = []
        if cls.indexOf(":") == -1:
            listid = "_:" + cls
        else:
            listid = "_:" + cls.split(":")[1]
        lastid = listid
        wq = self.WOQLSchema().add_class(cls, graph).label(clslabel)
        if clsdesc is not None:
            wq.description(clsdesc)
        if parent is not None:
            wq.parent(parent)
        confs = [wq]
        for i in choices:
            if choices[i] is None:
                continue
            if type(choices[i]) == list:
                chid = choices[i][0]
                clab = choices[i][1]
                desc = choices[i][2] or False
            else:
                chid = choices[i]
                clab = utils.labelFromURL(chid)
                desc = False
            cq = self.woqlQuery().insert(chid, cls, graph).label(clab)
            if desc is not None:
                cq.description(desc)
            confs.append(cq)
            if i < len(choices) == -1:
                nextid = listid + "_" + i
            else:
                nextid = "rdf:nil"
            clist.append(self.woqlQuery().add_quad(lastid, "rdf:first", chid, graph))
            clist.append(self.woqlQuery().add_quad(lastid, "rdf:rest", nextid, graph))
            lastid = nextid
        oneof = self.woqlQuery().woql_and(
            self.woqlQuery().add_quad(cls, "owl:oneOf", listid, graph), *clist
        )
        return self.woqlQuery().woql_and(*confs, oneof)

    def _libs(self, libs, parent, graph, prefix):
        bits = []
        if libs.indexOf("xdd") != -1:
            bits.append(self._load_xdd(graph))
            if libs.indexOf("box") != -1:
                bits.append(self.load_xdd_boxes(parent, graph, prefix))
                bits.append(self.load_xsd_boxes(parent, graph, prefix))
        elif libs.indexOf("box") != -1:
            bits.append(self.load_xsd_boxes(parent, graph, prefix))
        if len(bits) > 1:
            return self.woqlQuery().woql_and(*bits)
        return bits[0]

    def _load_xdd(self, graph=None):
        if graph is None:
            graph = self.graph
        return self.woqlQuery().woql_and(
            # geograhpic datatypes
            self._add_datatype(
                "xdd:coordinate",
                "Coordinate",
                "A latitude / longitude pair making up a coordinate, encoded as: [lat,long]",
                graph,
            ),
            self._add_datatype(
                "xdd:coordinatePolygon",
                "Coordinate Polygon",
                "A JSON list of [[lat,long]] coordinates forming a closed polygon.",
                graph,
            ),
            self._add_datatype(
                "xdd:coordinatePolyline",
                "Coordinate Polyline",
                "A JSON list of [[lat,long]] coordinates.",
                graph,
            ),
            # uncertainty range datatypes
            self._add_datatype(
                "xdd:dateRange",
                "Date Range",
                "A date (YYYY-MM-DD) or an uncertain date range [YYYY-MM-DD1,YYYY-MM-DD2]. "
                + "Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            self._add_datatype(
                "xdd:decimalRange",
                "Decimal Range",
                "Either a decimal value (e.g. 23.34) or an uncertain range of decimal values "
                + "(e.g.[23.4, 4.143]. Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            self._add_datatype(
                "xdd:integerRange",
                "Integer Range",
                "Either an integer (e.g. 30) or an uncertain range of integers [28,30]. "
                + "Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            self._add_datatype(
                "xdd:gYearRange",
                "Year Range",
                "A year (e.g. 1999) or an uncertain range of years: (e.g. [1999,2001])."
                + "Enables uncertainty to be encoded directly in the data",
                graph,
            ),
            # string refinement datatypes
            self._add_datatype("xdd:email", "Email", "A valid email address", graph),
            self._add_datatype(
                "xdd:html", "HTML", "A string with embedded HTML", graph
            ),
            self._add_datatype("xdd:json", "JSON", "A JSON encoded string", graph),
            self._add_datatype("xdd:url", "URL", "A valid http(s) URL", graph),
        )

    def _add_datatype(self, d_id, label, descr, graph=None):
        if graph is None:
            graph = self.graph
        # utility function for creating a datatype in woql
        dt = self, woqlQuery().insert(d_id, "rdfs:Datatype", graph).label(label)
        if descr is not None:
            dt.description(descr)
        return dt

    def load_xsd_boxes(self, parent, graph, prefix):
        # Loads box classes for all of the useful xsd classes the format is to generate the box classes for xsd:anyGivenType
        # as class(prefix:AnyGivenType) -> property(prefix:anyGivenType) -> datatype(xsd:anyGivenType)
        return self.woqlQuery().woql_and(
            self._box_datatype(
                "xsd:anySimpleType",
                "Any Simple Type",
                "Any basic data type such as string or integer. An xsd:anySimpleType value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:string",
                "String",
                "Any text or sequence of characters",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:boolean",
                "Boolean",
                "A true or false value. An xsd:boolean value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:decimal",
                "Decimal",
                "A decimal number. An xsd:decimal value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:double",
                "Double",
                "A double-precision decimal number. An xsd:double value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:float",
                "Float",
                "A floating-point number. An xsd:float value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:time",
                "Time",
                "A time. An xsd:time value. hh:mm:ss.ssss",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:date",
                "Date",
                "A date. An xsd:date value. YYYY-MM-DD",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:dateTime",
                "Date Time",
                "A date and time. An xsd:dateTime value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:dateTimeStamp",
                "Date-Time Stamp",
                "An xsd:dateTimeStamp value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:gYear",
                "Year",
                " A particular 4 digit year YYYY - negative years are BCE.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:gMonth",
                "Month",
                "A particular month. An xsd:gMonth value. --MM",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:gDay",
                "Day",
                "A particular day. An xsd:gDay value. ---DD",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:gYearMonth",
                "Year / Month",
                "A year and a month. An xsd:gYearMonth value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:gMonthDay",
                "Month / Day",
                "A month and a day. An xsd:gMonthDay value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:duration",
                "Duration",
                "A period of time. An xsd:duration value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:yearMonthDuration",
                "Year / Month Duration",
                "A duration measured in years and months. An xsd:yearMonthDuration value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:dayTimeDuration",
                "Day / Time Duration",
                "A duration measured in days and time. An xsd:dayTimeDuration value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:byte", "Byte", "An xsd:byte value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:short", "Short", "An xsd:short value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:integer",
                "Integer",
                "A simple number. An xsd:integer value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:long", "Long", "An xsd:long value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:unsignedByte",
                "Unsigned Byte",
                "An xsd:unsignedByte value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:unsignedInt",
                "Unsigned Integer",
                "An xsd:unsignedInt value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:unsignedLong",
                "Unsigned Long Integer",
                "An xsd:unsignedLong value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:positiveInteger",
                "Positive Integer",
                "A simple number greater than 0. An xsd:positiveInteger value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:nonNegativeInteger",
                "Non-Negative Integer",
                "A simple number that can't be less than 0. An xsd:nonNegativeInteger value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:negativeInteger",
                "Negative Integer",
                "A negative integer. An xsd:negativeInteger value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:nonPositiveInteger",
                "Non-Positive Integer",
                "A number less than or equal to zero. An xsd:nonPositiveInteger value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:base64Binary",
                "Base 64 Binary",
                "An xsd:base64Binary value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:anyURI",
                "Any URI",
                "Any URl. An xsd:anyURI value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:language",
                "Language",
                "A natural language identifier as defined by by [RFC 3066] . An xsd:language value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:normalizedString",
                "Normalized String",
                "An xsd:normalizedString value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:token", "Token", "An xsd:token value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:NMTOKEN", "NMTOKEN", "An xsd:NMTOKEN value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:Name", "Name", "An xsd:Name value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:NCName", "NCName", "An xsd:NCName value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:NOTATION",
                "NOTATION",
                "An xsd:NOTATION value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xsd:QName", "QName", "An xsd:QName value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:ID", "ID", "An xsd:ID value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:IDREF", "IDREF", "An xsd:IDREF value.", parent, graph, prefix
            ),
            self._box_datatype(
                "xsd:ENTITY", "ENTITY", "An xsd:ENTITY value.", parent, graph, prefix
            ),
        )

    def load_xdd_boxes(self, parent, graph, prefix):
        # Generates a query to create box classes for all of the xdd datatypes. the format is to generate the box classes for xdd:anyGivenType
        # as class(prefix:AnyGivenType) -> property(prefix:anyGivenType) -> datatype(xdd:anyGivenType)
        return self.woqlQuery().woql_and(
            self._box_datatype(
                "xdd:coordinate",
                "Coordinate",
                "A particular location on the surface of the earth, defined by latitude and longitude . An xdd:coordinate value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xdd:coordinatePolygon",
                "Geographic Area",
                "A shape on a map which defines an area. within the defined set of coordinates   An xdd:coordinatePolygon value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xdd:coordinatePolyline",
                "Coordinate Path",
                "A set of coordinates forming a line on a map, representing a route. An xdd:coordinatePolyline value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype("xdd:url", "URL", "A valid url.", parent, graph, prefix),
            self._box_datatype(
                "xdd:email", "Email", "A valid email address.", parent, graph, prefix
            ),
            self._box_datatype(
                "xdd:html", "HTML", "A safe HTML string", parent, graph, prefix
            ),
            self._box_datatype("xdd:json", "JSON", "A JSON Encoded String"),
            self._box_datatype(
                "xdd:gYearRange",
                "Year",
                "A 4-digit year, YYYY, or if uncertain, a range of years. An xdd:gYearRange value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xdd:integerRange",
                "Integer",
                "A simple number or range of numbers. An xdd:integerRange value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xdd:decimalRange",
                "Decimal Number",
                "A decimal value or, if uncertain, a range of decimal values. An xdd:decimalRange value.",
                parent,
                graph,
                prefix,
            ),
            self._box_datatype(
                "xdd:dateRange",
                "Date Range",
                "A date or a range of dates YYYY-MM-DD",
                parent,
                graph,
                prefix,
            ),
        )

    def _box_datatype(
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
        if graph is None:
            graph = self.graph
        prefix = prefix or "scm:"
        ext = datatype.split(":")[1]
        box_class_id = prefix + ext.charAt(0).toUpperCase() + ext.slice(1)
        box_prop_id = prefix + ext.charAt(0).toLowerCase() + ext.slice(1)
        box_class = self._add_class(box_class_id, graph).label(label)
        box_class.description("Boxed Class for " + datatype)
        if parent is not None:
            box_class.parent(parent)
        box_prop = (
            self._add_property(box_prop_id, datatype, graph)
            .label(label)
            .domain(box_class_id)
        )
        if descr is not None:
            box_prop.description(descr)
        return self.woqlQuery().woql_and(box_class, box_prop)
