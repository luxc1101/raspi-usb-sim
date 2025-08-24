import os

from .a_device import ADevice
from .device_data import DeviceDescriptors


class ECM(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-ecm)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, ecm_decsriptor: DeviceDescriptors, ecm_function: str) -> None:
        self.ecm_root = self.USB_CONFIGFS_HOME
        self.ecm_function = ecm_function
        ECM.DESCRIPTOR = ecm_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        os.system("sudo mkdir -p {}/g1/functions/{}".format(self.ecm_root, self.ecm_function)) # add a function e.g. hid (Human Interface Device)
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/dev_addr'".format(ECM.DESCRIPTOR.DEV_ADDR, self.ecm_root, self.ecm_function)) 
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/host_addr'".format(ECM.DESCRIPTOR.HOST_ADDR, self.ecm_root, self.ecm_function)) 
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/qmult'".format(ECM.DESCRIPTOR.QUMLT, self.ecm_root, self.ecm_function))

        os.system("sudo ln -s {}/g1/functions/{} {}/g1/configs/c.1".format(self.ecm_root, self.ecm_function, self.ecm_root)) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system("sudo bash -c 'echo {} > {}/g1/UDC'".format(udcname, self.ecm_root))
        os.system("sudo bash -c 'ifconfig usb0 10.0.0.1 netmask 255.255.255.252 up'")
        os.system("sudo bash -c 'route add -net default gw 10.0.0.2'")
        print("mount job finished!")

    def disable_the_gadget(self):
        return super().disable_the_gadget()