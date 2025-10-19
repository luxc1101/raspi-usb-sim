import os
import sys

from .fscreator import MountTarget
from .stdout_writer import StdoutWriter

class WatchdogService():
    '''
    cofigure watchdog service
    '''
    def __init__(self, target: MountTarget, file: str):
        self.target = target
        self.watchdog_config_file = file

    def config_watchdog_service(self):
        cwd = os.getcwd()
        os.system('sudo sed -i "s|^Img=.*|Img={}/{}|" {}'.format(cwd, self.target.img_name, self.watchdog_config_file))
        os.system('sudo sed -i "s|^watchpath=.*|watchpath={}|" {}'.format(self.target.mnt_path, self.watchdog_config_file))

    def start_watchdog_service(self):
        os.system("sudo systemctl restart fswd")
        self._service_output()
    
    @staticmethod
    def stop_watchdog_service():
        os.system('sudo systemctl stop fswd')

    def _service_output(self):
        StdoutWriter.write("status of watchdog service-> \n")
        os.system("sudo systemctl status fswd | grep -E 'Loaded|Active|CGroup|python'")
        StdoutWriter.write(self.target.mnt_path + " is unter watching, action timeout is 5s\n")