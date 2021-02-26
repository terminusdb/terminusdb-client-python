# connectionCapabilities.py


# const UTILS = require('./utils.js');

import pprint
import warnings

pp = pprint.PrettyPrinter(indent=4)

"""
    **Deprecated**
    Creates an entry in the connection registry for the server
    and all the databases that the client has access to
    maps the input authorties to a per-db array for internal storage and easy
    access control checks
    {doc:dbid => {system:authority =>
    [system:woql_select, system:create_document, auth3, ...]}}
"""


class ConnectionCapabilities:
    def __init__(self):
        warnings.warn("ConnectionCapabilities is deprecated.", DeprecationWarning)
        self.user = None
        self.dbdocs = {}
        self.orgdocs = {}
        self.databases = None
        self._jsonld_context = {}
        self._systemdb_context = {}

    def _clear(self):
        self.user = None
        self.dbdocs = {}
        self.orgdocs = {}
        self._jsonld_context = {}
        self._systemdb_context = {}

    def set_capabilities(self, capabilities=None):
        self._clear()
        self.databases = None
        if capabilities is not None:
            ctxt = capabilities.get("@context")
            if ctxt is not None:
                self._load_connection_context(ctxt)
        self.user = self._extract_user_info(capabilities)
        return self._extract_database_organizations()

    def get_databases(self):
        if self.databases is None:
            self.databases = self._databases_from_dbdocs()
        return self.databases

    def set_databases(self, newdbs):
        self.databases = newdbs

    def get_database(self, dbid, orgid):
        if self.databases is None:
            self.databases = self._databases_from_dbdocs()
        for db in self.databases:
            if db["id"] == dbid and db["organization"] == orgid:
                return db
        return None

    def get_user(self):
        return self.user

    def author(self):
        if self.user.get("author"):
            return self.user.get("author")
        else:
            return self.user.get("id")

    def _databases_from_dbdocs(self):
        dbs = []
        for docid in self.dbdocs:
            if not self.dbdocs[docid]["system"]:
                dbs.append(self._get_db_rec(self.dbdocs[docid]))
        return dbs

    def set_roles(self, role_output):
        cntnt = role_output.get("bindings")
        if cntnt is None:
            return False
        for pred in cntnt:
            onerec = {}
            onerec["dbdocid"] = pred["Database_ID"]
            onerec["organization"] = pred["Organization"]["@value"]
            roles = self._multiple_rdf_objects(pred["Owner_Role_Obj"], "system:Role")
            self.dbdocs[onerec["dbdocid"]] = roles
        self._extract_database_organizations()

        rdb = role_output.get("databases")
        if rdb:
            self.set_databases(rdb)
        odb = role_output.get("organizations")
        if odb:
            self.set_organizations(odb)

    def get_organizations(self):
        if self.organizations is None:
            self.organizations = self._organizations_from_orgdocs()
        return self.organizations

    def set_organizations(self, newdbs):
        self.organizations = newdbs

    def get_organization(self, orgid):
        if self.organizations is None:
            self.organizations = self._organizations_from_orgdocs()
        for org in self.organizations:
            if org["id"] == orgid:
                return org
        return None

    def _organizations_from_orgdocs(self):
        return self.orgdocs.values()

    def actions_permitted(self, actions, resnames):
        actlist = self._toarr(actions)
        reslist = self._toarr(resnames)
        for i in actlist.keys():
            for j in reslist.keys():
                if self._roles_cover_resource_action(actlist[i], reslist[j]):
                    return False
        return True

    def get_context_for_outbound_query(self, woql, dbid):
        """TODO: This should be refactored later"""
        return {}

    def _is_system_db(self, dbid):
        if dbid == "_system":
            return True
        return False

    def get_json_context(self):
        return self._jsonld_context

    def set_json_context(self, ctxt):
        self._jsonld_context = ctxt

    def get_system_context(self):
        return self._systemdb_context

    def _roles_cover_resource_action(self, action, resname):
        for docid in self.user["roles"].keys():
            if self._role_covers_resource_action(
                self.user["roles"][docid], action, resname
            ):
                return True
        return False

    def _role_covers_resource_action(self, role, action, resname):
        for docid in role["capabilities"].keys():
            if self._capability_covers_resource_action(
                role["capabilities"][docid], action, resname
            ):
                return True
        return False

    def _capability_covers_resource_action(self, cap, action, resname):
        if action[0:7] != "system:":
            action = "system:" + action
        if action not in cap["actions"]:
            return False
        if resname not in cap["resources"]:
            return False
        return True

    def _extract_user_info(self, capabilities):
        info = self._extract_rdf_basics(capabilities)
        info["id"] = self._single_rdf_value("system:agent_name", capabilities)
        info["author"] = self._single_rdf_value("system:user_identifier", capabilities)
        croles = capabilities.get("system:role")
        if croles is not None:
            info["roles"] = self._multiple_rdf_objects(croles, "system:Role")
        else:
            info["roles"] = []
        return info

    def _extract_user_role(self, jrole):
        nrole = self._extract_rdf_basics(jrole)
        croles = jrole.get("system:capability")
        if croles is not None:
            nrole["capabilities"] = self._multiple_rdf_objects(
                croles, "system:Capability"
            )
        else:
            nrole["capabilities"] = []
        return nrole

    def _extract_role_capability(self, jcap):
        nrole = self._extract_rdf_basics(jcap)
        acts = jcap.get("system:action")
        resources = jcap.get("system:capability_scope")
        if acts is not None:
            nrole["actions"] = self._extract_multiple_ids(acts)
        if resources is not None:
            nrole["resources"] = self._extract_capability_resources(resources)
        return nrole

    def _extract_capability_resources(self, scope):
        rnames = []
        resources = self._toarr(scope)
        for res in resources:
            rnames.append(self._extract_resource_name(res))
            rid = res.get("@id")
            rtype = res.get("@type")
            if not (rid is None or rtype is None):
                exist = self.dbdocs.get(rid)
                if exist is None and (
                    rtype == "system:SystemDatabase" or rtype == "system:Database"
                ):
                    self.dbdocs[rid] = self._extract_database(res)
                if rtype == "system:Organization":
                    self.orgdocs[rid] = self._extract_organization(res)
        return rnames

    def _extract_resource_name(self, jres):
        sys_id = self._single_rdf_value("system:resource_name", jres)
        if sys_id is None:
            sys_id = self._single_rdf_value("system:organization_name", jres)
        if sys_id is None:
            sys_id = self._single_rdf_value("system:database_name", jres)
        return sys_id

    def _extract_database(self, jres):
        db = self._extract_rdf_basics(jres)
        db["id"] = self._extract_resource_name(jres)
        if jres.get("@type") == "system:SystemDatabase":
            db["system"] = True
        else:
            db["system"] = False
        return db

    def _get_db_rec(self, rec):
        urec = {}
        for pred in rec.keys():
            if pred != "system":
                urec[pred] = rec[pred]
        return urec

    def _extract_database_organizations(self):
        for docid in self.dbdocs:
            for odocid in self.orgdocs:
                dbs = self.orgdocs[odocid].get("databases")
                if dbs is not None and docid in dbs:
                    self.dbdocs[docid]["organization"] = self.orgdocs[odocid]["id"]

    def _extract_organization(self, jres):
        org = self._extract_rdf_basics(jres)
        org["id"] = self._extract_resource_name(jres)
        dbs = jres.get("system:organization_database")
        kids = jres.get("system:organization_child")
        incs = jres.get("system:resource_includes")
        if dbs is not None:
            org["databases"] = self._extract_multiple_ids(dbs)
        if kids is not None:
            org["children"] = self._extract_multiple_ids(kids)
        if incs is not None:
            org["includes"] = self._extract_multiple_ids(incs)
        return org

    def _extract_multiple_ids(self, jres):
        jids = self._toarr(jres)
        ids = []
        for k in jids:
            ids.append(k["@id"])
        return ids

    def _multiple_rdf_objects(self, rdf, con_type):
        nvals = {}
        vals = self._toarr(rdf)
        for n in vals:
            if isinstance(n, dict):
                nid = n.get("@id")
                if nid is not None:
                    nvals[nid] = self._extract_rdf_object(con_type, n)
        return nvals

    def _extract_rdf_object(self, con_type, jres):
        if con_type == "system:Role":
            return self._extract_user_role(jres)
        elif con_type == "system:Capability":
            return self._extract_role_capability(jres)

    def _extract_rdf_basics(self, jres):
        info = {}
        info["label"] = self._single_rdf_value("rdfs:label", jres)
        info["comment"] = self._single_rdf_value("rdfs:comment", jres)
        return info

    def _single_rdf_value(self, pred, rdf):
        if rdf.get(pred) is None:
            return ""
        if isinstance(rdf[pred], list):
            return rdf[pred][0]["@value"]
        return rdf[pred]["@value"]

    def _multiple_rdf_values(self, pred, rdf):
        vals = []
        if rdf.get(pred) is None:
            return vals
        rdflist = self._toarr(rdf.get(pred))
        for item in rdflist:
            vals.append(item["@value"])
        return vals

    def _toarr(self, el):
        if isinstance(el, list):
            return el
        return [el]

    def _load_connection_context(self, ctxt):
        self._systemdb_context = ctxt
        for k in ctxt.keys():
            if k != "doc":
                self._jsonld_context[k] = ctxt[k]
