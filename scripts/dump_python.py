#!/bin/env python
import argparse
import json
import sys
import os
import inspect
import keyword
import dump_python_header

HEADER = inspect.getsource(dump_python_header)
F_CLASS = """
{cannotate}
class {cname}({bnames}):{cfields}
    pass
"""
F_FIELD = """
    {fname}: {tname}"""
BAD_WORDS = { 
    "self",
    *keyword.kwlist,
    *vars(__builtins__).keys(),
    *vars(list).keys(),
    *vars(dict).keys(),
    *vars(dump_python_header).keys(),
}
TYPE_NAMES = {
    0: "None",
    1: "bool",
    2: "Int8",
    3: "UInt8",
    4: "Int16",
    5: "UInt16",
    6: "Int32",
    7: "UInt32",
    8: "Int64",
    9: "UInt64",
    10: "float",
    11: "Vec2",
    12: "Vec3",
    13: "Vec4",
    14: "Mtx44",
    15: "Color",
    16: "str",
    17: "Hash",
    18: "File",
    0x80 | 0: "list",
    0x80 | 1: "list",
    0x80 | 2: "StructPtr",
    0x80 | 3: "StructValue",
    0x80 | 4: "Link",
    0x80 | 5: "Optional",
    0x80 | 6: "dict",
    0x80 | 7: "bool",
}

class Dumper:
    def __init__(self):
        self.lookup = {}
        self.hash_types = {}
        self.hash_fields = {}
        self.type_names = TYPE_NAMES
        self.filter_names = { w: Dumper._filter_word(w, BAD_WORDS) for w in BAD_WORDS if not w.startswith("_") }

    @staticmethod
    def _filter_word(word, bad_words):
        word_capitalized = word[:1].upper() + word[1:]
        if not word_capitalized in bad_words:
            return word_capitalized
        word_uncapitalized = word[:1].lower() + word[1:]
        if not word_uncapitalized in bad_words:
            return word_uncapitalized
        word_lower = word.lower()
        if not word_lower in bad_words:
            return word_lower
        word_upper = word.upper()
        if not word_upper in bad_words:
            return word_upper
        raise ValueError(f'Can not filter "{word}"')

    def _read_hash_list(self, output, hash_filename):
        if hash_filename:
            with open(hash_filename, "r") as inf:
                for line in inf.readlines():
                    line = line.rstrip().split(' ')
                    if line and not line[0].startswith('#'):
                        assert(len(line) == 2)
                        hash_num = int(line[0], 16)
                        hash_value = line[1]
                        if hash_value in self.filter_names:
                            hash_value = self.filter_names[hash_value]
                        output[hash_num] = hash_value

    def load_meta_file(self, metafile):
        meta = json.load(metafile)
        self.lookup = { c['hash']: c for c in meta['classes'] }
    
    def load_hash_types_file(self, filename):
        self._read_hash_list(self.hash_types, filename)
    
    def load_hash_fields_file(self, filename):
        self._read_hash_list(self.hash_fields, filename)
    
    def get_type_hash_name(self, hash_num):
        if not hash_num:
            return None
        if hash_num in self.hash_types:
            return self.hash_types[hash_num]
        return f"t_0x{hash_num:08x}"

    def get_field_hash_name(self, hash_num):
        if not hash_num:
            return None
        if hash_num in self.hash_fields:
            return self.hash_fields[hash_num]
        return f"m_0x{hash_num:08x}"

    def get_type_name(self, type_num, hash_num = None):
        type_name = self.type_names[type_num]
        hash_name = self.get_type_hash_name(hash_num)
        if type_name == "StructValue":
            return hash_name
        elif type_name == "StructPtr":
            return f"Optional[{hash_name}]"
        elif type_name == "Link":
            return f"Link[{hash_name}]"
        else:
            return type_name

    def get_field_type_name(self, field):
        if field["containerI"]:
            type_name = self.get_type_name(field["type"])
            value_name = self.get_type_name(field["containerI"]["type"], field["otherClass"])
            return f"{type_name}[{value_name}]"
        elif field["mapI"]:
            type_name = self.get_type_name(field["type"])
            key_name = self.get_type_name(field["mapI"]["key"])
            value_name = self.get_type_name(field["mapI"]["value"], field["otherClass"])
            return f"{type_name}[{key_name}, {value_name}]"
        else:
            type_name = self.get_type_name(field["type"], field["otherClass"])
            return type_name

    def dump_class_bases(self, klass, outf, done):
        bases = []
        if base := klass["parentClass"]:
            self.dump_class(base, outf, done)
            base_name = self.get_type_hash_name(base)
            bases.append(base_name)
        for base, offset in klass["secondaryBases"]:
            if base:
                self.dump_class(base, outf, done)
                base_name = self.get_type_hash_name(base)
                bases.append(base_name)
        return bases

    def dump_class_fields(self, klass):
        fields = []
        for field in sorted(klass["properties"], key=lambda f: f["offset"]):
            fhash = field['hash']
            fname = self.get_field_hash_name(fhash)
            tname = self.get_field_type_name(field)
            fields.append((fhash, fname, tname))
        return fields

    def dump_class(self, chash, outf, done):
        if chash in done:
            return
        done.add(chash)
        klass = self.lookup[chash]
        bases = self.dump_class_bases(klass, outf, done)
        fields = self.dump_class_fields(klass)

        cannotate = "@MetaClassEmpty" if len(fields) == 0 else "@MetaClass"
        cname = self.get_type_hash_name(chash)
        bnames = "MetaBase" if len(bases) == 0 else ', '.join(bases)
        cfields = ''.join([F_FIELD.format(fhash = fhash, fname = fname, tname = tname) for fhash, fname, tname in fields])

        result = F_CLASS.format(chash = chash, cannotate = cannotate, cname = cname, bnames = bnames, cfields = cfields)
        outf.write(result)
    
    def dump_all(self, outf):
        done = set()
        outf.write(HEADER)
        for chash in self.lookup.keys():
            self.dump_class(chash, outf, done)


src = os.path.dirname(os.path.realpath(sys.argv[0]))
parser = argparse.ArgumentParser(description="Generate rito bin type definitions.")
parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input meta.json file")
parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output bintypes.py file")
parser.add_argument('--bintypes', type=str, default=f"{src}/hashes.bintypes.txt", help='CDTB hashes.bintypes.txt file')
parser.add_argument('--binfields', type=str, default=f"{src}/hashes.binfields.txt", help='CDTB hashes.binfields.txt file')
args = parser.parse_args()

dumper = Dumper()
dumper.load_hash_types_file(args.bintypes)
dumper.load_hash_fields_file(args.binfields)
dumper.load_meta_file(args.infile)
dumper.dump_all(args.outfile)
