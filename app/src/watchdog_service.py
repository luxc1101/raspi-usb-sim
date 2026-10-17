import os
import subprocess

from .fscreator import MountTarget
from .stdout_writer import StdoutWriter

class WatchdogService():
    """Configure and manage the filesystem watchdog service.

    Updates the ``fswd`` configuration with the image and mount paths, and
    provides methods to restart or stop the service.

    Args:
        target: Filesystem image and mount-point details to monitor.
        file: Path to the watchdog service configuration file.
    """
    def __init__(self, target: MountTarget, file: str):
        self.target = target
        self.watchdog_config_file = file

    def config_watchdog_service(self):
        cwd = os.getcwd()
        subprocess.run('sudo sed -i "s|^Img=.*|Img={}/{}|" {}'.format(cwd, self.target.img_name, self.watchdog_config_file), shell=True)
        subprocess.run('sudo sed -i "s|^watchpath=.*|watchpath={}|" {}'.format(self.target.mnt_path, self.watchdog_config_file), shell=True)

    def start_watchdog_service(self):
        subprocess.run("sudo systemctl restart fswd", shell=True)
        self._service_output()

    @staticmethod
    def stop_watchdog_service():
        subprocess.run('sudo systemctl stop fswd', shell=True)

    def _service_output(self):
        StdoutWriter.write("status of watchdog service-> \n")
        subprocess.run("sudo systemctl status fswd | grep -E 'Loaded|Active|CGroup|python'", shell=True)
        StdoutWriter.write(self.target.mnt_path + " is unter watching, action timeout is 5s\n")
