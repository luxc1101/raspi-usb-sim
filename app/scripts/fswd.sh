#!/bin/bash
#*****************************************************
# Project:   Raspberrypi Zero USB filesystem simulator
# Autor:     Xiaochuan Lu
# Abteilung: SWTE
#*****************************************************
##############
# parameters 
# https://wiki.ubuntuusers.de/inotify/
##############
Img=/home/pi/fat32.img
watchpath=/mnt/usb_fat32
action_timeout=5
while inotifywait -e modify -e create -e delete -e attrib -e move $watchpath;
do
    sleep $action_timeout
    echo -e "mount point path $watchpath"
    # unmount
    sudo /sbin/modprobe g_mass_storage -r
    sleep 1
    # sync
    sudo sync
    sleep 1
    # mount
    sudo /sbin/modprobe g_mass_storage file=$Img stall=0 removable=1 ro=0 iManufacturer="Raspi" iProduct="PiZeroMsc_$(basename "$Img" | cut -d. -f1)" iSerialNumber="$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2)"
    sleep 1
done
