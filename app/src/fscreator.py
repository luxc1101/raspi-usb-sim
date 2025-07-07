#!/usr/bin/python3
#*****************************************************
# Project:   Raspberrypi Zero USB filesystem simulator
# Autor:     Xiaochuan Lu
# Abteilung: SWTE
#*****************************************************
import os
import sys
from dataclasses import dataclass
from enum import Enum


@dataclass
class FilesystemImage(Enum):
    CD          = 'cd.img'
    USERCOM     = 'user_compliance.img'
    GEICOM      = 'gei_compliance.img'
    MIBCOM      = 'mib_compliance.img'
    NTFS        = 'ntfs.img'
    EXT2        = 'ext2.img'
    EXT3        = 'ext3.img'
    EXT4        = 'ext4.img'
    FAT16       = 'fat16.img'
    FAT32       = 'fat32.img'
    EXFAT       = 'exfat.img'
    HFSPLUS     = 'hfsplus.img'
    PARTITION   = 'part.img'
    BTRFS       = 'btrfs.img'
    FREE        = 'free.img'

@dataclass
class MountTarget:
    img_name: str
    mnt_path: str

class CmdExecutor():
    
    def execute_cmd(self, cmd:str) -> bool:
        result = os.system(cmd)
        return os.WEXITSTATUS(result) == 0
    
    def read_popen(self, cmd:str):
        return os.popen(cmd).read().strip()

class FSCreator():
    
    def __init__(self, img_name:str, mnt_path:str) -> None:
        self.mount_target = MountTarget(img_name=img_name.lower(), mnt_path=mnt_path)
        self.fs_img = FilesystemImage
        self.executor = CmdExecutor()

    def _create_disk_image(self) -> bool:
        sys.stdout.write("going to create filesystem and partitions this is " + self.mount_target.img_name.split(".")[0] + " the mountpoint at " + self.mount_target.mnt_path + "\n")
        self.size = input("To create {} with input size (MB), may take a few minutes\n".format(self.mount_target.img_name))
        sys.stdout.write("Creating......" + "\n")
        block_size = 2
        if self.executor.execute_cmd("sudo dd bs={}MB if=/dev/zero of=$HOME/{} count={} 2>&1".format(block_size, self.mount_target.img_name, round(int(self.size)/block_size))):
            return True
        return False

    def _create_ntfs(self, fs_label:str):
        self.executor.execute_cmd("sudo mkdir -p {}".format(self.mount_target.mnt_path))
        lpd = self.executor.read_popen("sudo losetup -f --show {}".format(self.mount_target.img_name))
        self.executor.execute_cmd("sudo mkfs.ntfs -p 0 -S 0 -H 0 -L {} -Q {}".format(fs_label, lpd))
        self.executor.execute_cmd("sudo ntfsfix {}".format(lpd))
        self.executor.execute_cmd("sudo mount {} {}".format(lpd, self.mount_target.mnt_path))

    def _create_fat(self, fat_size:int ,volume_name:str):
        self.executor.execute_cmd("sudo mkdir -p  {}".format(self.mount_target.mnt_path))
        self.executor.execute_cmd("sudo mkfs.fat -F {} -n {} {}".format(fat_size, volume_name, self.mount_target.img_name))

    def _create_exfat(self, volume_name:str):
        self.executor.execute_cmd("sudo mkdir -p {}".format(self.mount_target.mnt_path))
        self.executor.execute_cmd("sudo mkfs.exfat -n {} {}".format(volume_name, self.mount_target.img_name))

    def _create_hfsplus(self, volume_name:str):
        self.executor.execute_cmd("sudo mkdir -p {}".format(self.mount_target.mnt_path))
        self.executor.execute_cmd("sudo mkfs.hfsplus {} -v {}".format(self.mount_target.img_name, volume_name))

    def _create_ext(self, ext_type:str, fs_label:str):
        self.executor.execute_cmd("sudo mkdir -p {}".format(self.mount_target.mnt_path))
        self.executor.execute_cmd("sudo mkfs.{} -L {} {} 2>&1".format(ext_type, fs_label, self.mount_target.img_name))
        self.executor.execute_cmd("sudo tune2fs -c0 -i0 {}".format(self.mount_target.img_name))

    def _create_btrfs(self, fs_label:str):
        self.executor.execute_cmd("sudo mkdir -p {}".format(self.mount_target.mnt_path))
        self.executor.execute_cmd("sudo mkfs.btrfs -L {} {}".format(fs_label, self.mount_target.img_name))

    def _create_partitions(self):
        self.executor.execute_cmd("sudo mkdir -p /mnt/usb_part_ntfs")
        self.executor.execute_cmd("sudo mkdir -p /mnt/usb_part_fat32")
        self.executor.execute_cmd("sudo losetup -fP {}".format(self.mount_target.img_name))
        lpds = self.executor.read_popen("sudo losetup -a | grep 'part'")
        valid_lpds = [line for line in lpds.splitlines() if '(deleted)' not in line]
        if valid_lpds:
            lpd = valid_lpds[0].split(':')[0]
            self.executor.execute_cmd("(echo n; echo p; echo 1; echo ''; echo '+{}M'; echo n; echo p; echo 2; echo ''; echo ''; echo w) | sudo fdisk {}".format(int(self.size)//2, lpd))
            lpd += "p1"
            sys.stdout.write(f'loop device: {lpd}')
            sys.stdout.write('mkfs NTFS')
            self.executor.execute_cmd("sudo mkfs.ntfs -p 0 -S 0 -H 0 -L SIMPARNTFS -Q {}".format(lpd))
            self.executor.execute_cmd(f"sudo ntfsfix {lpd}")
            self.executor.execute_cmd("sudo mount -o rw,users,sync,nofail {} /mnt/usb_part_ntfs".format(lpd))
            lpd = lpd[:-2]
            lpd += "p2"
            sys.stdout.write(f'loop device: {lpd}')
            sys.stdout.write('mkfs FAT32')
            self.executor.execute_cmd("sudo mkfs.fat -F 32 -n SIMPARFAT32 {}".format(lpd)) #  the minimum size for a FAT32 volume is about 32.25M
            self.executor.execute_cmd("sudo mount -o rw,users,sync,nofail,umask=0000 {} /mnt/usb_part_fat32".format(lpd))
            sys.stdout.write("Info: " + "partitions have no remote access please add test file into each USB drive partition!")

    def create_filesystem(self) -> None:

        if self._create_disk_image():
            if self.mount_target.img_name==self.fs_img.MIBCOM.value:
                self._create_ntfs('SIMMIBNTFS')

            elif self.mount_target.img_name==self.fs_img.GEICOM.value:
                self._create_ntfs('SIMGEINTFS')

            elif self.mount_target.img_name==self.fs_img.USERCOM.value:
                self._create_ntfs('SIMUSERNTFS')

            elif self.mount_target.img_name==self.fs_img.EXT2.value:
                self._create_ext('ext2', 'SIMEXT2')

            elif self.mount_target.img_name==self.fs_img.EXT3.value:
                self._create_ext('ext3', 'SIMEXT3')

            elif self.mount_target.img_name==self.fs_img.EXT4.value:
                self._create_ext('ext4', 'SIMEXT4')

            elif self.mount_target.img_name==self.fs_img.BTRFS.value:
                self._create_btrfs('SIMBTRFS')

            elif self.mount_target.img_name==self.fs_img.FAT16.value:
                self._create_fat(16, 'SIMFAT16')

            elif self.mount_target.img_name==self.fs_img.FAT32.value:
                self._create_fat(32, 'SIMFAT32')

            elif self.mount_target.img_name==self.fs_img.EXFAT.value:
                self._create_exfat('SIMEXFAT')

            elif self.mount_target.img_name==self.fs_img.NTFS.value:
                self._create_ntfs('SIMNTFS')

            elif self.mount_target.img_name==self.fs_img.HFSPLUS.value:
                self._create_hfsplus('HFSPLUS')

            elif self.mount_target.img_name==self.fs_img.FREE.value:
                self._create_ntfs('FREE')

            elif self.mount_target.img_name==self.fs_img.PARTITION.value:
                self._create_partitions()

        else:
            sys.stderr.write("create disk image for {} failed".format(self.mount_target.img_name))