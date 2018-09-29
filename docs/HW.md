# H/W recipe
raspberrypi Zero W with stretch
```
$ cat /proc/cpuinfo
processor	: 0
model name	: ARMv6-compatible processor rev 7 (v6l)
BogoMIPS	: 697.95
Features	: half thumb fastmult vfp edsp java tls
CPU implementer	: 0x41
CPU architecture: 7
CPU variant	: 0x0
CPU part	: 0xb76
CPU revision	: 7

Hardware	: BCM2835
Revision	: 9000c1
$ uname -a
Linux raspberrypi_zw 4.14.62+ #1134 Tue Aug 14 16:58:07 BST 2018 armv6l GNU/Linux
$ lsb_release -a
No LSB modules are available.
Distributor ID:	Raspbian
Description:	Raspbian GNU/Linux 9.4 (stretch)
Release:	9.4
Codename:	stretch
```

#### circuit diagram
Maybe, easy to configure, after H/W settings.
[![SunLight by setminami 951bfa33c4296aea - Upverter](https://upverter.com/setminami/951bfa33c4296aea/SunLight/embed_img/15382457110000/)](https://upverter.com/setminami/951bfa33c4296aea/SunLight/#/)

- refs
  - [GL538](http://akizukidenshi.com/download/ds/sharp/gl537_gl538.pdf)
  - [hx1838](http://www.datasheetcafe.com/HX1838-pdf-20841/)
  - [oled ssd1331](https://www.bluetin.io/displays/oled-display-raspberry-pi-ssd1331/)

#### /boot/config.txt (see also. environments/boot/config.txt l.51)
```
dtoverlay=lirc-rpi:gpio_out_pin=27,gpio_in_pin=22,gpio_in_pull=up,invert=on
```
