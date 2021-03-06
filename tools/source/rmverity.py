#!/usr/bin/env python3
#
# rmverity - by SuperR.
#
# Do not edit this file unless you know what you are doing

import os
import sys
import re
import argparse

parser = argparse.ArgumentParser(description="Remove dm-verity from boot.img, fstab, or zImage")
group = parser.add_mutually_exclusive_group()
group.add_argument("-s", "--status", action="store_true", help="returns \"yes\" or \"no\" if dm-verity is present and does not patch the file.")
group.add_argument("-b", "--backup", action="store_true", help="Make backup of original file before patching.")
parser.add_argument("filename", help="Path to the working file")
args = parser.parse_args()

filename = args.filename

def existf(thefile):
	try:
		if os.path.isdir(thefile):
			return 2
		if os.stat(thefile).st_size > 0:
			return 0
		else:
			return 1
	except OSError:
		return 2

if existf(filename) != 0:
    print('\n'+filename+' does not exist.\n')
    sys.exit()

wflag = None
with open(filename, 'rb') as f:
    data = f.read()

thechk = b'\x2c\x76\x65\x72\x69\x66\x79'
if re.search(thechk, data):
    if args.status:
        print('yes')
        sys.exit()

    print('Removing dm-verity from '+filename+' ...')
    result = {}
    for i in re.finditer(thechk, data):
        begin = i.start()
        bnum = 7
        while True:
            if data[begin + bnum] == 0:
                result[data[begin:bnum + begin]] = b'\x00'*bnum
                break
            elif data[begin+bnum:begin+bnum+1] == b'\n':
                result[data[begin:bnum + begin]] = b''
                break
            elif data[begin+bnum:begin+bnum+1] == b',':
                result[data[begin:bnum + begin]] = b''
                break
            else:
                bnum = bnum + 1
        
    for swap in list(result):
        data = data.replace(swap, result[swap])

    wflag = 1
else:
    if args.status:
        print('no')
        sys.exit()
    
if wflag:
    if args.backup:
        from shutil import copyfile
        if not args.status and existf(filename+'.bak') != 0:
            print('Backing up '+filename+' ...')
            copyfile(filename, filename+'.bak')

    with open(filename+'_new', 'wb') as o:
        devnull = o.write(data)
    os.replace(filename+'_new', filename)
    print('\n'+filename+' patched\n')
else:
    print('\nNo changes made to '+filename+'\n')