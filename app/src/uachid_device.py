import os

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter
from .uac_device import UAC
from .hid_device import HID

class UACHID(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions UAC](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-uac2)

    + [Gadgets functions HID](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-hid)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, uachid_descriptor: DeviceDescriptors, uac_function: str, hid_function: str) -> None:
        self.uachid_root = self.USB_CONFIGFS_HOME
        self.uac_function = uac_function
        self.hid_function = hid_function
        UACHID.DESCRIPTOR = uachid_descriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    
    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        #-----------------------
        # UAC
        # Interface Class = 01h
        #-----------------------
        self.uac_device = UAC(UACHID.DESCRIPTOR, self.uac_function)
        self.uac_device.create_the_functions()
        #-----------------------
        # HID
        # Interface Class = 03h
        #-----------------------
        self.hid_device = HID(UACHID.DESCRIPTOR, self.hid_function, 0, "")
        self.hid_device.create_the_functions()

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system(f"sudo bash -c 'echo {udcname} > {self.uachid_root}/g1/UDC'")
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()