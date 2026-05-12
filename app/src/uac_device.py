import os

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


class UAC(ADevice):
    '''
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-uac2)
        
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
        function_root = os.path.join(self.uac_root, "g1/functions", self.uac_function)
        os.system(f"sudo mkdir -p {function_root}") # add a function e.g. UAC (USB Audio Class)
        # playback host --> pi
        os.system(f"sudo bash -c 'echo {UAC.DESCRIPTOR.P_CHMARK} > {function_root}/p_chmask'") # set the playback channel mask
        os.system(f"sudo bash -c 'echo {UAC.DESCRIPTOR.P_SRATE} > {function_root}/p_srate'") # set the playback sampling rate
        os.system(f"sudo bash -c 'echo {UAC.DESCRIPTOR.P_SSIZE} > {function_root}/p_ssize'") # set the playback sample size (bytes)
        # capture pi --> host
        os.system(f"sudo bash -c 'echo {UAC.DESCRIPTOR.C_CHMARK} > {function_root}/c_chmask'") # set the capture channel mask
        os.system(f"sudo bash -c 'echo {UAC.DESCRIPTOR.C_SRATE} > {function_root}/c_srate'") # set the capture sampling rate
        os.system(f"sudo bash -c 'echo {UAC.DESCRIPTOR.C_SSIZE} > {function_root}/c_ssize'") # set the capture sample size (bytes)
        
        os.system(f"sudo ln -s {function_root} {self.uac_root}/g1/configs/c.1") # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system(f"sudo bash -c 'echo {udcname} > {self.uac_root}/g1/UDC'")
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()