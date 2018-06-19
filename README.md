This tool can, so far, given a serial port connected to a device with
brnboot/amazonboot, dump its flash into a file.

Homepage: https://github.com/rvalles/brntool

It has been tested with

* Arcadyan ARV4518PW http://wiki.openwrt.org/toh/arv4518pw (as distributed by the spanish isp ya.com)
* Arcadyan ARV7506PW11 (tested by Jan-Philipp Litza and einsiedlerkrebs)
* [Arcadyan ARV7518PW](http://wiki.openwrt.org/toh/astoria/arv7518pw) (with --size=0x800000 to whole memory)
* [Arcadyan ARV7519RW22-A-LT](https://openwrt.org/toh/arcadyan/arv7519) (AKA Livebox 2.1)
* SMC SMC7904WBRA (as distributed by the spanish isp ya.com)
* [Speedport W 722V Typ B (VGV8529HW22)](https://wiki.openwrt.org/toh/t-com/spw722vtypb) (with --size=0x800000)
* [DSL-EasyBOX 803 A, HW Version R01C](https://openwrt.org/toh/astoria/arv752dpw22)

About brnboot: http://wiki.openwrt.org/doc/techref/bootloader/brnboot

# Notes

The serial port in ARV4518PW SMC7904WBRA is hidden inside their case. If
opened, there's a 5x2 header. Going horizontally from the marked pin, which
is 1: 2.RX, 3.TX, 5.GND, 6.+3.3v. UART is at 115200bps.

Some devices might have a different pinout, but I have yet to encounter any
such hardware.

To dump the whole flash of my AR4518PW into some file, I do:
./brntool.py --read=AR4518PW_whole.dump --addr=0xB0000000 --verbose
--size=0x400000

If you specify `-` as the output filename in the `--read` option, the output will be sent to `stdout`.
On a Windows platform you **must** call the script with the `–u` option in order to prevent the replacement
of `'\x0a' ` by ` '\x0d\x0a' ` in this case.

And then turn it on.

A successful flash block read will output the address and size of the block while a botched one (a byte or
more gets lost in the serial port) will output '!' and retry. Even so, unless
in a hurry, I'd recommend to at least dump twice and compare the dumps, just
to be on the safe side.

See the "erase flash" menu on the menus brnboot provides through the serial
port in order to figure out the flash layout in these devices. I cannot
guarantee that none of the devices using brnboot will just start erasing the
whole flash by just selecting the option, so act at your own risk.

Thanks to Jan-Philipp Litza for patches and confirming ARV7506PW11 works.

Thanks to einsiedlerkrebs for more testing and reminding me about Python 3.

-------
Roc Vallès.
<vallesroc @.aaa@ @gmail.com>
