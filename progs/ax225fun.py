from scsiio import SCSIDev
import argparse, time

ap = argparse.ArgumentParser(description='AX225 fun')

ap.add_argument('--device', required=True,
                help='Path to the AX225 device (e.g. /dev/sg5)')

ap.add_argument('file',
                help='File to flash')

args = ap.parse_args()



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



def dis8051(code):
    code = bytes([v & 0xff for v in code])

    print("======== DIS8051 ========")

    print(code.hex('.'))

    print(">>>>>>>>>>>>>>>>>>>>>>>>>")



def makebar(ratio, length):
    bratio = int(ratio * length)

    bar = ''

    if bratio > 0:
        bar += '=' * (bratio - 1)
        bar += '>'

    bar += ' ' * (length - bratio)

    return bar



with SCSIDev(args.device) as dev:
    def ax_cmdenter():
        dev.execute(b'\xfa\x00YhHp', None, None)

    def ax_cmdexit():
        dev.execute(b'\xfa\x01\x00\x00\x00\x00', None, None)

    def ax_callcode(addr=0x200):
        dev.execute(b'\xfa\x02' + addr.to_bytes(4, 'big'), None, None)

    def ax_write512to0x200(data):
        data = bytes(data)
        dev.execute(b'\xfa\x03\x00\x00\x00\x00', data, None)

    def ax_read1024from0x200():
        data = bytearray(1024)
        dev.execute(b'\xfa\x04\x00\x00\x00\x00', None, data)
        return bytes(data)

    def ax_read4fromxdata(addr):
        data = bytearray(4)
        dev.execute(b'\xfa\x05YhHp' + addr.to_bytes(3, 'big'), None, data)
        return bytes(data)

    def ax_resetpopa():
        dev.execute(b'\xfa\xfeYhHp', None, None)

    #----------#----------#----------#----------#----------#

    try:
        ax_cmdexit()
    except:
        pass

    print(ax_read4fromxdata(0x4000 + 0x18f5))

    ax_cmdenter()

    #----------#----------#----------#----------#----------#

    def code2buff(code):
        #dis8051(code)

        buff = bytearray(b'Mizu' * (512//4))

        for i, b in enumerate(code):
            buff[i] = b & 0xff

        return buff

    #########################################################

    def cmacro_prologue():
        # disable ints
        code  = [0xc2, 0xaf]                 # clr <EA>

        # light up an LED
        code += [0x43, 0xfe, 0x02]          # orl 0xfe, #0x02

        # CS high
        code += [0x43, 0xf5, 0x08]          # orl 0xfd, #0x08

        # CS to output !!
        code += [0x53, 0xfd, ~0x08]         # anl 0xfd, #~0x08

        # whatever
        #code += [0x53, 0xf1, ~0x08]         # anl 0xf1, #~0x08
        #code += [0x00] * 8              # a couple of NOPs

        return code

    def cmacro_epilogue():
        # turn off the LED
        code  = [0x53, 0xfe, ~0x02]         # anl 0xfe, #~0x02

        # en ints
        code += [0xd2, 0xaf]                # setb <EA>

        # return
        code += [0x22]                      # ret
        return code

    #--- --- --- --- --- --- --- --- --- ---#

    def cmacro_cs_low():
        return  [0x53, 0xf5, ~0x08]         # anl 0xfd, #~0x02

    def cmacro_cs_high():
        code =  [0x43, 0xf5, 0x08]          # orl 0xfd, #0x02
        code += [0x00] * 2              # a couple of NOPs
        return code

    #--- --- --- --- --- --- --- --- --- ---#

    def cmacro_spi_sendz():
        return  [0x12, 0x6c,0x5a]           # acall 0x6c5a

    def cmacro_spi_sendb():
        return  [0x12, 0x6c,0x5c]           # acall 0x6c5c

    def cmacro_spi_sendb_imm(val):
        code  = [0x7f, val]                 # mov r7, #xxx
        code += cmacro_spi_sendb()
        return code

    def cmacro_spi_sendb_acc():
        code  = [0xff]                      # mov r7, a
        code += cmacro_spi_sendb()
        return code

    #--- --- --- --- --- --- --- --- --- ---#

    def cmacro_spi_recvb():
        return  [0x12, 0x6c,0xdd]           # acall 0x6cdd

    def cmacro_spi_recvb_acc():
        code  = cmacro_spi_recvb()
        code += [0xef]                      # mov a, r7
        return code

    #--- --- --- --- --- --- --- --- --- ---#

    def cmacro_spif_addr24(addr):
        code  = cmacro_spi_sendb_imm(addr >> 16)
        code += cmacro_spi_sendb_imm(addr >> 8)
        code += cmacro_spi_sendb_imm(addr >> 0)
        return code

    def cmacro_spif_enwrite():
        code  = cmacro_cs_low()
        code += cmacro_spi_sendb_imm(0x06)
        code += cmacro_cs_high()
        return code

    def cmacro_spif_pollbusy():
        code  = cmacro_cs_low()

        # send command: [05] read status reg
        code += cmacro_spi_sendb_imm(0x05)

        # poll the status reg's busy bit
        Loop = len(code)
        code += cmacro_spi_recvb_acc()
        code += [0x54, 0x01]                # anl a, #0x01
        code += [0x70, Loop - len(code) - 2]    # jnz <x>

        code += cmacro_cs_high()
        return code

    #########################################################

    def spif_genexec(cmd, idat=None, odatlen=None, pollbusy=False, enwrite=False):
        code  = cmacro_prologue()

        if enwrite:
            code += cmacro_spif_enwrite()

        code += cmacro_cs_low()
        code += cmacro_spi_sendb_imm(cmd)

        if (idat is not None) and (len(idat) > 0):
            code += [0x90, 0x03,0x00]           # mov dptr, #0x300
            code += [0x78, len(idat)]           # mov r0, #xxx
            Loop = len(code)
            code += [0xe0]                      # movx a, @dptr
            code += cmacro_spi_sendb_acc()
            code += [0xa3]                      # inc dptr
            code += [0xd8, Loop - len(code) - 2]    # djnz r0, <x>

        if (odatlen is not None) and (odatlen > 0):
            code += [0x90, 0x03,0x00]           # mov dptr, #0x300
            code += [0x78, odatlen]             # mov r0, #xxx
            Loop = len(code)
            code += cmacro_spi_recvb_acc()
            code += [0xf0]                      # movx @dptr, a
            code += [0xa3]                      # inc dptr
            code += [0xd8, Loop - len(code) - 2]    # djnz r0, <x>

        code += cmacro_cs_high()

        if pollbusy:
            code += cmacro_spif_pollbusy()

        code += cmacro_epilogue()

        buff = code2buff(code)

        if idat is not None:
            buff[0x100:0x100+len(idat)] = idat

        ax_write512to0x200(buff)
        ax_callcode()

        if odatlen is not None:
            buff = ax_read1024from0x200()
            return buff[0x100:0x100+odatlen]

    def spif_write_sr(val):
        code  = cmacro_prologue()

        code += cmacro_spif_enwrite()

        code += cmacro_cs_low()
        code += cmacro_spi_sendb_imm(0x01)
        code += cmacro_spi_sendb_imm(val)
        code += cmacro_cs_high()

        code += cmacro_spif_pollbusy()

        code += cmacro_epilogue()

        buff = code2buff(code)

        ax_write512to0x200(buff)
        ax_callcode()

    def spif_erase_sector(addr):
        code  = cmacro_prologue()

        code += cmacro_spif_enwrite()

        code += cmacro_cs_low()
        code += cmacro_spi_sendb_imm(0x20)
        code += cmacro_spif_addr24(addr)
        code += cmacro_cs_high()

        code += cmacro_spif_pollbusy()

        code += cmacro_epilogue()

        buff = code2buff(code)

        ax_write512to0x200(buff)
        ax_callcode()

    def spif_erase_block(addr):
        code  = cmacro_prologue()

        code += cmacro_spif_enwrite()

        code += cmacro_cs_low()
        code += cmacro_spi_sendb_imm(0xd8)
        code += cmacro_spif_addr24(addr)
        code += cmacro_cs_high()

        code += cmacro_spif_pollbusy()

        code += cmacro_epilogue()

        buff = code2buff(code)

        ax_write512to0x200(buff)
        ax_callcode()

    def spif_erase_chip():
        code  = cmacro_prologue()

        code += cmacro_spif_enwrite()

        code += cmacro_cs_low()
        code += cmacro_spi_sendb_imm(0xc7)
        code += cmacro_cs_high()

        code += cmacro_spif_pollbusy()

        code += cmacro_epilogue()

        buff = code2buff(code)

        ax_write512to0x200(buff)
        ax_callcode()

    def spif_program(addr, data):
        code  = cmacro_prologue()

        code += cmacro_spif_enwrite()

        code += cmacro_cs_low()
        code += cmacro_spi_sendb_imm(0x02)
        code += cmacro_spif_addr24(addr)

        code += [0x90, 0x03,0x00]           # mov dptr, #0x300
        code += [0x78, len(data)]           # mov r0, #xxx
        Loop = len(code)
        code += [0xe0]                      # movx a, @dptr
        code += cmacro_spi_sendb_acc()
        code += [0xa3]                      # inc dptr
        code += [0xd8, Loop - len(code) - 2]    # djnz r0, <x>

        code += cmacro_cs_high()

        code += cmacro_spif_pollbusy()

        code += cmacro_epilogue()

        buff = code2buff(code)
        buff[0x100:0x100+len(data)] = data

        ax_write512to0x200(buff)
        ax_callcode()

    ##################

    spif_write_sr(0x00)

    flashid = spif_genexec(0x9f, odatlen=3)
    print('Flash ID: %02x %02x %02x' % (flashid[0],flashid[1],flashid[2]))

    flashsize = 1 << flashid[2]
    print('Flash size: %x (%.2f MiB)' % (flashsize, flashsize / 1048576))

    #spif_erase_chip()

    for addr in range(0, flashsize, 0x10000):
        ratio = addr / flashsize
        print('\rerase@ %06x [%s] %3d%%' % (addr, makebar(ratio, 50), ratio * 100), end='', flush=True)
        spif_erase_block(addr)

    print()

    with open(args.file, 'rb') as f:
        f.seek(0, 2)
        fsize = f.tell()
        f.seek(0)

        addr = 0
        while addr < flashsize:
            ratio = addr / fsize
            print('\rwrite@ %06x [%s] %3d%%' % (addr, makebar(ratio, 50), ratio * 100), end='', flush=True)

            blk = f.read(0x1000)
            if blk == b'': break

            #print('@@@ %06x' % addr)

            #spif_erase_sector(addr)

            while len(blk) > 0:
                page = blk[:0x100]
                blk = blk[0x100:]

                spif_program(addr, page)

                addr += len(page)

        print()

    ##################

    '''
    with open('dump.bin', 'wb') as f:
        for addr in range(0, flashsize, 0x1000):
            print('@@@ %06x' % addr)

            for off in range(0, 0x1000, 0x100):
                code  = cmacro_prologue()
                code += cmacro_cs_low()

                code += cmacro_spi_sendb_imm(0x03)
                code += cmacro_spif_addr24(addr + off)

                # receive data
                code += [0x90, 0x03,0x00]           # mov dptr, #0x300
                code += [0x78, 0x00]                # mov r0, #0
                Loop = len(code)
                code += cmacro_spi_recvb_acc()
                code += [0xf0]                      # movx @dptr, a
                code += [0xa3]                      # inc dptr
                code += [0xd8, Loop - len(code) - 2]    # djnz r0, <x>

                code += cmacro_cs_high()

                code += cmacro_epilogue()

                buff = code2buff(code)

                ax_write512to0x200(buff)
                ax_callcode()
                buff = ax_read1024from0x200()

                f.write(buff[0x100:0x200])
    '''

    code  = cmacro_prologue()
    code += cmacro_cs_low()

    code += cmacro_spi_sendb_imm(0x0b)
    code += cmacro_spif_addr24(0x0000)
    code += cmacro_spi_sendz()

    # receive data
    code += [0x90, 0x03,0x00]           # mov dptr, #0x300
    code += [0x78, 0x00]                # mov r0, #0
    Loop = len(code)
    code += cmacro_spi_recvb_acc()
    code += [0xf0]                      # movx @dptr, a
    code += [0xa3]                      # inc dptr
    code += [0xd8, Loop - len(code) - 2]    # djnz r0, <x>

    code += cmacro_cs_high()

    code += cmacro_epilogue()

    buff = code2buff(code)
    ax_write512to0x200(buff)
    ax_callcode()
    buff = ax_read1024from0x200()
    hexdump(buff[0x100:0x200])

    #----------#----------#----------#----------#----------#

    ax_cmdexit()

