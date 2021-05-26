import datetime as dt
from typing import ForwardRef, List, Optional, Set, Union

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


def to_woql_type(input_type: type):
    if input_type in COVERT_TYPE:
        return COVERT_TYPE[input_type]
    elif hasattr(input_type, "__module__") and input_type.__module__ == "typing":
        if isinstance(input_type, ForwardRef):
            return input_type.__forward_arg__
        elif input_type._name:
            return [input_type._name.lower(), *map(to_woql_type, input_type.__args__)]
        else:
            return ["optional", *map(to_woql_type, input_type.__args__[:-1])]
    else:
        return str(input_type)


def from_woql_type(input_type: Union[str, list]):
    invert_type = {v: k for k, v in COVERT_TYPE.items()}
    if isinstance(input_type, "list"):
        if input_type[0] == "list":
            return List[input_type[1]]
        elif input_type[0] == "set":
            return Set[input_type[1]]
        elif input_type[0] == "optional":
            return Optional[input_type[1]]
    elif input_type in invert_type:
        return invert_type[input_type]
    else:
        raise ValueError("Input type cannot be converted to Python type")


def convert_array(input_array: Union[list, set]):
    pass
