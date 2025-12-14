import os
import sys
from ast import literal_eval

from src.acm_device import ACM
from src.device_data import DeviceDescriptors, DeviceFunction
from src.device_dictcreator import DeviceDictCreator
from src.ecm_device import ECM
from src.hid_device import HID
from src.msc_device import MSC
from src.rndis_device import RNDIS
from src.ncm_device import NCM
from src.usb_peripheral import USBPeripheral

paramdict = literal_eval(sys.argv[1])

class DeviceOperator():

    def __init__(self, parameter_dict):
        self.paramdict = parameter_dict
        self.simulator_action = str(self.paramdict["Cmd"])
        self.device_dict = DeviceDictCreator(os.path.join(os.getcwd(),"device_proj.json"))
        self.device_desc = DeviceDescriptors()
        self.device = USBPeripheral()

    
    def _isMSC(self) -> bool:
        if self.simulator_action.split(' ')[0] == "MSC":
            return True
        return False
    
    def _isHID(self) -> bool:
        if self.simulator_action.split(' ')[0] == "HID":
            str_PIDVID = self.simulator_action.split(' ')[1:]
            self.device_desc.idProduct = str_PIDVID[-1]
            self.device_desc.idVendor = str_PIDVID[-2]
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
        if self.simulator_action.split(' ')[0] == "RNDIS":
            str_PIDVID = self.simulator_action.split(' ')[1:]
            self.device_desc.idProduct = str_PIDVID[-1]
            self.device_desc.idVendor = str_PIDVID[-2]
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
        if self.simulator_action.split(' ')[0] == "ECM":
            str_PIDVID = self.simulator_action.split(' ')[1:]
            self.device_desc.idProduct = str_PIDVID[-1]
            self.device_desc.idVendor = str_PIDVID[-2]
            self.device_desc.bDeviceClass = 0xEF
            self.device_desc.bDeviceSubClass = 0x04
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated ECM device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False
    
    def _isAMC(self) -> bool:
        if self.simulator_action.split(' ')[0] == "CDC":
            str_PIDVID = self.simulator_action.split(' ')[1:]
            self.device_desc.idProduct = str_PIDVID[-1]
            self.device_desc.idVendor = str_PIDVID[-2]
            self.device_desc.bDeviceClass = 0x02
            self.device_desc.bDeviceSubClass = 0x00
            self.device_desc.bDeviceProtocol = 0x00
            self.device_desc.product = "Emulated CDC device"
            self.device_desc.bmAttributes = 0x80
            self.device_desc.CDC_PORT_NUM = 0
            return True
        return False
    
    def _isNCM(self) -> bool:
        if self.simulator_action.split(' ')[0] == "NCM":
            str_PIDVID = self.simulator_action.split(' ')[1:]
            self.device_desc.idProduct = str_PIDVID[-1]
            self.device_desc.idVendor = str_PIDVID[-2]
            self.device_desc.bDeviceClass = 0xEF
            self.device_desc.bDeviceSubClass = 0x02
            self.device_desc.bDeviceProtocol = 0x01
            self.device_desc.product = "Emulated NCM device"
            self.device_desc.bmAttributes = 0x80
            return True
        return False
    
    def _isEJECT(self) -> bool:
        if self.simulator_action == "EJECT":
            return True
        return False
    
    def _isDELETE(self) -> bool:
        if self.simulator_action.split(' ')[0] == "DELETE":
            return True
        return False
    
    def _isQUIT(self) -> bool:
        if self.simulator_action == "QUIT":
            return True
        return False
    
    def _isREMOUNT(self) -> bool:
        if self.simulator_action.split(' ')[0] == "REMOUNT":
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
        '''
        if self._isMSC():
            self.device_dict.fill_msc_dictionary()
            self.msc_dict = self.device_dict.msc_dict
            img_name = self.msc_dict[self.simulator_action.split("MSC ")[-1]]['img'].lower()
            mnt_path = self.msc_dict[self.simulator_action.split("MSC ")[-1]]['mnt']
            msc_device = MSC(img_name, 
                            mnt_path, 
                            samba=int(self.paramdict["Samba"]), 
                            watchdog=int(self.paramdict["WaDo"]))
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

        elif self._isEJECT():
            self._eject_device()
            return
        
        elif self._isREMOUNT():
            self.device_dict.fill_msc_dictionary()
            self.msc_dict = self.device_dict.msc_dict
            img_name = self.msc_dict[self.simulator_action.split("REMOUNT ")[-1]]['img'].lower()
            mnt_path = self.msc_dict[self.simulator_action.split("REMOUNT ")[-1]]['mnt']
            msc_device = MSC(img_name, 
                            mnt_path, 
                            samba=int(self.paramdict["Samba"]), 
                            watchdog=int(self.paramdict["WaDo"]))
            msc_device.remount_msc()
            return

        elif self._isDELETE():
            fs_image = self.simulator_action.split(' ')[-1]
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
    device_operator = DeviceOperator(paramdict)
    device_operator.operate_device()