import os
import time

from .a_device import ADevice
from .device_data import DeviceDescriptors, KeycodeDict
from .stdout_writer import StdoutWriter


class HID(ADevice):
    '''
    HID Keyboard
    ### Reference
    + [How to config gadget](https://docs.kernel.org/usb/gadget_configfs.html)

    + [Gadgets functions](https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-hid)
        
        - Gadgets functions depends on Kernel version
        
        - How to check kernel version:

            ```
            uname -r
            ```
    '''
    def __init__(self, hid_descriptor: DeviceDescriptors, hid_function: str, enable: int, input_string: str) -> None:
        self.hid_root = self.USB_CONFIGFS_HOME
        self.hid_function = hid_function
        self.input_enabled = enable
        self.input_string = input_string
        HID.DESCRIPTOR = hid_descriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()
    

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        function_root = os.path.join(self.hid_root, "g1/functions", self.hid_function)
        os.system(f"sudo mkdir -p {function_root}") # add a function e.g. hid (Human Interface Device)
        os.system(f"sudo bash -c 'echo {HID.DESCRIPTOR.HID_PROTOCAL} > {function_root}/protocol'") # set the HID protocol
        os.system(f"sudo bash -c 'echo {HID.DESCRIPTOR.HID_SUBCLASS} > {function_root}/subclass'") # set the device subclass
        os.system(f"sudo bash -c 'echo {HID.DESCRIPTOR.HID_REPORT_LENGTH} > {function_root}/report_length'") # set the byte length of HID reports
        os.system(f"sudo bash -c 'cat {HID.DESCRIPTOR.HID_DESCRIPTOR} > {function_root}/report_desc'") # write the binary blob of the report descriptor to report_desc; see HID class spec
        os.system(f"sudo ln -s {function_root} {self.hid_root}/g1/configs/c.1") # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = os.popen("ls /sys/class/udc").read().split("\n")[0] # read udcname
        os.system(f"sudo bash -c 'echo {udcname} > {self.hid_root}/g1/UDC'")
        os.system("sudo chmod 777 /dev/hidg0")  
        StdoutWriter.write("mount job finished!\n")
        if self.input_enabled==1:
            StdoutWriter.write(f"typing '{self.input_string}'\n")
            self.type_string()

    def disable_the_gadget(self):
        return super().disable_the_gadget()
    
    def type_string(self):
        '''
        Type a string by writing HID reports to /dev/hidg0 using keycodedict
        '''
        NULL = b'\x00'
        with open("/dev/hidg0", "wb") as char_device:
            time.sleep(1)
            for char in self.input_string:
                keycode = KeycodeDict.keycode_dict.get(char.lower())
                if keycode:
                    char_device.write(NULL*2 + keycode + NULL*5)  # press
                    char_device.write(NULL*8)                    # release