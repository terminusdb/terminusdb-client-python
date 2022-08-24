from ..woqlquery import WOQLQuery, Var, Doc # noqa
import re
import sys

__BARRED = ['re','vars']
__ALLOWED = ['__and__','__or__','__add__']
__module = sys.modules[__name__]

__exported = ['Var', 'Doc']

for attribute in dir(WOQLQuery()):
    if (isinstance(attribute, str) and (re.match('^[^_].*', attribute)
                                        or attribute in __ALLOWED)
            and not attribute in __BARRED):

        __exported.append(attribute)

        def __create_a_function():
            obj = WOQLQuery()
            func = getattr(obj,attribute)
            def __woql_fun(*args, **kwargs):
                return func(*args, **kwargs)
            return __woql_fun

        setattr(__module, attribute, __create_a_function())

__all__ = __exported
