from enum import Enum

def is_enum(datatype: type):
    try:
        return datatype == Enum or issubclass(datatype, Enum)
    except:
        return False