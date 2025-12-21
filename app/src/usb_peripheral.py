import os

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
        os.system('sudo systemctl is-active --quiet getty@ttyGS0.service > error 2>&1 && sudo systemctl stop getty@ttyGS0.service > error 2>&1')
        os.system('sudo bash -c "echo '' > /sys/kernel/config/usb_gadget/g1/UDC" > error 2>&1') # disabling the gadget
        os.system('func="$(ls /sys/kernel/config/usb_gadget/g1/functions/)" > error 2>&1 && sudo rm /sys/kernel/config/usb_gadget/g1/configs/c.1/$func > error 2>&1') # remove functions from configuration
        os.system('sudo rmdir /sys/kernel/config/usb_gadget/g1/configs/c.1/strings/0x409 > error 2>&1') # remove string dir in the configuration
        os.system('sudo rmdir /sys/kernel/config/usb_gadget/g1/configs/c.1 > error 2>&1') # remove the configurations
        os.system('func="$(ls /sys/kernel/config/usb_gadget/g1/functions/)" > error 2>&1 && sudo rmdir /sys/kernel/config/usb_gadget/g1/functions/$func > error 2>&1') # remove functions
        os.system('sudo rmdir /sys/kernel/config/usb_gadget/g1/strings/0x409 > error 2>&1') # remove string dir in gadget
        os.system('sudo rmdir /sys/kernel/config/usb_gadget/g1 > error 2>&1') # finally remove the while gadget
        os.system('sudo pkill umtprd > error 2>&1')
        os.system('sudo umount /dev/ffs-mtp > error 2>&1')
        