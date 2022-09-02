from ..woqlquery import WOQLQuery, Var, Vars, Doc # noqa
import re
import sys

__BARRED = ['re', 'vars']
__ALLOWED = ['__and__', '__or__', '__add__']
__module = sys.modules[__name__]
__exported = ['Var', 'Vars', 'Doc']


def __create_a_function(attribute):
    def __woql_fun(*args, **kwargs):
        obj = WOQLQuery()
        func = getattr(obj, attribute)
        return func(*args, **kwargs)
    return __woql_fun


for attribute in dir(WOQLQuery()):
    if (isinstance(attribute, str) and (re.match('^[^_].*', attribute)
                                        or attribute in __ALLOWED)
            and attribute not in __BARRED):

        __exported.append(attribute)

        setattr(__module, attribute, __create_a_function(attribute))

__all__ = __exported
