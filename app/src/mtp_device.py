import os
import subprocess

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter

class MTP(ADevice):
    """Configure a USB MTP gadget using FunctionFS and uMTP Responder.

    Creates and attaches the MTP configfs function. Enabling the gadget mounts
    FunctionFS, starts ``umtprd``, and binds the gadget to an available UDC.

    Args:
        mtp_descriptor: USB device descriptor values for the gadget.
        mtp_function: Configfs function name, typically ``ffs.mtp``.

    References:
        https://docs.kernel.org/usb/gadget_configfs.html
        https://github.com/viveris/uMTP-Responder
    """
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
        subprocess.run(f"sudo mkdir -p {function_root}", shell=True) # add a function e.g. hid (Human Interface Device)
        subprocess.run(f"sudo ln -s {function_root} {self.mtp_root}/g1/configs/c.1", shell=True) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        subprocess.run("sudo mkdir -p /dev/ffs-mtp", shell=True)
        subprocess.run("sudo mount -t functionfs mtp /dev/ffs-mtp", shell=True)
        subprocess.run("sudo umtprd &", shell=True) # start the umtprd service
        subprocess.run("sudo sleep 1", shell=True) # wait for umtprd to start
        udcname = subprocess.run('ls /sys/class/udc', shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0] # read udcname
        subprocess.run(f"sudo bash -c 'echo {udcname} > {self.mtp_root}/g1/UDC'", shell=True)
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()