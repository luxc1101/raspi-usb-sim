#***********************************************************
# Project:   Raspberrypi Zero USB filesystem simulator (HADES)
# Autor:     Xiaochuan Lu
# Abteilung: SWTE
#************************************************************
##########################
# Import all needed libs #
##########################
import os
import sys

from src.acm_device import ACM
from src.device_data import Color, DeviceDescriptors, DeviceFunction
from src.device_dictcreator import DeviceDictCreator
from src.ecm_device import ECM
from src.hid_device import HID
from src.msc_device import MSC
from src.ncm_device import NCM
from src.rndis_device import RNDIS
from src.mtp_device import MTP
from src.uac_device import UAC
from src.usb_peripheral import USBPeripheral

deviceType = sys.argv[1]
deviceArg0 = sys.argv[2]
deviceArg1 = sys.argv[3]

'''
A Python script saved in the /home/pi directory of a Raspberry Pi Zero W device, which will be executed in the new HADES to simulate a USB device

python mount_robot.py 'MSC' 'FAT32' '-'               # MSC device
python mount_robot.py 'HID' '0x0000' '0xffff'         # HID device
python mount_robot.py 'CDC' '0x0000' '0xffff'         # CDC device
python mount_robot.py 'ECM' '0x0000' '0xffff'         # ECM device
python mount_robot.py 'MTP' '0x0000' '0xffff'         # MTP device
python mount_robot.py 'UAC' '0x0000' '0xffff'         # UAC device
python mount_robot.py 'EJECT' '-' '-'                 # Eject device
'''

class DeviceOperator():

    def __init__(self):
        self.device_dict = DeviceDictCreator(os.path.join(os.getcwd(),"device_proj.json"))
        self.device_desc = DeviceDescriptors()
        self.device = USBPeripheral()

    def _isMSC(self) -> bool:
        if deviceType == "MSC":
            return True
        return False

    def _isHID(self) -> bool:
        if deviceType == "HID":
            self.device_desc.idVendor = deviceArg0
            self.device_desc.idProduct = deviceArg1
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
        if deviceType == "RNDIS":             
            self.device_desc.idVendor = deviceArg0
            self.device_desc.idProduct = deviceArg1
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
        if deviceType == "ECM":
            self.device_desc.idVendor = deviceArg0
            self.device_desc.idProduct = deviceArg1
            self.device_desc.bDeviceClass = 0xFF
            self.device_desc.bDeviceSubClass = 0x04
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated ECM device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False
    
    def _isAMC(self) -> bool:
        if deviceType == "CDC":
            self.device_desc.idVendor = deviceArg0
            self.device_desc.idProduct = deviceArg1
            self.device_desc.bDeviceClass = 0x02
            self.device_desc.bDeviceSubClass = 0x00
            self.device_desc.bDeviceProtocol = 0x00
            self.device_desc.product = "Emulated CDC device"
            self.device_desc.bmAttributes = 0x80
            self.device_desc.CDC_PORT_NUM = 0
            return True
        return False
    
    def _isNCM(self) -> bool:
        if deviceType == "NCM":
            self.device_desc.idVendor = deviceArg0
            self.device_desc.idProduct = deviceArg1
            self.device_desc.bDeviceClass = 0x0A
            self.device_desc.bDeviceSubClass = 0x0D
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated NCM device"
            self.device_desc.bmAttributes = 0x80
            self.device_desc.CDC_PORT_NUM = 0
            return True
        return False
    
    def _isMTP(self) -> bool:
        if deviceType == "MTP":
            self.device_desc.idVendor = deviceArg0
            self.device_desc.idProduct = deviceArg1
            self.device_desc.bDeviceClass = 0x06
            self.device_desc.bDeviceSubClass = 0x01
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated MTP device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False
    
    def _isUAC(self) -> bool:
        if deviceType == "UAC":
            self.device_desc.idVendor = deviceArg0
            self.device_desc.idProduct = deviceArg1
            self.device_desc.bDeviceClass = 0x01
            self.device_desc.bDeviceSubClass = 0x01
            self.device_desc.bDeviceProtocol = 0x00
            self.device_desc.product = "Emulated UAC device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False

    def _isEJECT(self) -> bool:
        if deviceType == "EJECT":
            return True
        return False
    
    def _isDELETE(self) -> bool:
        if deviceType == "DELETE":
            return True
        return False

    def _eject_device(self):
        self.device.disable_the_gadget()
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
            self.device_dict.fill_msc_dictionary_robot()
            self.msc_dict = self.device_dict.msc_dict
            img_name = self.msc_dict[deviceArg0]['img'].lower()
            mnt_path = self.msc_dict[deviceArg0]['mnt']
            msc_device = MSC(img_name, mnt_path, samba=0, watchdog=0)
            msc_device.enable_the_gadget()
            return

        elif self._isHID():
            self.device.usb_device = HID(self.device_desc, DeviceFunction.hid.value)

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
        
        elif self._isDELETE():
            fs_image = deviceArg0
            MSC.delete_img(fs_image)
            return

        else:
            sys.stderr.write(f"{Color.Red}{deviceType} is not supported!{Color.C_off}")
            return

        self.device.create_the_gadgets()
        self.device.create_the_configurations()
        self.device.create_the_functions()
        self.device.enable_the_gadget()

if __name__ == "__main__":
    device_operator = DeviceOperator()
    device_operator.operate_device()

