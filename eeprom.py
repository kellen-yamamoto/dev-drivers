#!/usr/bin/python

import os, sys, traceback, getopt, time
sys.path.append('/root/abstracts')
from spi_lib import spi_lib
handle = spi_lib()

from util_lib import util_lib
utilhandle = util_lib()


def usage() :
    print ''
    print 'Usage: ', sys.argv[0], ' -[rlwdsp]'
    print '   -r: read offset'
    print '   -l: length of read'
    print '   -w: write offset'
    print '   -d: data, comma separated'
    print '   -s: Name of file to save content to'
    print '   -p: Name of file to write to eeprom'
    print ''
    sys.exit(0)

def writeenable() :
    handle.spiparse('0x06', '0', '0x00')

#Enables entire chip to be written to
def unprotect() :
    writeenable()
    handle.spiparse('0x01', '0', '0x00')

#Erases chip
def clearmem() :
    print 'Erasing...'
    writeenable()
    handle.spiparse('0x60', '0', '0x00')
    #Max time of chip erase is 7 sec
    time.sleep(7)

#Erases 4kb block of memory
def clearblock(addr) :
    writeenable()
    handle.spiparse('0x20'+parseaddr(addr), '0', '0x00')
    #Max time of 4kb block erase is 200ms
    time.sleep(0.2)

def checkempty(addr, length) :
    ret = eepromread(addr, length).rstrip()
    for num in ret.split(' ') :
        if num != '0xff' :
            return 0
    return 1

#Separates address into 3 command bytes
def parseaddr(addr) :
    addrb3 = addr & 0xff
    addrb2 = addr>>8 & 0xff
    addrb1 = addr>>16 & 0xff
    addrstr = ','+'0x{:02x}'.format(addrb1)+','+'0x{:02x}'.format(addrb2)+','+'0x{:02x}'.format(addrb3)
    return addrstr

def eepromread(addr, length) :
    return handle.spiparse('0x03'+parseaddr(addr), length, None)

#Checks if memory location is empty, if it isn't, erases block before writing
def eepromwrite(addr, data) :
    if checkempty(addr, str(data.count(',')+1)) == 0 :
        clearblock(addr)
    writeenable()
    handle.spiparse('0x02'+parseaddr(addr), '0', data)

def savetofile(filename) :
    f = open(filename, 'wb')
    i = 0
    print 'Writing to file: ', filename
    while i < 0x07FFFF :
        ret = eepromread(i, str(128)).rstrip()
        intlist = ret.split(' ')
        for num in intlist :
            f.write('{:02x}'.format(int(num, 0)))
        i += 128
    f.close()
    print 'Done'
    return 0

def writefromfile(filename) :
    clearmem()
    f = open(filename, 'rb')
    i = 0
    writestr = ''
    print 'Writing', filename, 'to eeprom...'
    while i < 0x07FFFF :
        for s in range(0, 127) :
            ret = f.read(2)
            writestr += '0x'+ret+','
        writestr += '0x'+f.read(2)
        eepromwrite(i, writestr)
        i += 128
        writestr = ''
    f.close()
    print 'Done'
    return 0

def main() :
    try :
        opts, args = getopt.getopt(sys.argv[1:], 'r:l:w:d:s:p:')
    except getopt.GetoptError, err:
        print str(err)
        usage()

    rw = None
    addr = None
    data = None
    filename = None

    for o, a in opts :
        if o == '-r' :
            addr = int(a, 0)
        elif o == '-l' :
            rw = a
        elif o == '-w' :
            addr = int(a, 0)
            rw = '0'
        elif o == '-d' :
            data = a
        elif o == '-s' :
            rw = '1'
            filename = a
        elif o == '-p' :
            rw = '0'
            filename = a
        else :
            usage()

    unprotect()

    if filename != None :
        if int(rw, 0) == 1 :
            savetofile(filename)
        else :
            writefromfile(filename)
    elif (rw == None or addr == None) :
        print 'Missing arguments'
        usage()
    else :
        if int(rw, 0) == 0 :
            eepromwrite(addr, data)
        else :
            utilhandle.printhexgrid(addr, eepromread(addr, rw))
    sys.exit(0)

if __name__ == "__main__" :
    try :
        main()
    except Exception, e:
        print 'Exception: '+str(e.__class__)+': '+str(e)
        traceback.print_exc()
        handle.spireleaselock()
        sys.exit(0)
