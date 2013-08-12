#!/usr/bin/python

import os, sys, traceback, getopt
sys.path.append('/root/abstracts')
from i2c_lib import i2c_lib

def usage() :
    print ''
    print 'Usage: ', sys.argv[0], ' -[iesc]'
    print '   -i: Read internal temperature, no args'
    print '   -e: Read external temperature, no args'
    print '   -s: Read status reg, no args'
    print '   -c: Set configuration byte'
    print ''
    sys.exit(0)

def main() :
    try :
        opts, args = getopt.getopt(sys.argv[1:], 'iesc:')
    except getopt.GetoptError, err:
        print str(err)
        usage()
    addr = 76
    reg = None
    rw = None
    data = None

    for o, a in opts :
        if o == '-i' :
            reg = 0
            rw = 0
        elif o == '-e' :
            reg = 1
            rw = 0
        elif o == '-s' :
            reg = 2
            rw = 0
        elif o == '-c' :
            data = a
            reg = 9
            rw = 1
        else :
            usage()

    handle = i2c_lib()

    if (reg == None or (rw == 1 and data == None)) :
        print 'Missing arguments'
        usage()
    else :
        ret = handle.i2cparse(str(addr), str(reg), str(rw), data, str(1))
        if reg < 2 :
            print 'Temp: ', int((ret.rstrip()), 0)*1, ' C'
        else :
            if rw == 0 :
                print ret, bin(ret.rstrip())
    sys.exit(0)

if __name__ == "__main__" :
    try :
        main()
    except Exception, e:
        print 'Exception: '+str(e.__class__)+': '+str(e)
        traceback.print_exc()
        handle.i2creleaselock()
        sys.exit(0)
