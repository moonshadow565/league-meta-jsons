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


def fnv1a(s):
    h = 0x811c9dc5
    for b in s.encode('ascii').lower():
        h = ((h ^ b) * 0x01000193) % 0x100000000
    return h

def readhashes(filename):
    with open(filename, "r") as inf:
        lines = [ x.rstrip().split(' ') for x in inf.readlines() ]
        return { int(x[0], 16) : x[1] for x in lines }

def h2type(h):
    if h in h_types:
        return h_types[h]
    unktypes.add("0x{:08X}".format(h))
    return "t_0x{:08X}".format(h)

def h2field(h):
    if h in h_fields:
        return h_fields[h]
    unkfields.add("0x{:08X}".format(h))
    return "m_0x{:08X}".format(h)

simple_types = {
    t_none : "none_t",
    t_boolean : "bool",
    t_int8 : "int8_t",
    t_uint8 : "uint8_t",
    t_int16 : "int16_t",
    t_uint16 : "uint16_t",
    t_int32 : "int32_t",
    t_uint32 : "uint32_t",
    t_int64 : "int64_t",
    t_uint64 : "uint64_t",
    t_float32 : "float_t",
    t_point2D : "point2D_t",
    t_point3D : "point3D_t",
    t_point4D : "point4D_t",
    t_matrix44 : "matrix44_t",
    t_color : "color_t",
    t_string : "string_t",
    t_hash : "hash_t",
    t_file : "file_t",
    t_type24 : "bool",
}

is_old = False
def fix_type(t):
    if is_old:
        if t >= 18 and t < 0x80:
            t -= 18
            t |= 0x80
        if t >= 0x81:
            t += 1
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
            return "unique_ptr_t<{}>".format(h2type(k))
        elif t == t_struct_value:
            return h2type(k)
        elif t == t_link_offset:
            return "link_ptr_t<{}>".format(h2type(k))
        else:
            raise Exception(f"Nested type name too complex: {t}!")

def get_type(field):
    t = fix_type(field["type"])
    if t == t_container or t == t_container2:
        vt = get_nested_type(fix_type(field["containerI"]["type"]), field["otherClass"])
        sz = field["containerI"]["fixedSize"]
        #if sz < 0:
            #raise Exception("Invalid vector size type!")
        if sz < 1:
            return "vector_t<{}>".format(vt)
        else:
            return "array_t<{}, {}>".format(vt, sz)
    elif t == t_optional:
        vt = get_nested_type(fix_type(field["containerI"]["type"]), field["otherClass"])
        return "optional_t<{}>".format(vt)
    elif t == t_map:
        kt = get_nested_type(fix_type(field["mapI"]["key"]), 0)
        vt = get_nested_type(fix_type(field["mapI"]["value"]), field["otherClass"])
        st = field["mapI"]["storage"]
        #if st < 0:
            #raise Exception("Invalid map storage type!")
        if st < 1:
            return "map_t<{}, {}>".format(kt, vt)
        elif st == 1:
            return "unordered_map_t<{}, {}>".format(kt, vt)
        elif st == 2:
            return "vector_map_t<{}, {}>".format(kt, vt)
        else:
            raise Exception("Invalid map storage type!")
    else:
        return get_nested_type(t, field["otherClass"])
        

def dump_klass(klass, outf):
    def build_inheritance(klass):
        virtual = [ "{}".format(h2type(x[0])) for x in klass["secondaryBases"] if x[0] ]
        normal = [ h2type(klass["parentClass"]) ] if klass["parentClass"] else ["PropertyBase"] if klass["isPropertyBase"] else []
        bases = normal + virtual
        return ": {}".format(", ".join(bases)) if len(bases) > 0 else ""
    o = outf.write("struct {}{} {{\n".format(h2type(klass["hash"]), build_inheritance(klass)))
    for field in sorted(klass["properties"], key=lambda f: f["offset"]):
        tname = get_type(field)
        fname = h2field(field["hash"])
        o = outf.write("    {} {};\n".format(tname, fname))
    o = outf.write("};\n")


def find_klass(klasses, h):
    if not h:
        return None
    for klass in meta_klasses["classes"]:
        if klass["hash"] == h:
            return klass
    return None

def build_deps(klasses, root_hashes, skip = []):
    q = []
    deps = set()
    done = set()
    km = { k["hash"] : k for k in klasses }
    for h in root_hashes:
        q.append(h)
    done.add(0)
    for x in skip:
        done.add(x)
    
    while len(q) > 0:
        h = q.pop()
        if h in done:
            continue
        done.add(h)
        deps.add(h)
        k = km[h]
        p = int(k["parentClass"])
        if not p in done:
            q.append(p)
        for f in k["properties"]:
            o = int(f["otherClass"])
            if not o in done:
                q.append(o)
        for k2 in klasses:
            h2 = int(k2["hash"])
            if not h2 in done:
                if int(k2["parentClass"]) == h:
                    q.append(h2)
    return deps

def dump(klasses, outf, filterf = None):
    for klass in klasses:
        if not filterf or filterf(klass):
            dump_klass(klass, outf)

if __name__ == '__main__':
    folder = os.path.dirname(os.path.realpath(sys.argv[0]))
    h_fields = readhashes(f"{folder}/hashes.binfields.txt")
    h_types = readhashes(f"{folder}/hashes.bintypes.txt")
    meta_klasses = json.load(open(sys.argv[1]))
    is_old = tuple(int(x) for x in meta_klasses["version"].split('.')) < (10, 8)
    unktypes = set()
    unkfields = set()

    if len(sys.argv) > 2:
        root_hashes = { fnv1a(x) if not x.startswith('0x') else int(x) for x in sys.argv[2:] }
        deps = build_deps(meta_klasses["classes"], root_hashes, [ ])
        dump(meta_klasses["classes"], sys.stdout, lambda k: k["hash"] in deps)
    else:
        dump(meta_klasses["classes"], sys.stdout, None)
