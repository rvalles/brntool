#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import division #1/2 = float, 1//2 = integer, python 3.0 behaviour in 2.6, to make future port to 3 easier.
from optparse import OptionParser
import serial
import sys
#import struct
import re
lineregex = re.compile(r'0x(?:[0-9A-F]{8})((?: [0-9A-F]{2}){1,16})')
def get2menu(ser,verbose):
	if verbose:
		print >>sys.stderr,"Waiting for a prompt...",
	while True:
		ser.write("   !")
		if(ser.read(1)==']' and ser.read(1)==':'):
			while ser.read(256):
				pass
			if verbose:
				print >>sys.stderr,"Ok."
			return
def memreadblock(ser,addr,size):
	while ser.read(1):
		pass
	ser.write('r')
	while not (ser.read(1)=='0' and ser.read(1)=='x'):
		pass
	ser.write(hex(addr)[2:-1 if addr.__class__ == long else len(hex(addr))])
	ser.write('\r')
	while not (ser.read(1)=='.' and ser.read(1)=='.' and ser.read(1)=='.'):
		pass
	ser.write('3')
	while not ser.read(1)==')':
		pass
	ser.write(str(size))
	ser.write('\r')
	buf=''
	m = False
	while not m:
		m = lineregex.match(ser.readline().strip())
	while m:
		#addr = int(m.group(1), 16)
		bytes = [chr(int(x, 16)) for x in m.group(1)[1:].split(' ')]
		buf+=''.join(bytes)
		#print addr, bytes
		#print addr,' '.join(['%02X' % b for b in bytes])
		m = lineregex.match(ser.readline().strip())
	return buf
def memreadblock2file(ser,fd,addr,size):
	while True:
		buf=memreadblock(ser,addr,size)
		if len(buf)==size:
			break
		sys.stderr.write('!')
	sys.stderr.write('.')
	fd.write(buf)
	return
def memread(ser,path,addr,size,verbose):
	#bs=1024
	bs=10000 #10000 is usually the maximum size for an hexdump on brnboot.
	get2menu(ser,verbose)
	if path == "-":
		fd=sys.stdout
	else:
		fd=open(path,"wb")
	while 0<size:
		if size>bs:
			memreadblock2file(ser,fd,addr,bs)
			size-=bs
			addr+=bs
		else:
			memreadblock2file(ser,fd,addr,size)
			size=0
	fd.close()
	return
def main():
	optparser = OptionParser("usage: %prog [options]",version="%prog 0.1")
	optparser.add_option("--verbose", action="store_true", dest="verbose", help="be verbose", default=False)
	optparser.add_option("--serial", dest="serial", help="specify serial port", default="/dev/ttyUSB0", metavar="dev")
	optparser.add_option("--read", dest="read", help="read mem to file", metavar="path")
	#optparser.add_option("--write", dest="write",help="write mem from file", metavar="path")
	optparser.add_option("--addr", dest="addr",help="mem address", metavar="addr")
	optparser.add_option("--size", dest="size",help="size to copy", metavar="bytes")
	(options, args) = optparser.parse_args()
	if len(args) != 0:
		optparser.error("incorrect number of arguments")
	ser = serial.Serial(options.serial, 115200, timeout=1)
	if options.read:
		memread(ser,options.read,int(options.addr,0),int(options.size,0),options.verbose)
	return
if __name__ == '__main__':
	main()
