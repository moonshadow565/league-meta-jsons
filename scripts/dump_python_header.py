#!/bin/env python 
from __future__ import annotations 
import enum
import typing
from typing import Optional, Union, Any, NamedTuple, Mapping, Sequence, Generic, Type, TypeVar, cast, get_args

K = TypeVar('K')
V = TypeVar('V')

def Fnv1a32(s: Union[str, int]) -> int:
    if isinstance(s, int):
        return s
    if s.startswith('{') and s.endswith('}'):
        return int(s[1:-1], 16)
    h = 0x811c9dc5
    for b in s.encode('ascii').lower():
        h = ((h ^ b) * 0x01000193) % 0x100000000
    return h

class Null(NamedTuple):
    @staticmethod
    def create(value: Any) -> Null:
        return Null()
    @staticmethod
    def default() -> Null:
        return Null()
    def __repr__(self):
        return repr(None)

class Boolean(enum.IntEnum):
    FALSE: bool = False
    TRUE: bool = True
    @staticmethod
    def create(value: Any) -> Boolean:
        return Boolean(bool(value))
    @staticmethod
    def default() -> Boolean:
        return Boolean(False)
    def __repr__(self):
        return repr(bool(self))

class Int8(int):
    @staticmethod
    def create(value: int) -> Int8:
        return Int8(value)
    @staticmethod
    def default() -> Int8:
        return Int8()

class UInt8(int):
    @staticmethod
    def create(value: int) -> UInt8:
        return UInt8(value)
    @staticmethod
    def default() -> UInt8:
        return UInt8()
    
class Int16(int):
    @staticmethod
    def create(value: int) -> Int16:
        return Int16(value)
    @staticmethod
    def default() -> Int16:
        return Int16()

class UInt16(int):
    @staticmethod
    def create(value: int) -> UInt16:
        return UInt16(value)
    @staticmethod
    def default() -> UInt16:
        return UInt16()
    
class Int32(int):
    @staticmethod
    def create(value: int) -> Int32:
        return Int32(value)
    @staticmethod
    def default() -> Int32:
        return Int32()

class UInt32(int):
    @staticmethod
    def create(value: int) -> UInt32:
        return UInt32(value)
    @staticmethod
    def default() -> UInt32:
        return UInt32()

class Int64(int):
    @staticmethod
    def create(value: int) -> Int64:
        return Int64(value)
    @staticmethod
    def default() -> Int64:
        return Int64()
    
class UInt64(int):
    @staticmethod
    def create(value: int) -> UInt64:
        return UInt64(value)
    @staticmethod
    def default() -> UInt64:
        return UInt64()

class Float32(float):
    @staticmethod
    def create(value: float) -> Float32:
        return Float32(value)
    @staticmethod
    def default() -> Float32:
        return Float32()

class Vec2(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    @staticmethod
    def create(value: Sequence[float]) -> Vec2:
        return Vec2(*(Float32.create(a) for a in value))
    @staticmethod
    def default() -> Vec2:
        return Vec2()

class Vec3(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    z: Float32 = Float32()
    @staticmethod
    def create(value: Sequence[float]) -> Vec3:
        return Vec3(*(Float32.create(a) for a in value))
    @staticmethod
    def default() -> Vec3:
        return Vec3()

class Vec4(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    z: Float32 = Float32()
    w: Float32 = Float32()
    @staticmethod
    def create(value: Sequence[float]) -> Vec4:
        return Vec4(*(Float32.create(a) for a in value))
    @staticmethod
    def default() -> Vec4:
        return Vec4()

class Mtx44(NamedTuple):
    r0: Vec4 = Vec4()
    r1: Vec4 = Vec4()
    r2: Vec4 = Vec4()
    r3: Vec4 = Vec4()
    @staticmethod
    def create(value: Sequence[Sequence[float]]) -> Mtx44:
        return Mtx44(*(Vec4.create(r) for r in value))
    @staticmethod
    def default() -> Mtx44:
        return Mtx44()

class Color(NamedTuple):
    r: UInt8 = UInt8()
    g: UInt8 = UInt8()
    b: UInt8 = UInt8()
    a: UInt8 = UInt8()
    @staticmethod
    def create(value: Sequence[int]) -> Color:
        return Color(*(UInt8.create(c) for c in value))
    @staticmethod
    def default() -> Color:
        return Color()

class String(str):
    @staticmethod
    def create(value: str) -> String:
        return String(value)
    @staticmethod
    def default() -> String:
        return String()

class Hash(str):
    @staticmethod
    def create(value: str) -> Hash:
        return Hash(value)
    @staticmethod
    def default() -> Hash:
        return Hash()

class File(str):
    @staticmethod
    def create(value: str) -> File:
        return File(value)
    @staticmethod
    def default() -> File:
        return File()

class Container(Generic[V], list[V]):
    @staticmethod
    def create(value_type: Type[V], value: Sequence[Any]) -> Container[V]:
        return Container[value_type](Value(value_type, v) for v in value) # type: ignore
    @staticmethod
    def default(value_type: Type[V]) -> Container[V]:
        return Container[value_type]() # type: ignore

class Container2(Generic[V], list[V]):
    @staticmethod
    def get_type():
        return Container2[V]
    @staticmethod
    def create(value_type: Type[V], value: Sequence[Any]) -> Container2[V]:
        return Container2[value_type](Value(value_type, v) for v in value) # type: ignore
    @staticmethod
    def default(value_type: Type[V]) -> Container2[V]:
        return Container2[value_type]() # type: ignore

class Map(Generic[K, V], dict[K, V]):
    @staticmethod
    def create(key_type: Type[K], value_type: Type[V], value: dict[Any, Any]) -> Map[K, V]:
        return Map[key_type, value_type]((Value(key_type, k), Value(value_type, v)) for k, v in value.items()) # type: ignore
    @staticmethod
    def default(key_type: Type[K], value_type: Type[V]) -> Map[K, V]:
        return Map[key_type, value_type]() # type: ignore

class Option(Generic[V]):
    value_: Union[V, Null]
    def __init__(self, value: Union[V, Null] = Null()):
        self.value = value
    @staticmethod
    def create(value_type: Type[V], value: Any) -> Option[V]:
        return Option[value_type](Value(value_type, value) if value else Null()) # type: ignore
    @staticmethod
    def default(value_type: Type[V]) -> Option[V]:
        return Option[value_type]() # type: ignore
    def __repr__(self):
        return repr(self.value)

class Link(Generic[V], str):
    @staticmethod
    def create(value_type: Type[V], value: str) -> Link[V]:
        return Link[value_type](value) # type: ignore
    @staticmethod
    def default(value_type: Type[V]) -> Link[V]:
        return Link[value_type]() # type: ignore

class Flag(enum.IntEnum):
    FALSE: bool = False
    TRUE: bool = True
    @staticmethod
    def create(value: Any) -> Flag:
        return Flag(bool(value))
    @staticmethod
    def default() -> Flag:
        return Flag(False)
    def __repr__(self):
        return repr(bool(self))

def Value(ttype: Type[V], *args) -> V:
    if not args:
        return ttype.default(*get_args(ttype)) # type: ignore
    return ttype.create(*get_args(ttype), *args) # type: ignore

class MetaBase:
    types__ : dict[int, Type[MetaBase]] = {}
    def __init__(self, kvp: dict[int, Any]):
        pass
    @staticmethod
    def read_field_(kvp: dict[int, Any], type_name: Type[V], key: int) -> V:
        if not key in kvp:
            return Value(type_name)
        return Value(type_name, kvp[key])
    @staticmethod
    def create(value: dict[str, Any]) -> MetaBase:
        type_name = value["__type"]
        type_hash = Fnv1a32(type_name)
        type_ctor = MetaBase.types__[type_hash]
        kvp = { Fnv1a32(k): v for k, v in value.items() }
        return type_ctor(kvp) # type: ignore
    def __repr__(self):
        return repr(vars(self))
