import subprocess

from .fscreator import MountTarget
from .stdout_writer import StdoutWriter


class SambaService():
    """Configure and manage a Samba share for a mounted filesystem image.

    Updates the share entry in ``smb.conf`` using the image name and mount
    path, and provides methods to start or stop the Samba service.

    Args:
        target: Image name and local mount path to expose through Samba.
    """
    config_file = "/etc/samba/smb.conf"

    def __init__(self, target: MountTarget):
        self.target = target

    def config_samba_service(self,):
        lineNr = subprocess.run("grep -n 'raspiusb' {} | cut -d: -f1".format(self.config_file), shell=True, capture_output=True, text=True, check=True).stdout.splitlines()[0]
        subprocess.run("sudo sed -i '{}s/.*/[raspiusb_{}]/' {}".format(lineNr, self._getfsname_without_extension(self.target.img_name), self.config_file), shell=True)
        subprocess.run("sudo sed -i '/mnt/d' {}".format(self.config_file), shell=True)
        subprocess.run("sudo sed -i -e '$a path = {}' {}".format(self.target.mnt_path, self.config_file), shell=True)

    def start_samba_service(self):
        subprocess.run("sudo systemctl restart smbd.service", shell=True)
        self._service_output()

    @staticmethod
    def stop_samba_service():
        subprocess.run('sudo systemctl stop smbd.service', shell=True)

    def _service_output(self):
        StdoutWriter.write("status of samba service-> \n")
        StdoutWriter.write("{}".format(subprocess.run("sudo systemctl status smbd.service | grep -E 'Loaded|Active|Status'", shell=True, capture_output=True, text=True).stdout))
        StdoutWriter.write("Network access: ")
        hostname = subprocess.run('hostname', shell=True, capture_output=True, text=True).stdout.splitlines()[0]
        host_ip = subprocess.run('hostname -I', shell=True, capture_output=True, text=True).stdout.splitlines()[0]
        StdoutWriter.write("Hostname and IP: {} {}\n".format(hostname, host_ip))
        subprocess.run('sudo chmod 777 {}'.format(self.target.mnt_path), shell=True)
        StdoutWriter.write("list file in {}: \n".format(self.target.mnt_path))
        subprocess.run(f"tree -L 3 {self.target.mnt_path}", shell=True)

    def _getfsname_without_extension(self, image_name: str) -> str:
        return image_name.split(".")[0]