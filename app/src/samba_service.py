import os
import sys

from .fscreator import MountTarget
from .stdout_writer import StdoutWriter


class SambaService():
    '''
    configure samba service file smb.conf
    '''
    config_file = "/etc/samba/smb.conf"

    def __init__(self, target: MountTarget):
        self.target = target

    def config_samba_service(self,):
        lineNr = os.popen("grep -n 'raspiusb' {} | cut -d: -f1".format(self.config_file)).read().split("\n")[0]
        os.system("sudo sed -i '{}s/.*/[raspiusb_{}]/' {}".format(lineNr, self._getfsname_without_extension(self.target.img_name), self.config_file))
        os.system("sudo sed -i '/mnt/d' {}".format(self.config_file))
        os.system("sudo sed -i -e '$a path = {}' {}".format(self.target.mnt_path, self.config_file))

    def start_samba_service(self):
        os.system("sudo systemctl restart smbd.service")
        self._service_output()
    
    @staticmethod
    def stop_samba_service():
        os.system('sudo systemctl stop smbd.service') 

    def _service_output(self):
        StdoutWriter.write("status of samba service-> \n")
        StdoutWriter.write("{}".format(os.popen("sudo systemctl status smbd.service | grep -E 'Loaded|Active|Status'").read()))
        StdoutWriter.write("Network access: ")
        StdoutWriter.write("Hostname and IP: {} {}\n".format(os.popen('hostname').read().split("\n")[0], os.popen('hostname -I').read().split("\n")[0]))
        os.system('sudo chmod 777 {}'.format(self.target.mnt_path))
        StdoutWriter.write("list file in {}: \n".format(self.target.mnt_path))
        os.system(f"tree -L 3 {self.target.mnt_path}")

    def _getfsname_without_extension(self, image_name: str) -> str:
        return image_name.split(".")[0]