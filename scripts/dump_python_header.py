#!/bin/env python 
from __future__ import annotations 
import enum
import typing
from typing import Optional, Union, Any, NamedTuple, Mapping, Sequence, Generic, TypeVar, cast, get_args

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
    @classmethod 
    def create(cls, value: Any) -> Null:
        return Null()
    @classmethod
    def default(cls) -> Null:
        return Null()
    def __repr__(self):
        return repr(None)

class Boolean(enum.IntEnum):
    FALSE: bool = False
    TRUE: bool = True
    @classmethod 
    def create(cls, value: Any) -> Boolean:
        return Boolean(bool(value))
    @classmethod
    def default(cls) -> Boolean:
        return Boolean(False)
    def __repr__(self):
        return repr(bool(self))

class Int8(int):
    @classmethod 
    def create(cls, value: int) -> Int8:
        return Int8(value)
    @classmethod
    def default(cls) -> Int8:
        return Int8()

class UInt8(int):
    @classmethod 
    def create(cls, value: int) -> UInt8:
        return UInt8(value)
    @classmethod
    def default(cls) -> UInt8:
        return UInt8()
    
class Int16(int):
    @classmethod 
    def create(cls, value: int) -> Int16:
        return Int16(value)
    @classmethod
    def default(cls) -> Int16:
        return Int16()

class UInt16(int):
    @classmethod
    def create(cls, value: int) -> UInt16:
        return UInt16(value)
    @classmethod
    def default(cls) -> UInt16:
        return UInt16()
    
class Int32(int):
    @classmethod 
    def create(cls, value: int) -> Int32:
        return Int32(value)
    @classmethod
    def default(cls) -> Int32:
        return Int32()

class UInt32(int):
    @classmethod 
    def create(cls, value: int) -> UInt32:
        return UInt32(value)
    @classmethod
    def default(cls) -> UInt32:
        return UInt32()

class Int64(int):
    @classmethod 
    def create(cls, value: int) -> Int64:
        return Int64(value)
    @classmethod
    def default(cls) -> Int64:
        return Int64()
    
class UInt64(int):
    @classmethod 
    def create(cls, value: int) -> UInt64:
        return UInt64(value)
    @classmethod
    def default(cls) -> UInt64:
        return UInt64()

class Float32(float):
    @classmethod 
    def create(cls, value: int) -> Float32:
        return Float32(value)
    @classmethod
    def default(cls) -> Float32:
        return Float32()

class Vec2(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    @classmethod 
    def create(cls, value: Sequence[float]) -> Vec2:
        return Vec2(*(Float32.create(a) for a in value))
    @classmethod
    def default(cls) -> Vec2:
        return Vec2()

class Vec3(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    z: Float32 = Float32()
    @classmethod 
    def create(cls, value: Sequence[float]) -> Vec3:
        return Vec3(*(Float32.create(a) for a in value))
    @classmethod
    def default(cls) -> Vec3:
        return Vec3()

class Vec4(NamedTuple):
    x: Float32 = Float32()
    y: Float32 = Float32()
    z: Float32 = Float32()
    w: Float32 = Float32()
    @classmethod 
    def create(cls, value: Sequence[float]) -> Vec4:
        return Vec4(*(Float32.create(a) for a in value))
    @classmethod
    def default(cls) -> Vec4:
        return Vec4()

class Mtx44(NamedTuple):
    r0: Vec4 = Vec4()
    r1: Vec4 = Vec4()
    r2: Vec4 = Vec4()
    r3: Vec4 = Vec4()
    @classmethod 
    def create(cls, value: Sequence[Sequence[float]]) -> Mtx44:
        return Mtx44(*(Vec4.create(r) for r in value))
    @classmethod
    def default(cls) -> Mtx44:
        return Mtx44()

class Color(NamedTuple):
    r: UInt8 = UInt8()
    g: UInt8 = UInt8()
    b: UInt8 = UInt8()
    a: UInt8 = UInt8()
    @classmethod 
    def create(cls, value: Sequence[int]) -> Color:
        return Color(*(U8.create(c) for c in value))
    @classmethod
    def default(cls) -> Color:
        return Color()

class String(str):
    @classmethod 
    def create(cls, value: str) -> String:
        return String(value)
    @classmethod 
    def default(cls) -> String:
        return String()

class Hash(str):
    @classmethod 
    def create(cls, value: str) -> Hash:
        return Hash(value)
    @classmethod 
    def default(cls) -> Hash:
        return Hash()

class File(str):
    @classmethod 
    def create(cls, value: str) -> File:
        return File(value)
    @classmethod 
    def default(cls) -> File:
        return File()

class Container(Generic[V], list):
    @classmethod
    def create(cls, value_type: type, value: Sequence[Any]) -> Container[value_type]:
        return Container[value_type](Value(value_type, v) for v in value)
    @classmethod 
    def default(cls, value_type: type) -> Container[value_type]:
        return Container[value_type]()

class Container2(Generic[V], list):
    @classmethod
    def get_type():
        return Container2[V]
    @classmethod
    def create(cls, value_type: type, value: Sequence[Any]) -> Container2[value_type]:
        return Container2[value_type](Value(value_type, v) for v in value)
    @classmethod 
    def default(cls, value_type: type) -> Container2[value_type]:
        return Container2[value_type]()

class Map(Generic[K, V], dict):
    @classmethod
    def create(cls, key_type: type, value_type: type, value: dict[Any, Any]) -> Map[key_type, value_type]:
        return Map[key_type, value_type]((Value(key_type, k), Value(value_type, v)) for k, v in value.items())
    @classmethod 
    def default(cls, key_type: type, value_type: type) -> Map[key_type, value_type]:
        return Map[key_type, value_type]()

class Option(Generic[V]):
    value_: Union[V, Null]
    def __init__(self, value: Union[V, Null] = Null()):
        self.value = value
    @classmethod
    def create(cls, value_type: type, value: Any) -> Option[value_type]:
        return Option[value_type](Value(value_type, value) if value else Null())
    @classmethod
    def default(cls, value_type: type) -> Option[value_type]:
        return Option[value_type]()
    def __repr__(self):
        return repr(self.value)

class Link(Generic[V], str):
    @classmethod 
    def create(cls, value_type: type, value: str) -> Link[value_type]:
        return Link[value_type](value)
    @classmethod
    def default(cls, value_type: type) -> Link[value_type]:
        return Link[value_type]()

class Flag(enum.IntEnum):
    FALSE: bool = False
    TRUE: bool = True
    @classmethod 
    def create(cls, value: Any) -> Flag:
        return Flag(bool(value))
    @classmethod
    def default(cls) -> Flag:
        return Flag(False)
    def __repr__(self):
        return repr(bool(self))

def Value(ttype: type, *args) -> ttype:
    if not args:
        return ttype.default(*get_args(ttype))
    return ttype.create(*get_args(ttype), *args)

class MetaBase:
    types__ = {}
    def __init__(self, kvp: dict[int, Any]):
        pass
    @staticmethod
    def read_field_(kvp: dict[int, Any], type_name: type, key: int) -> type_name:
        if not key in kvp:
            return Value(type_name)
        return Value(type_name, kvp[key])
    @staticmethod
    def create(value: dict[str, Any]) -> MetaBase:
        type_name = value["__type"]
        type_hash = Fnv1a32(type_name)
        type_ctor = MetaBase.types__[type_hash]
        kvp = { Fnv1a32(k): v for k, v in value.items() }
        return type_ctor(kvp)
    def __repr__(self):
        return repr(vars(self))
