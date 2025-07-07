from abc import ABC, abstractmethod

from .device_data import DeviceDescriptors


class ADevice(ABC):
    '''
    An abstract class for usb device creating
    '''
    CONFIGFS_HOME = "/sys/kernel/config"
    USB_CONFIGFS_HOME = f"{CONFIGFS_HOME}/usb_gadget"
    DESCRIPTOR = DeviceDescriptors

    @abstractmethod
    def create_the_gadgets(self):
        pass

    @abstractmethod
    def create_the_configurations(self):
        pass

    @abstractmethod
    def create_the_functions(self):
        pass

    @abstractmethod
    def enable_the_gadget(self):
        pass

    @abstractmethod
    def disable_the_gadget(self):
        pass
    
    is_configfs_mounted: bool
    is_dwc2_in_devicetree: bool
    is_dwc2_in_modules: bool
    is_libcomposite_in_modules: bool