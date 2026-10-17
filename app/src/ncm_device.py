import os
import subprocess

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


class NCM(ADevice):
    """Configure a USB CDC-NCM gadget that provides an Ethernet interface.

    Creates and attaches the NCM configfs function using the descriptor's
    device and host MAC addresses and queue multiplier. Enabling the gadget
    binds it to an available UDC and configures ``usb0`` and its default route.

    Args:
        ncm_descriptor: USB and NCM descriptor values for the gadget.
        ncm_function: Configfs function name, such as ``ncm.usb0``.

    References:
        https://docs.kernel.org/usb/gadget_configfs.html
        https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-ncm
    """
    def __init__(self, ncm_descriptor: DeviceDescriptors, ncm_function: str) -> None:
        self.ncm_root = self.USB_CONFIGFS_HOME
        self.ncm_function = ncm_function
        NCM.DESCRIPTOR = ncm_descriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        function_root = os.path.join(self.ncm_root, "g1/functions", self.ncm_function)
        subprocess.run(f"sudo mkdir -p {function_root}", shell=True) # add a function e.g. hid (Human Interface Device)
        self._write_sysfs(f'{function_root}/dev_addr', NCM.DESCRIPTOR.DEV_ADDR)
        self._write_sysfs(f'{function_root}/host_addr', NCM.DESCRIPTOR.HOST_ADDR)
        self._write_sysfs(f'{function_root}/qmult', NCM.DESCRIPTOR.QUMLT)

        subprocess.run(f"sudo ln -s {self.ncm_root}/g1/functions/{self.ncm_function} {self.ncm_root}/g1/configs/c.1", shell=True) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = subprocess.run('ls /sys/class/udc', shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0] # read udcname
        self._write_sysfs(f'{self.ncm_root}/g1/UDC', udcname)
        subprocess.run("sudo bash -c 'ifconfig usb0 10.0.0.1 netmask 255.255.255.252 up'", shell=True)
        subprocess.run("sudo bash -c 'route add -net default gw 10.0.0.2'", shell=True)
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()