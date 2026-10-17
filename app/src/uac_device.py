import os
import subprocess

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .stdout_writer import StdoutWriter


class UAC(ADevice):
    """Configure a USB Audio Class 2 gadget for playback and capture.

    Sets the channel mask, sample rate, and sample size for playback from the
    host to the device and capture from the device to the host, then binds the
    gadget to an available USB Device Controller (UDC).

    Args:
        uac_decsriptor: USB and audio descriptor values for the gadget.
        uac_function: Configfs function name, such as ``uac2.usb0``.

    References:
        https://docs.kernel.org/usb/gadget_configfs.html
        https://www.kernel.org/doc/Documentation/ABI/testing/configfs-usb-gadget-uac2
    """
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
        subprocess.run(f"sudo mkdir -p {function_root}", shell=True) # add a function e.g. UAC (USB Audio Class)
        # playback host --> pi
        self._write_sysfs(f'{function_root}/p_chmask', UAC.DESCRIPTOR.P_CHMARK) # set the playback channel mask
        self._write_sysfs(f'{function_root}/p_srate', UAC.DESCRIPTOR.P_SRATE) # set the playback sampling rate
        self._write_sysfs(f'{function_root}/p_ssize', UAC.DESCRIPTOR.P_SSIZE) # set the playback sample size (bytes)
        # capture pi --> host
        self._write_sysfs(f'{function_root}/c_chmask', UAC.DESCRIPTOR.C_CHMARK) # set the capture channel mask
        self._write_sysfs(f'{function_root}/c_srate', UAC.DESCRIPTOR.C_SRATE) # set the capture sampling rate
        self._write_sysfs(f'{function_root}/c_ssize', UAC.DESCRIPTOR.C_SSIZE) # set the capture sample size (bytes)

        subprocess.run(f"sudo ln -s {function_root} {self.uac_root}/g1/configs/c.1", shell=True) # put the function into the configuration by creating a symlink

    # mount the gadget
    def enable_the_gadget(self):
        udcname = subprocess.run('ls /sys/class/udc', shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0] # read udcname
        self._write_sysfs(f'{self.uac_root}/g1/UDC', udcname)
        StdoutWriter.write("mount job finished!\n")

    def disable_the_gadget(self):
        return super().disable_the_gadget()