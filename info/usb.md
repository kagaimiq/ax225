# USB

It's basically a standard MUSB device controller with some DMA botched on top of it. (hello jieli & jianrong)

## Indirect reg dump

```
     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F
00: 1D 70 02 00 02 00 01 00 00 00 08 05 6F 01 01 00
10: 00 04 00 20 00 04 00 00 00 00 00 00 00 00 00 00
20: 02 01 00 00 xx xx xx xx 00 00 00 00 00 00 00 00
30: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
40: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
50: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
60: 00 00 00 00 00 00 00 00 00 00 00 00 2C 09 00 00
70: 00 00 00 00 00 00 00 00 11 0A 00 00 00 00 00 00 
```

- xx = reading this breaks the USB transfer (as this is the EP1 FIFO)

## Indirect reg access

```c
void musb_write(byte addr, byte val) {
	sfrE2 = addr;
	sfrE3 = val;
	sfrE8 = 0x11;
	while (!(sfrE8 & 0x80));
}

byte musb_read(byte addr) {
	sfrE2 = addr;
	sfrE8 = 0x31;
	while (!(sfrE8 & 0x80));
	return sfrE3;
}
```
