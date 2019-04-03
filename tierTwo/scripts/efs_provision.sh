#!/bin/sh
set -e

echo "[0] Updating and upgrading system.."
sudo apt update -qq
sudo apt upgrade -y -qq

echo "[1] Adding repositories.."
echo -ne '\n' | sudo add-apt-repository ppa:ubuntu-lxc/lxc-stable 
echo -ne '\n' | sudo add-apt-repository ppa:criu/ppa
sudo apt update -qq
	
echo "[2] Installing packages.."
sudo apt install lxc criu build-essential protobuf-c-compiler avahi-daemon asciidoc grub2 -y -qq
sudo apt-get install --no-install-recommends git build-essential libprotobuf-dev libprotobuf-c0-dev protobuf-compiler python-protobuf libnl-3-dev libpth-dev pkg-config libcap-dev libnet-dev -y -qq
kernel=$(echo $(uname -r) | cut -d'-' -f 1)

if [$kernel == "4.4.0"]
then
  sudo apt install linux-image-extra-$(uname -r) -y -qq
fi

echo "[3] Configuring interfaces.."
interface=$(route | grep '^default' | grep -o '[^ ]*$')
sudo rm -rf /etc/network/interfaces
sudo bash -c "echo -e 'auto lo\niface lo inet loopback\n\nauto $interface\niface $interface inet manual\n\nauto migbr\niface migbr inet dhcp\n\tbridge_ports $interface' >> /etc/network/interfaces"

sudo rm -rf /etc/lxc/default.conf
sudo bash -c "echo -e 'lxc.net.0.type = veth\nlxc.net.0.link = migbr\nlxc.net.0.flags = up\nlxc.net.0.hwaddr = 00:16:3e:xx:xx:xx' >> /etc/lxc/default.conf"

sudo service lxc-net restart

echo "[4] Creating container.."
sudo lxc-create -t download -n c1 -- -d ubuntu -r xenial -a amd64
sudo bash -c "echo -e '\n#Disable Apparmor\nlxc.apparmor.allow_incomplete = 1\n#hax for criu\nlxc.console.path = none\nlxc.tty.max = 0\nlxc.cgroup.devices.deny = c 5:1 rwm' >> /var/lib/lxc/c1/config"
sudo find /var/lib/lxc/c1/rootfs/dev/ -name 'tty*' -delete
for i in `seq 0 4`; do sudo touch /var/lib/lxc/c1/rootfs/dev/tty$i; done

echo "[5] Installing kernel 4.4.0-116.."
sudo apt install linux-image-4.4.0-116-generic linux-headers-4.4.0-116-generic -y -qq
sudo update-grub2

sudo reboot
