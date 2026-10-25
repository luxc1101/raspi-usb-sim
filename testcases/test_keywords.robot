*** Settings ***
Documentation    Test cases for Raspi USB SIM

Resource    resource/example.robot

suite setup    Connect SSH To Raspi USB SIM
suite teardown    Close All Connections


*** Test Cases ***
Test Case 1
    [Documentation]    Test case 1
    Ping USBTool IP

Test Case 2
    [Documentation]    Test case 2
    ${result}    Execute Command    whoami
    Should Be Equal    ${result}    pi

Test Case 3
    [Documentation]    Test case 3
    Mount Filesystem Raspi    FAT32
    ${result}    Execute Command    mountpoint /mnt/usb_fat32
    Should Be Equal    ${result}    /mnt/usb_fat32 is a mountpoint
    Unmount USB Device Raspi

Test Case 4
    [Documentation]    Test case 4
    Mount USB Device Raspi    HID    0x1d6b    0x0104
    Unmount USB Device Raspi

