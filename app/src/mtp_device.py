import os

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter

class MTP(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://github.com/viveris/uMTP-Responder/tree/master)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, mtp_descriptor: DeviceDescriptors, mtp_function: str) -> None:
        self.mtp_root = self.USB_CONFIGFS_HOME
        self.mtp_function = mtp_function
        MTP.DESCRIPTOR = mtp_descriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        function_root = os.path.join(self.mtp_root, "g1/functions", self.mtp_function)
        os.system(f"sudo mkdir -p {function_root}") # add a function e.g. hid (Human Interface Device)
        os.system(f"sudo ln -s {function_root} {self.mtp_root}/g1/configs/c.1") # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        os.system("sudo mkdir -p /dev/ffs-mtp")
        os.system("sudo mount -t functionfs mtp /dev/ffs-mtp")
        os.system("sudo umtprd &") # start the umtprd service
        os.system("sudo sleep 1") # wait for umtprd to start
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system(f"sudo bash -c 'echo {udcname} > {self.mtp_root}/g1/UDC'")
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()