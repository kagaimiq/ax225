# Firmware layout

- 00000-003FF = Bootloader
- 00440-004FF = Common code (loaded to XDATA 0x440-0x4ff)
- 00518-0053B = SCSI inquiry response: "Generic CD-ROM"
- ...
- 005B8-005B7 = SCSI read capacity response
- 005B8-005C3 = SCSI format capacity response
- 005C4-005E7 = SCSI inquiry response: "Generic Mass Storage"
- ...
- 005F9-00610 = ?? (loaded to DATA 0x68-0x7f)
- 00611-00622 = USB device descriptor
  * idVendor = 0x1908
  * idProduct = 0x9999
- 00623-00634 = USB string descriptor #1
  * forgotwhatitwas
- 00635-00656 = USB string descriptor #2
  * forgotwhatitwas
- 00657-00678 = USB string descriptor #3
  * "0000000000000251"
- ...
- 00800-009FF = Code bank 0x08
- 00A00-00BFF = Code bank 0x0A
- 00C00-00DFF = Code bank 0x0C
- 00E00-00FFF = Code bank 0x0E
- 01000-011FF = Code bank 0x10
- 01200-013FF = Code bank 0x12
- 01400-015FF = Code bank 0x14
- 01600-017FF = Code bank 0x16
- 01800-019FF = Code bank 0x18
- 01A00-01BFF = Code bank 0x1A
- 01C00-01DFF = Code bank 0x1C
- 01E00-01FFF = Code bank 0x1E
- 02000-021FF = Code bank 0x20
- 02200-023FF = Code bank 0x22
- 02400-025FF = Code bank 0x24
- 02600-027FF = Code bank 0x26
- 02800-029FF = Code bank 0x28
- 02A00-02BFF = Code bank 0x2A
- 0C000-0FFFF = Block allocation table
