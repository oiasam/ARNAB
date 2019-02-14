## User Connectivity Migration

This implementation is based on Wi5 open-source code (https://github.com/Wi5/odin-wi5)

### AP Agent
#### **Step 1: Flash OpenWRT image with the needed packages**

* If it is your first time with OpenWRT, flash Chaos Calmer factory `.bin` image from `ARNAB/tierOne/AP/images`
* If you already have OpenWRT system, perform an upgrade by flashing a sysupgrade image from `ARNAB/tierOne/AP/images`
* If you want to create your own OpenWRT image, you please do the following:
    * Run `./config.sh` to conifgure OpenWRT firmware with Click software router and driver pactches for TL-WR1043ND
    * Edit `openwrt/target/linux/ar71xx/image/Makefile` by changing WR1043V2 flash from `8M` to `16M`.
    * Then run `make -j 4` from `/openwrt`

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
### Agent Configuration
* Configure the network interfaces of the AP. Edit `/etc/config/network` to add the following:
    ```shell
    config interface 'loopback'
        option ifname 'lo'
        option proto 'static'
        option ipaddr '127.0.0.1'
        option netmask '255.0.0.0'

    config interface 'lan1'
        option ifname 'eth1.1'
        option force_link '1'
        option proto 'static'
        option netmask '255.255.255.0'
        option ip6assign '60'
        option ipaddr '192.168.1.14'

    config interface 'lan2'
        option ifname 'eth1.2'
        option force_link '1'
        option proto 'static'
        option netmask '255.255.255.0'
        option ip6assign '60'
        option ipaddr '192.168.2.14'

    config interface 'wan'
        option ifname 'eth0'
        option proto 'static'
        option netmask '255.255.255.0'
        option ipaddr '192.168.30.14'
        option gateway '192.168.30.254'
        option broadcast '192.168.30.255'
        option dns '8.8.8.8'

    config switch
        option name 'switch0'
        option reset '1'
        option enable_vlan '1'
        option mirror_source_port '0'
        option mirror_monitor_port '0'

    config switch_vlan 'eth1_1'
        option device 'switch0'
        option vlan '1'
        option ports '0t 4'
        option vid '1'

    config switch_vlan 'eth1_2'
        option device 'switch0'
        option vlan '2'
        option ports '0t 3'
        option vid '2'

    config switch_vlan 'eth1_3'
        option device 'switch0'
        option vlan '3'
        option ports '0t 2'
        option vid '3'

    config switch_vlan 'eth1_4'
        option device 'switch0'
        option vlan '4'
        option ports '0t 1'
        option vid '4'

    config switch_vlan
        option device 'switch0'
        option vlan '5'
        option ports '5 6'
        option vid '5'
    ```
    
* Configure the wifi interfaces of the AP. 
    * Plug in the auxiliary WiFi interface 
    * execute `wifi detect > /etc/config/wireless`
    * Edit `/etc/config/wireless` and make sure it looks like this:
    * Note that the interfaces names has to be `radio0` and `radio1`
    ```shell
    config wifi-device  radio0
            option type     mac80211
            option channel  1
            option hwmode   11g
            option path     'platform/qca955x_wmac'
            option htmode   HT20
            option disabled 0

    config wifi-iface
            option device   radio0
            option network  lan
            option mode     ap
            option ssid     AP14
            option encryption none

    config wifi-device  radio1
            option type     mac80211
            option channel  11
            option hwmode   11g
            option path     'platform/ehci-platform.0/usb1/1-1/1-1.4/1-1.4:1.0'
            option htmode   HT20
            option disabled 0

    config wifi-iface
            option device   radio1
            option network  lan
            option mode     ap
            option ssid     AP14-Aux
            option encryption none
    ```
* Configure the firewall of the AP. Edit `/etc/config/firewall` to add the following:
    ```shell
    config defaults
        option syn_flood '1'
        option input 'ACCEPT'
        option output 'ACCEPT'
        option forward 'ACCEPT'

    config zone
        option name 'lan1'
        list network 'lan1'
        option input 'ACCEPT'
        option output 'ACCEPT'
        option forward 'ACCEPT'

    config zone
        option name 'lan2'
        option network 'lan2'
        option input 'ACCEPT'
        option output 'ACCEPT'
        option forward 'ACCEPT'

    config zone
        option name 'wan'
        list network 'wan'
        option output 'ACCEPT'
        option masq '1'
        option mtu_fix '1'
        option input 'ACCEPT'
        option forward 'ACCEPT'

    config forwarding
        option src 'lan1'
        option dest 'wan'

    config forwarding
        option src 'lan2'
        option dest 'wan'

    config rule
        option name 'Allow-DHCP-Renew'
        option src 'wan'
        option proto 'udp'
        option dest_port '68'
        option target 'ACCEPT'
        option family 'ipv4'

    config rule
        option name 'Allow-Ping'
        option src 'wan'
        option proto 'icmp'
        option icmp_type 'echo-request'
        option family 'ipv4'
        option target 'ACCEPT'

    config rule
        option name 'Allow-IGMP'
        option src 'wan'
        option proto 'igmp'
        option family 'ipv4'
        option target 'ACCEPT'

    config rule
        option name 'Allow-DHCPv6'
        option src 'wan'
        option proto 'udp'
        option src_ip 'fe80::/10'
        option src_port '547'
        option dest_ip 'fe80::/10'
        option dest_port '546'
        option family 'ipv6'
        option target 'ACCEPT'

    config rule
        option name 'Allow-MLD'
        option src 'wan'
        option proto 'icmp'
        option src_ip 'fe80::/10'
        list icmp_type '130/0'
        list icmp_type '131/0'
        list icmp_type '132/0'
        list icmp_type '143/0'
        option family 'ipv6'
        option target 'ACCEPT'

    config rule
        option name 'Allow-ICMPv6-Input'
        option src 'wan'
        option proto 'icmp'
        list icmp_type 'echo-request'
        list icmp_type 'echo-reply'
        list icmp_type 'destination-unreachable'
        list icmp_type 'packet-too-big'
        list icmp_type 'time-exceeded'
        list icmp_type 'bad-header'
        list icmp_type 'unknown-header-type'
        list icmp_type 'router-solicitation'
        list icmp_type 'neighbour-solicitation'
        list icmp_type 'router-advertisement'
        list icmp_type 'neighbour-advertisement'
        option limit '1000/sec'
        option family 'ipv6'
        option target 'ACCEPT'

    config rule
        option name 'Allow-ICMPv6-Forward'
        option src 'wan'
        option dest '*'
        option proto 'icmp'
        list icmp_type 'echo-request'
        list icmp_type 'echo-reply'
        list icmp_type 'destination-unreachable'
        list icmp_type 'packet-too-big'
        list icmp_type 'time-exceeded'
        list icmp_type 'bad-header'
        list icmp_type 'unknown-header-type'
        option limit '1000/sec'
        option family 'ipv6'
        option target 'ACCEPT'

    config include
        option path '/etc/firewall.user'

    config rule
        option src 'wan'
        option dest 'lan'
        option proto 'esp'
        option target 'ACCEPT'

    config rule
        option src 'wan'
        option dest 'lan'
        option dest_port '500'
        option proto 'udp'
        option target 'ACCEPT'

    config rule
        option target 'ACCEPT'
        option name 'Allow-SSH-WAN'
        option proto 'tcp'
        option src 'wan'
        option src_port '22'
    ```
* Configure the DHCP of the AP. Edit `/etc/config/dhcp` to add the following:
    ```shell
    config dnsmasq
        option domainneeded	1
        option boguspriv	1
        option filterwin2k	0  # enable for dial on demand
        option localise_queries	1
        option rebind_protection 1  # disable if upstream must serve RFC1918 addresses
        option rebind_localhost 1  # enable for RBL checking and similar services
        #list rebind_domain example.lan  # whitelist RFC1918 responses for domains
        option local	'/lan/'
        option domain	'lan'
        option expandhosts	1
        option nonegcache	0
        option authoritative	1
        option readethers	1
        option leasefile	'/tmp/dhcp.leases'
        option resolvfile	'/tmp/resolv.conf.auto'
        #list server		'/mycompany.local/1.2.3.4'
        #option nonwildcard	1
        #list interface		br-lan
        #list notinterface	lo
        #list bogusnxdomain     '64.94.110.11'
        option localservice	1  # disable to allow DNS requests from non-local subnets

    config dhcp lan
        option interface	lan1
        option start 	100
        option limit	150
        option leasetime	12h

    config dhcp lan2
          option interface        lan2
          option start            200     
          option limit            250
          option leasetime        24h

    config dhcp wan
        option interface	wan
        option ignore	1
    ```
* Restart the network `/etc/init.d/network restart`
* Trun off the AP, move the following filesfrom PC to the USB in `/mnt/sda1/`:
    * [`click.zip`](https://github.com/oiasam/ARNAB/blob/master/tierOne/AP/Click/click.zip)
    * `agent-click-file-gen.py`
    * `start.sh`

* Start a Click Modular Router
    * Power ON the AP
    * Generate `agent.cli` using the following command
        ```shell
        python /mnt/sda1/agent-click-file-gen.py 1 500 500 18:a6:f7:ab:c2:fc 192.168.1.129 2819 /sys/kernel/debug/ieee80211/phy0/ath9k/bssid_extra wi5-demo 192.168.1.14 0 11 12 25 0 1 100 10 5 100 0 FF:FF:FF:FF:FF:FF > agent.cli
        ```
    * Run `start.sh` script (only press `Enter` when the controller is running)
