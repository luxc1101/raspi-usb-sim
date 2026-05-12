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
    def __init__(self, ncm_descriptor: DeviceDescriptors, ncm_function: str) -> None:
        self.ncm_root = self.USB_CONFIGFS_HOME
        self.ncm_function = ncm_function
        NCM.DESCRIPTOR = ncm_descriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        function_root = os.path.join(self.ncm_root, "g1/functions", self.ncm_function)
        os.system(f"sudo mkdir -p {function_root}") # add a function e.g. hid (Human Interface Device)
        os.system(f"sudo bash -c 'echo {NCM.DESCRIPTOR.DEV_ADDR} > {function_root}/dev_addr'") 
        os.system(f"sudo bash -c 'echo {NCM.DESCRIPTOR.HOST_ADDR} > {function_root}/host_addr'") 
        os.system(f"sudo bash -c 'echo {NCM.DESCRIPTOR.QUMLT} > {function_root}/qmult'")

        os.system(f"sudo ln -s {self.ncm_root}/g1/functions/{self.ncm_function} {self.ncm_root}/g1/configs/c.1") # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system(f"sudo bash -c 'echo {udcname} > {self.ncm_root}/g1/UDC'")
        os.system("sudo bash -c 'ifconfig usb0 10.0.0.1 netmask 255.255.255.252 up'")
        os.system("sudo bash -c 'route add -net default gw 10.0.0.2'")
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()