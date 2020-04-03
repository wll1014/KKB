#!/usr/bin/env python3
from __future__ import print_function
import os
import sys
import calendar
import codecs
import json
from optparse import OptionParser
from rdbtools import RdbParser, PrintAllKeys, MemoryCallback, ProtocolCallback, KeysOnlyCallback, KeyValsOnlyCallback
from rdbtools.encodehelpers import ESCAPE_CHOICES
from rdbtools.parser import HAS_PYTHON_LZF as PYTHON_LZF_INSTALLED
from rdbtools.parser import RdbCallback
from rdbtools import encodehelpers


class JSONCallback(RdbCallback):
    def __init__(self, out, string_escape=None):
        if string_escape is None:
            string_escape = encodehelpers.STRING_ESCAPE_UTF8
        super(JSONCallback, self).__init__(string_escape)
        self._out = out
        self._is_first_db = True
        self._has_databases = False
        self._is_first_key_in_db = True
        self._elements_in_key = 0
        self._element_index = 0

    def encode_key(self, key):
        if isinstance(key, int):
            key = str(key)
        else:
            key = str(key, encoding='utf8')
        return codecs.encode(json.dumps(key, ensure_ascii=False, indent=4, sort_keys=True), 'utf-8')

    def encode_value(self, val):
        if isinstance(val, int):
            val = str(val)
        else:
            val = str(val, encoding='utf8')
        return codecs.encode(json.dumps(val, ensure_ascii=False, indent=4, sort_keys=True), 'utf-8')

    def start_rdb(self):
        self._out.write(b'[')

    def start_database(self, db_number):
        if not self._is_first_db:
            self._out.write(b'},')
        self._out.write(b'{')
        self._is_first_db = False
        self._has_databases = True
        self._is_first_key_in_db = True

    def end_database(self, db_number):
        pass

    def end_rdb(self):
        if self._has_databases:
            self._out.write(b'}')
        self._out.write(b']')

    def _start_key(self, key, length):
        if not self._is_first_key_in_db:
            self._out.write(b',')
        self._out.write(b'\r\n')
        self._is_first_key_in_db = False
        self._elements_in_key = length
        self._element_index = 0

    def _end_key(self, key):
        pass

    def _write_comma(self):
        if self._element_index > 0 and self._element_index < self._elements_in_key:
            self._out.write(b',')
        self._element_index = self._element_index + 1

    def set(self, key, value, expiry, info):
        self._start_key(key, 0)
        self._out.write(self.encode_key(key) + b':' + self.encode_value(value))
        self._end_key(key)

    def start_hash(self, key, length, expiry, info):
        self._start_key(key, length)
        self._out.write(self.encode_key(key) + b':{')

    def hset(self, key, field, value):
        self._write_comma()
        self._out.write(self.encode_key(field) + b':' + self.encode_value(value))

    def end_hash(self, key):
        self._end_key(key)
        self._out.write(b'}')

    def start_set(self, key, cardinality, expiry, info):
        self._start_key(key, cardinality)
        self._out.write(self.encode_key(key) + b':[')

    def sadd(self, key, member):
        self._write_comma()
        self._out.write(self.encode_value(member))

    def end_set(self, key):
        self._end_key(key)
        self._out.write(b']')

    def start_list(self, key, expiry, info):
        self._start_key(key, 0)
        self._out.write(self.encode_key(key) + b':[')

    def rpush(self, key, value):
        self._elements_in_key += 1
        self._write_comma()
        self._out.write(self.encode_value(value))

    def end_list(self, key, info):
        self._end_key(key)
        self._out.write(b']')

    def start_sorted_set(self, key, length, expiry, info):
        self._start_key(key, length)
        self._out.write(self.encode_key(key) + b':{')

    def zadd(self, key, score, member):
        self._write_comma()
        self._out.write(self.encode_key(member) + b':' + self.encode_value(score))

    def end_sorted_set(self, key):
        self._end_key(key)
        self._out.write(b'}')

    def start_stream(self, key, listpacks_count, expiry, info):
        self._start_key(key, 0)
        self._out.write(self.encode_key(key) + b':{')

    def end_stream(self, key, items, last_entry_id, cgroups):
        self._end_key(key)
        self._out.write(b'}')

    def start_module(self, key, module_name, expiry, info):
        self._start_key(key, 0)
        self._out.write(self.encode_key(key) + b':{')
        return False

    def end_module(self, key, buffer_size, buffer=None):
        self._end_key(key)
        self._out.write(b'}')


def eprint(*args, **kwargs):
    """Print a string to the stderr stream"""
    print(*args, file=sys.stderr, **kwargs)


VALID_TYPES = ("hash", "set", "string", "list", "sortedset")


def main():
    usage = """usage: %prog [options] /path/to/dump.rdb

Example : %prog --command json -k "user.*" /var/redis/6379/dump.rdb"""

    parser = OptionParser(usage=usage)
    parser.add_option("-c", "--command", dest="command",
                      help="Command to execute. Valid commands are json, diff, justkeys, justkeyvals, memory and protocol",
                      metavar="FILE")
    parser.add_option("-f", "--file", dest="output",
                      help="Output file", metavar="FILE")
    parser.add_option("-n", "--db", dest="dbs", action="append",
                      help="Database Number. Multiple databases can be provided. If not specified, all databases will be included.")
    parser.add_option("-k", "--key", dest="keys", default=None,
                      help="Keys to export. This can be a regular expression")
    parser.add_option("-o", "--not-key", dest="not_keys", default=None,
                      help="Keys Not to export. This can be a regular expression")
    parser.add_option("-t", "--type", dest="types", action="append",
                      help="""Data types to include. Possible values are string, hash, set, sortedset, list. Multiple typees can be provided. 
                    If not specified, all data types will be returned""")
    parser.add_option("-b", "--bytes", dest="bytes", default=None,
                      help="Limit memory output to keys greater to or equal to this value (in bytes)")
    parser.add_option("-l", "--largest", dest="largest", default=None,
                      help="Limit memory output to only the top N keys (by size)")
    parser.add_option("-e", "--escape", dest="escape", choices=ESCAPE_CHOICES,
                      help="Escape strings to encoding: %s (default), %s, %s, or %s." % tuple(ESCAPE_CHOICES))

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.error("Redis RDB file not specified")
    dump_file = args[0]

    filters = {}
    if options.dbs:
        filters['dbs'] = []
        for x in options.dbs:
            try:
                filters['dbs'].append(int(x))
            except ValueError:
                raise Exception('Invalid database number %s' % x)

    if options.keys:
        filters['keys'] = options.keys

    if options.not_keys:
        filters['not_keys'] = options.not_keys

    if options.types:
        filters['types'] = []
        for x in options.types:
            if not x in VALID_TYPES:
                raise Exception('Invalid type provided - %s. Expected one of %s' % (x, (", ".join(VALID_TYPES))))
            else:
                filters['types'].append(x)

    out_file_obj = None
    try:
        if options.output:
            out_file_obj = open(options.output, "wb")
        else:
            # Prefer not to depend on Python stdout implementation for writing binary.
            out_file_obj = os.fdopen(sys.stdout.fileno(), 'wb')

        try:
            callback = {
                'diff': lambda f: DiffCallback(f, string_escape=options.escape),
                'json': lambda f: JSONCallback(f, string_escape=options.escape),
                'justkeys': lambda f: KeysOnlyCallback(f, string_escape=options.escape),
                'justkeyvals': lambda f: KeyValsOnlyCallback(f, string_escape=options.escape),
                'memory': lambda f: MemoryCallback(PrintAllKeys(f, options.bytes, options.largest),
                                                   64, string_escape=options.escape),
                'protocol': lambda f: ProtocolCallback(f, string_escape=options.escape)
            }[options.command](out_file_obj)
        except:
            raise Exception('Invalid Command %s' % options.command)

        if not PYTHON_LZF_INSTALLED:
            eprint("WARNING: python-lzf package NOT detected. " +
                   "Parsing dump file will be very slow unless you install it. " +
                   "To install, run the following command:")
            eprint("")
            eprint("pip install python-lzf")
            eprint("")

        parser = RdbParser(callback, filters=filters)
        parser.parse(dump_file)
    finally:
        if options.output and out_file_obj is not None:
            out_file_obj.close()


if __name__ == '__main__':
    main()
