#!/bin/bash
# OpenWrt firmware build script for TL-WR1043ND 
# Added features for the Horizon 2020 Wi-5 project:
#   - Click router with Odin Agent (To be moved to the AP after flashing)
#   - Open vSwitch

# Copyright (c) 2015 AirTies Wireless Networks

set -e

clean_up() {
  rm -rf openwrt odin-driver-patches 
}

clone_openwrt() {
  if ! [ -d openwrt ]; then
    git clone https://github.com/openwrt/chaos_calmer openwrt
  fi
}

patch_ath9k() {
  if ! [ -d odin-driver-patches ]; then
    git clone git://github.com/lalithsuresh/odin-driver-patches.git
  fi
  sed -e '1,2d' \
      -e 's/compat-wireless-2011-12-01.orig/a/' \
      -e 's/compat-wireless-2011-12-01/b/' \
      -e 's/ath9k_debugfs_open/simple_open/' \
    odin-driver-patches/ath9k/ath9k-bssid-mask.patch \
    > openwrt/package/kernel/mac80211/patches/580-ath9k-bssid-mask.patch
}

#add the required feeds, i.e. packages you want to make available in menuconfig
install_feeds() {
  cp openwrt/feeds.conf.default openwrt/feeds.conf
  #echo "src-link custom `pwd`/custom" >> openwrt/feeds.conf
  cd openwrt
  ./scripts/feeds update -a
  ./scripts/feeds install -a 
}

# select the packages you want to be set to be compiled and installed 
# to add the Support for wireless debugging in ath9k driver (this will call debug.c).
#   Kernel modules / Wireless drivers / kmod-ath / Atheros wireless debugging
#   set the flag CONFIG_PACKAGE_ATH_DEBUG=y in the .conf file
configure_openwrt() {
  TARGET_PROFILE="TLWR1043"
  make defconfig
  sed -i.orig \
      -e 's/\(CONFIG_TARGET_ar71xx_generic_Default\)=y/# \1 is not set/' \
      -e "s/# \(CONFIG_TARGET_ar71xx_generic_$TARGET_PROFILE\) is not set/\1=y/" \
      -e 's/# \(CONFIG_DEVEL\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_wireless-tools\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_luci\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_openvpn-nossl\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-openvswitch\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-tun\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-usb-storage\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-fs-ext4\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-fs-msdos\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-fs-vfat\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-nls-cp437\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-nls-iso8859-13\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-crypto-crc32c\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-lib-crc32c\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_hostapd\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_hostapd-utils\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_ATH_DEBUG\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-ath\) is not set/\1=y/' \
      -e 's/# \(CONFIG_PACKAGE_kmod-ath9k-htc\) is not set/\1=y/' \
      -e 's/\(CONFIG_PACKAGE_odhcp6c\)=y/# \1 is not set/' \
      -e 's/\(CONFIG_PACKAGE_odhcpd\)=y/# \1 is not set/' \
    .config
  make defconfig	
 
 # To be installed manually 
 #  - joe
 #  - nano
 #  - tcpdump
 #  - openvswitch
 #  - hostapd
 #  - hostapd-utils
 #  - usbutils
 #  - libstdcpp

#Remove the "CONFIG_USE_MIPS16=y" option. Uncheck the MIPS16 option:
#Advanced config. options/ Target opt./ Build packages with MIPS16 instructions
  sed -i.orig \
      -e 's/# \(CONFIG_TARGET_OPTIONS\) is not set/\1=y/' \
      -e 's/\(CONFIG_USE_MIPS16\)=y/# \1 is not set/' \
    .config
  make defconfig

#Remove the "CONFIG_PACKAGE_wpad-mini=y" option, it conflicts with hostpda
  #sed -i.orig \
      #-e 's/\(CONFIG_PACKAGE_wpad-mini\)=y/# \1 is not set/' \
    #.config
  #make defconfig
  
  sed -i.orig \
      -e 's/# \(CONFIG_PACKAGE_openvswitch-ipsec\) is not set/\1=y/' \
    .config
  make defconfig
}

clean_up
clone_openwrt
patch_ath9k
install_feeds
configure_openwrt
