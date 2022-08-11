'''
unpack_radio-dnl.py
(C)2022 by Go4IT@denkdose.de
Used to extract contents of the "radio.dnl" file:
 * V850 bootloader
 * V850 firmware
 * External EEPROM initial data
'''
import sys
import os.path

def usageExit():
    print("Usage: %s RADIO.DNL_FILE" % (sys.argv[0]))
    exit(1)

def dumpFrame(frame, offset=0, size=0):
    if size == 0:
        size = len(frame)
    print("Offset    00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")
    for pos in range(offset, len(frame), 0x10):
        if pos >= size:
            break
        print("%08X  " % (pos), end='')
        for i in range(pos, pos + 0x10):
            print("%02X " % (frame[i]), end='')
        print("")
    print("")

def getUint8_be(data, offset):
    return data[offset]

def getUint32_be(data, offset):
    v = (data[offset + 0] << 24) | (data[offset + 1] << 16) | (data[offset + 2] << 8) | (data[offset + 3])
    return v

# MAIN
if len(sys.argv) != 2:
    usageExit()
dnl_file = sys.argv[1]
if not os.path.isfile(dnl_file):
    usageExit()

with open(dnl_file, "rb") as ifh:
    current_block = 0x00
    while True:
        frame = ifh.read(0x80)
        if frame == b"":
            break
        if frame[0:8] == b"ADMINEND":
            print("End marker detected")
            break

        block_type = getUint8_be(frame, 0x00)
        block_index = getUint8_be(frame, 0x01)
        data_len = getUint32_be(frame, 0x06)
        if data_len < 0x100:
            frame_len = 0x100
        elif (data_len % 0x100) > 0:
            frame_len = ((data_len % 0x100) + 1) * 0x100
        else:
            frame_len = data_len

        if (block_type != current_block):
            if block_type == 0x34:
                block_name = "eeprom"
            elif block_type == 0x40:
                block_name = "v850"
            elif block_type == 0x82:
                block_name = "bootloader"
            else:
                block_name = "unknown"
            out_file = "block_0x%02X_%s.bin" % (block_type, block_name)
            ofh = open(out_file, "wb")
            current_block = block_type

        print("Block: 0x%02X" % (block_type))
        print("Index: #%d" % (block_index))
        print("Size:  0x%08X Bytes" % (data_len))
        print("File:  %s" % (out_file))
        dumpFrame(frame,0, 0x20)
        frame = ifh.read(frame_len)
        data = frame[0:data_len]
        ofh.write(data)
