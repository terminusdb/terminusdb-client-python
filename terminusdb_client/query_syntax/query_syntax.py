from ..woqlquery import WOQLQuery, Var, Doc # noqa
import re
import sys

__module = sys.modules[__name__]

__exported = ['Var', 'Doc']

for attribute in dir(WOQLQuery()):
    if (isinstance(attribute, str)
        and re.match('^[^_].*', attribute)
        and not attribute == 're'):

        _woql_obj_fun = getattr(WOQLQuery(), attribute)

        __exported.append(attribute)

        def __create_a_function(function, *args, **kwargs):
            def __woql_fun(*args, **kwargs):
                return function(*args, **kwargs)
            return __woql_fun

        setattr(__module, attribute, __create_a_function(_woql_obj_fun))

__all__ = __exported
