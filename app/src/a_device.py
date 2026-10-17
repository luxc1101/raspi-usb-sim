from abc import ABC, abstractmethod
import subprocess

from .device_data import DeviceDescriptors


class ADevice(ABC):
    """Define the interface and shared configfs utilities for USB gadgets.

    Subclasses implement gadget creation, configuration, function setup,
    enabling, and disabling for a specific USB device type.

    Attributes:
        CONFIGFS_HOME: Root directory for the configfs mount.
        USB_CONFIGFS_HOME: Directory containing USB gadget configurations.
        DESCRIPTOR: Device descriptor values used to configure the gadget.
    """
    CONFIGFS_HOME = "/sys/kernel/config"
    USB_CONFIGFS_HOME = f"{CONFIGFS_HOME}/usb_gadget"
    DESCRIPTOR: DeviceDescriptors = DeviceDescriptors()

    @staticmethod
    def _write_sysfs(path, value):
        """Write a value to a configfs or sysfs attribute using sudo."""
        subprocess.run(f"sudo bash -c 'echo {value} > {path}'", shell=True)

    @abstractmethod
    def create_the_gadgets(self):
        """Create the gadget and write its device descriptor attributes."""
        pass

    @abstractmethod
    def create_the_configurations(self):
        """Create the gadget's configuration and write its attributes."""
        pass

    @abstractmethod
    def create_the_functions(self):
        """Create and attach the device-specific USB functions."""
        pass

    @abstractmethod
    def enable_the_gadget(self):
        """Enable or mount the configured USB gadget."""
        pass

    @abstractmethod
    def disable_the_gadget(self):
        """Disable the gadget and release its associated resources."""
        pass
    
    is_configfs_mounted: bool
    is_dwc2_in_devicetree: bool
    is_dwc2_in_modules: bool
    is_libcomposite_in_modules: bool