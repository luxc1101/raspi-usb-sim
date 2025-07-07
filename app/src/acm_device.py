import os

from .a_device import ADevice
from .device_data import DeviceDescriptors


class ACM(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-acm)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, acm_decsriptor: DeviceDescriptors, acm_function: str) -> None:
        self.acm_root = ADevice.USB_CONFIGFS_HOME
        self.acm_function = acm_function
        ACM.DESCRIPTOR = acm_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        os.system("sudo mkdir -p {}/g1/functions/{}".format(self.acm_root, self.acm_function)) # add a function e.g. hid (Human Interface Device)
        # os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/port_num'".format(ACM.DESCRIPTOR.CDC_PORT_NUM, self.acm_root, self.acm_function)) 
        os.system("sudo ln -s {}/g1/functions/{} {}/g1/configs/c.1".format(self.acm_root, self.acm_function, self.acm_root)) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system("sudo bash -c 'echo {} > {}/g1/UDC'".format(udcname, self.acm_root))
        os.system('sudo bash -c \'echo "Hello from Pi" > /dev/ttyGS0\'')
        os.system("sudo systemctl is-active --quiet getty@ttyGS0.service || sudo systemctl start getty@ttyGS0.service")        
        print("mount job finished!")

    def disable_the_gadget(self):
        return super().disable_the_gadget()