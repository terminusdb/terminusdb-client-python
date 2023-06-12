#!/usr/bin/env python3
import inspect
import json

import terminusdb_client
from numpydoc.docscrape import FunctionDoc, ClassDoc

def parameter_to_document(param):
    return {'@type': 'Parameter', 'type': param.type, 'name': param.name, 'summary': "\n".join(param.desc)}

classes_to_scan = ['Client']#, 'WOQLQuery']
classes = []

for name, obj in inspect.getmembers(terminusdb_client):
    if inspect.isclass(obj) and 'terminusdb' in str(obj):
        if name in classes_to_scan:
            docstring_class = ClassDoc(obj)
            class_params = [parameter_to_document(x) for x in docstring_class['Attributes']]
            functions = []
            for func in obj.__dict__.values():
                if callable(func) and func.__doc__:
                    docstring_function = FunctionDoc(func)
                    parameters = [parameter_to_document(x) for x in docstring_function['Parameters']]
                    examples = '\n'.join(docstring_function['Examples'])
                    if len(docstring_function['Returns']) > 0:
                        ret = docstring_function['Returns'][0] # Functions always have one return
                        returns = {'@type': 'Returns', 'name': '', 'type': ret.type}
                        if len(ret.desc) > 0:
                            returns['summary'] = "\n".join(ret.desc)
                    else:
                        returns = {'@type': 'Returns', 'name': '', 'type': 'void'}
                    function_obj = {'@type': 'Definition',
                                    'name': func.__name__,
                                    'parameters': parameters,
                                    'returns': returns,
                                    'examples': [examples] if examples != "" else None,
                                    'summary': "\n".join(docstring_function['Summary'])}
                    functions.append(function_obj)
            class_obj = {'@type': 'Class', 'name': name, 'summary': "\n".join(docstring_class['Summary']), 'memberVariables': class_params, 'memberFunctions': functions}
            classes.append(class_obj)

application = {
    '@type': 'Application',
    'version': terminusdb_client.__version__.__version__,
    'name': terminusdb_client.__version__.__title__,
    'summary': terminusdb_client.__version__.__description__,
    'language': 'Python',
    'license': terminusdb_client.__version__.__license__,
    'modules': [
        {
            '@type': 'Module',
            'name': 'terminusdb_client',
            'classes': classes
         }
    ]}

print(json.dumps(application))
