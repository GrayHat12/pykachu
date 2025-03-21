# Pykachu
![python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
[![github](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/GrayHat12/pykachu)

## Introduction

Lightweigth and extensible serializer for python
Light and extensible, define how data should be in pure, canonical Python 3; serialize and parse with Pykachu.

This script allows the you to serialize python objects and parse them 
back with ease. 

Supports most standard data types out of the box and 
let's you specify a serialization and parsing strategy for your new
data types. 

You can even modify the strategy for existing supported data
types if you want.

This file can also be imported as a module and contains the following
exports:

* `register_support_class` - register support class for parsing/serializing data types
* `deregister_support_class` - deregister any previously registered class for the given data type
* `parse` - parse data to the mentioned type
* `serialize` - serialize python object
* `SupportInterface` - Abstract interface to implement for adding a new data type support

## Installation

Install using `pip install pykachu` or `conda install pykachu`.

## A Simple Example

```py
from typing import Optional
from datetime import datetime
from pykachu import serialize, parse
from dataclasses import dataclass

@dataclass
class User:
    id: int
    name: str
    signup_ts: Optional[datetime] = None
    friends: list[int] = []

user = User(id=123, name="John Doe", signup_ts=datetime.now(), friends=[1,2])
print(user)
#> User(id=123, name='John Doe', signup_ts=datetime.datetime(2025, 3, 22, 3, 26, 1, 551584), friends=[1, 2])
print(serialize(user))
#> {'id': 123, 'name': 'John Doe', 'signup_ts': '2025-03-22T03:26:01.551584', 'friends': [1, 2]}
new_user = parse(User, serialize(user), True)
print(new_user)
#> User(id=123, name='John Doe', signup_ts=datetime.datetime(2025, 3, 22, 3, 26, 1, 551584), friends=[1, 2])
```

### Support for custom types

Let's imagine a scenario where you have a custom class you wanna make serializable.
```py
class Rectangle:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    def area(self):
        return self.x * self.y
```

And we'll go through on how we can achieve this.
```py
from typing import Type
from pykachu import serialize, parse, SupportInterface, register_support_class

@register_support_class(Rectangle)
class RectangleSupport(SupportInterface):
    """
    Strategy for parsing/serializing our custom Rectangle class
    """

    @staticmethod
    def serialize(value: Rectangle):
        return {"x": value.x, "y": value.y}
    
    @staticmethod
    def parse(data_type: Type[Rectangle], value, strict):
        if isinstance(value, Rectangle):
            return value
        if isinstance(value, dict):
            if "x" in value and "y" in value and isinstance(value["x"], int) and isinstance(value["y"], int):
                return data_type(value["x"], value["y"])
        if strict:
            raise ValueError(f"{type(value)=} {value=} invalid for {data_type=}")
        else:
            return value
```
We've successfully added support, Not let's parse/serialize and test
```py
rect = Rectangle(10, 5)
rect.area()
#> 50
serialize(rect)
#> {'x': 10, 'y': 5}
new_rect = parse(Rectangle, {"x": 1, "y": 4}, True) 
new_rect
#> <__main__.Rectangle object at 0x7f9fbaa4b9d0>
new_rect.area()
#> 4
```