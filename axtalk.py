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

    #code += [0x90, 0x03, 0x00]          # mov dptr, #0x300
    #code += [0x78, 0x00]                # mov r0, #0
    #code += [0x79, 0x80]                # mov r1, #0

    #code += [0xe8]                      # mov a, r0
    #code += [0xff]                      # mov r7, a
    #code += [0x12, 0x6d,0xc4]           # acall 0x6dc4
    #code += [0xef]                      # mov a, r7
    #code += [0xf0]                      # movx @dptr, a
    #code += [0xa3]                      # inc dptr
    #code += [0x08]                      # inc r0
    #code += [0xd9, -11]                 # djnz r1, x

    code += [0x12, 0x6E,0xBC]           # acall 0x6ebc
    code += [0x12, 0x6F,0x0B]           # acall 0x6f0b

    code += [0x12, 0x6E,0xBC]           # acall 0x6ebc
    code += [0x12, 0x6F,0x0B]           # acall 0x6f0b

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

    buff = bytearray(1024)
    dev.execute(b'\xfa\x02\x00\x00\x02\x00konachan', None, buff)
    hexdump(buff)

    buff = bytearray(1024)
    dev.execute(b'\xfa\x04\x00\x00\x00\x00', None, buff)
    #hexdump(buff[0x100:0x180])
    hexdump(buff)

    #----------#----------#----------#----------#----------#

    dev.execute(b'\xfa\x01\x00\x00\x00\x00', None, None)

