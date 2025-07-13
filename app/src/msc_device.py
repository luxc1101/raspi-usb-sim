import os
import sys
import time

from .a_device import ADevice
from .device_data import DeviceDescriptors
from .fscreator import FilesystemImage, FSCreator, MountTarget
from .samba_service import SambaService
from .watchdog_service import WatchdogService


class MSC(ADevice):
    def __init__(self, image_name: str, mnt_path: str, samba: int, watchdog: int):
        self.mount_target = MountTarget(img_name=image_name.lower(), mnt_path=mnt_path)
        self.samba = samba
        self.watchdog = watchdog
        self.dev_desc = DeviceDescriptors()
        self.dev_desc.serialnumber = os.popen("cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2").read().split("\n")[0]

    def create_the_configurations(self):
        if self._isSambaOn():
            samba_service = SambaService(self.mount_target)
            samba_service.config_samba_service()
            samba_service.start_samba_service()
        if self._isWatchdogOn():
            watchdog_service = WatchdogService(target=self.mount_target, file='/home/pi/usbtool_install/fswd.sh')
            watchdog_service.config_watchdog_service()
            watchdog_service.start_watchdog_service()

    def create_the_functions(self):
        if self.mount_target.img_name == FilesystemImage.FAT16.value:
            return self._mount_fat()
        elif self.mount_target.img_name == FilesystemImage.FAT32.value:
            return self._mount_fat()
        elif self.mount_target.img_name == FilesystemImage.EXFAT.value:
            return self._mount_fat()
        elif self.mount_target.img_name == FilesystemImage.MIBCOM.value:
            return self._mount_fat()
        elif self.mount_target.img_name == FilesystemImage.USERCOM.value:
            return self._mount_fat()
        elif self.mount_target.img_name == FilesystemImage.GEICOM.value:
            return self._mount_fat()
        elif self.mount_target.img_name == FilesystemImage.FREE.value:
            return self._mount_fat()
        elif self.mount_target.img_name == FilesystemImage.HFSPLUS.value:
            return self._mount_hfsplus()
        elif self.mount_target.img_name == FilesystemImage.PARTITION.value:
            loop_device = "lsblk -f | grep -E 'loop[0-9]p[12]|loop[0-9][0-9]p[12]'"
            if "p1" not in os.popen(loop_device).read():
                return self._mount_partitions()
            return sys.stdout.write("NTFS and FAT32 partitions already mounted\n")
        else:
            return self._mount_others()
    
    def create_the_gadgets(self):
        FSCreator(img_name=self.mount_target.img_name, mnt_path=self.mount_target.mnt_path).create_filesystem()
    
    def enable_the_gadget(self):
        if not self._isimgcreated():
            self.create_the_gadgets()
            return self.enable_the_gadget()
        self.disable_the_gadget()
        if not self._ismounted():
            sys.stdout.write("going to mount " + self.mount_target.img_name + "\n")
            self.create_the_functions()
        sys.stdout.write("Information about the mounted filesystem:\n") 
        sys.stdout.write("="*60 + "\n")
        self._output_info_of_mounted_fs()
        if self.mount_target.img_name != FilesystemImage.PARTITION.value:
            self.create_the_configurations()
        sys.stdout.write("="*60 + "\n")
        self._reinsert_msc()

    def disable_the_gadget(self):
        self._umount_msc()

    def remount_msc(self):
        SambaService.stop_samba_service()
        WatchdogService.stop_watchdog_service()
        sys.stdout.write("remount " + f'{self.mount_target.img_name}' + " filesystem\n")
        self.disable_the_gadget()
        self.create_the_functions()
        self.create_the_configurations()
        self._reinsert_msc()

    @staticmethod
    def eject_msc():
        os.system('sudo /sbin/modprobe g_mass_storage -r')
        SambaService.stop_samba_service()
        WatchdogService.stop_watchdog_service()
        sys.stdout.write("eject current mounted device\n")
    
    @staticmethod
    def delete_img(fs_img: str):
        SambaService.stop_samba_service()
        WatchdogService.stop_watchdog_service()
        os.system("sudo rm {}.img > error 2>&1".format(fs_img))
        lpds = os.popen("sudo lsblk -f | grep '/mnt/usb_{}'".format(fs_img)).read().strip().split("\n")
        if lpds:
                for lpd in lpds:
                    sys.stdout.write(lpd)
                    lpnum = lpd.split(' ')[0] # loop2
                    if fs_img == 'part':
                        lpnum = lpd.split(' ')[0][2:] # part is e.g. '|-loop2p1'
                    os.system("sudo umount /dev/{} > error 2>&1".format(lpnum))
                    mnt = lpd.split(' ')[-1]
                    os.system("sudo rm -r {} > error 2>&1".format(mnt))
                    os.system("sudo losetup -d /dev/{} > error 2>&1".format(lpnum)) # detach the backing store from the loop device
                    sys.stdout.write("delete {}.img -> umount {} -> remove {}\n".format(fs_img, lpnum, mnt))
                    sys.stdout.write("delete job finished!\n")
        else:
            sys.stdout.write(f'WARN: None of loop device with mount point /mnt/usb_{fs_img}')
    
    def _reinsert_msc(self):
        os.system('sudo /sbin/modprobe g_mass_storage -r')
        time.sleep(1.5)
        os.system('sudo /sbin/modprobe g_mass_storage file=./{} stall=0 removable=1 ro=0 iManufacturer="Raspi" iProduct="PiZeroMsc_{}" iSerialNumber="{}"'.format(self.mount_target.img_name, self.mount_target.img_name.split('.')[0], self.dev_desc.serialnumber))
        sys.stdout.write("mount job finished!\n")

    def _umount_msc(self):
        if self.mount_target.img_name == FilesystemImage.PARTITION.value:
            os.system("sudo umount /mnt/usb_part_ntfs > error 2>&1")
            os.system("sudo umount /mnt/usb_part_fat32 > error 2>&1")
        else:
            os.system("sudo umount {} > error 2>&1".format(self.mount_target.mnt_path))

    def _isSambaOn(self) -> bool:
        if self.samba == 2 and self.mount_target.img_name != FilesystemImage.PARTITION.value:
            return True
        return False
    
    def _isWatchdogOn(self) -> bool:
        if self.watchdog == 2 and self.mount_target.img_name != FilesystemImage.PARTITION.value:
            return True
        return False
    
    def _ismounted(self) -> bool:
         if os.path.ismount(self.mount_target.mnt_path):
            sys.stdout.write("{} already mounted\n".format(self.mount_target.mnt_path))
            return True
         return False
    
    def _isimgcreated(self) -> bool:
        if os.path.exists("/home/pi/{}".format(self.mount_target.img_name)):
            sys.stdout.write(f"{self.mount_target.img_name} already existed\n")
            return True
        return False
    
    def _output_info_of_mounted_fs(self) -> None:
        if self.mount_target.img_name == FilesystemImage.PARTITION.value:
            os.system("sudo lsblk -f | grep -E 'loop[0-9]p[12]|loop[0-9][0-9]p[12]'")
        else:
            os.system("findmnt | grep -i {} | while read MP SOURCE FS OP; do echo MountPoint:$MP Source:$SOURCE FStype:$FS Option:$OP; done".format(self.mount_target.mnt_path))
            os.system("lsblk --fs -o NAME,FSTYPE,FSAVAIL,FSUSE%,MOUNTPOINT | grep -i {} | while read NAME FS FSAVAIL FSUSE MP; do echo Name:$NAME FStype:$FS FSavaiable:$FSAVAIL FSused:$FSUSE MountPoint:$MP; done".format(self.mount_target.mnt_path))

    def _mount_others(self):
        '''
        ext2, ext3, ext4, btrfs, ntfs
        '''
        os.system('sudo mount -o rw,users,sync,nofail {} {}'.format(self.mount_target.img_name, self.mount_target.mnt_path))

    def _mount_fat(self):
        '''
        fat16, fat32, exfat, mibcom, usercom, geicom, free
        '''
        os.system('sudo mount -o rw,users,sync,nofail,umask=0000 {} {}'.format(self.mount_target.img_name, self.mount_target.mnt_path))

    def _mount_hfsplus(self):
        os.system("sudo fsck.hfsplus -f {} > error 2>&1".format(self.mount_target.img_name))
        self._mount_others()

    def _mount_partitions(self):
        os.system("sudo losetup -fP {}".format(self.mount_target.img_name))
        lpds = os.popen("sudo losetup -a | grep 'part'").read().strip()
        valid_lpds = [line for line in lpds.splitlines() if '(deleted)' not in line]
        if valid_lpds:
            lpd = valid_lpds[0].split(':')[0]
            lpd += "p1"
            sys.stdout.write(f'loop device: {lpd}')
            os.system(f"sudo ntfsfix {lpd}")
            os.system("sudo mount -o rw,users,sync,nofail {} /mnt/usb_part_ntfs".format(lpd))
            lpd = lpd[:-2]
            lpd += "p2"
            sys.stdout.write(f'loop device: {lpd}')
            os.system("sudo mount -o rw,users,sync,nofail,umask=0000 {} /mnt/usb_part_fat32".format(lpd))
        else:
            sys.stderr.write(f'valid loop device is empty')
