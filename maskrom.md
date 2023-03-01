# The MaskROM

The MaskROM, which is 12 KiB long, contains all the logic required for the card reader to operate.

- [Dump](MaskROM.bin)

## ROM memory usage

### IDATA

- 0x22, bit 7 = 0x57C6 checks for the '0x55 0xaa' sign first, then reads out data
- 0x23, bit 0 = Use handlers in SRAM 0x408-0x419
- 0x24, bit 2 = USB speed (0 = fullspeed, 1 = highspeed)
- 0x48-0x4F = setup packet storage
- 0x67 = SPI flash bank (64k) from which it has booted from.

### SRAM

- 0x408-0x409 = Main loop handler (overrides ROM: 0x6D2F)
- 0x40A-0x40B = ... (overrides ROM: 0x4FBD)
- 0x40C-0x40D = IRQ0 handler (overrides ROM: 0x4C97)
- 0x40E-0x40F = .. overrides something in ROM: 0x6B83
- 0x410-0x411 = .. overrides something in ROM: 0x6C86
- 0x412-0x413 = USB setup packet handler (overrides ROM: 0x5069)
- 0x414-0x415 = USB GET_DESCRIPTOR handler (overrides ROM: 0x50AF)
- 0x416-0x417 = card detect thing hook or like
- 0x418-0x419 = received SCSI command hook
- 0x41A-0x41B = .
- 0x41C-0x41D = USB device descriptor (ROM: 0x534A)
- 0x41E-0x41F = USB config descriptor (ROM: 0x537C)
- 0x420-0x421 = USB string descriptor idx1/mfr (ROM: 0x5380)
- 0x422-0x423 = USB string descriptor idx2/product (ROM: 0x5390)
- 0x424-0x425 = USB string descriptor idx3/serial (ROM: 0x53AC)

## ROM symbols

### Functions

- 0x57C6: SPI flash read
  * R2 <= flash addr 16..23
  * R3 <= flash addr 8..15
  * R4 <= dest end 8..15
  * R5 <= dest end 0..7
  * R6 <= dest start 8..15
  * R7 <= dest start 0..7

- 0x59C2: USB EP1.OUT recv 512 bytes on fullspeed (called by 0x6F69)

- 0x5A14: Main loop entrance

- 0x5A64: USB EP1.IN send 512 bytes on fullspeed (called by 0x6EBC)

- 0x5D4D: Store 4 bytes in XDATA
  * DPTR <= addr
  * R4 <= byte0
  * R5 <= byte1
  * R6 <= byte2
  * R7 <= byte3

- 0x6A4F: USB indirect reg write
  * R5 <= data
  * R7 <= address

- 0x6A95: copy XDATA into XDATA
  * R3 <= length
  * R4 <= source addr 8..15
  * R5 <= source addr 0..7
  * R6 <= dest addr 8..15
  * R7 <= dest addr 0..7

- 0x6B6A: check the checksum (in SPI boot)
  * R4 <= addr end 8..15
  * R5 <= addr end 0..7
  * R6 <= addr start 8..15
  * R7 <= addr start 0..7
  * CY => checksum matches 0x5A

- 0x6C5A: SPI send zero

- 0x6C5C: SPI send byte
  * R7 <= data

- 0x6CDD: SPI receive byte
  * R7 => data

- 0x6D2F: Main loop handler

- 0x6D6A: USB EP1.IN send
  * R6 <= size 8..15
  * R7 <= size 0..7

- 0x6D7F: Delay in milliseconds
  * R7 <= delay time (ms)

- 0x6DB3: copy XDATA into IDATA
  * R3 <= length
  * R4 <= source addr 8..15
  * R5 <= source addr 0..7
  * R7 <= dest addr

- 0x6DC4: USB indirect reg read
  * R7 <= address
  * R7 => data

- 0x6EA0: Stuff initializations

- 0x6EBC: USB EP1.IN send 512 bytes

- 0x6F0B: USB EP1.IN wait for tx done

- 0x6F18: USB EP1.OUT wait for rx done

- 0x6F69: USB EP1.OUT receive 512 bytes

- 0x6F8A: USB EP1.OUT reset rx status

### etc

- 0x534A: USB device descriptor => VID 0x1908, PID 0x0225
- 0x535C: USB configuration descriptor
- 0x537C: USB string descriptor, index 0 => lang 0x409
- 0x5380: USB string descriptor, index 1 => "Generic"
- 0x5390: USB string descriptor, index 2 => "USB2.0 Device"
- 0x53AC: USB string descriptor, index 3 => "20120218120009"
- 0x58D6: SCSI inquiry string => "Generic" "Mass-Storage" "1.09"
- 0x58FA: SCSI inquiry string => "Generic" "Flash-Disk" "1.09"

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
  * AA:aa = Address to jump to

### Write 512 bytes into SRAM 0x200

Writes 512 bytes into the SRAM location 0x200, which is generally reserved for the user code.

- Command: `FA 03 -- -- -- --`
- Data in: 512 bytes of data to be written

### Read 1024 bytes from SRAM 0x200

Reads 1024 bytes from the SRAM location 0x200, which retreives the 512 byte block written with
a previous command, plus the range where the ROM's variables and the 8051's DATA resides in.

- Command: `FA 04 -- -- -- --`
- Data out: 1024 bytes of data that was read out

### Read 4 bytes from XDATA

Reads 4 bytes from arbitraty XDATA location.

- Command: `FA 05 59 68 48 70 -- AA:aa`
  * AA:aa = Address
- Data out: 4 bytes of read data

### Reset or something like that

Enters something..

- Command: `FA FE 59 68 48 70`
