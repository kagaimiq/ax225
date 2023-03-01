# Info about the internals

## MCU

The MCU is compatible with the Intel 8051 instruction set, althrough there is some differences:

- There's no MUL/DIV instructions, and therefore no 'B' register at SFR 0xF0
- the "AX225 Feature List" (ax225-fl-001) claims that it runs up to 48 MIPS (while running at 48 MHz),
  implying that it has (almost) single-cycle instructions.
- The CODE and XDATA memory spaces are tied together, so that a code fetch or the MOVC instruction returns the same data that is accessed with the MOVX instruction.
- The DATA/IDATA is shared with the SRAM, instead of having a dedicated memory area.
  This is consistent with other Appotech/Buildwin chips such as AX2226, CW6631, etc.

## CODE/XDATA memory map

| Range         | Size                | Usage                 |
|---------------|---------------------|-----------------------|
| 0x0000-0x3FFF | 1.5k, wraps each 2k | SRAM                  |
| 0x4000-0xFFFF | 12k, wraps each 16k | [MaskROM](maskrom.md) |

### SRAM map:

| Range       | Usage                    |
|-------------|--------------------------|
| 0x000-0x4FF | Free                     |
| 0x500-0x57F | 8051's IDATA (0x80-0xff) |
| 0x580-0x5FF | 8051's IDATA (0x00-0x7f) |

## SFRs

- 0xEF:

  *set to 0x0F by the ROM in startup, #8*

- 0xF1:

  *set to 0xFC by the ROM on startup, #4*

- 0xF2:

  *set to 0x00 by the ROM on startup, #7*

- 0xF3:

  *set to 0x00 by the ROM on startup, #3*

- 0xF4:
  -  b1 = "SPI Flash SCK" level
  -  b2 = "SPI Flash MISO" level
  -  b3 = "SPI Flash MOSI" level

  *set to 0x0F by the ROM on startup, #5*

- 0xF5:
  -  b3 = "SPI Flash CS" level
  -  b6 = ?? level .. another CS?

  *set to 0xFC by the ROM on startup, #1*

- 0xFC:
  -  b1 = "SPI Flash SCK" direction
  -  b2 = "SPI Flash MISO" direction
  -  b3 = "SPI Flash MOSI" direction
  * 0 = output, 1 = input

  *set to 0x0F by the ROM on startup, #6*

- 0xFD:
  -  b3 = "SPI Flash CS" direction
  -  b6 = ?? direction .. another CS?
  * 0 = output, 1 = input

  *set to 0xFC by the ROM on startup, #2*

- 0xFE:
  -  b1 = LED thingy, 0 == light up (driver enabled...)
  -  b4 = USB Soft-connect, 0 == connected
