import os

from .a_device import ADevice
from .device_data import DeviceDescriptors


class RNDIS(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-rndis)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, rndis_decsriptor: DeviceDescriptors, rndis_function: str) -> None:
        self.rndis_root = ADevice.USB_CONFIGFS_HOME
        self.rndis_function = rndis_function
        RNDIS.DESCRIPTOR = rndis_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        os.system("sudo mkdir -p {}/g1/functions/{}".format(self.rndis_root, self.rndis_function)) # add a function e.g. hid (Human Interface Device)
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/dev_addr'".format(RNDIS.DESCRIPTOR.DEV_ADDR, self.rndis_root, self.rndis_function)) 
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/host_addr'".format(RNDIS.DESCRIPTOR.HOST_ADDR, self.rndis_root, self.rndis_function)) 
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/qmult'".format(RNDIS.DESCRIPTOR.QUMLT, self.rndis_root, self.rndis_function))
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/class'".format(RNDIS.DESCRIPTOR.RNDIS_CLASS, self.rndis_root, self.rndis_function))
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/subclass'".format(RNDIS.DESCRIPTOR.RNDIS_SUBCLASS, self.rndis_root, self.rndis_function))
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/protocol'".format(RNDIS.DESCRIPTOR.RNDIS_PORTOCAL, self.rndis_root, self.rndis_function))

        os.system("sudo ln -s {}/g1/functions/{} {}/g1/configs/c.1".format(self.rndis_root, self.rndis_function, self.rndis_root)) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system("sudo bash -c 'echo {} > {}/g1/UDC'".format(udcname, self.rndis_root))
        print("mount job finished!")

    def disable_the_gadget(self):
        return super().disable_the_gadget()