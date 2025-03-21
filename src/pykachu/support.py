"""
Existing Supported Datatype Implementations

Contains the default implementation for serialization and parsing for out of the box supported data types
"""

from .pykachu import register_support_class, SupportInterface, serialize, parse
from dataclasses import is_dataclass, asdict, fields
from datetime import date, datetime
from .helpers import is_enum
from enum import Enum
import typing as tp

@register_support_class(int)
class IntSupport(SupportInterface):
    """
    Strategy for parsing/serializing integer data types
    """
    
    @staticmethod
    def serialize(value):
        return value
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if isinstance(value, int) or not strict:
            return value
        raise ValueError(f"{type(value)=} {value=} expected to be an int")

@register_support_class(bytes)
class BytesSupport(SupportInterface):
    """
    Strategy for parsing/serializing byte data types
    """

    @staticmethod
    def serialize(value: bytes):
        return value.hex()
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return bytes.fromhex(value)
        if strict:
            raise ValueError(f"{type(value)=} {value=} expected to be a hex string or bytes")
        return value

@register_support_class(tp.Any)
class AnySupport(SupportInterface):
    """
    Strategy for parsing/serializing any data type
    """

    @staticmethod
    def serialize(value):
        return value
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        return value

@register_support_class(float)
class FloatSupport(SupportInterface):
    """
    Strategy for parsing/serializing float data type
    """

    @staticmethod
    def serialize(value):
        return value
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if isinstance(value, float) or not strict:
            return value
        raise ValueError(f"{type(value)=} {value=} expected to be an float")

@register_support_class(str)
class StrSupport(SupportInterface):
    """
    Strategy for parsing/serializing str data type
    """

    @staticmethod
    def serialize(value):
        return value
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if isinstance(value, str) or not strict:
            return value
        raise ValueError(f"{type(value)=} {value=} expected to be an str")

@register_support_class(bool)
class BoolSupport(SupportInterface):
    """
    Strategy for parsing/serializing bool data type
    """

    @staticmethod
    def serialize(value):
        return value
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if isinstance(value, bool) or not strict:
            return value
        raise ValueError(f"{type(value)=} {value=} expected to be an bool")

@register_support_class(tp.Union)
class UnionSupport(SupportInterface):
    """
    Strategy for parsing/serializing Union data type
    """

    @staticmethod
    def serialize(value):
        return value
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        args = tp.get_args(data_type)
        if not args:
            raise ValueError(f"Invalid {data_type=}. Union type needs args")
        if type(None) in args and value is None:
            return value
        for arg in args:
            try:
                return parse(arg, value, True)
            except:
                continue
        if strict:
            raise ValueError(f"{type(value)=} {value=} did not match any types {args=}")
        return value

@register_support_class(tp.Literal)
class LiteralSupport(SupportInterface):
    """
    Strategy for parsing/serializing Literal data type
    """

    @staticmethod
    def serialize(value):
        return value
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        args = tp.get_args(data_type)
        if not args:
            raise ValueError(f"Invalid {data_type=}. Literal type needs args")
        if type(None) in args and value is None:
            return value
        for arg in args:
            if value == arg:
                return value
        if strict:
            raise ValueError(f"{type(value)=} {value=} did not match any types {args=}")
        return value

@register_support_class(list)
class ListSupport(SupportInterface):
    """
    Strategy for parsing/serializing List data type
    """

    @staticmethod
    def serialize(value):
        return [serialize(item) for item in value]
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if not isinstance(value, tp.Iterable):
            if strict:
                raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
            else:
                return value
        arg = tp.get_args(data_type)
        if not arg:
            return [item for item in value]
        if len(arg) != 1:
            raise ValueError(f"Invalid {data_type=} with {arg=}. list should only have =1 arg")
        arg = arg[0]
        return [parse(arg, item, strict) for item in value]

@register_support_class(set)
class SetSupport(SupportInterface):
    """
    Strategy for parsing/serializing set data type
    """

    @staticmethod
    def serialize(value):
        return [serialize(item) for item in value]
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if not isinstance(value, tp.Iterable):
            if strict:
                raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
            else:
                return value
        arg = tp.get_args(data_type)
        if not arg:
            return set([item for item in value])
        if len(arg) != 1:
            raise ValueError(f"Invalid {data_type=} with {arg=}. list should only have =1 arg")
        arg = arg[0]
        return set([parse(arg, item, strict) for item in value])

@register_support_class(tuple)
class TupleSupport(SupportInterface):
    """
    Strategy for parsing/serializing tuple data type
    """

    @staticmethod
    def serialize(value):
        return [serialize(item) for item in value]
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if not isinstance(value, tp.Iterable):
            if strict:
                raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
            else:
                return value
        args = tp.get_args(data_type)
        if not args:
            return tuple(value)
        if len(value) != len(args):
            if strict:
                raise ValueError(f"{args=} {value=} len mismatch for tuple")
        index_args = 0
        index_items = 0
        value = [item for item in value]
        final = []
        while index_items < len(value):
            arg = ...
            item = ...
            if index_args < len(args):
                arg = args[index_args]
                index_args+=1
            if index_items < len(value):
                item = value[index_items]
                index_items+=1
            if arg is Ellipsis and item is Ellipsis:
                break
            elif arg is not Ellipsis and item is not Ellipsis:
                final.append(parse(arg, item, strict))
            elif arg is Ellipsis and item is not Ellipsis:
                final.append(item)
            else:
                raise ValueError(f"wtf i don't know what to do, i don't think this should ever happen. bachao bachao")
        return tuple(final)

@register_support_class(dict)
class DictSupport(SupportInterface):
    """
    Strategy for parsing/serializing dict data type
    """

    @staticmethod
    def serialize(value: dict):
        return {serialize(key): serialize(val) for key, val in value.items()}
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if not isinstance(value, dict):
            if strict:
                raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
            else:
                return value
        args = tp.get_args(data_type)
        if not args:
            return value
        if len(args) != 2:
            raise ValueError(f"Invalid {data_type=} with {args=}. list should only have =2 arg")
        return {
            parse(args[0], key, strict): parse(args[1], val, strict) for key, val in value.items()
        }

@register_support_class(is_enum)
class EnumSupport(SupportInterface):
    """
    Strategy for parsing/serializing enums
    """

    @staticmethod
    def serialize(value: Enum):
        if isinstance(value.value, (int, float, bool)):
            return value.value
        else:
            return value.name
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        for enumeration in data_type:
            if enumeration.name == value or enumeration.value == value:
                return enumeration
        if strict:
            raise ValueError(f"{value=} invalid for {data_type=}")
        return value

@register_support_class(is_dataclass)
class DataclassSupport(SupportInterface):
    """
    Strategy for parsing/serializing dataclasses
    """

    @staticmethod
    def serialize(value):
        return serialize(asdict(value))
    
    @staticmethod
    def parse(data_type: type, value, strict: bool):
        if not isinstance(value, dict):
            if strict:
                raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
            else:
                return value
        all_fields = fields(data_type)
        # print(f"{all_fields=} {data_type=}")
        final_map = {}
        for field in all_fields:
            if field.name in value:
                # print(f"{field.name=} {field.type=}")
                final_map[field.name] = parse(field.type, value[field.name], strict)
        return data_type(**final_map)

@register_support_class(datetime)
class DatetimeSupport(SupportInterface):
    """
    Strategy for parsing/serializing datetime
    """

    @staticmethod
    def serialize(value: datetime):
        return value.isoformat()
    
    @staticmethod
    def parse(data_type: tp.Type[datetime], value, strict):
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return data_type.fromisoformat(value)
        if strict:
            raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
        else:
            return value

@register_support_class(date)
class DatetimeSupport(SupportInterface):
    """
    Strategy for parsing/serializing date
    """

    @staticmethod
    def serialize(value: date):
        return value.isoformat()
    
    @staticmethod
    def parse(data_type: tp.Type[date], value, strict):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return data_type.fromisoformat(value)
        if strict:
            raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
        else:
            return value