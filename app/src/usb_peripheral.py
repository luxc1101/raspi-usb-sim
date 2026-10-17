import subprocess
from .a_device import ADevice


class USBPeripheral(ADevice):
    """Manage shared configfs setup for a selected USB gadget function.

    Loads the ``libcomposite`` module, writes device and configuration
    descriptors, and delegates function setup and enabling to ``usb_device``.
    The wrapped device can be passed at construction or assigned before setup.
    The static teardown method removes the shared gadget configuration.

    Args:
        usb_device: Device-specific ``ADevice`` implementation, or ``None``
            when it will be assigned later.
    """

    def __init__(self, usb_device: ADevice = None) -> None:
        self.usb_device = usb_device
        self.usb_root = self.USB_CONFIGFS_HOME
        subprocess.run('sudo modprobe libcomposite', shell=True)
        super().__init__()

    def create_the_gadgets(self):
        '''
        create the gadget and write the device descriptors
        '''
        subprocess.run('sudo mkdir -p {}/g1'.format(self.usb_root), shell=True)
        self._write_sysfs('{}/g1/idVendor'.format(self.usb_root), self.usb_device.DESCRIPTOR.idVendor)
        self._write_sysfs('{}/g1/idProduct'.format(self.usb_root), self.usb_device.DESCRIPTOR.idProduct)
        self._write_sysfs('{}/g1/bcdUSB'.format(self.usb_root), self.usb_device.DESCRIPTOR.bcdUSB)
        self._write_sysfs('{}/g1/bcdDevice'.format(self.usb_root), self.usb_device.DESCRIPTOR.bcdDevice)
        self._write_sysfs('{}/g1/bDeviceClass'.format(self.usb_root), self.usb_device.DESCRIPTOR.bDeviceClass)
        self._write_sysfs('{}/g1/bDeviceSubClass'.format(self.usb_root), self.usb_device.DESCRIPTOR.bDeviceSubClass)
        self._write_sysfs('{}/g1/bDeviceProtocol'.format(self.usb_root), self.usb_device.DESCRIPTOR.bDeviceProtocol)
        subprocess.run('sudo mkdir -p {}/g1/strings/0x409'.format(self.usb_root), shell=True)
        self._write_sysfs('{}/g1/strings/0x409/serialnumber'.format(self.usb_root), self.usb_device.DESCRIPTOR.serialnumber)
        self._write_sysfs('{}/g1/strings/0x409/manufacturer'.format(self.usb_root), self.usb_device.DESCRIPTOR.manufacturer)
        self._write_sysfs('{}/g1/strings/0x409/product'.format(self.usb_root), self.usb_device.DESCRIPTOR.product)

    def create_the_configurations(self):
        '''
        create the configuration and write the configuration descriptors
        '''
        subprocess.run('sudo mkdir -p {}/g1/configs/c.1/strings/0x409'.format(self.usb_root), shell=True)
        self._write_sysfs('{}/g1/configs/c.1/strings/0x409/configuration'.format(self.usb_root), self.usb_device.DESCRIPTOR.configuration)
        self._write_sysfs('{}/g1/configs/c.1/MaxPower'.format(self.usb_root), self.usb_device.DESCRIPTOR.MaxPower)
        self._write_sysfs('{}/g1/configs/c.1/bmAttributes'.format(self.usb_root), self.usb_device.DESCRIPTOR.bmAttributes)

    def create_the_functions(self):
        '''
        create the functions for the gadget
        '''
        self.usb_device.create_the_functions()

    # mount the gadget
    def enable_the_gadget(self):
        '''
        mount the gadget by writing the udc name to UDC file
        '''
        self.usb_device.enable_the_gadget()

    @staticmethod
    def disable_the_gadget():
        '''
        disable the gadget by stopping the getty service, unmounting the gadget, and removing the gadget configuration
        '''
        subprocess.run('sudo systemctl is-active --quiet getty@ttyGS0.service && sudo systemctl stop getty@ttyGS0.service', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('sudo bash -c "echo '' > /sys/kernel/config/usb_gadget/g1/UDC"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # disabling the gadget
        subprocess.run('func="$(ls /sys/kernel/config/usb_gadget/g1/functions/)"; for f in $func; do sudo rm /sys/kernel/config/usb_gadget/g1/configs/c.1/$f; done', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove functions from configuration
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove string dir in the configuration
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1/configs/c.1', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove the configurations
        subprocess.run('func="$(ls /sys/kernel/config/usb_gadget/g1/functions/)"; for f in $func; do sudo rmdir /sys/kernel/config/usb_gadget/g1/functions/$f; done', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove functions
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1/strings/0x409', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove string dir in gadget
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # finally remove the while gadget
        subprocess.run('sudo pkill umtprd', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('sudo umount /dev/ffs-mtp', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
