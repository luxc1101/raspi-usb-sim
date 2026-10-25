*** Settings ***
Documentation    Provides common keywords to work with the target

Library    SSHLibrary
Library    Process


*** Variables ***
${USER}                 pi
${KEY}                  pass
${RASPI_IP}             192.168.2.77


*** Keywords ***
Ping USBTool IP
    [Documentation]    ping an IP address and chenk if it is reachable
    ${result}=    Run Process    ping    -n    2    ${RASPI_IP}
    Should Not Contain     ${result.stdout}     Unreachable
    Should Not Contain     ${result.stdout}     erreichbar
    RETURN    ${USER}    ${RASPI_IP}    ${KEY}

Connect SSH To Raspi USB SIM
    [Documentation]    SSH connection to Raspi USB SIM
    ...    Arguments:
    ...    ${Alias}    Enables logging of SSH protocol
    [Arguments]    ${alias}=raspi
    ${USER}    ${RASPI_IP}    ${KEY}    Ping USBTool IP
    SSHLibrary.Open Connection    ${RASPI_IP}
    Set Default Configuration    timeout=10s
    Login    ${USER}    ${KEY}
    # Enable Ssh Logging    ${alias}.log

Reboot Raspi
    [Documentation]    reboot Raspi
    ...    Arguments:
    Execute Command    reboot

Reboot Raspi And Reconnect
    [Documentation]    reboot and reconnect raspi
    Reboot Raspi
    Sleep    60s    reason=wait for raspi reboot
    Connect SSH To Raspi USB SIM

Mount Filesystem Raspi
    [Documentation]    Mount filesystem by system type:
    ...    Type:
    ...    "MIB Compliance Media": MIB Compliance Media
    ...    "EXT2": 2ed Extended Filesystem
    ...    "EXT3": 3rd Extended Filesystem
    ...    "EXT4": 4th Extended Filesystem
    ...    "FAT16": File Allocation Table 16
    ...    "FAT32": File Allocation Table 32
    ...    "NTFS": New Technology File System
    ...    "EXFAT": Extensible File Allocation Table
    ...    "HFSPLUS": Extended Hierarchical Filesystem
    ...    "PARTITION": Partition Filesystem
    ...    "Free Partition": Free Filesystem
    [Arguments]    ${Fs}
    Write    usbsim-robot -t MSC -f "${Fs}"
    Sleep    5s    reason=mount filesystem
    ${Readoutput}    Read Until    pi@
    Should End With    ${Readoutput}    pi@

Unmount USB Device Raspi
    [Documentation]    Unmount Filesystem from Raspi
    Write    usbsim-robot -t EJECT
    Sleep    5s    reason=unmount Raspi
    ${Readoutput}    Read Until    pi@
    Should End With    ${Readoutput}    pi@

Mount USB Device Raspi
    [Documentation]    Mount different type of USB equipment (HID, ECM. CDC) except MSC device
    ...
    ...  Arguements:
    ...  ${DeviceType}    USB device type: HID, ECM or CDC
    ...  ${DeviceVID}     USB device vendor ID (16 bit hex) e.g. 0x0000...0xFFFF
    ...  ${DevicePID}     USB device product ID (16 bit hex) e.g. 0x0000...0xFFFF
    ...
    ...  Example:
    ...  Mount USB Device Raspi | ${DeviceType} | ${DeviceVID} | ${DevicePID}
    [Arguments]    ${DeviceType}  ${DeviceVID}  ${DevicePID}    ${EnableInput}=0    ${Input}=swte
    Write    usbsim-robot -t "${DeviceType}" -v "${DeviceVID}" -p "${DevicePID}" -e ${EnableInput} -k "${Input}"
    Sleep    5s    reason=mount usb device
    ${Readoutput}    Read Until    pi@
    Should End With    ${Readoutput}    pi@

Remount Filesystem Raspi
    [Documentation]    Remount Filesystem from Raspi
    ...
    ...    Arguements:
    ...    ${Fs}    filesystem
    ...    ${Raspiconfig}    raspi configuration json file
    ...
    [Arguments]    ${Fs}
    Unmount USB Device Raspi
    Mount Filesystem Raspi    ${Fs}
