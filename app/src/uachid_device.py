import subprocess

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter
from .uac_device import UAC
from .hid_device import HID

class UACHID(ADevice):
    """Configure a composite USB gadget with UAC2 audio and HID functions.

    Creates both functions under the gadget's configfs configuration and
    binds the composite gadget to an available UDC.

    Args:
        uachid_descriptor: Shared USB, audio, and HID descriptor values.
        uac_function: Configfs function name for the UAC2 audio interface.
        hid_function: Configfs function name for the HID interface.

    References:
        https://docs.kernel.org/usb/gadget_configfs.html
        https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-uac2
        https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-hid
    """
    def __init__(self, uachid_descriptor: DeviceDescriptors, uac_function: str, hid_function: str) -> None:
        self.uachid_root = self.USB_CONFIGFS_HOME
        self.uac_function = uac_function
        self.hid_function = hid_function
        UACHID.DESCRIPTOR = uachid_descriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        #-----------------------
        # UAC
        # Interface Class = 01h
        #-----------------------
        self.uac_device = UAC(UACHID.DESCRIPTOR, self.uac_function)
        self.uac_device.create_the_functions()
        #-----------------------
        # HID
        # Interface Class = 03h
        #-----------------------
        self.hid_device = HID(UACHID.DESCRIPTOR, self.hid_function, 0, "")
        self.hid_device.create_the_functions()

    # mount the gadget
    def enable_the_gadget(self):
        udcname = subprocess.run('ls /sys/class/udc', shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0] # read udcname
        self._write_sysfs(f'{self.uachid_root}/g1/UDC', udcname)
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()