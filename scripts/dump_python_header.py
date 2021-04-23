#!/bin/env python 
from __future__ import annotations 
import typing
import dataclasses
from enum import IntEnum, EnumMeta
from dataclasses import dataclass
from dataclasses import field as Field
from typing import Optional, Union, Any, NamedTuple, Mapping, Sequence, Generic, Type, TypeVar


K = TypeVar('K')
V = TypeVar('V')

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

class DefaultEnumMeta(EnumMeta):
    default = object()
    def __call__(cls, value=default, *args, **kwargs):
        if value is DefaultEnumMeta.default:
            return next(iter(cls))
        return super().__call__(value, *args, **kwargs)

class Null(NamedTuple):
    @staticmethod
    def create(value: Any) -> Null:
        return Null()
    def __repr__(self):
        return repr(None)

class Boolean(IntEnum, metaclass=DefaultEnumMeta):
    FALSE: bool = False
    TRUE: bool = True
    @staticmethod
    def create(value: Any) -> Boolean:
        return Boolean(bool(value))
    def __repr__(self):
        return repr(bool(self))

class Int8(int):
    @staticmethod
    def create(value: int) -> Int8:
        return Int8(value)

class UInt8(int):
    @staticmethod
    def create(value: int) -> UInt8:
        return UInt8(value)
    
class Int16(int):
    @staticmethod
    def create(value: int) -> Int16:
        return Int16(value)

class UInt16(int):
    @staticmethod
    def create(value: int) -> UInt16:
        return UInt16(value)
    
class Int32(int):
    @staticmethod
    def create(value: int) -> Int32:
        return Int32(value)

class UInt32(int):
    @staticmethod
    def create(value: int) -> UInt32:
        return UInt32(value)

class Int64(int):
    @staticmethod
    def create(value: int) -> Int64:
        return Int64(value)
    
class UInt64(int):
    @staticmethod
    def create(value: int) -> UInt64:
        return UInt64(value)

class Float32(float):
    @staticmethod
    def create(value: float) -> Float32:
        return Float32(value)

class Vec2(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    @staticmethod
    def create(value: Sequence[float]) -> Vec2:
        return Vec2(*(Float32.create(a) for a in value))

class Vec3(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    z: Float32 = Float32()
    @staticmethod
    def create(value: Sequence[float]) -> Vec3:
        return Vec3(*(Float32.create(a) for a in value))

class Vec4(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    z: Float32 = Float32()
    w: Float32 = Float32()
    @staticmethod
    def create(value: Sequence[float]) -> Vec4:
        return Vec4(*(Float32.create(a) for a in value))

class Mtx44(NamedTuple):
    r0: Vec4 = Vec4()
    r1: Vec4 = Vec4()
    r2: Vec4 = Vec4()
    r3: Vec4 = Vec4()
    @staticmethod
    def create(value: Sequence[Sequence[float]]) -> Mtx44:
        return Mtx44(*(Vec4.create(r) for r in value))

class Color(NamedTuple):
    r: UInt8 = UInt8()
    g: UInt8 = UInt8()
    b: UInt8 = UInt8()
    a: UInt8 = UInt8()
    @staticmethod
    def create(value: Sequence[int]) -> Color:
        return Color(*(UInt8.create(c) for c in value))

class String(str):
    @staticmethod
    def create(value: str) -> String:
        return String(value)

class Hash(str):
    @staticmethod
    def create(value: str) -> Hash:
        return Hash(value)

class File(str):
    @staticmethod
    def create(value: str) -> File:
        return File(value)

class Container(Generic[V], list[V]):
    @staticmethod
    def create(value_type: Type[V], value: Sequence[Any]) -> Container[V]:
        return Container[value_type](create(value_type, v) for v in value) # type: ignore

class Container2(Generic[V], list[V]):
    @staticmethod
    def get_type():
        return Container2[V]
    @staticmethod
    def create(value_type: Type[V], value: Sequence[Any]) -> Container2[V]:
        return Container2[value_type](create(value_type, v) for v in value) # type: ignore

class Map(Generic[K, V], dict[K, V]):
    @staticmethod
    def create(key_type: Type[K], value_type: Type[V], value: dict[Any, Any]) -> Map[K, V]:
        return Map[key_type, value_type]((create(key_type, k), create(value_type, v)) for k, v in value.items()) # type: ignore

class Option(Generic[V]):
    value_: Union[V, Null]
    def __init__(self, value: Union[V, Null] = Null()):
        self.value = value
    @staticmethod
    def create(value_type: Type[V], value: Any) -> Option[V]:
        return Option[value_type](create(value_type, value) if value else Null()) # type: ignore
    def __repr__(self):
        return repr(self.value)

class Link(Generic[V], str):
    @staticmethod
    def create(value_type: Type[V], value: str) -> Link[V]:
        return Link[value_type](value) # type: ignore

class Flag(IntEnum, metaclass=DefaultEnumMeta):
    FALSE: bool = False
    TRUE: bool = True
    @staticmethod
    def create(value: Any) -> Flag:
        return Flag(bool(value))
    def __repr__(self):
        return repr(bool(self))

def create(type_name: Type[V], *args) -> V:
    type_args = typing.get_args(type_name)
    return type_name.create(*type_args, *args) # type: ignore

MetaClassList : dict[int, Any] = {}

def MetaClassEmpty(cls):
    chash = Fnv1a32(cls.__name__)
    MetaClassList[chash] = cls
    return cls

def MetaClass(cls):
    for key, value in cls.__annotations__.items():
        default_factory = lambda type_name = value: eval(type_name)()
        metadata = { "key": Fnv1a32(key) }
        field = Field(default_factory = default_factory, metadata = metadata)
        setattr(cls, key, field)
    cls = dataclass(cls)
    chash = Fnv1a32(cls.__name__)
    MetaClassList[chash] = cls
    return cls

@dataclass
class MetaBase:
    @classmethod
    def create(cls: Type[V], value: dict[str, Any]) -> V:
        type_ctor = MetaClassList[Fnv1a32(value["__type"])]
        lookup = { Fnv1a32(k): v for k, v in value.items() }
        result = type_ctor()
        for field in dataclasses.fields(type_ctor):
            key = field.metadata["key"]
            if not key in lookup:
                continue
            value = create(eval(field.type), lookup[key]) # type: ignore
            setattr(result, field.name, value)
        return result
