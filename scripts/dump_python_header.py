#!/bin/env python 
from __future__ import annotations 
import typing
import dataclasses
from typing import Optional, Union, Any, NamedTuple, Generic, TypeVar, Callable, Mapping

def Fnv1a32(s: Union[str, int]) -> int:
    if isinstance(s, int):
        return s
    if s.startswith('{') and s.endswith('}'):
        return int(s[1:-1], 16)
    if s.startswith('t_0x') or s.startswith('m_0x'):
        return int(s[4:], 16)
    h = 0x811c9dc5
    for b in s.encode('ascii').lower():
        h = ((h ^ b) * 0x01000193) % 0x100000000
    return h

NoneType = type(None)
TypeV = TypeVar('TypeV', covariant=True)


Int8 = int

UInt8 = int

Int16 = int

UInt16 = int

Int32 = int

UInt32 = int

Int64 = int

UInt64 = int

class Vec2(NamedTuple):
    x: float = float()
    y: float = float()

class Vec3(NamedTuple):
    x: float = float()
    y: float = float()
    z: float = float()

class Vec4(NamedTuple):
    x: float = float()
    y: float = float()
    z: float = float()
    w: float = float()

class Mtx44(NamedTuple):
    r0: Vec4 = Vec4()
    r1: Vec4 = Vec4()
    r2: Vec4 = Vec4()
    r3: Vec4 = Vec4()

class Color(NamedTuple):
    r: UInt8 = UInt8()
    g: UInt8 = UInt8()
    b: UInt8 = UInt8()
    a: UInt8 = UInt8()

class Hash(str):
    pass

class File(str):
    pass

@dataclasses.dataclass(frozen=True, order=True)
class Link(Generic[TypeV]):
    entry: str = ""
    type_name: Optional[type] = None

    def get(self, lookup: Mapping[str, Any]) -> Optional[V]:
        if self.entry in lookup:
            found = lookup[self.entry]
            if isinstance(found, dict):
                created = MetaCreate(self.type_name, found)
                lookup[self.entry] = created
                return created
            else:
                return found
        return None

@dataclasses.dataclass
class MetaBase:
    pass

_MetaClassList : dict[int, Any] = {}

_META_CREATE: dict[Any, Any] = {
    NoneType: lambda a, v: None,
    bool: lambda a, v: bool(v),
    Int8: lambda a, v: Int8(v),
    UInt8: lambda a, v: UInt8(v),
    Int16: lambda a, v: Int16(v),
    UInt16: lambda a, v: UInt16(v),
    Int32: lambda a, v: Int32(v),
    UInt32: lambda a, v: UInt32(v),
    Int64: lambda a, v: Int64(v),
    UInt64: lambda a, v: UInt64(v),
    float: lambda a, v: float(v),
    Vec2: lambda a, v: Vec2(*(float(x) for x in v)),
    Vec3: lambda a, v: Vec3(*(float(x) for x in v)),
    Vec4: lambda a, v: Vec4(*(float(x) for x in v)),
    Mtx44: lambda a, v: Mtx44(*(Vec4(*x) for x in v)),
    Color: lambda a, v: Color(*(UInt8(x) for x in v)),
    str: lambda a, v: str(v),
    Hash: lambda a, v: Hash(v),
    File: lambda a, v: File(v),
    Union: lambda a, v: None if v == None else MetaCreate(a[0], v),
    Link: lambda a, v: Link(v, a[0]),
    list: lambda a, v: list(MetaCreate(a[0], x) for x in v),
    dict: lambda a, v: dict((MetaCreate(a[0], x), MetaCreate(a[1], y)) for x,y in v.items()),
}

def MetaCreate(type_name: typing.Type[TypeV], value: Any) -> TypeV:
    type_args = typing.get_args(type_name)
    if type_args:
        type_origin = typing.get_origin(type_name)
        return _META_CREATE[type_origin](type_args, value)
    elif type_name in _META_CREATE:
        return _META_CREATE[type_name](type_args, value)
    else:
        type_ctor = _MetaClassList[Fnv1a32(value["__type"])]
        result = type_ctor()
        assert(isinstance(result, type_name))
        lookup = { Fnv1a32(k): v for k, v in value.items() }
        for field in dataclasses.fields(type_ctor):
            key = field.metadata["key"]
            if key in lookup:
                value = MetaCreate(eval(field.type), lookup[key]) # type: ignore
                setattr(result, field.name, value)
        return result

_META_DEFAULT: dict[str, Any] = {
    'NoneType': None,
    'bool': bool(),
    'Int8': Int8(),
    'UInt8': UInt8(),
    'Int16': Int16(),
    'UInt16': UInt16(),
    'Int32': Int32(),
    'UInt32': UInt32(),
    'Int64': Int64(),
    'UInt64': UInt64(),
    'float': float(),
    'Vec2': Vec2(),
    'Vec3': Vec3(),
    'Vec4': Vec4(),
    'Mtx44': Mtx44(),
    'Color': Color(),
    'str': str(),
    'Hash': Hash(),
    'File': File(),
}

def MetaField(key: int, type_name: str) -> dataclasses.Field:
    metadata: dict[str, Any] = { "key": key }
    if type_name.startswith('Optional['):
        return dataclasses.field(default = eval("None"), metadata = metadata)
    elif type_name in _META_DEFAULT:
        return dataclasses.field(default = _META_DEFAULT[type_name], metadata = metadata)
    else:
        return dataclasses.field(default_factory = lambda: eval(type_name)(), metadata = metadata)

def MetaClassEmpty(cls):
    chash = Fnv1a32(cls.__name__)
    _MetaClassList[chash] = cls
    return cls

def MetaClass(cls):
    for name, type_name in cls.__annotations__.items():
        setattr(cls, name, MetaField(Fnv1a32(name), type_name))
    return MetaClassEmpty(dataclasses.dataclass(cls))
