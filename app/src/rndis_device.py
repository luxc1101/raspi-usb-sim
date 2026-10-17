import os
import subprocess

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


class RNDIS(ADevice):
    """Configure a USB RNDIS gadget that provides a network interface.

    Creates and attaches the RNDIS configfs function using the descriptor's
    MAC addresses, queue multiplier, and RNDIS class settings. Enabling the
    gadget binds it to an available USB Device Controller (UDC).

    Args:
        rndis_descriptor: USB and RNDIS descriptor values for the gadget.
        rndis_function: Configfs function name, such as ``rndis.usb0``.

    References:
        https://docs.kernel.org/usb/gadget_configfs.html
        https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-rndis
    """
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
        subprocess.run(f"sudo mkdir -p {function_root}", shell=True) # add a function e.g. hid (Human Interface Device)
        self._write_sysfs(f'{function_root}/dev_addr', RNDIS.DESCRIPTOR.DEV_ADDR)
        self._write_sysfs(f'{function_root}/host_addr', RNDIS.DESCRIPTOR.HOST_ADDR)
        self._write_sysfs(f'{function_root}/qmult', RNDIS.DESCRIPTOR.QUMLT)
        self._write_sysfs(f'{function_root}/class', RNDIS.DESCRIPTOR.RNDIS_CLASS)
        self._write_sysfs(f'{function_root}/subclass', RNDIS.DESCRIPTOR.RNDIS_SUBCLASS)
        self._write_sysfs(f'{function_root}/protocol', RNDIS.DESCRIPTOR.RNDIS_PROTOCOL)

        subprocess.run(f"sudo ln -s {self.rndis_root}/g1/functions/{self.rndis_function} {self.rndis_root}/g1/configs/c.1", shell=True) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = subprocess.run('ls /sys/class/udc', shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0] # read udcname
        self._write_sysfs(f'{self.rndis_root}/g1/UDC', udcname)
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()