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
LXCPATH=$(sudo lxc-config lxc.lxcpath)
checkpoint_dir=/mnt/tmpfs/$name
pre_dump_min=2
pre_dump_max=9

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
sudo ssh $host "for i in {1..10}; do sudo mkdir -p $checkpoint_dir/$i/; done"
}

do_rsync() {
 sudo  rsync -rltha --devices --rsync-path=" sudo rsync" $1 $host:$1
}

pre_copy_migrate() {
  #echo "pre-dumping started for $name.."
  sudo lxc-checkpoint -n $name -D $checkpoint_dir/$((pre_dump_min-1))/ -p -v
  do_rsync $checkpoint_dir/$((pre_dump_min-1))/
  for i in `seq $pre_dump_min $pre_dump_max`; do 
    sudo lxc-checkpoint -n $name -D $checkpoint_dir/$i/ --predump-dir=../$((i-1)) -p -v; 
    do_rsync $checkpoint_dir/$i/;
  done
  
  #final dump done of $name
  sudo lxc-checkpoint -n $name -D $checkpoint_dir/$((pre_dump_max+1))/ --predump-dir=../$pre_dump_max -s -v

  #copy the final checkpoint from src to dst
  do_rsync $checkpoint_dir/$((pre_dump_max+1))/

  #restor the container at the dst
  ssh $host "sudo lxc-checkpoint -n $name -D $checkpoint_dir/$((pre_dump_max+1))/ --predump-dir=../$pre_dump_max -r -v"

}

clean_up_source
clean_up_destination
do_rsync $LXCPATH/$name/
pre_copy_migrate

sleep 2
ssh $host "sudo lxc-stop -n $name && sudo lxc-destroy -n $name"
sudo lxc-start -n $name
sleep 5
