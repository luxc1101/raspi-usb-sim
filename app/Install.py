# -*- coding: utf-8 -*-
#*****************************************************
# Project:   Raspberrypi Zero USB filesystem simulator
# Autor:     Xiaochuan Lu
# Abteilung: SWTE
#*****************************************************

import os
import sys

import Icons
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QMainWindow
from scp import SCPClient

os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"]             = "1"
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

class Ui_RaspiInstallation(QMainWindow):
    def setup_ui(self, RaspiInstallation:QtWidgets.QDialog, ssh_client=None):
        self.ssh_client = ssh_client
        self.remote_path = "/home/pi/"  # Change this to desired remote path
        self.install_script = "install.sh"  # Name of the installation script   
        RaspiInstallation.setWindowTitle("Install USB Gadget on Rpi")
        RaspiInstallation.resize(400, 200)
        RaspiInstallation.setWindowIcon(QtGui.QIcon(":/icon/install.png"))
        RaspiInstallation.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        self.gridLayout_2 = QtWidgets.QGridLayout(RaspiInstallation)
        self.groupBox_install = QtWidgets.QGroupBox(RaspiInstallation)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_install)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.LB_Upload = QtWidgets.QLabel(self.groupBox_install)
        self.horizontalLayout.addWidget(self.LB_Upload)
        self.LE_Upload = QtWidgets.QLineEdit(self.groupBox_install)
        self.horizontalLayout.addWidget(self.LE_Upload)
        self.toolButton = QtWidgets.QToolButton(self.groupBox_install)
        self.toolButton.setMaximumSize(QtCore.QSize(50, 50))
        self.toolButton.setIcon(QtGui.QIcon(':/icon/explorer.png'))
        self.toolButton.setToolTip('Click to open installation folder')
        self.horizontalLayout.addWidget(self.toolButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.PB_Install = QtWidgets.QProgressBar(self.groupBox_install)
        self.PB_Install.setValue(0)
        self.PB_Install.setMaximumHeight(13)
        self.PB_Install.setAlignment(QtCore.Qt.AlignCenter)
        self.QP = QtGui.QPalette()
        self.QP.setColor(QtGui.QPalette.Base, QtGui.QColor('#797d7f')) # BG
        self.QP.setColor(QtGui.QPalette.Text, Qt.white) # text color
        self.PB_Install.setPalette(self.QP)
        self.verticalLayout_2.addWidget(self.PB_Install)
        self.gridLayout_2.addWidget(self.groupBox_install, 0, 0, 1, 1)
        self.groupBox_details = QtWidgets.QGroupBox(RaspiInstallation)
        self.groupBox_details.setObjectName("groupBox_details")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_details)
        self.gridLayout.setObjectName("gridLayout")
        self.Install_Details = QtWidgets.QTextBrowser(self.groupBox_details)
        self.Install_Details.setObjectName("Install_Details")
        self.QP.setColor(QtGui.QPalette.Base, Qt.black) # BG
        self.QP.setColor(QtGui.QPalette.Text, Qt.white)
        self.Install_Details.setPalette(self.QP)
        self.gridLayout.addWidget(self.Install_Details, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox_details, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(RaspiInstallation)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setText("Install")
        self.gridLayout_2.addWidget(self.buttonBox, 2, 0, 1, 1)
        
        self.worker = InstallWorker(self.ssh_client, self.LE_Upload.text(), self.remote_path)
        self.buttonBox.rejected.connect(lambda: self._cancel_installation(RaspiInstallation)) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(RaspiInstallation)

        self.LB_Upload.setText("upload")
        self.LE_Upload.setPlaceholderText("Select installation file")
        self.groupBox_install.setTitle("Install")
        self.groupBox_details.setTitle("Details")

        self.toolButton.clicked.connect(self.select_installation_folder)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.scp_installation)

    def closeEvent(self, event):
        if self.worker.isRunning():
            self.worker.stop()
        event.accept()

    def _cancel_installation(self, dialog):
        if self.worker.isRunning():
            self.worker.stop()
        dialog.reject()

    def select_installation_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Installation Folder", os.getcwd())
        if folder:
            self.LE_Upload.setText(folder)
    
    def ansi_to_html(self, text):
        ansi_map = {
        '\033[1;96m': '<span style="color:#00ffff; font-size:8pt; font-weight:800;">',  # bright cyan
        '\033[1;92m': '<span style="color:#00ff00; font-size:8pt; font-weight:800;">',  # bright green
        '\033[1;91m': '<span style="color:#ff5555; font-size:8pt; font-weight:800;">',  # bright red
        '\033[0m': '</span>',                           # reset
        }
        for code, html in ansi_map.items():
            text = text.replace(code, html)
        return text
    
    def scp_installation(self):
        """
        Securely copy the installation files to the Raspberry Pi.
        """
        if not self.ssh_client:
            self._update_trace("No SSH connection available.")
            return 

        if not os.path.isdir(self.LE_Upload.text()):
            self._update_trace("Please select a valid folder to upload.")
            return
        
        self.PB_Install.setValue(0)
        self.PB_Install.setFormat("Starting...")

        self.worker.progress_signal.connect(self._on_scp_progress)
        self.worker.detail_signal.connect(self._update_trace)
        self.worker.finished_signal.connect(self._on_install_finished)
        self.worker.local_path = self.LE_Upload.text()
        self.worker.start()
    
    def _update_trace(self, text):
        """
        Update the trace output in the details section.
        """
        self.Install_Details.append(self.ansi_to_html(text))
        
    def _on_scp_progress(self, filename, percent):
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.PB_Install.setValue(percent)
        self.PB_Install.setFormat(f"{filename}... {percent}%")

    def _on_install_finished(self, message):
        self._update_trace(message)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

class InstallWorker(QThread):
    """
    Worker thread to install USB Gadget.
    """
    progress_signal = pyqtSignal(str, int)  # filename, percent
    detail_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str)  # success, message

    def __init__(self, ssh_client, local_path, remote_path):
        super().__init__()
        self.ssh_client = ssh_client
        self.local_path = local_path
        self.remote_path = remote_path
        self._running = True

    def run(self):

        def progress(filename, size, sent):
            percent = int((sent / size) * 100) if size > 0 else 0
            basefile = filename.decode() if isinstance(filename, bytes) else filename
            basefile = os.path.basename(basefile)
            self.progress_signal.emit(basefile, percent)
            if percent == 0:
                self.detail_signal.emit(f"Uploading: {basefile}")

        try:
            self.detail_signal.emit("\033[1;96mStarting upload...\033[0m")
            with SCPClient(self.ssh_client.get_transport(), progress=progress) as scp:
                scp.put(self.local_path, recursive=True, remote_path=self.remote_path)
            remote_target = os.path.join(self.remote_path, os.path.basename(self.local_path))
            cmd = f'sudo chmod -R 777 "{remote_target}"'
            self.ssh_client.exec_command(cmd)
            self.detail_signal.emit("Upload successfully.")
            
            self.progress_signal.emit("installing...", 0)
            self.detail_signal.emit("\033[1;96mStarting install...\033[0m")
            cmd = f'cd {remote_target} && dos2unix install.sh && sh install.sh .'
            stdin, stdout, stderr = self.ssh_client.exec_command(cmd)
            for line in iter(lambda: stdout.readline(2048), ""):
                if not line:
                    break
                line = line.strip()
                if line.startswith("PROGRESS:"):
                    percent = int(line.split(":")[1])
                    self.progress_signal.emit("installing...", percent)
                else:
                    self.detail_signal.emit(line)
            self.finished_signal.emit("Installation finished.")
        
        except Exception as e:
            self.finished_signal.emit(f"failed: {str(e)}")

    def stop(self):
        self._running = False
        self.terminate()

if __name__ == "__main__":
    dialogapp = QtWidgets.QApplication(sys.argv)
    RaspiInstallation = QtWidgets.QDialog()
    installationdialogui = Ui_RaspiInstallation()
    installationdialogui.setup_ui(RaspiInstallation)
    RaspiInstallation.show()
    sys.exit(dialogapp.exec_())