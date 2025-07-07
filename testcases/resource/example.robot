*** Settings ***
Documentation    Provides common keywords to work with the target

Library    SSHLibrary
Library    Process


*** Variables ***
${USBTOOL_CONFIG}             testcases/resources/usbtool_config.json


*** Keywords ***
Read USBTool Config File
    [Documentation]    Read usbtool config json file with ssh connection info
    [Arguments]    ${path}=${USBTOOL_CONFIG}
    ${json_data}        Evaluate    json.load(open('${path}'))    modules=json
    ${USER}             Set Variable        ${json_data['SSHConf']['User']}
    ${RASPI_IP}         Set Variable        ${json_data['SSHConf']['IPAddress']}
    ${KEY}              Set Variable        ${json_data['SSHConf']['Key']}
    RETURN    ${USER}    ${RASPI_IP}    ${KEY}

Ping USBTool IP
    [Documentation]    ping an IP address and chenk if it is reachable
    ${USER}    ${RASPI_IP}    ${KEY}    Read USBTool Config File
    ${result}=    Run Process    ping    -c    4    ${RASPI_IP}
    Should Not Contain     ${result.stdout}     Unreachable
    RETURN    ${USER}    ${RASPI_IP}    ${KEY}

Connect SSH To Raspi USB SIM
    [Documentation]    SSH connection to Raspi USB SIM (pi@192.168.188.38 )
    ...    Arguments:
    ...    ${Alias}    Enables logging of SSH protocol and output to gaven logfile "${Alias}.log"
    [Arguments]    ${alias}=raspi
    ${USER}    ${RASPI_IP}    ${KEY}    Ping USBTool IP
    SSHLibrary.Open Connection    ${RASPI_IP}
    Set Default Configuration    timeout=10s
    Login    ${USER}    ${KEY}
    Enable Ssh Logging    ${alias}.log

Reboot Raspi
    [Documentation]    reboot Raspi and sleep for ${Sleep} second
    ...    Arguments:
    ...    ${Sleep}    defaut timeout=60s
    [Arguments]    ${Sleep}=60s
    Write    reboot
    Sleep    ${Sleep}

Reboot Raspi And Reconnect
    [Documentation]    reboot and reconnect raspi
    Reboot Raspi
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
    ...    "QUIT": Quit and eject the device
    ...
    ...    Arguements:
    ...    ${FS}    filesystem
    ...
    ...    Example:
    ...    Mount Filesystem Raspi | ${FS}
    [Arguments]    ${Fs}
    Write    python mountfs_robot.py "${Fs}" - -
    Sleep    3s    reason=mount filesystem
    ${Readoutput}    Read Until    pi@
    Should End With    ${Readoutput}    pi@

Unmount USB Device Raspi
    [Documentation]    Unmount Filesystem from Raspi
    ...    "QUIT": Quit and unmount the device
    Write    python mountfs_robot.py QUIT - -
    Sleep    3s    reason=unmount Raspi
    ${Readoutput}    Read Until    pi@
    Should End With    ${Readoutput}    pi@

Mount USB Device Raspi
    [Documentation]    mount different type of USB equipment (HID, ECM. CDC) except MSC device
    ...
    ...  Arguements:
    ...  ${DeviceType}    USB device type: HID, ECM or CDC
    ...  ${DeviceVID}     USB device vendor ID (16 bit hex) e.g. 0x0000...0xFFFF
    ...  ${DevicePID}     USB device product ID (16 bit hex) e.g. 0x0000...0xFFFF
    ...
    ...  Example:
    ...  Mount USB Device Raspi | ${DeviceType} | ${DeviceVID} | ${DevicePID}
    [Arguments]    ${DeviceType}  ${DeviceVID}  ${DevicePID}
    Write    python mountfs_robot.py "${DeviceType}" "${DeviceVID}" "${DevicePID}"
    Sleep    2s    reason=mount usb device
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
