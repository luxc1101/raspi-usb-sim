import os

from .a_device import ADevice
from .device_data import DeviceDescriptors


class HID(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-hid)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, hid_decsriptor: DeviceDescriptors, hid_function: str) -> None:
        self.hid_root = self.USB_CONFIGFS_HOME
        self.hid_function = hid_function
        HID.DESCRIPTOR = hid_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        os.system("sudo mkdir -p {}/g1/functions/{}".format(self.hid_root, self.hid_function)) # add a function e.g. hid (Human Interface Device)
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/protocol'".format(HID.DESCRIPTOR.HID_PROTOCAL, self.hid_root, self.hid_function)) # set the HID protocol
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/subclass'".format(HID.DESCRIPTOR.HID_SUBCLASS, self.hid_root, self.hid_function)) # set the device subclass
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/report_length'".format(HID.DESCRIPTOR.HID_REPORT_LENGTH, self.hid_root, self.hid_function)) # set the byte length of HID reports
        os.system("sudo bash -c 'cat {} > {}/g1/functions/{}/report_desc'".format(HID.DESCRIPTOR.HID_DESCRIPTOR, self.hid_root, self.hid_function)) # write the binary blob of the report descriptor to report_desc; see HID class spec
        os.system("sudo ln -s {}/g1/functions/{} {}/g1/configs/c.1".format(self.hid_root, self.hid_function, self.hid_root)) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system("sudo bash -c 'echo {} > {}/g1/UDC'".format(udcname, self.hid_root))
        print("mount job finished!")

    def disable_the_gadget(self):
        return super().disable_the_gadget()