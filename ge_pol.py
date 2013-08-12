#!/usr/bin/python

#ge_pol using smbus module

import sys, traceback, os
import smbus
import ctypes
from array import array
b = smbus.SMBus(0)

def convert_linear(val) :
    mantissa_raw = ctypes.c_short(val & 0x3ff)
    if mantissa_raw.value & 0x200 :
        mantissa_raw.value |= 0xfc00

    mantissa = float(mantissa_raw.value)

    exp_raw = ctypes.c_short(val >> 11)
    if exp_raw.value & 0x10 :
        exp_raw.value |= 0xffe0

    exp = float(exp_raw.value)
    factor = pow(2.0, exp)

    return mantissa*factor

def read_vout(addr) :
    vout_raw = b.read_word_data(addr, 0x8b)
    if vout_raw < 0 :
        print 'Error reading i2c'
    vout_cal_offset_raw = b.read_word_data(addr, 0xd4)
    if vout_cal_offset_raw < 0 :
        print 'Error reading i2c'
    vout_cal_gain_raw = b.read_word_data(addr, 0xd5)
    if vout_cal_gain_raw < 0 :
        print 'Error reading i2c'

    vout_uncal = vout_raw * pow(2, -10)
    vout_cal_offset = vout_cal_offset_raw * pow(2, -10)
    vout_cal_gain = convert_linear(vout_cal_gain_raw)

    return (vout_uncal * (1 + vout_cal_gain)) + vout_cal_offset

def read_calibrated_value(addr, base_addr, cal_offset_addr, cal_gain_addr) :
    base_raw = b.read_word_data(addr, base_addr)
    if base_raw < 0 :
        print 'Error reading i2c'
    base_cal_offset_raw = b.read_word_data(addr, cal_offset_addr)
    if base_cal_offset_raw < 0 :
        print 'Error reading i2c'
    base_cal_gain_raw = b.read_word_data(addr, cal_gain_addr)
    if base_cal_gain_raw < 0 :
        print 'Error reading i2c'

    base_uncal = convert_linear(base_raw)
    base_cal_offset = convert_linear(base_cal_offset_raw)
    base_cal_gain = convert_linear(base_cal_gain_raw)

    return (base_uncal * (1 + base_cal_gain)) + base_cal_offset

def read_vin(addr) :
    return read_calibrated_value(addr, 0x88, 0xd6, 0xd7)

def read_iout(addr) :
    return convert_linear(b.read_word_data(addr, 0x8c))

def main() :

    if len(sys.argv) != 2 :
        print 'missing arguments'
        sys.exit(0)
    addr = int(sys.argv[1], 16)

    print hex(b.read_byte_data(addr, 0x10))
    print hex(b.read_byte_data(addr, 0x20))
#   Register does not exist
#    print b.read_word_data(addr, 0x21)
    print hex(b.read_word_data(addr, 0x22))
#   More accurate without adjusting voltage offset
#    b.write_word_data(addr, 0x22, 0x0016)
    print hex(b.read_word_data(addr, 0x22))
    b.write_word_data(addr, 0x22, 0x0000)
#   Produces IOError
#    b.write_byte(addr, 0x11)
    print 'Vin: ', read_vin(addr), 'V'
    print 'Vout: ', read_vout(addr), 'V'
    print 'Iout: ', read_iout(addr), 'I'
    sys.exit(0)

if __name__ == "__main__" :
    try :
        main()
    except Exception, e:
        print 'Exception: '+str(e.__class__)+': '+str(e)
        traceback.print_exc()
        sys.exit(0)
