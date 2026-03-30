import os
import sys
import argparse
# from ast import literal_eval

from src.acm_device import ACM
from src.device_data import DeviceDescriptors, DeviceFunction
from src.device_dictcreator import DeviceDictCreator
from src.ecm_device import ECM
from src.hid_device import HID
from src.msc_device import MSC
from src.rndis_device import RNDIS
from src.ncm_device import NCM
from src.mtp_device import MTP
from src.uac_device import UAC
from src.usb_peripheral import USBPeripheral


parser = argparse.ArgumentParser(description='Simulate a USB device on Rpi')
parser.add_argument('--type', type=str, required=True, choices=['MSC', 'HID', 'ECM', 'CDC', 'NCM', 'MTP', 'UAC', 'EJECT', 'DELETE', 'REMOUNT', 'QUIT'], help='Type of USB device to simulate (MSC, HID, ECM, CDC, NCM, MTP, UAC, EJECT, DELETE, REMOUNT)')
parser.add_argument('--vid', type=str, help='Vendor ID for the USB device')
parser.add_argument('--pid', type=str, help='Product ID for the USB device')
parser.add_argument('--fs', type=str, help='Filesystem type for MSC device (e.g., FAT32, NTFS)')
parser.add_argument('--samba', type=int, choices=[0, 2], default=0, help='Whether to configure samba service for MSC device (0 or 2)')
parser.add_argument('--wado', type=int, choices=[0, 2], default=0, help='Whether to start watchdog for MSC device (0 or 2)')


class DeviceOperator():

    def __init__(self):
        self.args = parser.parse_args()
        if self.args.type == "MSC" and not self.args.fs:
            parser.error("--fs argument is required when --type is MSC")
        self.device_dict = DeviceDictCreator(os.path.join(os.getcwd(),"device_proj.json"))
        self.device_desc = DeviceDescriptors()
        self.device = USBPeripheral()

    
    def _isMSC(self) -> bool:
        if self.args.type == "MSC":
            return True
        return False
    
    def _isHID(self) -> bool:
        if self.args.type == "HID":
            self.device_desc.idProduct = self.args.pid
            self.device_desc.idVendor = self.args.vid
            self.device_desc.bDeviceClass = 0x03
            self.device_desc.bDeviceSubClass = 0x02
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated HID device"
            self.device_desc.bmAttributes = 0x80
            self.device_desc.HID_PROTOCAL = 1
            self.device_desc.HID_SUBCLASS = 1
            self.device_desc.HID_DESCRIPTOR = "kybd-descriptor.bin"
            self.device_desc.HID_REPORT_LENGTH = 8
            return True
        return False
    
    def _isRNDIS(self) -> bool:
        if self.args.type == "RNDIS":
            self.device_desc.idProduct = self.args.pid
            self.device_desc.idVendor = self.args.vid
            self.device_desc.bDeviceClass = 0xEF
            self.device_desc.bDeviceSubClass = 0x04
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated RNDIS device"
            self.device_desc.bmAttributes = 0x80
            self.device_desc.RNDIS_CLASS = 0xEF
            self.device_desc.RNDIS_SUBCLASS = 0x04
            self.device_desc.RNDIS_PORTOCAL = 0x01
            return True
        return False
    
    def _isECM(self) -> bool:
        if self.args.type == "ECM":
            self.device_desc.idProduct = self.args.pid
            self.device_desc.idVendor = self.args.vid
            self.device_desc.bDeviceClass = 0xFF
            self.device_desc.bDeviceSubClass = 0x04
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated ECM device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False
    
    def _isAMC(self) -> bool:
        if self.args.type == "CDC":
            self.device_desc.idProduct = self.args.pid
            self.device_desc.idVendor = self.args.vid
            self.device_desc.bDeviceClass = 0x02
            self.device_desc.bDeviceSubClass = 0x00
            self.device_desc.bDeviceProtocol = 0x00
            self.device_desc.product = "Emulated CDC device"
            self.device_desc.bmAttributes = 0x80
            self.device_desc.CDC_PORT_NUM = 0
            return True
        return False
    
    def _isNCM(self) -> bool:
        if self.args.type == "NCM":
            self.device_desc.idProduct = self.args.pid
            self.device_desc.idVendor = self.args.vid
            self.device_desc.bDeviceClass = 0x02
            self.device_desc.bDeviceSubClass = 0x0D
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated NCM device"
            self.device_desc.bmAttributes = 0x80
            self.device_desc.CDC_PORT_NUM = 0
            return True
        return False
    
    def _isMTP(self) -> bool:
        if self.args.type == "MTP":
            self.device_desc.idProduct = self.args.pid
            self.device_desc.idVendor = self.args.vid
            self.device_desc.bDeviceClass = 0x06
            self.device_desc.bDeviceSubClass = 0x01
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated MTP device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False
    
    def _isUAC(self) -> bool:
        if self.args.type == "UAC":
            self.device_desc.idProduct = self.args.pid
            self.device_desc.idVendor = self.args.vid
            self.device_desc.bDeviceClass = 0x01
            self.device_desc.bDeviceSubClass = 0x01
            self.device_desc.product = "Emulated UAC device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False

    def _isEJECT(self) -> bool:
        if self.args.type == "EJECT":
            return True
        return False
    
    def _isDELETE(self) -> bool:
        if self.args.type == "DELETE":
            return True
        return False
    
    def _isQUIT(self) -> bool:
        if self.args.type == "QUIT":
            return True
        return False
    
    def _isREMOUNT(self) -> bool:
        if self.args.type == "REMOUNT":
            return True
        return False

    def _eject_device(self):
        USBPeripheral.disable_the_gadget()
        MSC.eject_msc()

    def operate_device(self):
        '''
        MSC
        HID
        ECM
        CDC
        NCM
        MTP
        UAC
        '''
        if self._isMSC():
            self.device_dict.fill_msc_dictionary()
            self.msc_dict = self.device_dict.msc_dict
            img_name = self.msc_dict[self.args.fs]['img'].lower()
            mnt_path = self.msc_dict[self.args.fs]['mnt']
            msc_device = MSC(img_name, 
                            mnt_path, 
                            samba=int(self.args.samba), 
                            watchdog=int(self.args.wado))
            msc_device.enable_the_gadget()
            return
        
        elif self._isHID():
            self.device.usb_device = HID(self.device_desc, DeviceFunction.hid.value, enable=0, input_string="")

        elif self._isRNDIS():
            self.device.usb_device = RNDIS(self.device_desc, DeviceFunction.rndis.value)

        elif self._isECM():
            self.device.usb_device = ECM(self.device_desc, DeviceFunction.ecm.value)

        elif self._isAMC():
            self.device.usb_device = ACM(self.device_desc, DeviceFunction.acm.value)
        
        elif self._isNCM():
            self.device.usb_device = NCM(self.device_desc, DeviceFunction.ncm.value)

        elif self._isMTP():
            self.device.usb_device = MTP(self.device_desc, DeviceFunction.mtp.value)

        elif self._isUAC():
            self.device.usb_device = UAC(self.device_desc, DeviceFunction.uac2.value)

        elif self._isEJECT():
            self._eject_device()
            return
        
        elif self._isREMOUNT():
            self.device_dict.fill_msc_dictionary()
            self.msc_dict = self.device_dict.msc_dict
            img_name = self.msc_dict[self.args.fs]['img'].lower()
            mnt_path = self.msc_dict[self.args.fs]['mnt']
            msc_device = MSC(img_name, 
                            mnt_path, 
                            samba=int(self.args.samba), 
                            watchdog=int(self.args.wado))
            msc_device.remount_msc()
            return

        elif self._isDELETE():
            fs_image = self.args.fs
            MSC.delete_img(fs_image)
            return
        
        elif self._isQUIT():
            MSC.eject_msc()
            USBPeripheral.disable_the_gadget()
            return
        
        self.device.create_the_gadgets()
        self.device.create_the_configurations()
        self.device.create_the_functions()
        self.device.enable_the_gadget()
 
if __name__ == "__main__":
    device_operator = DeviceOperator()
    device_operator.operate_device()