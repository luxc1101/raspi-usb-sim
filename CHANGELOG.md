#### version 1.0.1
-  `feat`: Config.py can automatically grep the path of `USERPROFILE` (e.g. `C:/Users/wrk_TestRadio/`), the log path should be `%USERPROFILE%/Desktop/putty.log` as default

#### version 1.0.2
-  `feat`: Config.py add a wireless network profile to computer, useful for pre-configuring network settings or automating network connections without manually entering the SSID and password
- `fix`: potential dependency conflict downgrade `PyQt5==5.15.9`, `PyQt5-sip==12.12.2`, add `pyqt5-tools==5.15.9.3.3` in `requirements.txt`
- `fix`: correct app version showing no GUI
- `docs`: adjust README.md
- `docs`: add `readme.txt` in `dist` folder
- `refactor`: pipeline add global var `WIFI_CONFIG`, put folder `wifi_config` into `dist` folder
- `refactor`: pipeline use [`venv`](https://packaging.python.org/en/latest/tutorials/installing-packages/#creating-and-using-virtual-environments]) by default in Python 3.3 and later

#### version 1.0.3
- `refactor`: pipeline copy `fswd.sh` into `dist` folder
- `refactor`: Putty ssh login, input username and password in oneline
- `fix`: putty security alert hinders putty setup
- `fix`: wifi autoconnection sometimes failed
- `fix`: UI scaling issue with windows different scaling from 100% to 200%
- `docs`: Wifi ssid and password will not be stored in repository
- `feat`: putty session window will be minimized 

#### version 1.0.4  
- `fix`: general issue: using the tool as a remote mimicking a user typing into putty, new version uses PyPi paramiko [SSHClient](https://docs.paramiko.org/en/latest/api/client.html) instead of Putty
- `fix` mount partitions sometimes failed
- `fix` delete partitions image failed
- `fix` NTFS filesystem sector warning
- `docs`: update README.me for new version
- `feat`: cancel Configuration dialog
- `feat`: create SSH Connection Dialog
- `feat`: add free partition in Filesystem Tab filesystem Combox 

#### version 1.0.5
- `fix`: command prompt pop up after running application
- `fix`: ssh connection with wrong 'gear' icon
- `fix` delect action with text 'Delete Img', could lead to lack of understanding
- `feat`: ssid combobox updates visiable ssid from local machine dynamically
- `feat`: click Action 'Delete Filesystem' needs a extra confirmation by clicking OK on a popup dialog

#### version 1.0.6
- `feat`: `Quit` action will close the current window, if click OK in pop up dialog
- `feat`: `SSH Connect` and `SSH Disconnect` works as one action
- `fix`: `Delete filesystem` activate at wrong tab
- `fix`: `Connect` button after SSH Connetion does not save input parameter

#### version 1.0.7
- `feat`: `SSH Connect` and `SSH Disconnect` works as two action (two buttons)
- `feat`: Shift `checkboxes` watchdog and samba service to `MSC Tab` and rename Watchdog as **Auto Remount**, Samba Service as **Shared Folder**
- `feat`: Remove `Quit` action from actionbar, the `Quit` is integrated into `closeEvent` which will be triggered when the application is closed
- `feat`: Remove `Delete Filesystem` action from actionbar. The `Delete Filesystem` is integrated into `MSC Tab` as a Tool Button
- `feat`: Remove `Remote Folder` action from actionbar. The `Remote Folder` is integrated into `MSC Tab` as a Tool Button
- `feat`: Shared Folder button opens the explorer
- `feat`: `Command Window` and `Trace` work as one component before they are splited as two
- `feat`: `Statusbar` with LED indicator working as SSHClient heartbeat
- `feat`: `Status` in `MSC Tab` with LED indicator showing the filesystem exixtance
- `feat`: Cursor over widgets to display tooltips
- `feat`: Create `Tab Ethernet Adapter` (`Tab ECM`)
- `feat`: Create `Tab Human Interface Device` (`Tab HID`)
- `feat`: Create `Tab Communication Device Class` (`Tab CDC`)
- `feat`: Create `Tab Mass Storage Class` (`Tab MSC`)
- `feat`: Create Radio Button `customized` in Tab `ECM`, `HID`, `CDC`

#### version 1.0.8
- `fix`: unable to build SSH connection after reboot or repower raspi device.
- `fix`: modify files through DUT or PC, the changes will not seem to be reflected through the Samba share over the network
- `fix`: rename (include file extension) or shift file in shared network can not trgger the auto remount function
- `fix`: spell mistakes
- `feat`: if the mount job finished, it should show up a prompt to let tester easily know mount job is done
- `feat`: list files on shared network with specific color `#FFFFFF`
- `feat`: MSC tab shows dynamically mounted MSC device capacity information (available: <?>% <?>MB free)
- `feat`: update the quick user guide 
- `feat`: horizontal slider and `Assign` pushbutton to set up the capacity for filesystem creating
- `docs`: update `README.md`
  
#### version 1.0.9
- `fix`: `dd` command output in stderr
- `fix`: if WiFi name (SSID) has blank space, WiFi connection on PC is failed
- `feat`: run `install.sh` to install needed packages and configure raspi device
- `feat`: update the AppIcon.png
- `feat`: add Manufacturer, Product and SerialNumber info for MSC device
- `feat`: remove package `hfsutils` which works with legacy HFS but not HFS+
- `feat`: change block size for filesystem from `1M` to `2MB`
- `feat`: use raspi device serial number as simulated device serial number
- `feat`: add hint `SSHClient is connecting...` on trace window if SSH connect button is clicked
- `feat`: clean IP address in SSH connection window through pressing key `<-` (backspace)
- `docs`: update `README.md`
- `docs`: update `CHANGELOG.md`
  
#### version 1.1.0
- `feat`: add `BtrFS` filesytem as unreadable (unsupported) filesystem
- `docs`: update `CHANGELOG.md`

#### version 1.1.1
- `fix`: hfs+ filesystem sometomes raises -ro (read-only) flag
- `fix`: mkfs.ext<x> command output in stderr
- `refactor`: replace `fsc.py` by `fscrator.py` and refcator the code inside
- `docs`: update `README.md`

#### version 1.1.2
- `refactor`: replace `mountfs_gui` and `mountfs_robot` by `mount_app` and `mount_robot`
- `feat`: add folder `pimount` contains all customized python libs for `mount_app` and `mount_robot`
- `fix`: when click `CDM Send` button, GUI drop-down CMDline will remove default command
- `docs`: update `README.md`

#### version 1.1.3
- `refactor`: change folder name `pimount` to `src`
- `feat`: add button `Install USB Gadget`
- `feat`: remove `CD` from MSC Tab
- `feat`: format `compliance` and `free` img as exfat filesystem
- `docs`: update `README.md`