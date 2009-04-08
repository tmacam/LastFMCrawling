#!/usr/bin/python

import bsddb
import gdbm
import sys

def main(args):
    if not args:
        sys.stderr.write("Usage: gdbm2bsddb.py IN.gdbm OUT.bsddb\n")
        sys.exit(1)
    try:
        _input, _output = args
    except:
        sys.stderr.write("Wrong number of arguments.\n")
        sys.stderr.write("Usage: gdbm2bsddb.py IN.gdbm OUT.bsddb\n")
        sys.exit(1)

    input = gdbm.open(_input,"r")
    output = bsddb.hashopen(_output,"c")

    k = input.firstkey()
    while k:
        output[k] = input[k]
        k = input.nextkey(k)
    input.close()
    output.close()


if __name__ == '__main__':
    main(sys.argv[1:])
    print "Done."
