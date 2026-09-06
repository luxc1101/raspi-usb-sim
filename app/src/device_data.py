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
    HID_PROTOCOL: int = 0
    HID_DESCRIPTOR: str = ''
    HID_REPORT_LENGTH: int = 0
    HID_SUBCLASS: int = 0

    # Ethernet Adapter attributes
    RNDIS_CLASS: hex = 0x02
    RNDIS_SUBCLASS: hex = 0x06
    RNDIS_PROTOCOL: hex = 0x00
    DEV_ADDR: str = "00:dd:dc:eb:6d:a1"
    HOST_ADDR: str = "00:50:b6:19:ee:24"
    QUMLT: int = 5

    # CDC-ACM attributes
    CDC_PORT_NUM: int = 0

    # UAC attributes
    P_CHMARK: hex = 0x03      # playback channel mark, stereo (0x03 = left + right)
    P_SRATE: int = 48000      # playback sampling rate
    P_SSIZE: bytes = 2        # playback sample size (bytes) 2 bytes = 16 bits
    
    C_CHMARK: hex = 0x03      # capture channel mark, stereo (0x03 = left + right)
    C_SRATE: int = 48000      # capture sampling rate
    C_SSIZE: bytes = 2        # capture sample size (bytes) 2 bytes = 16 bits


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
    ncm             = 'ncm.usb0'
    mtp             = 'ffs.mtp'
    uac1            = 'uac1.usb0'
    uac2            = 'uac2.usb0'


@dataclass
class Color:
    Cyan = '\033[1;96m'
    Yellow = '\033[1;93m'
    Green = '\033[1;92m'
    Red = '\033[1;91m'
    C_off = '\033[0m'


@dataclass
class KeycodeDict:
    keycode_dict = {
        'a': b'\x04', 'b': b'\x05', 'c': b'\x06', 'd': b'\x07', 'e': b'\x08',
        'f': b'\x09', 'g': b'\x0a', 'h': b'\x0b', 'i': b'\x0c', 'j': b'\x0d',
        'k': b'\x0e', 'l': b'\x0f', 'm': b'\x10', 'n': b'\x11', 'o': b'\x12',
        'p': b'\x13', 'q': b'\x14', 'r': b'\x15', 's': b'\x16', 't': b'\x17',
        'u': b'\x18', 'v': b'\x19', 'w': b'\x1a', 'x': b'\x1b', 'y': b'\x1c',
        'z': b'\x1d',
        '1': b'\x1e', '2': b'\x1f', '3': b'\x20', '4': b'\x21', '5': b'\x22',
        '6': b'\x23', '7': b'\x24', '8': b'\x25', '9': b'\x26', '0': b'\x27',
        ' ': b'\x2c',
        '-': b'\x2d', '=': b'\x2e', '[': b'\x2f', ']': b'\x30', '\\': b'\x31',
        ';': b'\x33', "'": b'\x34', '`': b'\x35', ',': b'\x36', '.': b'\x37', '/': b'\x38',
        '_': b'\x2d', '+': b'\x2e', '{': b'\x2f', '}': b'\x30', '|': b'\x31',
        ':': b'\x33', '"': b'\x34', '~': b'\x35', '<': b'\x36', '>': b'\x37', '?': b'\x38',
        '!': b'\x1e', '@': b'\x1f', '#': b'\x20', '$': b'\x21', '%': b'\x22',
        '^': b'\x23', '&': b'\x24', '*': b'\x25', '(': b'\x26', ')': b'\x27'
    }