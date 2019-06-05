#!/bin/bash

function check_group () {
  echo $1 | awk '/^[1-9][0-9]?$/ { if ($1 < 32) print $1 }'
}

function check_root () {
  [ -n "$SUDO_USER" ] && echo "Ok"
  [ -n "$SUDO_USER" ] && return
  [ "$UID" == "0" ] && echo "Ok"
  echo "KO"
}

function main () {
  [ "$(check_root)" == "KO" ] && echo "Use as root or sudo!"
  [ "$(check_root)" == "KO" ] && return
  [ -z "$(check_group $1)" ] && echo "usage: $(basename $0) <group>"
  [ -z "$(check_group $1)" ] && return

  VLAN_ID=$((500 + $1))
  GRP_NAME=$(printf "osm-group%02d" $1)
  ETH=$(ls /sys/class/net/ | egrep '^e[^.]+$' | tail -1)

  modprobe 8021q
  ip link set dev $ETH up
  vconfig add $ETH $VLAN_ID
  ip addr add 10.208.0.1/24 dev $ETH.$VLAN_ID
  ip link set dev $ETH.$VLAN_ID up

  printf "Using VLAN %d\n" $VLAN_ID
  ip addr show $ETH.$VLAN_ID
}

check_root
check_group $1
main $*
