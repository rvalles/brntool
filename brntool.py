#!/usr/bin/python
# -*- coding: utf-8 -*-
# Keep python2 working
from __future__ import division  # 1/2 = float, 1//2 = integer
from __future__ import print_function  # print("blah", file=whatever)
# Keep python2 working end
from optparse import OptionParser
import serial
import sys
import re

lineregex = re.compile(r'0x(?:[0-9A-F]{8})((?: [0-9A-F]{2}){1,16})')


def get2menu(ser, verbose):
    if verbose:
        print("Waiting for a prompt...", file=sys.stderr)
    while True:
        ser.write("   !".encode())
        if (ser.read(1) == b']' and ser.read(1) == b':'):
            while ser.read(256):
                pass
            if verbose:
                print("Ok.", file=sys.stderr)
            return


def memreadblock(ser, addr, size):
    while ser.read(1):
        pass
    ser.write('r'.encode())
    while not (ser.read(1) == b'0' and ser.read(1) == b'x'):
        pass

    ser.write(("%x" % addr).encode())
    ser.write('\r'.encode())
    while not (ser.read(1) == b'.' and ser.read(1) == b'.' and ser.read(1) == b'.'):
        pass
    ser.write('3'.encode())
    while not ser.read(1) == b')':
        pass
    ser.write(str(size).encode())
    ser.write('\r'.encode())
    buf = ''
    m = False
    while not m:
        m = lineregex.match(ser.readline().decode().strip())
    while m:
        bytes = [chr(int(x, 16)) for x in m.group(1)[1:].split(' ')]
        buf += ''.join(bytes)
        m = lineregex.match(ser.readline().decode().strip())
    return buf


def memreadblock2file(ser, fd, addr, size):
    while True:
        buf = memreadblock(ser, addr, size)
        if len(buf) == size:
            break
        sys.stderr.write('!')
    fd.write(buf.encode())
    return


def memread(ser, path, addr, size, verbose):
    bs = 10000  # 10000 is usually the maximum size for an hexdump on brnboot.
    get2menu(ser, verbose)
    if path == "-":
        fd = sys.stdout
    else:
        fd = open(path, "wb")
    while 0 < size:
        if size > bs:
            memreadblock2file(ser, fd, addr, bs)
            size -= bs
            addr += bs
            print("Addr: " + hex(addr), file=sys.stderr)
            print("Size: " + str(size), file=sys.stderr)
        else:
            memreadblock2file(ser, fd, addr, size)
            size = 0
    fd.close()
    return


def main():
    optparser = OptionParser("usage: %prog [options]", version="%prog 0.1")
    optparser.add_option("--verbose", action="store_true", dest="verbose", help="be verbose", default=False)
    optparser.add_option("--serial", dest="serial", help="specify serial port", default="/dev/ttyUSB0", metavar="dev")
    optparser.add_option("--read", dest="read", help="read mem to file", metavar="path")
    optparser.add_option("--addr", dest="addr", help="mem address", metavar="addr")
    optparser.add_option("--size", dest="size", help="size to copy", metavar="bytes")
    (options, args) = optparser.parse_args()
    if len(args) != 0:
        optparser.error("incorrect number of arguments")
    ser = serial.Serial(options.serial, 115200, timeout=1)
    if options.read:
        memread(ser, options.read, int(options.addr, 0), int(options.size, 0), options.verbose)
    return


if __name__ == '__main__':
    main()
