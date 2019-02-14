User Connectivity Migration

This implementation is based on Wi5 open-source code (https://github.com/Wi5/odin-wi5)

## AP Agent
#### **Step 1: Flash OpenWRT image with the needed packages**

* If it is your first time with OpenWRT, flash Chaos Calmer factory `.bin` image from `ARNAB/tierOne/AP/images`
* If you already have OpenWRT system, perform an upgrade by flashing a sysupgrade image from `ARNAB/tierOne/AP/images`
* If you want to create your own OpenWRT image, you please do the following:
- Run `./config.sh` to conifgure OpenWRT firmware with Click software router and driver pactches for TL-WR1043ND
- Edit `openwrt/target/linux/ar71xx/image/Makefile` by changing WR1043V2 flash from `8M` to `16M`.
- Then run `make -j 4` from `/openwrt`

#### **Step 2: USB support**
* **Install the following packages** 
```opkg update```
```opkg install kmod-usb-storage block-mount kmod-fs-ext4 e2fsprogs usbutils```

* **Mount the USB** 
    ```shell
    block detect > /etc/config/fstab
    mkfs.ext4 /dev/sda1
    mkdir -p /mnt/sda1
    mount /dev/sda1 /mnt/sda1
    tar -C /overlay -cvf - . | tar -C /mnt/sda1 -xf -
    ```

* **Configure File System Table**

    1. then edit /etc/config/fstab using `vi` to look like this:
        ```shell
        config 'global'
            option	anon_swap	'0'
            option	anon_mount	'0'
            option	auto_swap	'1'
            option	auto_mount	'1'
            option	delay_root	'5'
            option	check_fs	'0'

        config 'mount'
            option target /overlay
            option device /dev/sda1
            option fstype ext4
            option options rw,sync
            option enabled 1
            option enabled_fsck 0
        ```
    1. Restart the AP.
    1. Check that `/overlay` size has been extended
        ```shell
        root@OpenWrt:~# df
        Filesystem           1K-blocks      Used Available Use% Mounted on
        rootfs                 7587528     18048   7161008   0% /
        /dev/root                 4352      4352         0 100% /rom
        tmpfs                    30556       424     30132   1% /tmp
        /dev/sda1              7587528     18048   7161008   0% /overlay
        overlayfs:/overlay     7587528     18048   7161008   0% /
        tmpfs                      512         0       512   0% /dev
        ```
#### **Step 3: Install the remaining packages**

```shell 
opkg remove wpad-mini
opkg install nano tcpdump hostapd hostapd-utils openvswitch openvswitch-python openvswitch-ipsec libstdcpp unzip

```
