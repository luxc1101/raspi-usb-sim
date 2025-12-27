#!/bin/bash
# this script is going to install all requiremed packages for usb tool, setup pre-configuration and services 
# sudo rm install.sh && sudo nano install.sh
# sudo apt-get update
# sudo apt-get upgrade
# sudo sed -i 's/dtoverlay=dwc2/dtoverlay=aaa/g' /boot/config.txt
if [ -z "$1" ] ; then
  echo No path argument, please give root path argument
  exit 1
fi

# global var
OVERLAY_NAME=dwc2 # an important component in embedded systems that need USB On-The-Go support. It allows the USB controller to function either as a host or a device, this driver is essential for using USB gadget functionality, enabling the Pi to act as a peripheral to another computer or to control USB peripherals in host mode.
LIBCOMPOSITE=libcomposite
BOOT_CONFIG=/boot/config.txt # configure the Raspberry Pi's boot behavior, It is essential for controlling how the Raspberry Pi behaves during startup and how it interacts with connected hardware.
BOOT_CONFIG_=/boot/firmware/config.txt
SWREQ=$1/requirements.txt # requirements list
MODULES=/etc/modules # file in Linux systems is used to specify kernel modules that should be loaded at boot time ensures that the necessary modules are automatically loaded during the boot process.
CONFIGFS=configfs # configfs is a ram-based filesystem and a filesystem-based manager of kernel objects, Linux USB gadget configured through configfs https://www.kernel.org/doc/Documentation/usb/gadget_configfs.txt
CONFIGFS_MNT=/sys/kernel/config
BOOT_CMDLINE=/boot/cmdline.txt
BOOT_CMDLINE_=/boot/firmware/cmdline.txt
SAMBA_CONF=/etc/samba/smb.conf
PWD=$(pwd)
FS_WATCHDOG_SER=fswd.service
FS_WATCHDOG_SH=fswd.sh
SYS_SER=/lib/systemd/system
USER=pi
SRC=src
MOUNTFS_GUI_SCRIPT=mount_app.py
MOUNTFS_HADES_SCRIPT=mount_robot.py
KB_DESCRIPTOR=kybd-descriptor.bin
UMTPRESPONDER=umtprd
UMTPRESPONDER_CONF=umtprd.conf

DEFAULT_HOMEDIR_PI=/home/pi
DEVICE_PROJ_JSON=device_proj.json


Cyan='\033[1;96m'
Green='\033[1;92m'
Red='\033[1;91m'
C_off='\033[0m'

# Check which boot config file exists and use the appropriate one
if [ -f "$BOOT_CONFIG_" ]; then
  BOOT_CONFIG_ACTIVE="$BOOT_CONFIG_"
elif [ -f "$BOOT_CONFIG" ]; then
  BOOT_CONFIG_ACTIVE="$BOOT_CONFIG"
else
  echo "${Red}Neither ${BOOT_CONFIG} nor ${BOOT_CONFIG_} found${C_off}"
  exit 1
fi

# Check which boot cmdline file exists and use the appropriate one
if [ -f "$BOOT_CMDLINE_" ]; then
  BOOT_CMDLINE_ACTIVE="$BOOT_CMDLINE_"
elif [ -f "$BOOT_CMDLINE" ]; then
  BOOT_CMDLINE_ACTIVE="$BOOT_CMDLINE"
else
  echo "${Red}Neither ${BOOT_CMDLINE} nor ${BOOT_CMDLINE_} found${C_off}"
  exit 1
fi

echo "PROGRESS:5"
echo "${Cyan}apt-get update and upgrade${C_off}"
sudo apt-get update && sudo apt-get upgrade -y
echo "${Cyan}apt-get update and upgrade finished${C_off}"
echo "PROGRESS:10"


# Check if [all] section exists
if grep -q "^\[all\]" $BOOT_CONFIG_ACTIVE; then
  # Add dtoverlay=dwc2 after [all] section if not already present
  if ! sed -n '/^\[all\]/,/^\[.*\]/p' $BOOT_CONFIG_ACTIVE | grep -q "dtoverlay=${OVERLAY_NAME}"; then
    sudo sed -i "/^\[all\]/a dtoverlay=${OVERLAY_NAME}" $BOOT_CONFIG_ACTIVE
    echo "Added ${OVERLAY_NAME} to [all] section in ${BOOT_CONFIG_ACTIVE}"
  else
    echo "${OVERLAY_NAME} already present in [all] section of ${BOOT_CONFIG_ACTIVE}"
  fi
else
  # No [all] section, append at end
  echo "dtoverlay=${OVERLAY_NAME}" | sudo tee -a $BOOT_CONFIG_ACTIVE
  echo "Added ${OVERLAY_NAME} at end of ${BOOT_CONFIG_ACTIVE}"
fi

echo "PROGRESS:12"
if grep -q "modules-load=${OVERLAY_NAME}" $BOOT_CMDLINE_ACTIVE; then
  echo "${OVERLAY_NAME} already in ${BOOT_CMDLINE_ACTIVE}"
else
  sudo sed -i "s/\(rootwait\)/\1 modules-load=${OVERLAY_NAME}/" $BOOT_CMDLINE_ACTIVE
  echo "Added ${OVERLAY_NAME} to ${BOOT_CMDLINE_ACTIVE}"
fi
echo "PROGRESS:14"
if grep -q "${OVERLAY_NAME}" $MODULES; then
  echo "${OVERLAY_NAME} already in ${MODULES}"
else
  echo "${OVERLAY_NAME}" | sudo tee -a $MODULES
fi
echo "PROGRESS:16"
if grep -q "${LIBCOMPOSITE}" $MODULES; then
  echo "${LIBCOMPOSITE} already in ${MODULES}" 
else
  echo "${LIBCOMPOSITE}" | sudo tee -a $MODULES
fi
echo "PROGRESS:18"
if findmnt | grep -q "${CONFIGFS}"; then
  echo "${CONFIGFS} already mounted"
else
  sudo mount -t ${CONFIGFS} none ${CONFIGFS_MNT}
fi
echo "PROGRESS:20"

echo "${Cyan}Pakcages installation${C_off}"
echo "" >> ${SWREQ}
sudo dos2unix ${SWREQ} ||  { echo "${Red}converting ${SWREQ} to Unix format... failed${C_off}"; exit 1; }
# read package name from requirements.txt and install
while read -r package; do
  echo "${Green}installing ${package}...${C_off}"
  if [ -n "$package" ]; then
    sudo apt-get install -y "$package"
    result=$?
    if [ $result -ne 0 ]; then
      echo "${Red}${package} installation failed${C_off}"
      exit 1
    fi
    echo "${Green}${package} installed${C_off}"
  fi
done < "${SWREQ}"
echo "${Cyan}Packages installtion successfully finished${C_off}"
echo "PROGRESS:50"

# config samba service
# https://www.samba.org/samba/docs/4.13/man-html/smb.conf.5.html
echo "${Cyan}Samba service configuration${C_off}"
dpkg -s samba > /dev/null 2>&1
# shellcheck disable=SC2181
if [ $? -eq 0 ] && [ -e $SAMBA_CONF ]; then
  if ! grep -q "raspiusb" $SAMBA_CONF; then
    sudo sed -i -e '$a [raspiusb_]' $SAMBA_CONF || { echo "${Red}Samba service '[raspiusb_]' configuration failed ${C_off}"; exit 1; }
    sudo sed -i -e '$a browseable = yes' $SAMBA_CONF || { echo "${Red}Samba service 'browseable = yes' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a read only = no' $SAMBA_CONF || { echo "${Red}Samba service 'read only = no' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a writeable = yes' $SAMBA_CONF || { echo "${Red}Samba service 'writeable = yes' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a guest ok = yes' $SAMBA_CONF || { echo "${Red}Samba service 'guest ok = yes' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a create mask = 0777' $SAMBA_CONF || { echo "${Red}Samba service 'create mask = 0777' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a directory mask = 0777' $SAMBA_CONF || { echo "${Red}Samba service 'directory mask = 0777' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a strict sync = yes' $SAMBA_CONF || { echo "${Red}Samba service 'strict sync = yes' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a sync always = yes' $SAMBA_CONF || { echo "${Red}Samba service 'sync always = yes' configuration failed${C_off}"; exit 1; }
    sudo sed -i -e '$a path = /mnt/' $SAMBA_CONF || { echo "${Red}Samba service 'path = /mnt/' configuration failed${C_off}"; exit 1; }
  fi
else
  echo "${Red}Samba service configuration failed${C_off}"
  exit 1
fi
echo "PROGRESS:70"
echo "${Cyan}Samba service configuration successfully finished${C_off}"

# config watchdog for filesystem
echo "${Cyan}Watchdog service configuration${C_off}"
sudo sed -i "s|^ExecStart=.*|ExecStart=${PWD}/${FS_WATCHDOG_SH}|" ${FS_WATCHDOG_SER} || { echo "${Red}Watchdog service 'ExecStart' configuration failed${C_off}"; exit 1;}
sudo sed -i "s|^User=.*|User=${USER}|" ${FS_WATCHDOG_SER} || { echo "${Red}Watchdog service 'User' configuration failed${C_off}"; exit 1;}

dpkg -s inotify-tools > /dev/null 2>&1
if [ $? -eq 0 ] && [ -e "${1}/${FS_WATCHDOG_SH}" ] && [ -e "${1}/${FS_WATCHDOG_SER}" ]; then
  sudo dos2unix $1/$FS_WATCHDOG_SH ||  { echo "${Red}Watchdog service converting ${FS_WATCHDOG_SH} to Unix format... failed${C_off}"; exit 1; }
  sudo chmod 777 $1/$FS_WATCHDOG_SH || { echo "${Red}Watchdog service 'chmod $FS_WATCHDOG_SH' failed${C_off}"; exit 1; }
  sudo cp "${1}/${FS_WATCHDOG_SER}" $SYS_SER || { echo "${Red}Watchdog service 'cp $FS_WATCHDOG_SER' failed${C_off}"; exit 1; }
  sudo chmod 777 $SYS_SER/$FS_WATCHDOG_SER || { echo "${Red}Watchdog service 'chmod $FS_WATCHDOG_SER' failed${C_off}"; exit 1; }
  sudo systemctl daemon-reload || { echo "${Red}Watchdog service 'daemon-reload' failed${C_off}"; exit 1; }
  sudo systemctl enable $FS_WATCHDOG_SER || { echo "${Red}Watchdog service 'enable fswd.service' failed${C_off}"; exit 1; }
else
  echo "${Red}Watchdog service configuration failed${C_off}"
  exit 1
fi
echo "PROGRESS:90"
echo "${Cyan}Watchdog service configuration successfully finished${C_off}"
sudo find $SRC -type f -exec chmod 777 {} \;
sudo chmod 777 $MOUNTFS_GUI_SCRIPT
sudo chmod 777 $MOUNTFS_HADES_SCRIPT
sudo chmod 777 $KB_DESCRIPTOR
sudo chmod 777 $UMTPRESPONDER
sudo chmod 777 $UMTPRESPONDER_CONF
sudo mkdir -p /etc/umtprd || { echo "${Red}Creating /etc/umtprd directory failed${C_off}"; exit 1; }
sudo cp $1/$UMTPRESPONDER_CONF /etc/umtprd/ || { echo "${Red}Copy-paste '$UMTPRESPONDER_CONF' failed${C_off}"; exit 1; }
sudo cp $1/$UMTPRESPONDER /usr/bin/$UMTPRESPONDER || { echo "${Red}Copy-paste '$UMTPRESPONDER' failed${C_off}"; exit 1; }
sudo cp -a $1/$SRC $DEFAULT_HOMEDIR_PI || { echo "${Red}Copy-paste '$SRC' failed${C_off}"; exit 1; }
sudo cp $1/$MOUNTFS_GUI_SCRIPT $DEFAULT_HOMEDIR_PI ||  { echo "${Red}Copy-paste '$MOUNTFS_GUI_SCRIPT' failed${C_off}"; exit 1; }
sudo cp $1/$MOUNTFS_HADES_SCRIPT $DEFAULT_HOMEDIR_PI ||  { echo "${Red}Copy-paste '$MOUNTFS_HADES_SCRIPT' failed${C_off}"; exit 1; }
sudo cp $1/$KB_DESCRIPTOR $DEFAULT_HOMEDIR_PI || { echo "${Red}Copy-paste '$KB_DESCRIPTOR' failed${C_off}"; exit 1; }
sudo cp $1/$DEVICE_PROJ_JSON $DEFAULT_HOMEDIR_PI || { echo "${Red}Copy-paste '$DEVICE_PROJ_JSON' failed${C_off}"; exit 1; }

echo "PROGRESS:100"
echo "USBTool enabled. Rebooting system now..."
sleep 2
sudo reboot
