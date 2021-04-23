#!/bin/env python
import json
import sys
import os

SRC = os.path.dirname(os.path.realpath(sys.argv[0]))

HEADER = open(f"{SRC}/dump_python_header.py").read()

F_CLASS = """
class {cname}({bnames}):{f_field_decl}
    def __init__(self, kvp: dict[int, Any] = {{}}):
        super({cname}, self).__init__(kvp){f_field_init}
    @staticmethod
    def create(value: dict[str, Any]) -> {cname}:
        return MetaBase.create(value) # type: ignore
    @staticmethod
    def default() -> {cname}:
        return {cname}()
MetaBase.types__[0x{chash:08x}] = {cname}
"""
F_FIELD_DECL = """
    {fname}: {tname}"""
F_FIELD_INIT = """
        self.{fname} = MetaBase.read_field_(kvp, {tname}, 0x{fhash:08x})"""


HASH_TYPES = { int(line[:8], 16) : line[9:].rstrip() for line in open(f"{SRC}/hashes.bintypes.txt", "r").readlines() if line.rstrip() }

HASH_FIELDS = { int(line[:8], 16) : line[9:].rstrip() for line in open(f"{SRC}/hashes.binfields.txt", "r").readlines() if line.rstrip() }

# TODO: might be good idea to somehow generate this from HEADER
FILTER_NAMES = {
    # bin types
    "Fnv1a32": "fnv1a32",
    "Null": "null",
    "Int8": "int8",
    "UInt8": "uint8",
    "Int16": "int16",
    "UInt16": "uint16",
    "Int32": "int32",
    "UInt32": "uint32",
    "Int64": "int64",
    "UInt64": "uint64",
    "Float32": "float32",
    "Vec2": "vec2",
    "Vec3": "vec3",
    "Vec4": "vec4",
    "Mtx44": "mtx44",
    "Color": "color",
    "String": "string",
    "Hash": "hash",
    "Container": "container",
    "Container2": "container2",
    "Option": "option",
    "Link": "link",
    "Map": "map",
    "Value": "value",
    "MetaBase": "metaBase",
    # typing
    "Union": "union",
    "Optional": "optional",
    "PropertyBase": "propertyBase",
    "Any": "any",
    "NamedTuple": "namedTuple",
    "Sequence": "sequence",
    "Generic": "generic",
    "Mapping": "mapping",
    "TypeVar": "typeVar",
    "K": "k",
    "V": "v",
    "cast": "cast",
    "enum": "Enum",
    # builtin types and functions
    "isinstance": "IsInstance",
    "repr": "Repr",
    "vars": "Vars",
    "len": "Len",
    "type": "Type",
    "str": "Str",
    "int": "Int",
    "float": "Float",
    "list": "List",
    "tuple": "Tuple",
    "range": "Range",
    "dict": "Dict",
    "bytes": "Bytes",
    "set": "Set",
    # builtin types member functions
    "create": "Create",
    "default": "Default",
    "append": "Append",
    "clear": "Clear",
    "copy": "Copy",
    "count": "Count",
    "extend": "Extend",
    "fromkeys": "FromKeys",
    "get": "Get",
    "index": "Index",
    "insert": "Insert",
    "items": "Items",
    "keys": "Keys",
    "pop": "Pop",
    "popitem": "Popitem",
    "setdefault": "Setdefault",
    "remove": "Remove",
    "reverse": "Reverse",
    "update": "Update",
    "values": "Values",
    # builtin constants
    "NoneType": "noneType",
    "None": "none",
    "False": "false",
    "True": "true",
    # keywords
    "self": "Self",
    "await": "Await",
    "else": "Else",
    "import": "Import",
    "pass": "Pass",
    "break": "Break",
    "except": "Except",
    "in": "In",
    "raise": "Raise",
    "class": "Class",
    "finally": "Finally",
    "is": "Is",
    "return": "Return",
    "and": "And",
    "continue": "Continue",
    "for": "For",
    "lambda": "Lambda",
    "try": "Try",
    "as": "As",
    "def": "Def",
    "from": "From",
    "nonlocal": "Nonlocal",
    "while": "While",
    "assert": "Assert",
    "del": "Del",
    "global": "Global",
    "not": "Not",
    "with": "With",
    "async": "Async",
    "elif": "Elif",
    "if": "If",
    "or": "Or",
    "yield": "Yield",
}

TYPE_NAMES = {
    0: "Null",
    1: "Boolean",
    2: "Int8",
    3: "UInt8",
    4: "Int16",
    5: "UInt16",
    6: "Int32",
    7: "UInt32",
    8: "Int64",
    9: "UInt64",
    10: "Float32",
    11: "Vec2",
    12: "Vec3",
    13: "Vec4",
    14: "Mtx44",
    15: "Color",
    16: "String",
    17: "Hash",
    18: "File",
    0x80 | 0: "Container",
    0x80 | 1: "Container2",
    0x80 | 2: "StructPtr",
    0x80 | 3: "StructValue",
    0x80 | 4: "Link",
    0x80 | 5: "Option",
    0x80 | 6: "Map",
    0x80 | 7: "Boolean",
}

def get_type_hash_name(hash_num):
    if not hash_num:
        return None
    if hash_num in HASH_TYPES:
        result = HASH_TYPES[hash_num]
        if result in FILTER_NAMES:
            return FILTER_NAMES[result]
        else:
            return result
    return f"t_0x{hash_num:08x}"

def get_field_hash_name(hash_num):
    if not hash_num:
        return None
    if hash_num in HASH_FIELDS:
        result = HASH_FIELDS[hash_num]
        if result in FILTER_NAMES:
            return FILTER_NAMES[result]
        else:
            return result
    return f"m_0x{hash_num:08x}"

def get_type_name(type_num, hash_num = None):
    type_name = TYPE_NAMES[type_num]
    hash_name = get_type_hash_name(hash_num)
    if type_name == "StructValue":
        return hash_name
    elif type_name == "StructPtr":
        return f"Option[{hash_name}]"
    elif type_name == "Link":
        return f"Link[{hash_name}]"
    else:
        return type_name

def get_field_type_name(field):
    if field["containerI"]:
        type_name = get_type_name(field["type"])
        value_name = get_type_name(field["containerI"]["type"], field["otherClass"])
        return f"{type_name}[{value_name}]"
    elif field["mapI"]:
        type_name = get_type_name(field["type"])
        key_name = get_type_name(field["mapI"]["key"])
        value_name = get_type_name(field["mapI"]["value"], field["otherClass"])
        return f"{type_name}[{key_name}, {value_name}]"
    else:
        type_name = get_type_name(field["type"], field["otherClass"])
        return type_name

class Dumper:
    def __init__(self, meta, outf):
        self.lookup = { c['hash']: c for c in meta['classes'] }
        self.outf = outf
        self.done = set()

    def dump_class_bases(self, klass):
        bases = []
        if base := klass["parentClass"]:
            self.dump_class(base)
            base_name = get_type_hash_name(base)
            bases.append(base_name)
        for base, offset in klass["secondaryBases"]:
            if base:
                self.dump_class(base)
                base_name = get_type_hash_name(base)
                bases.append(base_name)
        if not len(bases):
            bases.append("MetaBase")
        return bases

    def dump_class_fields(self, klass):
        fields = []
        for field in sorted(klass["properties"], key=lambda f: f["offset"]):
            fhash = field['hash']
            fname = get_field_hash_name(fhash)
            tname = get_field_type_name(field)
            fields.append((fhash, fname, tname))
        return fields

    def dump_class(self, chash):
        if chash in self.done:
            return
        self.done.add(chash)
        klass = self.lookup[chash]
        bases = self.dump_class_bases(klass)
        fields = self.dump_class_fields(klass)
        
        cname = get_type_hash_name(chash)
        bnames = ', '.join(bases)
        
        f_field_decl = ''.join([F_FIELD_DECL.format(fhash = fhash, fname = fname, tname = tname) for fhash, fname, tname in fields])
        f_field_init = ''.join([F_FIELD_INIT.format(fhash = fhash, fname = fname, tname = tname) for fhash, fname, tname in fields])
        f_class = F_CLASS.format(chash = chash, cname = cname, bnames = bnames, f_field_decl = f_field_decl, f_field_init = f_field_init)
        self.outf.write(f_class)
    
    def dump_all(self):
        self.done = set()
        self.outf.write(HEADER)
        for chash in self.lookup.keys():
            self.dump_class(chash)

meta = json.load(open(sys.argv[1]))
Dumper(meta, sys.stdout).dump_all()
