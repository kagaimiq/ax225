# Info about the internals

## MCU

The MCU is compatible with the Intel 8051 instruction set, althrough there is some differences:

- There's no MUL/DIV instructions, and therefore no 'B' register at SFR 0xF0
- the "AX225 Feature List" (ax225-fl-001) claims that it runs up to 48 MIPS (while running at 48 MHz),
  implying that it has almost single-cycle instructions and stuff.

## CODE/XDATA memory map

The CODE/XDATA memory spaces are tied together so that
a code fetch or a MOVC/MOVX returns the same data on the same address..

| Range         | Size                | Usage                 |
|---------------|---------------------|-----------------------|
| 0x0000-0x3FFF | 1.5k, wraps each 2k | SRAM                  |
| 0x4000-0xFFFF | 12k, wraps each 16k | [MaskROM](maskrom.md) |

### SRAM map:

Unusually, the 8051's DATA/IDATA is mapped into the main SRAM, just like it happens
with some other Appotech chips... (e.g. AX2226)

| Range       | Usage                    |
|-------------|--------------------------|
| 0x000-0x4FF | Free                     |
| 0x500-0x57F | 8051's IDATA (0x80-0xff) |
| 0x580-0x5FF | 8051's IDATA (0x00-0x7f) |

## SFRs

- sfrEF:

  *set to 0x0F by the ROM in startup, #8*

- sfrF1:

  *set to 0xFC by the ROM on startup, #4*

- sfrF2:

  *set to 0x00 by the ROM on startup, #7*

- sfrF3:

  *set to 0x00 by the ROM on startup, #3*

- sfrF4:
  -  b1 = "SPI Flash SCK" level
  -  b2 = "SPI Flash MISO" level
  -  b3 = "SPI Flash MOSI" level

  *set to 0x0F by the ROM on startup, #5*

- sfrF5:
  -  b3 = "SPI Flash CS" level
  -  b6 = ?? level .. another CS?

  *set to 0xFC by the ROM on startup, #1*

- sfrFC:
  -  b1 = "SPI Flash SCK" direction
  -  b2 = "SPI Flash MISO" direction
  -  b3 = "SPI Flash MOSI" direction
  * 0 = output, 1 = input

  *set to 0x0F by the ROM on startup, #6*

- sfrFD:
  -  b3 = "SPI Flash CS" direction
  -  b6 = ?? direction .. another CS?
  * 0 = output, 1 = input

  *set to 0xFC by the ROM on startup, #2*

- sfrFE:
  -  b1 = LED thingy, 0 == light up (driver enabled...)
  -  b4 = USB Soft-connect, 0 == connected
