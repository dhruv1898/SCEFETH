# Installation instructions

## For Enddevice
Upload the script in the Enddevice folder on the Pycom devices.


## Setting up Habitat and Gateway

Each gateway and habitat are Raspberry Pi 2 which runs on [OpenWrt](https://openwrt.org/), a Linux operating system which targets embedded devices. It enables the user to customize the device using packages for different applications. The latest firmware of OpenWrt can be installed on the RPi 2 devices from [here](https://openwrt.org/toh/raspberry\_pi\_foundation/raspberry\_pi). After successful installation of the OpenWrt each RPi 2 devices are needed to be enabled to download necessary packages. Therefore, ethernet access is setup as follows:-
- Open the network files using: 
  ```
  vim /etc/config/network
  ```
- Edit the network file by changing the IP address in the 'lan' interface according to the network to which it is connected. The DNS and gateway address should be added in the 'lan' interface as shown and then reboot the device:
  ```
  config interface 'lan'
    option device 'br-lan'
    option proto 'static'
    option dns '<dns address>'
    option gateway '<gateway address>'
    option ipaddr '<ip address>'
    option netmask '255.255.255.0'
    option ip6assign '60'
  ```
- Now, install the necessary packages for the usb adapters from [here](https://openwrt.org/docs/guide-user/storage/usb-installing)
- Install the package to enable the Edimax ew-7811un adapter using the following command and then reboot the device:
  ```
  opkg install kmod-rtl8192cu
  ```

### OLSR installation
Now, install the following packages to use OLSR on openwrt:
```
opkg update

opkg install luci-app-olsr luci-app-olsr-services luci-app-olsr-viz luci-lib-json
opkg install olsrd olsrd-mod-arprefresh olsrd-mod-bmf olsrd-mod-dot-draw olsrd-mod-dyn-gw olsrd-mod-dyn-gw-plain olsrd-mod-httpinfo olsrd-mod-mdns 
opkg install olsrd-mod-nameservice olsrd-mod-p2pd olsrd-mod-pgraph olsrd-mod-secure olsrd-mod-txtinfo olsrd-mod-watchdog olsrd-mod-quagga
opkg install wireless-tools
```
Installation instructions can also be followed from [here](http://lechacal.com/wiki/index.php/Mesh_networking_on_OpenWRT_15.05_with_OLSR). After installing all the necessary packages for OLSR, now setup Wired LAN. Go to ```Network|Interfaces```, uncheck ```create a bridge over specified interface(s)``` in the LAN interfaces and ensure ```Ethernet Adapter: "eth0" (lan)``` is ticked on. Now set up the Wi-Fi mesh interface on ```Network|Wifi``` and edit the Wi-Fi interface. Find ```Interface Configuration``` and add the following ESSID, mode and network:
```
ESSID: OLSR
Mode: 802.11s
Network: mesh
```
If the Wi-Fi interface is disabled, then enable it. Now go to ```Network|Interfaces```, edit the interface MESH and set up the following parameters:
```
Protocol: Static address
IPv4 address: <custom ip address>
IPv4 netmask: 255.255.255.0
Use custom DNS servers: 8.8.8.8
```
Go to Firewall Settings tab and tick on ```unspecified -or- create:``` and enter 'mesh'. Now, go to ```Network|Firewall```  and remove ```wan(empty)$=>$REJECT```  entry in the ```Zones``` section. For entry ```mesh```  change Forward as Accept. 
After setting up Firewall, we setup OLSR. Go to ```Services|OLSR IPv4```  and select the ```Network```  parameter to ```mesh```  in the \textit{Interfaces} section. Now select the \textit{Plugins} tab and check on ```olsr\_jsoninfo.so.0.0```.

## Expanding space for OpenWrt
OpenWrt filesystem by default creates a partition of 100 megabytes on an 8GB SD card, which is insufficient to install the necessary packages and store the data during communication in the network. Therefore, it is recommended to use the remaining storage space on the SD card by creating an extra partition. The instructions to do so are as follows
1. Install packages:
```
opkg update && opkg install block-mount kmod-fs-ext4 kmod-usb-storage kmod-usb-ohci kmod-usb-uhci e2fsprogs fdisk
```
2. Create new partition, /dev/mmcblk0p3, and reboot
```
root@Rpi3:~# fdisk /dev/mmcblk0

Welcome to fdisk (util-linux 2.34).
Changes will remain in memory only, until you decide to write them.
Be careful before using the write command.


Command (m for help): p
Disk /dev/mmcblk0: 14.43 GiB, 15485370368 bytes, 30244864 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x5452574f

Device         Boot Start    End Sectors  Size Id Type
/dev/mmcblk0p1 *     8192  49151   40960   20M  c W95 FAT32 (LBA)
/dev/mmcblk0p2      57344 581631  524288  256M 83 Linux

Command (m for help): n 
Partition type
   p   primary (2 primary, 0 extended, 2 free)
   e   extended (container for logical partitions)
Select (default p): p
Partition number (3,4, default 3): 
First sector (2048-30244863, default 2048): 5811632
Last sector, +/-sectors or +/-size{K,M,G,T,P} (5811632-30244863, default 30244863): 

Created a new partition 3 of type 'Linux' and of size 11.7 GiB.

Command (m for help): p
Disk /dev/mmcblk0: 14.43 GiB, 15485370368 bytes, 30244864 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0x5452574f

Device         Boot   Start      End  Sectors  Size Id Type
/dev/mmcblk0p1 *       8192    49151    40960   20M  c W95 FAT32 (LBA)
/dev/mmcblk0p2        57344   581631   524288  256M 83 Linux
/dev/mmcblk0p3      5811632 30244863 24433232 11.7G 83 Linux

Command (m for help): w
The partition table has been altered.
Syncing disks.

root@Rpi3:~# reboot
```
3. Format new partition
```
root@Rpi3:~# mkfs.ext4 /dev/mmcblk0p3 
mke2fs 1.44.5 (15-Dec-2018)
Discarding device blocks: done                            
Creating filesystem with 3054154 4k blocks and 764032 inodes
Filesystem UUID: 8f3f385e-2ee5-4618-b2e2-e5be282acef9
Superblock backups stored on blocks: 
	32768, 98304, 163840, 229376, 294912, 819200, 884736, 1605632, 2654208

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (16384 blocks): done
Writing superblocks and filesystem accounting information: done
```
4. Configuring rootfs_data, extroot, transferring the data and reboot
```
root@Rpi3:~# DEVICE="/dev/mmcblk0p3"
root@Rpi3:~# eval $(block info "${DEVICE}" | grep -o -e "UUID=\S*")
root@Rpi3:~# uci -q delete fstab.overlay
root@Rpi3:~# uci set fstab.overlay="mount"
root@Rpi3:~# uci set fstab.overlay.uuid="${UUID}"
root@Rpi3:~# uci set fstab.overlay.target="/overlay"
root@Rpi3:~# uci commit fstab
root@Rpi3:~# 
root@Rpi3:~# mount /dev/mmcblk0p3 /mnt
root@Rpi3:~# cp -a -f /overlay/. /mnt
root@Rpi3:~# umount /mnt
root@Rpi3:~# reboot
```
5. Preserving software package lists across boots
```
root@Rpi3:~# sed -i -r -e "s/^(lists_dir\sext\s).*/\1\/usr\/lib\/opkg\/lists/" /etc/opkg.conf
root@Rpi3:~# opkg update
```
Or, modify /etc/opkg.conf in Web interface, and the steps to expand the partition can also be found [here](https://forum.openwrt.org/t/expanding-openwrt-squashfs-image-sdcard/60606/6).

### Installing python packages for SPI communication of RPi2 with Dragino Shield
Use the following commands to install the necessary python packages:
```
opkg install python3
opkg install python3-pip
opkg install python3-dev
pip install virtualenv
opkg install gcc
opkg install python3-base-src
pip3 install -U pip wheel setuptools
```
Now, edit ```/usr/lib/python*/_sysconfigdata.py``` and remove all lines matching:
```
-ffile-prefix-map=/builder/shared-workdir/build/sdk/build_dir/target-aarch64_cortex-a53_musl/Python-*=Python-*
```
replace * with the python version on your system). To check if the operation was successful enter the following command:
```
pip3 install -U pip wheel setuptools
```
Now, enable the spi bus by adding the following line at the end of ```/boot/config.txt```:
```
dtparam=spi=on
```
After enabling the spi bus, use the following commands to install the necessary packages to use GPIO pins on the RPi2: 
```
python3 -m pip install rpi.gpio
python3 -m pip install spidev
opkg install spidev-test
opkg install kmod-spi-bcm2835
opkg install kmod-spi-dev
```
### Pin connection of Dragino\_v1.4 with RPi 2
Table below shows the pin connection of the Dragino\_v1.4 shield with the raspberry pi 2.
|**Dragino\_v1.4** 	| **Raspberry Pi 2** 	| **BCM Pin mapping**	|
|-----------------------|-----------------------|-----------------------|
|Reset		   	|11		     	|17			|
|DIO0 (interrupt pin)	|22		     	|25			|
|MOSI - 37		|19		     	|10			|
|MISO - 33		|21			|9			|
|SCLK - 34		|23			|11			|
|CS - 10		|24			|8			|
|3V3 - power		|1			|-			|
|GND			|6			|-			|
#### Setup of the devices
The image below shows the collage of some of the end-devices, gateways and the habitat used in the experiment.
![Alt text](https://github.com/dhruv1898/SCEFETH/blob/main/Setup%20image/Setup_Collage.png)
### Source Code installation and time synchronization of the network
The source code to be installed on the Habitat, Gateways and the End-devices from the directories: [Habitat](https://github.com/dhruv1898/SCEFETH/tree/main/Habitat), [Gateway](https://github.com/dhruv1898/SCEFETH/tree/main/Gateway) and the [End-device](https://github.com/dhruv1898/SCEFETH/tree/main/End-device). The gateway clocks are synchronized with the Habitat using ntplib python library and can be installed using the following command:
```
pip install ntplib
```
After successful installation of the devices now to perform the E2H communication run the following commands:
- On the habitat
```
python Habitat_E2H.py
```
- On the gateway
```
python G_E2H.py
```
For the H2E communication run the following commands:
- On the habitat
```
python Habitat_H2E.py
```
- On the gateway for time-synchronization 
```
python G_H2E_Time_sync.py
```
On the gateway for H2E comunication
```
python G_H2E.py
```
