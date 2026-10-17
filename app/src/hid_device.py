import os
import time
import subprocess

from .a_device import ADevice
from .device_data import DeviceDescriptors, KeycodeDict
from .stdout_writer import StdoutWriter


class HID(ADevice):
    """Configure a USB HID keyboard gadget with optional text input.

    The HID report descriptor and settings are written to configfs. When
    enabled, the gadget binds to an available UDC; if input is enabled, mapped
    characters from ``input_string`` are sent through ``/dev/hidg0``.

    Args:
        hid_descriptor: USB and HID descriptor values for the gadget.
        hid_function: Configfs function name, such as ``hid.usb0``.
        enable: Set to 1 to type ``input_string`` after enabling, otherwise 0.
        input_string: Text to send when input is enabled.

    References:
        https://docs.kernel.org/usb/gadget_configfs.html
        https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-hid
    """
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
        subprocess.run(f"sudo mkdir -p {function_root}", shell=True) # add a function e.g. hid (Human Interface Device)
        self._write_sysfs(f'{function_root}/protocol', HID.DESCRIPTOR.HID_PROTOCOL) # set the HID protocol
        self._write_sysfs(f'{function_root}/subclass', HID.DESCRIPTOR.HID_SUBCLASS) # set the device subclass
        self._write_sysfs(f'{function_root}/report_length', HID.DESCRIPTOR.HID_REPORT_LENGTH) # set the byte length of HID reports
        subprocess.run(f"sudo bash -c 'cat {HID.DESCRIPTOR.HID_DESCRIPTOR} > {function_root}/report_desc'", shell=True) # write the binary blob of the report descriptor to report_desc; see HID class spec
        subprocess.run(f"sudo ln -s {function_root} {self.hid_root}/g1/configs/c.1", shell=True) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = subprocess.run('ls /sys/class/udc', shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0] # read udcname
        self._write_sysfs(f'{self.hid_root}/g1/UDC', udcname)
        subprocess.run("sudo chmod 777 /dev/hidg0", shell=True)
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