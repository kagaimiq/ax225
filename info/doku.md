# The USB SPI Flash board

*(dump from my localhost dokuwiki page, so don't surprise if you'll see it poorly-written!)*

At the near end of year 2020 (28th December), i've got an MP3 music stroboscope box, which itself was built of the MP3 player part (based on JL AC1082 chip), and the Power supply part that also contained the LED controller which could react to the sound via its microphone with settable threshold or just blink.

Apart of stroboscope itself, it also contained an IR remote, and a USB flash that contained some sample music.

After the past experience from the Bluetooth MP3 Rotating light thing, i've thought that could also be some SPI Flash drive based on some unknown chip.

After opening it up, i was right BUT:
  - The chip itself was a blob instead of a package with some marking
  - The flash itself haven't any markings at all, whereas the previous had an AT26F004 (4 MBit flash)

There's our board. (with the SPI flash and LED removed, and with the USB connector replaced with cable)
`{{ usbspiflashdisk.jpg?500 }}`

After investigation, i've found that this flash must be at least 8 Mbits (1 MiB) long - since the size of the volume was near 1 MiB... And i was right, after connecting to my STM32 Serprog adapter, and then running `flashrom` on it, it showed me that the chip was **TBD**, and it is 8 Mbits long indeed.

**More on the previous thing**
I said that i had some _past experience_, and so there what it was:

At the near end of the year 2018 (December 27th) (hmm.....) i got that "Bluetooth MP3 rotating light thing", which itself was built of the Bluetooth/MP3 board (which also could do **WAV** and **FLAC**!), and it was built on the JL AC6908C chip, a power supply with the LED controller that reacts to the sound via its internal microphone, a motor to rotate the LED board, and the LEDs itself.

By the way, it seems strange to me that on this thing there were two speakers but the AC6908C was mono only, while in the stroboscope there is only one speaker but the AC1082 is stereo and there were two 8002 amplifiers, so it was designed to be with two speakers!!! but there the 8002s are connected to the same input.

And the solutions these things use it looks like it was made by the same company since:
  - Power supply does both the power supply and the LED control
  - The speakers are the same
  - The speaker holes have the same look!
  - ....?

The board on the stroboscope contained the `XL-15/32-V4` which is the board name, and the URL www.xl12345.com (yes pretty creative name, isn't it?)

If you look at their website, then you'll find out that this company makes all sorts of the lighting effect things, so i assume these were created by this company.

----

Ok, enough preface, now let's talk about the USB thing!

_i assume this is based on an AX216 chip (in the die form, as this chip can do)_\

`<wrap em>NO THIS IS THE AX225 AND IT IS ONLY AVAILABEL IN THE DIE FORM !!!</wrap>`

## SPI Flash boot
How this chip boots?

first of all, it has its SPI interface initialized with clock speed of **_at least less than 36MHz, the maximum speed STM32F103C8 can do in slave mode on SPI1_**, and with SPI Mode 3 (idle clock high, ...)
`<wrap em>actually it doesnt have any spi interface at all!!! it instead does everything through BitBANG!!!</wrap>`

Then, 16 times, using the command 0x03 (Read) from addresses 0x000000, 0x010000, and so on; it reads the data this way:

First it pick one byte, and if it is 0x55, it reads next byte, and if it is 0xaa, then it read 1022 more bytes, so the firmware begins from the 0x55 0xaa bytes and the beginning is 1024 bytes long.

But it's somehow is protected against any change !!
IDK whether the ending "HPUW" thing is the CRC or whatever but it means that would be very hard!!!
`<wrap em>ACtually it checks whether the sum of all bytes into a 8bit value is equals to 0x5A!!!</wrap>`

So the that payload then reads 24 bytes from address 0x5f9 ...

**initial payload analysis**

so the first 2 bytes is the 0x55 0xaa magic bytes, and then the 0x02 0x01 0x0d bytes could be seen, in 8051 this will jump to the address 0x010d, and indeed, this code is mapped into the address 0x0000 !
because before this address in disassembly the RET instruction can be seen!

So we can see that it:
  - disables all interrupts
  - writes 0 to the SFR 0xa9
  - then sets some bit memory
  - writes zero to the xdata 0x0439
  - writes 8 to intmem 0x21 ...
  - clears 0x48 in SDR 0xfd
  - sets 0x48 in SFR 0xf5...
  - then it calls the function that
    - checks that we are indeed the 1.09 scsi veresion (the version field starts at CODE 0x58f5)
    - and if we not then it calls some functions aat 0x6ea0 and 0x5a14... 
  - then it calls the function at 0x6ea0
  - and at 0x6d7f with R7 set to 200
  - then then function that reads 0xc0 bytes from spi flash addr 0x0440 into XDATA 0x0440 !!
  - then the function that reads 0x18 bytes from spi flash 0x5f9 .... into DATA 0x68 !!!
  - then it calls function that writes [0x04 0x45 0x04 0x4a 0x4c 0x97 0x6d 0xa1 0x6c 0x70 0x04 0x40 0x49 0xab 0x6d 0x0d 0x6d 0x0d] into XDATA starting at 0x0408
  - then after all another operation i am lazy to  describe it completely jumps to the address 0x5a14

there is also another code blob at 0x200 but fsdlflsdkjfjsdfldjsflksdfdsgad


BUT !!!
I Guess that ::
  - the SFR 0xF5 is related to the GPIO of some sort, and the bit3 controlls the CS pin!!!
  - And since there was the mask that was clearing the SFR 0xFD and setting into the 0xF5, i guess the SFR 0xFD is the GPIO Direction regisetr!!!!!
  - But What is 0xF1 ???!?! It also gets cleared with the same 0x48 thing!!    --> But in the 0x440 payload that is loaded to XDATA 0x440 ...;411414141
  - Because the AX216 has the P3.3 near the SPI pins i guess it is related !!!!
  - So the 0x6C5C might be the SPI send function!
  - And the 0x6CDD is the SPI Receive ??
  - And the DATA 0x67 is the bank number the bootloader has probed all the stuff on !!


Whatever where these CODE things are:
  - 0x57C6 => Readout the flash 'bank' to the code space (R2->FAddr23..16, R3->FAddr15..8, R4->EAddr15..8, R5->EAddr7..0, R6->SAddr15..8, R7->SAddr7..0)
  - 0x58C5 = SCSI inquiry data?
  - 0x58F5 = SCSI inquiry version field
  - 0x5A14 = whatever that is called when the SCSI Inquiry thing is not 1.09 and at the end
  - 0x5D4D = something that is called with all the parameters
  - 0x6C5C = SPI Send (takes the byte to send in R7)
  - 0x6CDD = SPI Receive (returns the received byte in R7, also it takes something in A?)
  - 0x6D7F = something that is called with arg R7=200
  - 0x6EA0 = whatever that is called when the SCSI Inquiry thing is not 1.09 and after that checker

----

**The parts of spi flash we now have at emmoe!!!**

```
 XD:0x0200~0x03DB ==> The Banked code data
 XD:0x0440~0x0500 ==> The Bank switching code [0x440->Decriptor handler bank 8, 0x445->Desc handler bank10]
  
 XD:0x0408~0x0419 ==> The Entry points ??
     0x0445 -> ====> USB SCSI Request Handler ?
     0x044A ->   Does something
     0x4C97 -> ?
     0x6DA1 -> 
     0x6C70 -> ?
     0x0440 -> ====> USB Device descriptor Handler ?
     0x49AB -> ?
     0x6D0D -> ?
     0x6D0D -> ?
```
