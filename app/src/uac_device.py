import os

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


class UAC(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-uac1)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, uac_decsriptor: DeviceDescriptors, uac_function: str) -> None:
        self.uac_root = self.USB_CONFIGFS_HOME
        self.uac_function = uac_function
        UAC.DESCRIPTOR = uac_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        os.system("sudo mkdir -p {}/g1/functions/{}".format(self.uac_root, self.uac_function)) # add a function e.g. UAC (USB Audio Class)
        # playback host --> pi
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/p_chmask'".format(UAC.DESCRIPTOR.P_CHMARK, self.uac_root, self.uac_function)) # set the playback channel mask
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/p_srate'".format(UAC.DESCRIPTOR.P_SRATE, self.uac_root, self.uac_function)) # set the playback sampling rate
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/p_ssize'".format(UAC.DESCRIPTOR.P_SSIZE, self.uac_root, self.uac_function)) # set the playback sample size (bytes)
        # capture pi --> host
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/c_chmask'".format(UAC.DESCRIPTOR.C_CHMARK, self.uac_root, self.uac_function)) # set the capture channel mask
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/c_srate'".format(UAC.DESCRIPTOR.C_SRATE, self.uac_root, self.uac_function)) # set the capture sampling rate
        os.system("sudo bash -c 'echo {} > {}/g1/functions/{}/c_ssize'".format(UAC.DESCRIPTOR.C_SSIZE, self.uac_root, self.uac_function)) # set the capture sample size (bytes)
        
        os.system("sudo ln -s {}/g1/functions/{} {}/g1/configs/c.1".format(self.uac_root, self.uac_function, self.uac_root)) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system("sudo bash -c 'echo {} > {}/g1/UDC'".format(udcname, self.uac_root))
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()