# connectionCapabilities.py

from .api_endpoint_const import APIEndpointConst

# const UTILS = require('./utils.js');
from .errorMessage import ErrorMessage
from .errors import AccessDeniedError


"""
    Creates an entry in the connection registry for the server
    and all the databases that the client has access to
    maps the input authorties to a per-db array for internal storage and easy
    access control checks
    {doc:dbid => {terminus:authority =>
    [terminus:woql_select, terminus:create_document, auth3, ...]}}
"""


class ConnectionCapabilities:
    def __init__(self):
        self.connection = {}
        self.user = None
        self._jsonld_context = {}
        self._terminusdb_context = {}

    def _action_to_array(self, actions):
        if isinstance(actions, list) is False:
            return []
        action_list = []
        for item in actions:
            action_list.append(item["@id"])

        return action_list

    def set_capabilities(self, capabilities=None):
        self.connection = {}
        if capabilities is not None:
            self.capabilitiesKeys = capabilities.keys()
        else:
            self.capabilitiesKeys = []

        for pred in self.capabilitiesKeys:
            if (pred == "terminus:authority") and (pred in capabilities):
                if type(capabilities[pred]) == list:
                    auths = capabilities[pred]
                else:
                    auths = [capabilities[pred]]
                for item in auths:
                    access = item["terminus:access"]
                    scope = access["terminus:authority_scope"]
                    actions = access["terminus:action"]
                    if type(scope) != list:
                        scope = [scope]
                    if type(actions) == list:
                        action_arr = [obj["@id"] for obj in actions]
                    else:
                        action_arr = []
                    for nrec in scope:
                        if nrec["@id"] not in self.connection:
                            self.connection[nrec["@id"]] = nrec
                        self.connection[nrec["@id"]]["terminus:authority"] = action_arr
            elif pred == "@context":
                self._load_connection_context(capabilities[pred])
            else:
                self.connection[pred] = capabilities[pred]
            self.user = self._extract_user_info(capabilities)

    def _extract_user_info(self, capabilities):
        info = {}
        if capabilities.get("rdfs:comment"):
            info["notes"] = capabilities["rdfs:comment"].get("@value")
        if capabilities.get("rdfs:label"):
            info["name"] = capabilities["rdfs:label"].get("@value")
        if capabilities.get("terminus:agent_name"):
            info["id"] = capabilities["terminus:agent_name"].get("@value")
        if capabilities.get("terminus:commit_log_id"):
            info["author"] = capabilities["terminus:commit_log_id"].get("@value")
        return info

    def get_user(self):
        return self.user

    def author(self):
        if self.user.get("author"):
            return self.user.get("author")
        else:
            return self.user.get("id") + " " + self.user.get("name")

    def _form_resource_name(self, dbid, account):
        if dbid == "terminus":
            return "terminus"
        return f"{account}|{dbid}"

    def find_resource_document_id(self, dbid, account):
        testrn = self._form_resource_name(dbid, account)
        for pred in self.connection.keys():
            rec = self.connection[pred]
            if "terminus:resource_name" in rec:
                resource_name = rec["terminus:resource_name"]
                if (
                    "@value" in resource_name
                    and rec["terminus:resource_name"]["@value"] == testrn
                ):
                    return pred
        return None

    def _load_connection_context(self, context_dict):
        self._terminusdb_context = context_dict
        for prefix in context_dict.keys():
            if prefix != "doc":
                self._jsonld_context[prefix] = context_dict[prefix]

    def get_context_for_outbound_query(self, woql_dict, dbid):
        if woql_dict.get("@context"):
            return woql_dict.get("@context")
        else:
            ret = {}
            for prefix in self._jsonld_context.keys():
                if prefix != "doc":
                    ret[prefix] = self._jsonld_context[prefix]
            return ret

    def get_json_context(self):
        return self._jsonld_context

    def get_terminus_context(self):
        return self._terminusdb_context

    def capabilities_permit(self, action, dbid=None, account=None):
        if action == APIEndpointConst.CREATE_DATABASE:
            rec = self._get_server_record()
        elif dbid is not None:
            rec = self._get_db_record(dbid, account)
        else:
            raise ValueError("no dbid provided in capabilities check ", action, dbid)
        if rec:
            auths = rec.get("terminus:authority")
            terminus_action_name = "terminus:" + action
            if auths and terminus_action_name in auths:
                return True
            else:
                raise ValueError("No record found for connection: ", action, dbid)
        raise AccessDeniedError(
            ErrorMessage.getAccessDeniedMessage(action, dbid, account)
        )

    def _get_server_record(self):
        """retrieves the meta-data record returned by connect for the connected server
           Returns
           =======
           {terminus:Server} JSON server record as returned by WOQLClient.connect
        """
        for obj in self.connection.values():
            if isinstance(obj, dict) and obj.get("@type") == "terminus:Server":
                return obj
        return None

    def _get_db_record(self, dbid, account):
        """retrieves the meta-data record returned by connect for a particular database
           Returns
           =======
           {terminus:Database} terminus:Database JSON document as returned by WOQLClient.connect
        """
        docid = self.find_resource_document_id(dbid, account)
        if docid is not None:
            return self.connection[docid]
        return None

    def _extract_metadata(self, dbrec):
        meta = {"db": "", "account": "", "title": "", "description": ""}
        if ("terminus:resource_name" in dbrec) and (
            "@value" in dbrec["terminus:resource_name"]
        ):
            rn = dbrec["terminus:resource_name"]["@value"]
            if rn == "terminus":
                meta["db"] = rn
            elif type(rn) is str and rn:
                bits = rn.split("|")
                if len(bits) == 1:
                    meta["db"] = rn
                else:
                    meta["account"] = bits[0]
                    meta["db"] = bits[1]
        if "rdfs:label" in dbrec:
            if type(dbrec["rdfs:label"]) == list:
                label = dbrec["rdfs:label"][0]
            else:
                label = dbrec["rdfs:label"]
            if label is not None and label and "@value" in label:
                meta["title"] = label["@value"]
            else:
                meta["title"] = meta["db"]
        if "rdfs:comment" in dbrec:
            if type(dbrec["rdfs:comment"]) == list:
                cmt = dbrec["rdfs:comment"][0]
            else:
                cmt = dbrec["rdfs:comment"]
            if cmt is not None and cmt and "@value" in cmt:
                meta["description"] = cmt["@value"]
        return meta

    def _get_db_metadata(self, dbid, account):
        dbrec = self._get_db_record(dbid, account)
        if dbrec is not None:
            return self._extract_metadata(dbrec)

    def remove_db(self, dbid=None, account=None):
        """
          removes a database record from the connection registry (after deletion, for example)
          @param {String} [dbid] optional DB ID - if omitted current connection config db will be used
          @param {String} [srvr] optional server URL - if omitted current connection config server will be used
          @returns {[terminus:Database]} array of terminus:Database JSON documents as returned by WOQLClient.
        """
        docid = self.find_resource_document_id(dbid, account)
        if docid is not None:
            del self.connection[docid]

    def get_server_db_records(self):
        """
          returns all records about databases on the currently connected server
        """
        dbrecs = {}
        for oid in self.connection:
            if (
                isinstance(self.connection[oid], dict)
                and self.connection[oid].get("@type") == "terminus:Database"
            ):
                dbrecs[oid] = self.connection[oid]
        return dbrecs

    def get_server_db_metadata(self):
        """
          returns a meta data list {db: title: description:}  about all databases on the currently connected server
        """
        dbrecs = self.get_server_db_records()
        metas = []
        for oid in dbrecs:
            met = self._extract_metadata(dbrecs[oid])
            if met is not None:
                metas.append(met)
        return metas
