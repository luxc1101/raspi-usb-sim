import os
from dataclasses import dataclass
from enum import Enum


@dataclass
class DeviceDescriptors:
    '''
    https://docs.kernel.org/usb/gadget_configfs.html
    https://www.keil.com/pack/doc/mw/USB/html/_u_s_b__device__descriptor.html
    '''
    idVendor: hex = 0x00           # Vendor ID https://knowledgebase.42gears.com/article/how-to-find-the-deviceclassid-and-deviceinstanceid-for-the-usb-devices/
    idProduct: hex = 0x00          # Product ID https://knowledgebase.42gears.com/article/how-to-find-the-deviceclassid-and-deviceinstanceid-for-the-usb-devices/
    serialnumber: str = os.popen("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2").read().split("\n")[0]       # device serial number
    manufacturer: str = "Raspi"      # manufacturer attribute
    product: str = ""            # cleartext product description
    configuration: str = "Config 1"        # name of this configuration
    bcdDevice: hex = 0x0100          # usb device descriptor, identifies the version of the device. This value is a binary-coded decimal number.
    bcdUSB: hex = 0x0200             # indicates the version of the USB specification to which the device conforms. For example, 0x0200 indicates that the device is designed as per the USB 2.0 specification.
    bDeviceClass: hex = 0x00       # class code  https://www.usb.org/defined-class-codes
    bDeviceSubClass: hex = 0x00    # class code  https://www.usb.org/defined-class-codes
    bDeviceProtocol: hex = 0x00    # class code  https://www.usb.org/defined-class-codes
    MaxPower: int = 250           # in mA
    bmAttributes: hex = 0x00       # Configuration characteristics (D7: Reserved (set to one), D6: Self-powered, D5: Remote Wakeup, D4...0: Reserved (reset to zero)) 
    
    # HID attributes
    HID_PROTOCAL: int = 0
    HID_DESCRIPTOR: str = ''
    HID_REPORT_LENGTH: int = 0
    HID_SUBCLASS: int = 0

    # Ethernet Adapter attributes
    RNDIS_CLASS: hex = 0x02
    RNDIS_SUBCLASS: hex = 0x06
    RNDIS_PORTOCAL: hex = 0x00
    DEV_ADDR: str = "00:dd:dc:eb:6d:a1"
    HOST_ADDR: str = "00:dc:c8:f7:75:14"
    QUMLT: int = 5

    # CDC-ACM attributes
    CDC_PORT_NUM: int = 0



@dataclass
class DeviceFunction(Enum):
    '''
    https://www.kernel.org/doc/Documentation/ABI/testing/
    '''
    hid             = 'hid.usb0'
    acm             = 'acm.usb0'
    ecm             = 'ecm.usb0'
    rndis           = 'rndis.usb0'
    mass_storage    = 'mass_storage.usb0'
    serial          = 'gser.usb0'

@dataclass
class Color:
    Cyan = '\033[1;96m'
    Yellow = '\033[1;93m'
    Green = '\033[1;92m'
    Red = '\033[1;91m'
    C_off = '\033[0m'
