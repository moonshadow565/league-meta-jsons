#!/bin/env python
import json
import sys
import os

t_none = 0
t_boolean = 1
t_int8 = 2
t_uint8 = 3
t_int16 = 4
t_uint16 = 5
t_int32 = 6
t_uint32 = 7
t_int64 = 8
t_uint64 = 9
t_float32 = 10
t_point2D = 11
t_point3D = 12
t_point4D = 13
t_matrix44 = 14
t_color = 15
t_string = 16
t_hash = 17
t_file = 18
t_container = 0x80 | 0
t_container2 = 0x80 | 1
t_struct_ptr = 0x80 | 2
t_struct_value = 0x80 | 3
t_link_offset = 0x80 | 4
t_optional = 0x80 | 5
t_map = 0x80 | 6
t_type24 = 0x80 | 7

simple_types = {
    t_none : "None",
    t_boolean : "bool",
    t_int8 : "int",
    t_uint8 : "int",
    t_int16 : "int",
    t_uint16 : "int",
    t_int32 : "int",
    t_uint32 : "int",
    t_int64 : "int",
    t_uint64 : "int",
    t_float32 : "float",
    t_point2D : "list[float]",
    t_point3D : "list[float]",
    t_point4D : "list[float]",
    t_matrix44 : "list[list[float]]",
    t_color : "list[int]",
    t_string : "str",
    t_hash : "str",
    t_file : "str",
    t_type24 : "bool",
}

simple_default = {
    t_none : "None",
    t_boolean : "False",
    t_int8 : "0",
    t_uint8 : "0",
    t_int16 : "0",
    t_uint16 : "0",
    t_int32 : "0",
    t_uint32 : "0",
    t_int64 : "0",
    t_uint64 : "0",
    t_float32 : "0.0",
    t_point2D : "[0.0, 0.0,]",
    t_point3D : "[0.0, 0.0, 0.0,]",
    t_point4D : "[0.0, 0.0, 0.0, 0.0,]",
    t_matrix44 : "[[0.0, 0.0, 0.0, 0.0,], [0.0, 0.0, 0.0, 0.0,], [0.0, 0.0, 0.0, 0.0,], [0.0, 0.0, 0.0, 0.0,],]",
    t_color : "[0, 0, 0, 0,]",
    t_string : "\"\"",
    t_hash : "\"\"",
    t_file : "\"\"",
    t_container : "[]",
    t_container2 : "[]",
    t_struct_ptr : "None",
    t_link_offset : "\"\"",
    t_optional: "None",
    t_map : "{}",
    t_type24 : "false",
}

keyword_remap = {
    # typing Uppercase -> lowercase
    "Union": "union",
    "Optional": "optional",
    "PropertyBase": "propertyBase",
    "Any": "any",

    # builtin types lowercase -> Uppercase
    "type": "Type",
    "str": "Str",
    "int": "Int",
    "float": "Float",
    "decimal": "Decimal",
    "list": "List",
    "tuple": "Tuple",
    "range": "Range",
    "dict": "Dict",
    "bytes": "Bytes",
    "set": "Set",
    # constants Uppercase -> lowercase
    "None": "none",
    "False": "false",
    "True": "true",
    # keywords lowercase -> Uppercase
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

def readhashes(filename):
    with open(filename, "r") as inf:
        lines = [ x.rstrip().split(' ') for x in inf.readlines() ]
        return { int(x[0], 16) : x[1] for x in lines }

def h2type(h):
    if h in h_types:
        r = h_types[h]
        if r in keyword_remap:
            return keyword_remap[r]
        else:
            return r
    return f"t_0x{h:08x}"

def h2field(h):
    if h in h_fields:
        r = h_fields[h]
        if r in keyword_remap:
            return keyword_remap[r]
        else:
            return r
    return f"m_0x{h:08x}"

def fix_type(t):
    return t

def get_nested_type(t, k):
    if t in simple_types:
        if k:
            raise Exception("other class is NOT 0 for type: {}".format(t))
        return simple_types[t]
    else:
        if k == 0:
            raise Exception("other class is 0 for type: {}".format(t))
        if t == t_struct_ptr:
            return "Optional[{}]".format(h2type(k))
        elif t == t_struct_value:
            return h2type(k)
        elif t == t_link_offset:
            return "Union[None, str, {}]".format(h2type(k))
        else:
            raise Exception(f"Nested type name too complex: {t}!")

def get_type(field):
    t = fix_type(field["type"])
    if t == t_container or t == t_container2:
        vt = get_nested_type(fix_type(field["containerI"]["type"]), field["otherClass"])
        return f"list[{vt}]"
    elif t == t_optional:
        vt = get_nested_type(fix_type(field["containerI"]["type"]), field["otherClass"])
        return f"Optional[{vt}]"
    elif t == t_map:
        kt = get_nested_type(fix_type(field["mapI"]["key"]), 0)
        vt = get_nested_type(fix_type(field["mapI"]["value"]), field["otherClass"])
        return f"dict[{kt}, {vt}]"
    else:
        return get_nested_type(t, field["otherClass"])

def get_nested_default(t, k):
    if t == t_struct_value:
        if k == 0:
            raise Exception("other class is 0 for type: {}".format(t))
        return "{}({{}})".format(h2type(k))
    else:
        return simple_default[t]

def get_default(field):
    t = fix_type(field["type"])
    k = field["otherClass"]
    return get_nested_default(t, k)

def get_default_item(field):
    t = fix_type(field["containerI"]["type"])
    k = field["otherClass"]
    return get_nested_default(t, k)

def dump_klass(chash, klass_lookup, done, outf):
    if chash in done:
        return
    klass = klass_lookup[chash]
    bases = []
    if base := klass["parentClass"]:
        dump_klass(base, klass_lookup, done, outf)
        bases.append(h2type(base))
    for base, offset in klass["secondaryBases"]:
        if base:
            dump_klass(base, klass_lookup, done, outf)
            bases.append(h2type(base))
    if not len(bases):
        bases.append("MetaBase")
    cname = h2type(chash)
    bname = ', '.join(bases)
    o = outf.write(f"class {cname}({bname}):\n")
    fields = list(sorted(klass["properties"], key=lambda f: f["offset"]))
    for field in fields:
        fhash = field["hash"]
        fname = h2field(fhash)
        tname = get_type(field)
        o = outf.write(f"    {fname}: {tname} = property(lambda s: s.fields__[0x{fhash:08x}])\n")
    o = outf.write(f"\n")
    o = outf.write("    def __init__(self, kvp: dict[str, Any]):\n")
    o = outf.write(f"        super({cname}, self).__init__(kvp)\n")
    for field in fields:
        fhash = field["hash"]
        fdefault = get_default(field)
        o = outf.write(f"        if not 0x{fhash:08x} in self.fields__:\n")
        o = outf.write(f"            self.fields__[0x{fhash:08x}] = {fdefault}\n")
        if field["containerI"] and field["containerI"]["fixedSize"] > 0:
            o = outf.write(f"\n")
            sz = field["containerI"]["fixedSize"]
            fidefault = get_default_item(field)
            o = outf.write(f"        for _ in range(len(self.fields__[0x{fhash:08x}]), {sz}):\n")
            o = outf.write(f"            self.fields__[0x{fhash:08x}].append({fidefault})\n")
    o = outf.write("\n")
    done[chash] = cname

def dump(meta, outf):
    outf.write("""from __future__ import annotations 
from typing import Optional, Union, Any

def fnv1a(s: str):
    if s.startswith('{') and s.endswith('}'):
        return int(s[1:-1], 16)
    h = 0x811c9dc5
    for b in s.encode('ascii').lower():
        h = ((h ^ b) * 0x01000193) % 0x100000000
    return h

class MetaBase:
    type_constructors__ = {}
    def __init__(self, kvp: dict[str, Any]):
        self.fields__ = {}
        for key, value in kvp.items():
            key = fnv1a(key)
            if isinstance(value, dict) and "__type" in value:
                value = MetaBase.construct_from(value)
            self.fields__[key] = value

    def construct_from(value: dict[str, Any]) -> Any:
        type_name = value["__type"]
        type_hash = fnv1a(type_name)
        type_ctor = MetaBase.type_constructors__[type_hash] if type_hash in MetaBase.type_constructors__ else MetaBase
        return type_ctor(value)

""")
    klass_lookup = { klass['hash']: klass for klass in meta['classes'] }
    done = {}
    for chash in klass_lookup.keys():
        dump_klass(chash, klass_lookup, done, outf)
    outf.write("MetaBase.type_constructors__ = {\n")
    for chash, cname in done.items():
        outf.write(f"    0x{chash:08x}: {cname},\n")
    outf.write("}\n")

folder = os.path.dirname(os.path.realpath(sys.argv[0]))
h_fields = readhashes(f"{folder}/hashes.binfields.txt")
h_types = readhashes(f"{folder}/hashes.bintypes.txt")
meta = json.load(open(sys.argv[1]))

dump(meta, sys.stdout)
