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
    def __init__(self, mtp_decsriptor: DeviceDescriptors, mtp_function: str) -> None:
        self.mtp_root = self.USB_CONFIGFS_HOME
        self.mtp_function = mtp_function
        MTP.DESCRIPTOR = mtp_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        os.system("sudo mkdir -p {}/g1/functions/{}".format(self.mtp_root, self.mtp_function)) # add a function e.g. hid (Human Interface Device)
        os.system("sudo ln -s {}/g1/functions/{} {}/g1/configs/c.1".format(self.mtp_root, self.mtp_function, self.mtp_root)) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        os.system("sudo mkdir -p /dev/ffs-mtp")
        os.system("sudo mount -t functionfs mtp /dev/ffs-mtp")
        os.system("sudo umtprd &") # start the umtprd service
        os.system("sudo sleep 1") # wait for umtprd to start
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system("sudo bash -c 'echo {} > {}/g1/UDC'".format(udcname, self.mtp_root))
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()