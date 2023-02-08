from scsiio import SCSIDev

def hexdump(data, width=16):
    for i in range(0, len(data), width):
        s = '%8X: ' % i

        for j in range(width):
            if (i+j) < len(data):
                s += '%02X ' % data[i+j]
            else:
                s += '-- '

        s += ' |'

        for j in range(width):
            if (i+j) < len(data):
                c = data[i+j]
                if c < 0x20 or c >= 0x7f: c = ord('.')
                s += chr(c)
            else:
                s += ' '

        s += '|'

        print(s)
    print()


with SCSIDev('/dev/sg3') as dev:
    try:
        dev.execute(b'\xfa\x01\x00\x00\x00\x00', None, None)
    except:
        pass

    dev.execute(b'\xfa\x00YhHp', None, None)

    #----------#----------#----------#----------#----------#

    buff = bytearray(b'Mizu' * (512//4))

    # disable ints
    code = [0xc2, 0xaf]                 # clr <EA>
    # light up LED
    code += [0x53, 0xfe, ~0x02]         # anl 0xfe, #~0x02

    # en CS pin --- SHOULD FIX THAT PROBLEM!!
    code += [0x53, 0xfd, ~0x08]         # anl 0xfd, #~0x08
    # CS low
    code += [0x53, 0xf5, ~0x08]         # anl 0xf5, #~0x08


    code += [0x90, 0x03,0x00]           # mov dptr, 0x0300
    code += [0x78, 0]                   # mov r8, 0

    code += [0x12, 0x6c,0xdd]           # lcall 0x6cdd

    # CS high
    code += [0x43, 0xf5, 0x08]          # orl 0xf5, #0x08

    # turn off the LED
    code += [0x43, 0xfe, 0x02]          # anl 0xfe, #0x02
    # en ints
    code += [0xd2, 0xaf]                # setb <EA>
    # return
    code += [0x22]                      # ret

    for i, b in enumerate(code):
        buff[i] = b & 0xff

    buff = bytes(buff)

    dev.execute(b'\xfa\x03\x00\x00\x00\x00', buff, None)

    #----------#----------#----------#----------#----------#

    dev.execute(b'\xfa\x02\x00\x00\x02\x00', None, None)

    buff = bytearray(1024)
    dev.execute(b'\xfa\x04\x00\x00\x00\x00', None, buff)
    hexdump(buff[0x100:0x180])

    #----------#----------#----------#----------#----------#

    dev.execute(b'\xfa\x01\x00\x00\x00\x00', None, None)

