import datetime as dt
from typing import ForwardRef, Union

COVERT_TYPE = {
    str: "xsd:string",
    bool: "xsd:boolean",
    float: "xsd:decimal",
    int: "xsd:integer",
    dt.datetime: "xsd:dataTime",
    dt.date: "xsd:date",
    dt.time: "xsd:time",
    dt.timedelta: "xsd:duration",
}


def convert_type(input_type: type):
    if input_type in COVERT_TYPE:
        return COVERT_TYPE[input_type]
    elif hasattr(input_type, "__module__") and input_type.__module__ == "typing":
        if isinstance(input_type, ForwardRef):
            return input_type.__forward_arg__
        elif input_type._name:
            return [input_type._name.lower(), *map(convert_type, input_type.__args__)]
        else:
            return ["optional", *map(convert_type, input_type.__args__[:-1])]
        return str(input_type)


def convert_array(input_array: Union[list, set]):
    pass
