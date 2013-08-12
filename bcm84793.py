#!/usr/bin/python

import os, sys, traceback, getopt
sys.path.append('/root/abstracts')
from mdio_lib import mdio_lib

def usage() :
    print ''
    print 'Usage: ', sys.argv[0], ' - [rw]'
    print '   -r: read from reg 0, no arguments'
    print '   -w: write data to reg 0, no arguments'
    print ''
    sys.exit(0)

def main() :
    try :
        opts, args = getopt.getopt(sys.argv[1:], 'rw:')
    except getopt.Getopterror, err:
        print str(err)
        usage()

    phy = 0
    addr = 1
    rw = None
    data = None
    reg = None

    for o, a in opts :
        if o == '-r' :
            reg = 0
            rw = 0
        elif o == '-w' :
            reg = 0
            rw = 1
            data = a
        else :
            usage()

    handle = mdio_lib()

    if (reg == None or rw == None) :
        print 'Missing arguments'
        usage()
    else :
        ret = handle.mdioparse(str(phy), str(addr), str(reg), rw, data)


if __name__ == "__main__" :
    try :
        main()
    except Exception, e:
        print 'Exception: '+str(e.__class__)+': '+str(e)
        traceback.print_exc()
        handle.mdioreleaselock()
        sys.exit(0)
