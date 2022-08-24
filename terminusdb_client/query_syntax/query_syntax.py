from ..woqlquery import WOQLQuery, Var, Doc
import re as regexp
import sys


__module = sys.modules[__name__]
for attribute in dir(WOQLQuery()):
    if isinstance(attribute,str) and regexp.match('^[^_].*', attribute):
        print(attribute)
        _woql_obj_fun = getattr(WOQLQuery(),attribute)
        def __create_a_function(function, *args, **kwargs):
            def __woql_fun(*args, **kwargs):
                return function(*args, **kwargs)
            return __woql_fun

        setattr(__module, attribute, __create_a_function(_woql_obj_fun))
