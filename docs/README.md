# IrControl
construct for raspi ZeroW with lircd

## Motivation
I wanna simulate sunlight (e.g., SunRise/Set, MoonLight, etc...) with RGB ledlight by time in water plants tank as a sublight.<br>

like below.<br>
<img src="./img/violet.png" alt="sunrize" width="250">
<img src="./img/orange.png" alt="sunset" width="250">
<img src="./img/blue.png" alt="moon light" width="250">

## lircd setup memo
On the premise, check one by one, from here to bottom in order.
If there are a point which you can shortcut, I've put [shortcut] link.

### H/W recipe
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
![](./img/irc_pi_schem.png)

#### /boot/config.txt (see also. environments/boot/config.txt l.51)
```
dtoverlay=lirc-rpi:gpio_out_pin=25,gpio_in_pin=24,gpio_in_pull=up,invert=on
```

#### <a name="light"></a>[ledlight](https://www.amazon.co.jp/gp/product/B079QKB128/ref=oh_aui_detailpage_o05_s00?ie=UTF8&psc=1)
I use a ready-made ledlight with RGB Infra-red remote controller by 24Key, because a number of ledlights can be controlled at the same time very simply.<br><br>
The docs are written for use like https://www.led-paradise.com/product/1301.<br><br>
Why? Many cheap RGB controller (maybe chinese) have same IR signal, and they are cheaper than wifi or BT's similar products.

#### appearance
<img src="./img/appearance.png" alt="for examples" width="500">

### lircd setup procedure
#### install
```
$ sudo apt-get install lirc
...
$ lircd -v
lircd 0.9.4c
```

#### configure and check
run below
```
# cd [Top of this repo]
cp /etc/lirc/lircd.conf.d/lirc_options.conf ~/.
sudo cp environments/etc/lirc/lirc_options.conf /etc/lirc/lircd.conf.d/.
sudo reboot
```

and check below, when rebooted.
```
$ sudo /etc/init.d/lircd start
$ ls -la /dev/lirc0
crw-rw---- 1 root video 243, 0 Sep  9 17:29 /dev/lirc0

# check a ir receiver implementation
# direct some IR remote controller to IR reciever(e.g., hx1838)
$ mode2 -d /dev/lirc0 <enter>
Using driver default on device /dev/lirc0
Trying device: /dev/lirc0
Using device: /dev/lirc0
# push some button
space 16777215
pulse 4662
space 1241
pulse 204
space 529
....

# check irLED implementation
$ irsend LIST "" ""

devinput
```

Hyp. `irsend LIST "" ""` outputs above, It might be wrong. Because when I ran like `sudo sh -c 'mv /etc/lirc/lircd.conf.d/devinput.lircd.conf ~/. && lirc-make-devinput'` to remake devinput settings and re- reboot, the lircd behavior has stabilized on my env.


```
# If you ran lirc-make-devinput, you may see like below.
$ irsend LIST "" ""

devinput-32
devinput-64

$ irsend list devinput-64 ""

000000000000000b KEY_0
0000000000000056 KEY_102ND
00000000000001b9 KEY_10CHANNELSDOWN
...

# the send_once devinput-?? result were failed. Maybe this behavior is not wrong.
# But after recorded signal sequence(with irrecord), [irsend send_* recorded_remote command] not fail, on my env at least.
$ irsend send_once devinput-32 KEY_0

transmission failed
Error running command: Input/output error
```


####  <a name="sc-1-ret"></a>record your infra-red controller signals
You will use the same or similar LED light like [above one](#light), you can [shortcut](#sc-1).

```
# > TL;DR
# 1. press "enter key" twice
# 2. wait about 10seconds
# 3. enter your IR remote controller's literal identifier
#   - the repo presuppose the name as "ledlight"
# 4. push remote controller keys randomly, until irrecord output next prompt
# 5.  push again, like #4, maybe, the session will output dots some longer but you must never give up until appear next prompt
# 6. Loop Recording, with push a remote controller key by loop.
# 7. end

$ irrecord -d /dev/lirc0
Using driver devinput on device /dev/lirc0

irrecord -  application for recording IR-codes for usage with lirc
Copyright (C) 1998,1999 Christoph Bartelmus(lirc@bartelmus.de)
....
Press RETURN to continue.

Usually you should not create a new config file for devinput

Press RETURN to continue.
# 1

# CONFIRM NO Infra-red signal around ir receiver, you must wait ...
Checking for ambient light  creating too much disturbances.
Please don't press any buttons, just wait a few seconds...

No significant noise (received 0 bytes)
#2

Enter name of remote (only ascii, no spaces) : ledlight


Using ledlight.lircd.conf as output filename
# 3

Now start pressing buttons on your remote control.

# IMPORTANT!
It is very important that you press many different buttons randomly
and hold them down for approximately one second. Each button should
generate at least one dot but never more than ten dots of output.
Don't stop pressing buttons until two lines of dots (2x80) have
been generated.

Press RETURN now to start recording.
# 4. not two lines on your terminal, but 160(2x80 characters) exactly.
...............................................................................
...............................................................................

Got gap (108559 us)}

Please keep on pressing buttons like described above.
# 5. push like above again, the session will be something longer than
...............................................................................
...............................................................................
...............................................................................
...............................................................................
...............................................................................

Please enter the name for the next button (press <ENTER> to finish recording)
on
# 6 for example keyname "on"

Now hold down button "on".
.................................
# 6.1 push remote controller key "ON"

Please enter the name for the next button (press <ENTER> to finish recording)
off

Now hold down button "off".
.................................
# 6.2 push remote controller key "OFF"
# loop the session #6 until all of keys that you wanna control were pushed

Please enter the name for the next button (press <ENTER> to finish recording)
# 7. end of "ledlight" recording.

Successfully written config file ledlight.lircd.conf
```

#### put RGB LED Controller config file
Check that irrecord had generated "ledlight.lircd.conf" on current location.

```
sudo cp ./ledlight.lircd.conf /etc/lirc/lircd.conf.f/.
```

<a name="sc-1"></a>
or copy settings included in the repo for RGB ledlight.

```
sudo cp ./environments/etc/lirc/lircd.conf.d/ledlight.lircd.conf /etc/lirc/lircd.conf.d/.
```

and `sudo reboot` again.

### Test
Let's try to send signal.

```
# check registered remote signals
$ irsend LIST "" ""

devinput-32
ledlight
devinput-64
# check ledlight commands
$ irsend LIST ledlight ""

0000000000f7c03f on
0000000000f740bf off
0000000000f700ff up
0000000000f7807f down
0000000000f720df r0
0000000000f710ef r1
0000000000f730cf r2
0000000000f7609f b0
0000000000f750af b1
0000000000f7708f b2
0000000000f7e01f w
# above command names (e.g., on, off, ...) are assumed to use script/python3/RGB_control.py


# send off, led will turn off
$ irsend send_once ledlight off

# send on, led will turn on
$ irsend send_once ledlight on

# send r0, led will turn red
$ irsend send_once ledlight r0

```

TODO: write "how to debug"
