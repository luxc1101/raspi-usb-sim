import os

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


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
    def __init__(self, rndis_descriptor: DeviceDescriptors, rndis_function: str) -> None:
        self.rndis_root = self.USB_CONFIGFS_HOME
        self.rndis_function = rndis_function
        RNDIS.DESCRIPTOR = rndis_descriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        function_root = os.path.join(self.rndis_root, "g1/functions", self.rndis_function)
        os.system(f"sudo mkdir -p {function_root}") # add a function e.g. hid (Human Interface Device)
        os.system(f"sudo bash -c 'echo {RNDIS.DESCRIPTOR.DEV_ADDR} > {function_root}/dev_addr'") 
        os.system(f"sudo bash -c 'echo {RNDIS.DESCRIPTOR.HOST_ADDR} > {function_root}/host_addr'") 
        os.system(f"sudo bash -c 'echo {RNDIS.DESCRIPTOR.QUMLT} > {function_root}/qmult'")
        os.system(f"sudo bash -c 'echo {RNDIS.DESCRIPTOR.RNDIS_CLASS} > {function_root}/class'")
        os.system(f"sudo bash -c 'echo {RNDIS.DESCRIPTOR.RNDIS_SUBCLASS} > {function_root}/subclass'")
        os.system(f"sudo bash -c 'echo {RNDIS.DESCRIPTOR.RNDIS_PORTOCAL} > {function_root}/protocol'")

        os.system(f"sudo ln -s {self.rndis_root}/g1/functions/{self.rndis_function} {self.rndis_root}/g1/configs/c.1") # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system(f"sudo bash -c 'echo {udcname} > {self.rndis_root}/g1/UDC'")
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()