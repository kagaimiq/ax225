# The MaskROM

The MaskROM, which is 12 KiB long, contains all the logic required for the card reader to operate.

- [Dump](MaskROM.bin)

## ROM memory usage

### IDATA

- 23, bit 0 = Use external handlers

### SRAM

- 408-409 = Main loop handler (ROM: 0x6D2F)

## ROM functions

- 0x6A4F: USB indirect reg write
  - R5 <= data
  - R7 <= address

- 0x6C5A: SPI send zero

- 0x6C5C: SPI send byte
  - R7 <= data

- 0x6CDD: SPI receive byte
  - R7 => data

- 0x6D2F: Main loop handler

- 0x6D7F: Delay in milliseconds
  - R7 <= delay time (ms)

- 0x6DC4: USB indirect reg read
  - R7 <= address
  - R7 => data

## Extra SCSI commands

### Enter (unlock) extra commands

This makes possible to access the commands 01/02/03/04, however then you can't access
the commands 00/05/FE (i.e. those which have the `59 68 48 70` magic bytes)

- Command: `FA 00 59 68 48 70`

### Exit (lock) extra commands

This makes the commands 01/02/03/04 inacessible, bringing commands 00/05/FE back.

- Command: `FA 01 -- -- -- --`

### Call the code

Jumps to the code in the specified address.

- Command: `FA 02 -- -- AA:aa`
- AA:aa = Address to jump to

### Write 512 bytes into XDATA 0x200

Writes 512 bytes into the XDATA location 0x200, which is generally reserved for the user code.

- Command: `FA 03 -- -- -- --`
- Data in: 512 bytes of data to be written

### Read 1024 bytes from XDATA 0x200

Reads 1024 bytes from the XDATA location 0x200, which retreives the 512 byte block written with
a previous command, plus the range where the ROM's data and the 8051's DATA resides in.

- Command: `FA 04 -- -- -- --`
- Data out: 1024 bytes of that that was read out

### Read 4 bytes from XDATA

Reads 4 bytes from arbitraty XDATA location.

So i could've used it to dump the MaskROM!
But i hacked up the firmware on the SPI flash so that it reads the code/xdata instead of the flash,
because i didn't knew that at the first place.

- Command: `FA 05 59 68 48 70 -- AA:aa`
- Data out: 4 bytes of read data
- AA:aa = Address

### Reset or something like that

This enters somewhere, the opcode looks like it's related to a "reset" of some kind.

- Command: `FA FE 59 68 48 70`
