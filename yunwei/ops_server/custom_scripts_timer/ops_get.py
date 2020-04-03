#!/usr/bin/env python3
# coding: utf-8
__author__ = 'wanglei_sxcpx@kedacom.com'

import re
from optparse import OptionParser

from exec_custom_scripts import ScriptsHandler


def main():
    key = ''
    params = ''
    usage = """usage: %prog [options]

Example : %prog -k "ops.test", %prog -k "ops.test[1,2]" """

    parser = OptionParser(usage=usage)
    parser.add_option("-k", "--key", dest="key", default=None,
                      help="Key of your custom script to execute")
    (options, args) = parser.parse_args()
    if options.key:
        key = options.key.strip()

    s = ScriptsHandler()
    key_conf = s.get_key_conf()
    # print(key_conf)

    if not key:
        print('-k not specified')
        exit(1)
    if '[' in key and ']' in key:
        re_match = re.match(r'((\w+\.?)+)\[(.*)\]', key)
        script_key = re_match.group(1)
        if re_match.group(3):
            params_list = re_match.group(3).split(',')
            for param in params_list:
                params += '\'%s\' ' % param
    else:
        script_key = key
    cmdline = key_conf.get(script_key)
    if not cmdline:
        print('key: %s is undefined' % key)
        exit(2)

    exec_result = s.exec_cmdline(script_key, 30, cmdline, params)
    stdout = exec_result.get('stdout')
    stderr = exec_result.get('stderr')
    print('cmdline: %s %s' % (cmdline, params))
    print('stdout: %s, stderr: %s' % (stdout, stderr))


if __name__ == '__main__':
    main()
