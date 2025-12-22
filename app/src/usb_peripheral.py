import os
import subprocess
from .a_device import ADevice


class USBPeripheral(ADevice):

    def __init__(self, usb_device: ADevice = None) -> None:
        self.usb_device = usb_device
        self.usb_root = self.USB_CONFIGFS_HOME
        os.system('sudo modprobe libcomposite')
        super().__init__()

    def create_the_gadgets(self):
        os.system("sudo mkdir -p {}/g1".format(self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/idVendor'".format(self.usb_device.DESCRIPTOR.idVendor, self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/idProduct'".format(self.usb_device.DESCRIPTOR.idProduct, self.usb_root)) 
        os.system("sudo bash -c 'echo {} > {}/g1/bcdUSB'".format(self.usb_device.DESCRIPTOR.bcdUSB, self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/bcdDevice'".format(self.usb_device.DESCRIPTOR.bcdDevice, self.usb_root))     
        os.system("sudo bash -c 'echo {} > {}/g1/bDeviceClass'".format(self.usb_device.DESCRIPTOR.bDeviceClass, self.usb_root)) 
        os.system("sudo bash -c 'echo {} > {}/g1/bDeviceSubClass'".format(self.usb_device.DESCRIPTOR.bDeviceSubClass, self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/bDeviceProtocol'".format(self.usb_device.DESCRIPTOR.bDeviceProtocol, self.usb_root))
        os.system("sudo mkdir -p {}/g1/strings/0x409".format(self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/strings/0x409/serialnumber'".format(self.usb_device.DESCRIPTOR.serialnumber, self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/strings/0x409/manufacturer'".format(self.usb_device.DESCRIPTOR.manufacturer, self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/strings/0x409/product'".format(self.usb_device.DESCRIPTOR.product, self.usb_root))

    def create_the_configurations(self):
        os.system("sudo mkdir -p {}/g1/configs/c.1/strings/0x409".format(self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/configs/c.1/strings/0x409/configuration'".format(self.usb_device.DESCRIPTOR.configuration, self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/configs/c.1/MaxPower'".format(self.usb_device.DESCRIPTOR.MaxPower, self.usb_root))
        os.system("sudo bash -c 'echo {} > {}/g1/configs/c.1/bmAttributes'".format(self.usb_device.DESCRIPTOR.bmAttributes, self.usb_root))

    def create_the_functions(self):
        self.usb_device.create_the_functions()

    # mount the gadget
    def enable_the_gadget(self):
        self.usb_device.enable_the_gadget()
    
    @staticmethod
    def disable_the_gadget():
        subprocess.run('sudo systemctl is-active --quiet getty@ttyGS0.service && sudo systemctl stop getty@ttyGS0.service', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('sudo bash -c "echo '' > /sys/kernel/config/usb_gadget/g1/UDC"', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # disabling the gadget
        subprocess.run('func="$(ls /sys/kernel/config/usb_gadget/g1/functions/)" && sudo rm /sys/kernel/config/usb_gadget/g1/configs/c.1/$func ', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove functions from configuration
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove string dir in the configuration
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1/configs/c.1', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove the configurations
        subprocess.run('func="$(ls /sys/kernel/config/usb_gadget/g1/functions/)" && sudo rmdir /sys/kernel/config/usb_gadget/g1/functions/$func', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove functions
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1/strings/0x409', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # remove string dir in gadget
        subprocess.run('sudo rmdir /sys/kernel/config/usb_gadget/g1', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # finally remove the while gadget
        subprocess.run('sudo pkill umtprd', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run('sudo umount /dev/ffs-mtp', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        