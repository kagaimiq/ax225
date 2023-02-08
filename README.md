# Appotech AX225

The SD/MMC/MemoryStick card reader chip blop, the Appotech AX225.

Might be in some/many cheapo USB SD card readers, and stuff like that.

## General specs

- Intel 8051-compatible "RISC" MCU
  - 48 MHz clock speed
  - Weird mapping of the 8051's DATA into the SRAM (consistent with other chips like AX2226, etc)
  - No MUL/DIV instructions.
  - XDATA and CODE is tied together, if not access the same thing..
  - Claims to have 7 interrupt vectors, but in ROM only ONE is used.
- 12 KiB MaskROM
  - Basically contains the whole logic of the card reader
  - Can boot up from the SPI flash
- 1.5 KiB SRAM
  - Shared with 8051's DATA (for some reason, the 'IDATA' comes first, then goes 'DATA')
  - Shared with other stuff
- Package
  - **Die** (=== The Epoxy Blob)
  - Nothing else!!

## Contents

- [General info](infos.txt)
- [SFR map](sfr.txt)
- [SPIdrive](spidrive/index.md) - a flash drive that came with some mp3 strobo light thing

```
[89535.499960] dwmac-sun8i 1c30000.ethernet eth0: Link is Up - 100Mbps/Full - flow control off
[91585.475920] usb 5-1: new high-speed USB device number 5 using ehci-platform
[91585.676797] usb 5-1: New USB device found, idVendor=1908, idProduct=0225, bcdDevice= 1.09
[91585.685002] usb 5-1: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[91585.692180] usb 5-1: Product: USB2.0 Device
[91585.696373] usb 5-1: Manufacturer: Generic
[91585.700468] usb 5-1: SerialNumber: 20120218120009
[91585.706506] usb-storage 5-1:1.0: USB Mass Storage device detected
[91585.714443] scsi host0: usb-storage 5-1:1.0
[91586.746846] scsi 0:0:0:0: Direct-Access     Generic  Mass-Storage     1.09 PQ: 0 ANSI: 2
[91586.755488] sd 0:0:0:0: Attached scsi generic sg0 type 0
[91587.020590] sd 0:0:0:0: [sda] Media removed, stopped polling
[91587.027090] sd 0:0:0:0: [sda] Attached SCSI removable disk
```
