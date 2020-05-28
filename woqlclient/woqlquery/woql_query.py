from .woql_core import WOQLCore


class WOQLQuery(WOQLCore):
    def __init__(self, query=None):
        """defines the internal functions of the woql query object - the language API is defined in WOQLQuery

        Parameters
        ----------
        query json-ld query for initialisation"""
        super().__init__(query)

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
