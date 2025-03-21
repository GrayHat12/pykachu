from dataclasses import dataclass
from enum import IntEnum, StrEnum, Enum, auto
from pykachu import parse, serialize

class EnumA(IntEnum):
    A = auto()
    B = auto()

class EnumB(StrEnum):
    A = auto()
    B = auto()

class EnumC(Enum):
    A = auto()
    B = auto()

@dataclass
class DataB:
    a: bool
    b: bytes
    f: tuple[EnumA, int]

@dataclass
class DataC:
    c: EnumA
    d: EnumB
    e: tuple[EnumC, EnumA]

@dataclass
class DataA:
    x: list[int]
    y: list[str]
    z: tuple[DataB, DataC]
    w: dict[EnumB, EnumC]

if __name__ == "__main__":
    # import json
    # data = DataA(
    #     x=[1,2,4],
    #     y=["a", "b", "c"],
    #     z=(DataB(a=False, b=b'helloworld', f=(EnumA.A, 3)), DataC(c=EnumA.B, d=EnumB.A, e=(EnumC.B, EnumA.B))),
    #     w={EnumB.A: EnumC.B, EnumB.B: EnumC.A}
    # )
    # with open("./dump.json", "w+") as f:
    #     json.dump(serialize(data), f)
    
    # with open("./dump.json", "r") as f:
    #     datab = parse(DataA, json.load(f), strict=True)
    #     print(datab)
    from typing import Optional
    from datetime import datetime
    from pykachu import serialize, parse
    from dataclasses import dataclass, field

    @dataclass
    class User:
        id: int
        name: str
        signup_ts: Optional[datetime] = None
        friends: list[int] = field(default_factory=list)

    # external_data = {'id': '123', 'signup_ts': '2017-06-01 12:22', 'friends': [1, '2', b'3']}
    user = User(id=123, name="John Doe", signup_ts=datetime.now(), friends=[1,2])
    print(user)
    print(serialize(user))
    new_user = parse(User, serialize(user), True)
    #> User id=123 name='John Doe' signup_ts=datetime.datetime(2017, 6, 1, 12, 22) friends=[1, 2, 3]
    print(new_user)
    #> 123