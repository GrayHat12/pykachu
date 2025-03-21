from abc import ABC, abstractmethod
import typing as tp
import inspect
import json

T = tp.TypeVar('T')

__GLOBAL_SUPPORT_REGISTER: dict[type | tp.Callable[[tp.Type], bool], tp.Type['SupportInterface']] = {}

def __is_valid_callable(data_type):
    if callable(data_type):
        try:
            inspect.signature(data_type)
        except:
            return False
        return data_type.__name__.startswith("is_")
    else:
        return False

def register_support_class(data_type: type | tp.Callable[[tp.Type], bool]):
    """
    Decorator to regiser a serialize support for your datatype

    Args:
        datatype (`type` | `Callable[[Type], bool]`): Register it against a type or a function which when given a type returns `True` if the decorated class can parse/serialize it

    Example usage::
    ```py
    @register_support_class(int)
    class IntSupport(SupportInterface):
        @staticmethod
        def serialize(value):
            return value
        @staticmethod
        def parse(data_type: type, value, strict: bool):
            if isinstance(value, int) or not strict:
                return value
            raise ValueError(f"{type(value)=} {value=} expected to be an int")
    ```
    """
    global __GLOBAL_SUPPORT_REGISTER
    def wrapper(cls: tp.Type['SupportInterface']):
        __GLOBAL_SUPPORT_REGISTER[data_type] = cls
        return cls
    return wrapper

def deregister_support_class(data_type: type | tp.Callable[[tp.Type], bool]):
    """
    Decorator to deregister support for a datatype

    Args:
        datatype (`type` | `Callable[[Type], bool]`): Deregister any SupportInterface previously registered against this input

    Example usage::
    ```py
    deregister_support_class(int)
    parse(int, 10, True) # will fail because the serialization support was deregistered
    ```
    """
    global __GLOBAL_SUPPORT_REGISTER
    if data_type in __GLOBAL_SUPPORT_REGISTER:
        del __GLOBAL_SUPPORT_REGISTER[data_type]

def parse(data_type: tp.Type[T], value, strict: bool = False) -> T:
    """
    This function parses a value in this specific datatype

    Args:
        data_type (`Type[T]`): The datatype to parse the value to.
        value (`Any`): A serialized value to be parsed.
        strict (`bool = Falsse`): if `True`, failure to parse returns an error, else the object is loosely parsed and no error is raised

    Returns:
        T: Instance of the datatype with value parsed

    Example:
    ```py
    @dataclass
    class Rectangle:
        length: float
        width: float
    rec = Rectangle(length=10.0, width=5.5)
    serialized_dict = serialize(rec)
    parsed_rectangle = parse(Rectangle, serialized_dict, True)
    parsed_rectangle.length, parsed_rectangle.width # 10.0, 5.5
    ```
    """
    global __GLOBAL_SUPPORT_REGISTER
    resolver = None
    origin = tp.get_origin(data_type)
    if data_type in __GLOBAL_SUPPORT_REGISTER:
        resolver = __GLOBAL_SUPPORT_REGISTER[data_type]
    else:
        # if not origin:
        #     # consider it any
        #     return parse(tp.Any, value, strict)
        if origin in __GLOBAL_SUPPORT_REGISTER:
            resolver = __GLOBAL_SUPPORT_REGISTER[origin]
    
    if not resolver:
        for matcher, potential_resolver in __GLOBAL_SUPPORT_REGISTER.items():
            if callable(matcher) and __is_valid_callable(matcher) and (matcher(data_type) or matcher(origin)):
                resolver = potential_resolver
                break
    
    if not resolver:
        if strict:
            raise ValueError(f'no registered support class found for {data_type=}')
        else:
            return value
    # print(f"Using {resolver=} for {data_type=} {value=}")
    return resolver.parse(data_type, value, strict)

def serialize(value):
    """
    This function serialized a python object

    Args:
        value (`Any`): A value to be serialized.

    Returns:
        Any: Instance of the datatype with value parsed

    Example:
    ```py
    @dataclass
    class Rectangle:
        length: float
        width: float
    rec = Rectangle(length=10.0, width=5.5)
    serialize(rec) # {"length": 10.0, "width": 5.5}
    ```
    """
    def default_handler(val):
        global __GLOBAL_SUPPORT_REGISTER
        resolver = None
        if type(val) in __GLOBAL_SUPPORT_REGISTER:
            resolver = __GLOBAL_SUPPORT_REGISTER[type(val)]
        else:
            for key, v in __GLOBAL_SUPPORT_REGISTER.items():
                if callable(key) and __is_valid_callable(key) and key(type(val)):
                    resolver = v
        if not resolver:
            raise ValueError(f'no registered support class found for {type(val)=} {val=}')
        return resolver.serialize(val)
    return json.loads(json.dumps(value, default=default_handler))

class SupportInterface(ABC):
    """
    This class provides a standard interface for all devs to implement serialization and parsing strategies for any data type.

    Example:
    ```py
    @register_support_class(bytes) # don't forget to register your function
    class BytesSupport(SupportInterface): # Inherit from SupportInterface
        @staticmethod
        def serialize(value: bytes): # Implement serialization
            return value.hex() # bytes types are to be stored as hex strings
        @staticmethod
        def parse(data_type: type, value, strict: bool): # Implement parsing
            if isinstance(value, bytes): # if value is already bytes use it directly
                return value
            if isinstance(value, str): # if value is str, parse it as bytes from hex
                return bytes.fromhex(value)
            if strict: # incase of failure, check for strict mode, if strict, raise Error else let it continue
                raise ValueError(f"{type(value)=} {value=} expected to be a hex string or bytes")
            return value
    ```
    """

    @staticmethod
    @abstractmethod
    def serialize(value: T):
        """
        Abstract interface for serialization, Supposed to return a json serializable data type
        """
        pass

    @staticmethod
    @abstractmethod
    def parse(data_type: type, value, strict: bool) -> T:
        """
        Abstract interface for parsing, Supposed to parse the `value` and return an object of `data_type`
        """
        pass