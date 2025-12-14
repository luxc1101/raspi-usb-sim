import os

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


class NCM(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-ncm)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, ncm_decsriptor: DeviceDescriptors, ncm_function: str) -> None:
        self.ncm_root = self.USB_CONFIGFS_HOME
        self.ncm_function = ncm_function
        NCM.DESCRIPTOR = ncm_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        os.system("sudo mkdir -p {}/g1/functions/{}".format(self.ncm_root, self.ncm_function)) # add a function e.g. hid (Human Interface Device)
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/dev_addr'".format(NCM.DESCRIPTOR.DEV_ADDR, self.ncm_root, self.ncm_function)) 
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/host_addr'".format(NCM.DESCRIPTOR.HOST_ADDR, self.ncm_root, self.ncm_function)) 
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/qmult'".format(NCM.DESCRIPTOR.QUMLT, self.ncm_root, self.ncm_function))

        os.system("sudo ln -s {}/g1/functions/{} {}/g1/configs/c.1".format(self.ncm_root, self.ncm_function, self.ncm_root)) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system("sudo bash -c 'echo {} > {}/g1/UDC'".format(udcname, self.ncm_root))
        os.system("sudo bash -c 'ifconfig usb0 10.0.0.1 netmask 255.255.255.252 up'")
        os.system("sudo bash -c 'route add -net default gw 10.0.0.2'")
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()