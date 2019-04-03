#!/bin/sh
set -e

# Works for CRIU 2.6, 3.11

usage() {
  echo $0 container user@IP.to.migrate.to
  exit 1
}

if [ "$(id -u)" != "0" ]; then
  echo "ERROR: Must run as root."
  usage
fi

if [ "$#" != "2" ]; then
  echo "Bad number of args."
  usage
fi

name=$1
host=$2

clean_up_source() {
 # echo "Cleaning up the source host.."
  if [ -d /mnt/tmpfs/$name ]; then
   # echo "------ Found dump directory, deleting and recreating.."
    sudo rm -rf /mnt/tmpfs/$name
    sudo mkdir -p /mnt/tmpfs/$name
  else
    #echo "------ Dump directory not found, creating.."
    sudo mkdir -p /mnt/tmpfs/$name
  fi
 }

clean_up_destination() {
 # echo "Cleaning up the destination host.."
  sudo ssh $host 'bash -s' <<'ENDSSH'
  if [ -d /mnt/tmpfs/$name ]; 
  then
   # echo "------ Found dump directory, deleting and recreating.."
    sudo rm -rf /mnt/tmpfs/$name
    sudo mkdir -p /mnt/tmpfs/$name
  else
    #echo "------ Dump directory not found, creating.."
    sudo mkdir -p /mnt/tmpfs/$name
  fi
ENDSSH
}

do_rsync() {
 sudo  rsync -rltha --devices --rsync-path=" sudo rsync" $1 $host:$1
}

# we assume the same lxcpath on both hosts, that is bad.
LXCPATH=$(sudo lxc-config lxc.lxcpath)
checkpoint_dir=/mnt/tmpfs/$name

#clean up the dump directory
clean_up_source
clean_up_destination

# copy the content of the container from src to dst lxc path
#echo "Transferring static files.."
do_rsync $LXCPATH/$name/


# checkpoint the container
#echo "Checkpointing.."
sudo lxc-checkpoint -n $name -D $checkpoint_dir -s -v

# copy the checkpoint from src to dst
#echo "Copying over the checkpoint.."
do_rsync $checkpoint_dir/

# restor the container at the destination
#echo "Restoring container at the destination.."
ssh $host "sudo lxc-checkpoint -r -n $name -D $checkpoint_dir -v"

sleep 2
#echo "Stopping at remote host"
ssh $host "sudo lxc-stop -n $name && sudo lxc-destroy -n $name"
sudo lxc-start -n $name
sleep 5
