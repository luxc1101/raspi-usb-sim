import os
import subprocess

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


class ACM(ADevice):
    """Configure a USB CDC ACM gadget that exposes a virtual serial port.

    The gadget function is created under configfs and linked to configuration
    ``c.1``. Enabling it binds the gadget to an available UDC and starts the
    ``getty@ttyGS0`` service when needed.

    Args:
        acm_decsriptor: USB device descriptor values for the gadget.
        acm_function: Configfs function name, such as ``acm.usb0``.

    References:
        https://docs.kernel.org/usb/gadget_configfs.html
        https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-acm
    """
    def __init__(self, acm_decsriptor: DeviceDescriptors, acm_function: str) -> None:
        self.acm_root = self.USB_CONFIGFS_HOME
        self.acm_function = acm_function
        ACM.DESCRIPTOR = acm_decsriptor
        super().__init__()

    def create_the_gadgets(self):
        return super().create_the_gadgets()

    def create_the_configurations(self):
        return super().create_the_configurations()

    def create_the_functions(self):
        function_root = os.path.join(self.acm_root, "g1/functions", self.acm_function)
        subprocess.run(f"sudo mkdir -p {function_root}", shell=True) # add a function e.g. hid (Human Interface Device)
        subprocess.run(f"sudo ln -s {function_root} {self.acm_root}/g1/configs/c.1", shell=True) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = subprocess.run('ls /sys/class/udc', shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0] # read udcname
        self._write_sysfs(f'{self.acm_root}/g1/UDC', udcname)
        subprocess.run('sudo bash -c \'echo "Hello from Pi" > /dev/ttyGS0\'', shell=True)
        subprocess.run("sudo systemctl is-active --quiet getty@ttyGS0.service || sudo systemctl start getty@ttyGS0.service", shell=True)
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()