# -*- coding: utf-8 -*-
#*****************************************************
# Project:   Raspberrypi Zero MSC filesystem simulator
# Autor:     Xiaochuan Lu
# Abteilung: SWTE
#*****************************************************
import json
import logging
import os
import sys
import time

import Icons
import paramiko
from Config import Ui_RaspiSshConnection
from Install import Ui_RaspiInstallation
from Help import Ui_Form
from paramiko import SSHClient
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QEventLoop, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import QFrame, QLabel, QMainWindow, QMessageBox
from QLed import QLed

version = '1.1.6'
'''
This setup is going to make application look better on high-DPI displays (such as 4K or Retina screens), 
handling both UI scaling and sharpness of icons/images. 
'''
os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"]             = "1"
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)    # enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)       # use highdpi icons


logging.basicConfig(filename="session.log", format='%(asctime)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filemode='w', level=logging.DEBUG, encoding='utf-8')


class Ui_MainWindow(QMainWindow):
    '''
    UI Main window
    '''
    with open(os.path.join(os.getcwd(), "Config.json"),'r',encoding="utf8") as f:
        setup_dict = json.load(f)

    with open(os.path.join(os.getcwd(),"device_proj.json"),'r', encoding="utf8") as f:
        device_dict_proj = json.load(f)

    def __init__(self):
        super().__init__()
        self.Param = {}                                                      # login parameter dictionary
        self.ssh = SSHClient()                                               # create new ssh client
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())       # Set policy to use when connecting to servers without a known host key.
        self.ssh_isconnected = False                                         # flag: SSHClient is not connected
        self.paramdict = {"WaDo": 0, "Samba": 0, "Cmd": ""}                  # default parameter dictionary, which will be sent to SSHClient
        self.logger = logging.getLogger(__name__)                            # create a logger
        self.msc_dict = {"":["None",""]}                                     # defualt case when the combobox MSC is empty
        self.setup_ui()

    def connect_ssh(self):
        '''
        show SSH connection dialog and push the param through to main window
        '''
        if not self.ssh_isconnected:
            self.SSHConnectionWin = QtWidgets.QDialog()
            self.configui = Ui_RaspiSshConnection()
            self.configui.setup_ui(self.SSHConnectionWin)
            self.configui.SSHConnection_signal.connect(self.login_SSHClient)
            self.SSHConnectionWin.open()        
    
    def show_help_window(self):
        '''
        show info about this tool and quick user guide
        '''
        self.Helpwin = QtWidgets.QDialog()
        self.ui = Ui_Form()
        self.ui.setup_ui(self.Helpwin)
        self.Helpwin.show()
    
    def show_installation_window(self):
        '''
        show installation window to install USB Gadget on Raspberry Pi
        '''
        self.InstallWin = QtWidgets.QDialog()
        self.ui = Ui_RaspiInstallation()
        self.ui.setup_ui(self.InstallWin, ssh_client=self.ssh)
        self.InstallWin.show()

    def setup_ui(self):
        '''
        create and layout QWidgets 
        '''
        self.resize(330, 550)
        self.setWindowIcon(QtGui.QIcon(":/icon/AppIcon.png"))
        self.setWindowTitle("USB Tool")
        self.centralW = QtWidgets.QWidget(self)
        self.firstLayout = QtWidgets.QGridLayout(self.centralW)
        self.firstLayout.setContentsMargins(10, 10, 10, 10)
        self.firstLayout.setSpacing(5)

        self._setup_menu_and_toolbar()  # setup menu and toolbar
        self._setup_tabs()  # setup tabs and widgets
        self._setup_trace_groupbox()    # setup trace groupbox
        self._setup_statusbar()  # setup status bar
        self._setup_projection_group()  # setup project group
        self._connect_signals()  # connect signals to slots

        ####################
        #     Threads      #
        ####################
        self.threads = {} # threads dictionary
        # threads[0] thread updates command exection
        self.threads[0] = CmdExecution(parent=None, ssh=self.ssh)
        self.threads[0].output_signal.connect(self.update_cmdexecution)
        # threads[1] thread updates traces on trace window
        self.threads[1] = TraceThread(parent=None)
        self.threads[1].trace_signal.connect(self.update_trace)
        # threads[2] thread SSHClient heartbeat monitor
        self.threads[2] = SSHStatusMonitor(parent=None, ssh_client=self.ssh)
        self.threads[2].connection_status_signal.connect(self.update_SSHClient_connectedstate)
        # threads[3] thread 
        self.threads[3] = FSavaiableMonitor(parent=None, ssh_client=self.ssh)
        self.threads[3].fs_available_status_signal.connect(self.update_mscspace_value)
        self.thread_sshclientstatus_update() # start threads[2] SSHClient hearbeat thread at the beginning 

    def _setup_menu_and_toolbar(self):
        '''
        setup menu and toolbar
        '''
        ### MenuBar and ToolBar
        self.menuBar = QtWidgets.QMenuBar(self)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 100, 25))
        self.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(self)
        # self.mainToolBar.setStyleSheet("QToolBar QToolButton:enabled { border: 2px solid #a6acaf; border-radius: 5px;}")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.menuCalls = QtWidgets.QMenu(self.menuBar)
        self.menuCalls.setTitle("Calls")
        # self.menuCalls.setStyleSheet("QMenu::item:enabled { border: 2px solid cyan; border-radius: 3px;}")
        self.menuProjects = QtWidgets.QMenu(self.menuBar)
        self.menuProjects.setTitle("Projects")

        ### Actions
        self.actionSSHConnect = self._setup_actionicon("SSH Connect", ":/icon/ssh-raspi.png")
        self.actionSSHDisconnect = self._setup_actionicon("SSH Disconnect", ":/icon/ssh-disconnect-raspi.png")
        self.actionEject = self._setup_actionicon("Eject", ":/icon/disconnect.png")
        self.actionMount = self._setup_actionicon("Mount", ":/icon/connect.png")
        self.actionClear = self._setup_actionicon("Clear Trace Window", ":/icon/clear.png")
        self.actionHelp = self._setup_actionicon("About USB Tool", ":/icon/help.png")
        self.actionInstall = self._setup_actionicon("Install USB Gadget", ":/icon/install.png")

        self.menuBar.addAction(self.menuCalls.menuAction())
        self.menuBar.addAction(self.menuProjects.menuAction())

        self.menuCalls.addAction(self.actionSSHConnect)
        self.menuCalls.addAction(self.actionSSHDisconnect)
        self.menuCalls.addAction(self.actionMount)
        self.menuCalls.addAction(self.actionEject)
        self.menuCalls.addAction(self.actionClear)
        self.menuCalls.addAction(self.actionHelp)
        self.menuCalls.addAction(self.actionInstall)

        self.mainToolBar.addAction(self.actionSSHConnect)
        self.mainToolBar.addAction(self.actionSSHDisconnect)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionMount)
        self.mainToolBar.addAction(self.actionEject)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionClear)
        self.mainToolBar.addAction(self.actionInstall)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.actionHelp)
    
    def _setup_actionicon(self, action_text: str, icon_map: str) -> QtWidgets.QAction:
        action = QtWidgets.QAction(self)
        action.setText(action_text)
        actionicon = QtGui.QIcon()
        actionicon.addPixmap(QtGui.QPixmap(icon_map), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        action.setIcon(actionicon)
        return action

    def _setup_msc_tab(self):
        '''
        setup MSC tab
        '''
        ### MSC Widgets
        self.MSC = QtWidgets.QWidget()
        self.mscLayout = QtWidgets.QGridLayout(self.MSC)
        self.mscLayout.setContentsMargins(1, 1, 1, 3)
        self.mscLayout.setSpacing(5)
        self.groupBox_mtfs = QtWidgets.QGroupBox(self.MSC)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(50)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_mtfs.sizePolicy().hasHeightForWidth())
        self.groupBox_mtfs.setSizePolicy(sizePolicy)
        self.groupBox_mtfs.setFont(font)
        # self.groupBox_mtfs.setStyleSheet("")
        self.groupBox_mtfs.setFlat(False)
        self.mscLayout_in = QtWidgets.QGridLayout(self.groupBox_mtfs)
        self.mscLayout_in.setContentsMargins(10, 5, 10, 5)
        self.mscLayout_in.setSpacing(5)
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setSpacing(5)
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setSpacing(6)
        self.LB_Filesystem = QtWidgets.QLabel(self.groupBox_mtfs)
        self.LB_Filesystem.setText("Device Info")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.LB_Filesystem)
        self.horizontalLayout_FS = QtWidgets.QHBoxLayout()
        self.horizontalLayout_FS.setSpacing(5)
        self.comboBox_MSC = QtWidgets.QComboBox(self.groupBox_mtfs)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_MSC.sizePolicy().hasHeightForWidth())
        self.comboBox_MSC.setSizePolicy(sizePolicy)
        self.horizontalLayout_FS.addWidget(self.comboBox_MSC)
        self.TB_SharedFolder = QtWidgets.QToolButton(self.groupBox_mtfs)
        self.TB_SharedFolder.setAutoRaise(True)
        self.TB_SharedFolder.setMaximumSize(QtCore.QSize(50, 50))
        self.TB_SharedFolder.setIcon(QtGui.QIcon(':/icon/remote'))
        self.TB_SharedFolder.setToolTip('Click to open shared network folder of current MSC device')
        self.horizontalLayout_FS.addWidget(self.TB_SharedFolder)
        self.TB_DeleteFS = QtWidgets.QToolButton(self.groupBox_mtfs)
        self.TB_DeleteFS.setAutoRaise(True)
        self.TB_DeleteFS.setPopupMode(QtWidgets.QToolButton.DelayedPopup)
        self.TB_DeleteFS.setMaximumSize(QtCore.QSize(50, 50))
        self.TB_DeleteFS.setIcon(QtGui.QIcon(':/icon/delete'))
        self.TB_DeleteFS.setToolTip('Click to delete current file system')
        self.horizontalLayout_FS.addWidget(self.TB_DeleteFS)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_FS)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.PB_MscSpace = QtWidgets.QProgressBar(self.groupBox_mtfs)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.PB_MscSpace.sizePolicy().hasHeightForWidth())
        self.PB_MscSpace.setSizePolicy(sizePolicy)
        self.PB_MscSpace.setValue(0)
        self.PB_MscSpace.setMaximumHeight(11)
        self.PB_MscSpace.setAlignment(QtCore.Qt.AlignCenter)
        self.PB_MscSpace.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.QP = QtGui.QPalette()
        self.QP.setColor(QtGui.QPalette.Base, QtGui.QColor('#797d7f')) # BG
        self.QP.setColor(QtGui.QPalette.Text, Qt.white) # text color
        self.PB_MscSpace.setPalette(self.QP)
        self.PB_MscSpace.setToolTip('Free disc space of mounted msc device')
        self.PB_MscSpace.setFormat('available: {}% ({} MB free {})'.format('unknown','unknown', ''))
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.PB_MscSpace)
        self.horizontalLayout_spaceslider = QtWidgets.QHBoxLayout()
        self.horizontalLayout_spaceslider.setSpacing(3)
        self.horizontalSlider = QtWidgets.QSlider(self.groupBox_mtfs)
        self.defaultSliderPosition = 64
        self.horizontalSlider.setMaximumHeight(20)
        self.horizontalSlider.setMinimum(32)
        self.horizontalSlider.setMaximum(1024)
        self.horizontalSlider.setSingleStep(16)
        self.horizontalSlider.setSliderPosition(self.defaultSliderPosition)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setToolTip("Slider to assign disc space for creating of filesystem")
        self.LB_MinSapce = QLabel(f"{self.horizontalSlider.minimum()}")
        self.LB_MaxSpace = QLabel(f"N/A") # not available 
        self.horizontalLayout_spaceslider.addWidget(self.LB_MinSapce)
        self.horizontalLayout_spaceslider.addWidget(self.horizontalSlider)
        self.horizontalLayout_spaceslider.addWidget(self.LB_MaxSpace)
        self.LE_CurrentValue = QtWidgets.QLineEdit(self.groupBox_mtfs)
        self.LE_CurrentValue.setMaximumSize(QtCore.QSize(40, 20))
        CurrentVRegex = QtCore.QRegExp(r"^\d+$")
        self.CurrentV_validator = QtGui.QRegExpValidator(CurrentVRegex, self.LE_CurrentValue)
        self.LE_CurrentValue.setValidator(self.CurrentV_validator)
        self.horizontalLayout_spaceslider.addWidget(self.LE_CurrentValue)
        self.LE_CurrentValue.setText(str(self.defaultSliderPosition))
        self.LB_Unit = QLabel("MB")
        self.horizontalLayout_spaceslider.addWidget(self.LB_Unit)
        self.B_SpaceOK = QtWidgets.QPushButton(self.groupBox_mtfs)
        self.B_SpaceOK.setMaximumSize(QtCore.QSize(55, 20))
        self.B_SpaceOK.setText("Assign")
        self.B_SpaceOK.setToolTip("Send space value from slider to SSHClient")
        self.horizontalLayout_spaceslider.addWidget(self.B_SpaceOK)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_spaceslider)

        self.LB_Status = QtWidgets.QLabel(self.groupBox_mtfs)
        self.LB_Status.setText("Status of Filesystem")
        self.LB_Status.setToolTip("LED indicate the existence of filesystem")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.LB_Status)
        self.ImgLed=QLed(self, onColour=QLed.Green, shape=QLed.Round) # image led indicator
        self.horizontalLayout.addWidget(self.ImgLed)
        self.checkBox_WaDo = QtWidgets.QCheckBox(self.groupBox_mtfs)
        self.checkBox_WaDo.setText("Auto Remount")
        self.checkBox_WaDo.setToolTip('Enable or disable auto remount for current MSC device')
        self.checkBox_Samba = QtWidgets.QCheckBox(self.groupBox_mtfs)
        self.checkBox_Samba.setText("Shared Folder")
        self.checkBox_Samba.setToolTip('Enable or disable network shared folder for current MSC device')
        self.horizontalLayout.addWidget(self.checkBox_WaDo)
        self.horizontalLayout.addWidget(self.checkBox_Samba)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 1)
        self.formLayout.setLayout(3, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.gridLayout_3.addLayout(self.formLayout, 0, 0, 1, 1)
        self.mscLayout_in.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        self.mscLayout.addWidget(self.groupBox_mtfs, 0, 0, 1, 1)
        self.tabWidget.addTab(self.MSC, "Mass Storage Class")

    def _setup_tabs(self):
        '''
        setup tabs for MSC, ECM, HID and CDC
        '''
        self.tabWidget = QtWidgets.QTabWidget(self.centralW)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumHeight(140)
        self.tabWidget.setCurrentIndex(0)

        self._setup_msc_tab()  # setup MSC tab

        self.ECM = TabContent()
        self.tabWidget.addTab(self.ECM, "Ethernet Adapter")
        
        self.HID = TabContent()
        self.tabWidget.addTab(self.HID, "Human Interface Device")
        
        self.CDC = TabContent()
        self.tabWidget.addTab(self.CDC, "Communication Device Class")

        ### add all tabs into firstLayout
        self.firstLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

    def _setup_trace_groupbox(self):
        '''
        setup trace groupbox
        '''
        self.groupBox_trace = QtWidgets.QGroupBox(self.centralW)
        self.groupBox_trace.setTitle("Trace")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_trace)
        self.gridLayout.setContentsMargins(10, 10, 10, 10)
        self.gridLayout.setSpacing(10)
        self.textEdit_trace = QtWidgets.QTextEdit(self.groupBox_trace, readOnly= True)
        self.textEdit_trace.setPlaceholderText("command and output is shown here")
        self.gridLayout.addWidget(self.textEdit_trace, 0, 0, 1, 1)
        self.firstLayout.addWidget(self.groupBox_trace, 1, 0, 1, 1)
        self.QP.setColor(QtGui.QPalette.Base, Qt.black) # BG
        self.QP.setColor(QtGui.QPalette.Text, Qt.white)
        self.textEdit_trace.setPalette(self.QP)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(5)

        self.CB_SendCmd = QtWidgets.QComboBox(self.groupBox_trace)
        key_list = ["", "REMOUNT FILESYSTEM", "EJECT + QUIT", "POWER OFF RASPI", "REBOOT"]
        cmd_list = ["", "REMOUNT", "QUIT", "sudo halt", "sudo reboot"]
        self.cmd_dic = dict(zip(key_list, cmd_list))
        self.CB_SendCmd.addItems(self.cmd_dic.keys())

        self.LE_SendCmd = QtWidgets.QLineEdit(self.groupBox_trace)
        self.LE_SendCmd.setPlaceholderText("Send the CMD manually here")
        self.CB_SendCmd.setLineEdit(self.LE_SendCmd)
        self.CB_SendCmd.setToolTip('Drop-down menu to send hot commands')
        self.horizontalLayout_2.addWidget(self.CB_SendCmd)
        self.B_SendCmd = QtWidgets.QPushButton(self.groupBox_trace)
        self.B_SendCmd.setText("CMD Send")
        self.B_SendCmd.setMaximumSize(130,50)
        self.horizontalLayout_2.addWidget(self.B_SendCmd)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 1)
        self.firstLayout.addWidget(self.groupBox_trace, 2, 0, 1, 1)
        self.setCentralWidget(self.centralW)
    
    def _setup_statusbar(self):
        '''
        Set up the status bar with version, date, and SSH status.
        '''
        self.statusBar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.statusBar.reformat()
        self.statusBar.setStyleSheet('border: 0; background-color: #FFF8DC;')
        self.statusBar.setStyleSheet("QtWidgets.QStatusBar::item {border: none;}")
        self.statusMessage = QLabel()
        self.statusMessage.setText("SSH disconnected")
        self.VersionQL = QLabel(f"Version: <b>{version}</b>")
        date = "Date: {}".format(QDate.currentDate().toString(Qt.ISODate))
        self.DataQL = QLabel(date)
        self.SSHLed = QLed(self, onColour=QLed.Green, shape=QLed.Circle)
        self.statusBar.addWidget(self.SSHLed)
        self.statusBar.addWidget(self.statusMessage)
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.VersionQL)
        self.statusBar.addPermanentWidget(VLine())
        self.statusBar.addPermanentWidget(self.DataQL)

    def _setup_projection_group(self):
        '''
        setup project group
        '''
        self.projectGroup = QtWidgets.QActionGroup(self.menuProjects)
        self.projectGroup.setExclusive(True)
        self.mib_proj_action = QtWidgets.QAction("MIB3", self.menuProjects, checkable=True, checked=False)
        self.gei_proj_action = QtWidgets.QAction("GEI", self.menuProjects, checkable=True, checked=False)
        self.user_proj_action = QtWidgets.QAction("User", self.menuProjects, checkable=True, checked=False)
        self.menuProjects.addAction(self.mib_proj_action)
        self.menuProjects.addAction(self.gei_proj_action)
        self.menuProjects.addAction(self.user_proj_action)
        self.projectGroup.addAction(self.mib_proj_action)
        self.projectGroup.addAction(self.gei_proj_action)
        self.projectGroup.addAction(self.user_proj_action)
        for action in self.projectGroup.actions():
            if self.setup_dict["Project"] == action.text():
                action.setChecked(True)
                break
        self.mib_proj_action.triggered.connect(lambda: self.load_device_dict_by_project(self.mib_proj_action.text()))
        self.gei_proj_action.triggered.connect(lambda: self.load_device_dict_by_project(self.gei_proj_action.text()))
        self.user_proj_action.triggered.connect(lambda: self.load_device_dict_by_project(self.user_proj_action.text()))

        self.load_device_dict_by_project(projectkey=self.setup_dict["Project"])
    
    def _connect_signals(self):
        '''
        connect signals to slots
        '''
        QtCore.QMetaObject.connectSlotsByName(self)
        self.check_imgexistence()
        self.actionSSHDisconnect.triggered.connect(self.exit_SSHClient)
        self.actionSSHConnect.triggered.connect(self.connect_ssh)
        self.actionMount.triggered.connect(self.mount_device)
        self.actionEject.triggered.connect(self.eject_device)
        self.actionClear.triggered.connect(self.clear_trace)
        self.actionHelp.triggered.connect(self.show_help_window)
        self.B_SendCmd.clicked.connect(lambda: self.send_command_to_SSHClient(self.LE_SendCmd.text()))
        self.LE_SendCmd.returnPressed.connect(lambda: self.send_command_to_SSHClient(self.LE_SendCmd.text()))
        self.TB_DeleteFS.clicked.connect(self.delete_filesystem)
        self.TB_SharedFolder.clicked.connect(self.open_remote_folder)
        self.comboBox_MSC.currentIndexChanged.connect(self.check_imgexistence)
        self.checkBox_Samba.stateChanged.connect(self.auto_remount_shared_folder)
        self.checkBox_WaDo.stateChanged.connect(self.auto_remount_shared_folder)
        self.horizontalSlider.valueChanged.connect(self.slider_value_changed)
        self.LE_CurrentValue.textChanged.connect(self.sync_slider_value_by_LE)
        self.B_SpaceOK.clicked.connect(self.assign_fs_block_space)
        self.actionInstall.triggered.connect(self.show_installation_window) 

    ####################
    #   Functions      #
    ####################
    @staticmethod
    def create_messagebox(title:str, msgtext:str, msgtype:str, iconimg):
        '''
        configration message box
        title: Window title
        msgtext: set text
        msgtype: i - info; w - warning; e - error
        '''
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(msgtext)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msg.setWindowIcon(QtGui.QIcon(":/icon/AppIcon.png"))
        if iconimg:
            msg.setWindowIcon(QtGui.QIcon(f":/icon/{iconimg}"))
        if msgtype == "i":
            msg.setIcon(QMessageBox.Information)
        elif msgtype == "w":
            msg.setIcon(QMessageBox.Warning) 
        elif msgtype == "e":
            msg.setIcon(QMessageBox.Critical) 
        return msg.exec()

    def init_QWidgets_state_SSHDisconnected(self):
        '''
        initialize QWidgets state if SSHClient is disconnected
        '''
        self.tabWidget.setEnabled(True)             # QTabWidget
        self.MSC.setEnabled(True)                   # QWidget
        self.comboBox_MSC.setEnabled(False)         # QComboBox
        self.TB_SharedFolder.setEnabled(False)      # QToolButton
        self.TB_DeleteFS.setEnabled(False)          # QToolButton
        self.ImgLed.value = False                   # QLed
        self.checkBox_WaDo.setEnabled(False)        # QCheckBox
        self.checkBox_Samba.setEnabled(False)       # QCheckBox
        self.CB_SendCmd.setEnabled(False)           # QComboBox
        self.LE_SendCmd.setEnabled(False)           # QLineEdit
        self.B_SendCmd.setEnabled(False)            # QPushButton
        self.actionEject.setEnabled(False)          # QAction
        self.actionMount.setEnabled(False)          # QAction
        self.actionClear.setEnabled(True)           # QAction
        self.actionHelp.setEnabled(True)            # QAction
        self.SSHLed.value = False                   # QLed
        self.LE_CurrentValue.setEnabled(False)
        self.horizontalSlider.setEnabled(False)
        self.B_SpaceOK.setEnabled(False)
        self.actionInstall.setEnabled(False)        # QAction
    
    def enable_QWdigets_status_SSHConnected(self):
        '''
        permanent enabled QWidgets if SSHClient is connected
        '''
        self.CB_SendCmd.setEnabled(True)           # QComboBox
        self.LE_SendCmd.setEnabled(True)           # QLineEdit
        self.B_SendCmd.setEnabled(True)            # QPushButton
        self.actionInstall.setEnabled(True)        # QAction
    
    def closeEvent(self, event):
        '''
        initialize raspberry device and save the latest loaded project name in `Config.json` 
        afterwards close app
        '''
        with open(os.path.join(os.getcwd(), "Config.json"),'r',encoding="utf8") as f:
            setup_dict = json.load(f)

        if self.ssh_isconnected:
            self.quit_application() # initialze raspi device
        for action in self.projectGroup.actions(): # last selected project name saved in Config.json
            if action.isChecked():
                setup_dict["Project"] = action.text()
                with open(os.path.join(os.getcwd(), "Config.json"), 'w') as f:
                    json.dump(setup_dict, f)
                break
        # subprocess.check_output('cmd /c "netsh wlan disconnect"', shell=True) # disconnect WiFi
        event.accept()
    
    def load_device_dict_by_project(self, projectkey):
        '''
        reload devices when project is changed
        '''
        self.device_dict = self.device_dict_proj[projectkey]    # load device dictionary be porject key
        self.comboBox_MSC.clear()                               # clear current MSC device combobox
        self.ECM.comboBox_Device.clear()                        # clear ECM combobox
        self.HID.comboBox_Device.clear()                        # clear HID combobox
        self.CDC.comboBox_Device.clear()                        # clear CDC combobox
        msc_supported = self.device_dict["MSC"]["0"]            # msc supported devices
        ecm_supported = self.device_dict["ECM"]["0"]            # ecm supported devices
        hid_supported = self.device_dict["HID"]["0"]            # hid supported devices
        cdc_supported = self.device_dict["CDC"]["0"]            # cdc supported devices
        
        for id , dev in enumerate(msc_supported):
            self.msc_dict[dev["dev"]] = [dev["img"].split('.')[0],str(id)]
            self.comboBox_MSC.addItem(dev["dev"])
        for _ , dev in enumerate(ecm_supported):
            self.ECM.comboBox_Device.addItem(dev["dev"] + ':' + ' ' + dev["VID"] + ' ' + dev["PID"])
        for _ , dev in enumerate(hid_supported):
            self.HID.comboBox_Device.addItem(dev["dev"] + ':' + ' ' + dev["VID"] + ' ' + dev["PID"])
        for _ , dev in enumerate(cdc_supported):
            self.CDC.comboBox_Device.addItem(dev["dev"] + ':' + ' ' + dev["VID"] + ' ' + dev["PID"])

    def color_message(self, message:str, color:str) -> str:
        '''
        return text with specific color
        '''
        color_content =  "<span style=\" font-size:8pt; font-weight:800; color:{};\" >".format(color)
        color_content += message
        color_content += "</span>"
        return color_content

    def thread_cmdexecution_update(self, cmd):
        '''
        thread to execute command in SSHClient
        '''
        self.threads[0].set_command(cmd)
        if not self.threads[0].isRunning():
            self.threads[0]._running = True
            self.threads[0].start()

    def thread_trace_update(self, msg, color='lime'):
        '''
        update traces on trace window
        '''
        if "status of samba service" in msg or "status of watchdog service" in msg:
            color = '#5EEFFF'

        self.threads[1].set_message(self.color_message(msg, color))
        if not self.threads[1].isRunning():
            self.threads[1]._running = True
            self.threads[1].start()

    def thread_sshclientstatus_update(self):
        '''
        start the sshclient status monitor thread
        '''
        if not self.threads[2].isRunning():
            self.threads[2].start()
    
    def thread_fsavaiablestatus_update(self, fsname):
        '''
        start the fsavaiable status monitor thread
        '''
        self.threads[3].set_fsname(fsname)
        if not self.threads[3].isRunning():
            self.threads[3]._running = True
            self.threads[3].start()

    def update_SSHClient_connectedstate(self, sshstatus):
        '''
        receive the from thread SSHStatusMonitor emitted signal
        '''
        self.SSHLed.value = sshstatus
        self.ssh_isconnected = sshstatus
        if sshstatus:
            self.statusMessage.setText("SSH connected")         # update statusbar message
            self.actionSSHDisconnect.setEnabled(True)           # enable SSHCient Disconnect action
            self.actionSSHConnect.setEnabled(False)             # disable SSHClient connect action
            self.enable_QWdigets_status_SSHConnected()          # enable permanent QWdigets if SSHClient is connected
        else:
            self.statusMessage.setText("SSH disconnected")      # update statusbar message
            self.actionSSHDisconnect.setEnabled(False)          # disable SSHCient Disconnect action
            self.actionSSHConnect.setEnabled(True)              # enable SSHCient Disconnect action
            self.init_QWidgets_state_SSHDisconnected()          # init QWidgets state if SSHClient is disconnected

    def slider_value_changed(self):
        '''
        sync LineEdit value by slider value 
        '''
        self.LE_CurrentValue.setText(f"{self.horizontalSlider.value()}")

    def sync_slider_value_by_LE(self):
        '''
        sync slider value by LineEdit input value
        '''
        if self.LE_CurrentValue.text().isdigit():
            input_value = int(self.LE_CurrentValue.text())
            if self.horizontalSlider.minimum() <= input_value <= self.horizontalSlider.maximum():
                self.horizontalSlider.setValue(input_value)
                return
            return
        self.horizontalSlider.setValue(self.horizontalSlider.minimum())
        return

    def assign_fs_block_space(self):
        '''
        push button to send slider value to SSHClient
        '''
        self.send_command_to_SSHClient(str(self.horizontalSlider.value()))

    def send_command_to_SSHClient(self, cmd:str):
        '''
        send command to SSHClient
        '''
        try:
            # Ensure SSH connection is established
            if not self.ssh.get_transport() or not self.ssh.get_transport().is_active():
                self.thread_trace_update('SSH is not connected!', 'red')
                self.statusMessage.setText("SSH disconnected")
                return
            cmd = f"{self.translate_hotkey_to_command(hotkey=cmd)}"
            # Execute command
            if 'call' not in cmd: # normal command
                self.thread_trace_update(f'rpi:~ $ {cmd}', '#c69deb')
                if cmd == "sudo reboot" or cmd == "sudo halt":
                    self.thread_cmdexecution_update(cmd)
                    if cmd == "sudo halt":
                        self.thread_trace_update(msg="To repower Rpi device, replug the cable please.", color="orange")
                    time.sleep(0.5)
                    self.terminate_threads(keepThreadID=[2])

            if 'call' in cmd: # special command
                cmd = cmd.split('call')[-1]  

            self.thread_cmdexecution_update(cmd)

        except Exception as e:
            self.thread_trace_update(f'ERROR: executing command {cmd}: {e}', 'red')

        if len(self.LE_SendCmd.text()) != 0:
            if self.LE_SendCmd.text() not in self.cmd_dic.keys() and self.CB_SendCmd.count() > len(self.cmd_dic):
                self.CB_SendCmd.removeItem(self.CB_SendCmd.count()-1)
            self.LE_SendCmd.clear()
            self.CB_SendCmd.setCurrentIndex(0)
            
    def translate_hotkey_to_command(self, hotkey):
        '''
        translate the hotkey to command and return the translated command
        '''
        if hotkey in self.cmd_dic.keys() and self.ssh_isconnected:
            if hotkey == "REMOUNT FILESYSTEM": # remount current filesystem
                self.actionMount.setEnabled(False)
                self.actionEject.setEnabled(True)
                self.paramdict["Cmd"] = f"{self.cmd_dic[hotkey]} {self.comboBox_MSC.currentText()}"
                newcmd = 'call' + 'python -u mount_app.py' + ' ' + '"' + str(self.paramdict) + '"'
                self.change_tabwidgets_state_by_mount(tabID=self.tabWidget.currentIndex(), mounted=True)
                return newcmd
            elif hotkey == 'EJECT + QUIT': # eject the mounted device
                self.paramdict["Cmd"] = f"{self.cmd_dic[hotkey]}"
                self.actionEject.setEnabled(False)
                self.actionMount.setEnabled(True)                                                                             
                newcmd = 'call' + 'python -u mount_app.py' + ' ' + '"' + str(self.paramdict) + '"'
                self.change_tabwidgets_state_by_mount(tabID=self.tabWidget.currentIndex(), mounted=False)
                return newcmd 
            elif hotkey == "REBOOT" or hotkey == "POWER OFF RASPI": # reboot or power off raspi device
                return self.cmd_dic[hotkey]
        return hotkey

    def login_SSHClient(self, param):
        '''
        login SSHClient to build SSH connection between USB Tools and raspi device
        '''
        ssh_timeout = 5 # ssh connection timeout 5 sec
        loop = QEventLoop()
        self.update_trace(f'<span style=" font-size:8pt; font-weight:800; color:lime; ">SSHClient is connecting (timeout {ssh_timeout}s)......</span>')
        QTimer.singleShot(1, loop.quit)
        loop.exec_()
        self.Param = param
        # logging.basicConfig(filename=self.Param['Log'], format='%(asctime)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filemode='w', level=logging.DEBUG, encoding='utf-8')
        try:
            # Check if SSH client is connected
            if not self.ssh.get_transport() or not self.ssh.get_transport().is_active():
                loop = QEventLoop()
                # Timer to stop waiting after 1 msec
                self.ssh.connect(hostname = self.Param["IP"], port=int(self.Param["Port"]) ,username=self.Param["User"], password=self.Param["Key"], timeout=ssh_timeout)
                QTimer.singleShot(1, loop.quit)
                loop.exec_()
        except Exception as e:
            self.thread_trace_update(f'Error connecting to {self.Param["IP"]}: {e}', 'red')
            self.exit_SSHClient()

        if self.ssh_isconnected:
            self.update_max_space()
            self.check_imgexistence()
            self.thread_trace_update(f'Connected to {self.Param["IP"]}')
            self.actionMount.setEnabled(True)
            self.change_tabwidgets_state_by_mount(tabID=self.tabWidget.currentIndex(), mounted=False)
    
    def terminate_threads(self, keepThreadID = None):
        '''
        terminate the running thread, except for specific ID threads all running threads will be terminated 
        '''
        if keepThreadID == None:
            for key, thread in self.threads.items():
                if thread.isRunning():
                    thread.stop()
        else:
            for key, thread in self.threads.items():
                if key not in keepThreadID and thread.isRunning():
                        thread.stop()

    def exit_SSHClient(self):
        '''
        disconnect SSHClient and disconnect WIFi
        '''
        if self.ssh.get_transport() and self.ssh.get_transport().is_active():
            self.ssh.close()
            loop = QEventLoop()
            # Timer to stop waiting after 3 seconds
            QTimer.singleShot(500, loop.quit)
            loop.exec_()
            if not self.ssh_isconnected:
                self.thread_trace_update('SSH connection closed', 'orange')
        time.sleep(0.5)
        self.terminate_threads(keepThreadID=[2])

    def open_remote_folder(self):
        '''
        open remote folder if samba service active
        '''
        try:
            if self.checkBox_Samba.isChecked():
                ip_address = self.Param['IP']
                folder_name = 'raspiusb_{}'.format(self.msc_dict[self.comboBox_MSC.currentText()][0])
                self.logger.info(fr"open network folder: \\{ip_address}\{folder_name}")
                os.startfile(fr'\\{ip_address}\{folder_name}') # open network folder through explorer
        except Exception as e:
            self.create_messagebox(title="Shared Folder", msgtext= f"{e}", msgtype= 'e', iconimg="remote.png")

    def auto_remount_shared_folder(self):
        '''
        watchdog service on/off (auto remount)
        samba service on/off (shared folder)
        '''
        self.paramdict["WaDo"] = self.checkBox_WaDo.checkState()
        self.paramdict["Samba"] = self.checkBox_Samba.checkState()
        if self.checkBox_Samba.isChecked() and self.actionEject.isEnabled() and self.comboBox_MSC.currentText() != 'Partition':
            self.TB_SharedFolder.setEnabled(True)       # QToolButton Shared Folder enable
            self.checkBox_Samba.setEnabled(False)       # QCheckbox Shared Folder disable
            self.checkBox_WaDo.setEnabled(False)        # QCheckbox Auto Remount disable
        elif self.actionEject.isEnabled():
            self.TB_SharedFolder.setEnabled(False)      # QToolButton Shared Folder disable
            self.checkBox_Samba.setEnabled(False)       # QCheckbox Shared Folder disable
            self.checkBox_WaDo.setEnabled(False)        # QCheckbox Auto Remount disable
        elif self.actionMount.isEnabled():
            self.TB_SharedFolder.setEnabled(False)      # QToolButton Shared Folder disable
            self.checkBox_Samba.setEnabled(True)        # QCheckbox Shared Folder enable
            self.checkBox_WaDo.setEnabled(True)         # QCheckbox Auto Remount enable
        else:
            self.checkBox_Samba.setEnabled(False)        # QCheckbox Shared Folder enable
            self.checkBox_WaDo.setEnabled(False)         # QCheckbox Auto Remount enable

    def change_tabwidgets_state_by_mount(self, tabID:int, mounted:bool):
        if mounted: # mounted
            self.menuProjects.setEnabled(False)
            for id in range(self.tabWidget.count()):
                if id != tabID:
                    self.tabWidget.setTabEnabled(id, False) # disable tab by index
            if tabID == 0: # in MSC Tab disable part of QWidgets
                self.comboBox_MSC.setEnabled(False)
                self.auto_remount_shared_folder()
                self.check_imgexistence()
                self.update_max_space()
                self.TB_DeleteFS.setEnabled(False)
                return 
            elif tabID !=0: # disable any tab in ECM HID CDC 
                return self.tabWidget.setTabEnabled(tabID, False)

        else: # unmounted
            self.menuProjects.setEnabled(True)
            self.comboBox_MSC.setEnabled(True)
            self.auto_remount_shared_folder()
            self.check_imgexistence()
            for id in range(self.tabWidget.count()):
                self.tabWidget.setTabEnabled(id, True) # enable all tabs by index

    def delete_filesystem(self):
        '''
        delete image file of current filesytem in combobox
        '''
        cmd = 'call'
        self.paramdict["Cmd"] = f"DELETE {self.msc_dict[self.comboBox_MSC.currentText()][0]}"
        cmd += 'python -u mount_app.py' + ' ' + '"' + str(self.paramdict) + '"'
        result = self.create_messagebox(title='Delete Filesystem', msgtext=f'ready to delete {self.msc_dict[self.comboBox_MSC.currentText()][0]} file system?', msgtype='w', iconimg='delete.png')
        if result == QtWidgets.QMessageBox.Ok:
            self.send_command_to_SSHClient(cmd)
            loop = QEventLoop()
            self.threads[0].finished.connect(loop.quit)
            loop.exec_()
        self.check_imgexistence()
        self.update_max_space()

    def clear_trace(self):
        '''
        clean all log in QTextExit but NOT the Putty.log
        '''
        self.textEdit_trace.clear()
    
    def update_trace(self, msg:str):
        '''
        line by line append trace messsage to QTextEdit
        '''
        self.textEdit_trace.append(msg)
        # Set the value of the scrollbar to the maximum (bottom of the text area)
        self.textEdit_trace.verticalScrollBar().setValue(self.textEdit_trace.verticalScrollBar().maximum())
        self.logger.info(msg)

    def update_cmdexecution(self, output):
        '''
        update the stdin, stdout, stderr form ssh execution 
        '''
        if "ERROR" in output:
            self.thread_trace_update(f'{output}', 'red')
        elif "WARN" in output:
            self.thread_trace_update(f'{output}', 'orange')
        else:
            self.thread_trace_update(output)

    def update_mscspace_value(self, fsstatus:dict):
        '''
        update the free disc space value
        '''
        if fsstatus["FSused"] == "unknown" or fsstatus["FSavail"] == "unknown":
            self.PB_MscSpace.setValue(0)
            self.PB_MscSpace.setFormat('available: {}% ({} MB free) {}'.format(fsstatus["FSused"], fsstatus["FSavail"], fsstatus["Note"]))
            return
        self.PB_MscSpace.setValue(int(fsstatus["FSused"]))
        self.PB_MscSpace.setFormat('available: {}% ({} MB free) {}'.format(100-fsstatus["FSused"], fsstatus["FSavail"], fsstatus["Note"]))
        return
    
    def update_max_space(self):
        '''
        update the max avaiable space for creating of filesystem block
        '''
        if self.ssh_isconnected:
            _, stdout, _ = self.ssh.exec_command('df -Bm | grep -i "/dev/root"')
            out = stdout.read().decode('ascii', errors='ignore').strip()
            max_availspace = out.lstrip().split("M")[-2]
            self.LB_MaxSpace.setText(max_availspace.lstrip())
            self.horizontalSlider.setMaximum(int(max_availspace))
            return
        return


    def check_imgexistence(self):
        '''
        check if current filesystem *.img file exits 
        '''
        if self.ssh_isconnected:
            _, stdout, _ = self.ssh.exec_command('ls')
            # print(f'{self.msc_dict[self.comboBox_MSC.currentText()][0]}.img')
            if f'{self.msc_dict[self.comboBox_MSC.currentText()][0]}.img' in str(stdout.read().decode('ascii', errors='ignore').strip()):
                self.ImgLed.onColour = QLed.Green
                self.ImgLed.value = True
                self.TB_DeleteFS.setEnabled(True)
                self.LE_CurrentValue.setEnabled(False)
                self.horizontalSlider.setEnabled(False)
                self.B_SpaceOK.setEnabled(False)
                return
            self.ImgLed.value = False
            self.TB_DeleteFS.setEnabled(False)
            if not self.ImgLed.value and not self.actionMount.isEnabled():
                self.LE_CurrentValue.setEnabled(True)
                self.horizontalSlider.setEnabled(True)
                self.B_SpaceOK.setEnabled(True)
            return
        return

    def mount_device(self):
        '''
        mount devices

        tabwidget 0: MSC
        tabwidget 1: ECM
        tabwidget 2: HID
        tabwidget 3: CDC
        '''
        cmd = 'call'

        if self.tabWidget.currentIndex() == 0: # tab 0: MSC 
            self.paramdict["Cmd"] = f"MSC {self.comboBox_MSC.currentText()}" # MSC FAT32
        
        if self.tabWidget.currentIndex() == 1: # tab 1: ECM
            if self.ECM.radioButton_sup.isChecked() and self.ECM.comboBox_Device.currentText() != '':
                self.paramdict["Cmd"] = f'ECM {self.ECM.comboBox_Device.currentText()}'
            else:
                if len(self.ECM.LE_VID.text()) != 4 or len(self.ECM.LE_PID.text()) != 4:
                    self.create_messagebox(title="ECM Device", msgtext="please give 2 Byte number for VID and PID", msgtype= "e", iconimg="connect.png")
                    return
                self.paramdict["Cmd"] = f'ECM Unknown 0x{self.ECM.LE_VID.text()} 0x{self.ECM.LE_PID.text()}'

        if self.tabWidget.currentIndex() == 2: # tab 2: HID
            if self.HID.radioButton_sup.isChecked() and self.HID.comboBox_Device.currentText() != '':
                self.paramdict["Cmd"] = f'HID {self.HID.comboBox_Device.currentText()}'
            else:
                if len(self.HID.LE_VID.text()) != 4 or len(self.HID.LE_PID.text()) != 4:
                    self.create_messagebox(title="HID Device", msgtext="please give 2 Byte number for VID and PID", msgtype= "e", iconimg="connect.png")
                    return
                self.paramdict["Cmd"] = f'HID Unknown 0x{self.HID.LE_VID.text()} 0x{self.HID.LE_PID.text()}'

        if self.tabWidget.currentIndex() == 3: # tab 3: CDC
            if self.CDC.radioButton_sup.isChecked() and self.CDC.comboBox_Device.currentText() != '':
                self.paramdict["Cmd"] = f'CDC {self.CDC.comboBox_Device.currentText()}'
            else:
                if len(self.CDC.LE_VID.text()) != 4 or len(self.CDC.LE_PID.text()) != 4:
                    self.create_messagebox(title="CDC Device", msgtext="please give 2 Byte number for VID and PID", msgtype= "e", iconimg="connect.png")
                    return
                self.paramdict["Cmd"] = f'CDC Unknown 0x{self.CDC.LE_VID.text()} 0x{self.CDC.LE_PID.text()}'

        cmd += 'python -u mount_app.py' + ' ' + '"' + str(self.paramdict) + '"'
        # print(cmd)
        self.send_command_to_SSHClient(cmd)
        self.thread_trace_update(self.paramdict["Cmd"], '#c69deb')

        loop = QEventLoop()
        self.actionEject.setEnabled(False)
        self.actionMount.setEnabled(False)
        self.change_tabwidgets_state_by_mount(tabID=self.tabWidget.currentIndex(), mounted=True)
        self.threads[0].finished.connect(loop.quit)
        loop.exec_()  # This blocks until loop.quit() is called
        self.actionEject.setEnabled(True)
        if self.tabWidget.currentIndex() == 0: # MSC
            # self.check_fsavailability()
            self.thread_fsavaiablestatus_update(fsname=self.msc_dict[self.comboBox_MSC.currentText()][0])
        self.change_tabwidgets_state_by_mount(tabID=self.tabWidget.currentIndex(), mounted=True)

    def eject_device(self):
        '''
        eject the current mounted drive device
        '''
        cmd = 'call'
        self.paramdict["Cmd"] = "EJECT"
        cmd += 'python -u mount_app.py' + ' ' + '"' + str(self.paramdict) + '"'
        self.send_command_to_SSHClient(cmd)
        loop = QEventLoop()
        self.actionEject.setEnabled(False)
        self.actionMount.setEnabled(False)
        self.threads[0].finished.connect(loop.quit)
        loop.exec_()  # This blocks until loop.quit() is called
        self.actionMount.setEnabled(True)
        if self.tabWidget.currentIndex() == 0: # MSC
            # self.update_mscspace_value("unknow")
            
            self.terminate_threads(keepThreadID=[0,1,2])
        self.change_tabwidgets_state_by_mount(tabID=self.tabWidget.currentIndex(), mounted=False)


    def quit_application(self):
        '''
        eject current mounted device and stop sharedfolder and watchdog for Mainwindow closeEvent()
        '''
        cmd = 'call'
        self.paramdict["Cmd"] = "QUIT"
        cmd += 'python -u mount_app.py' + ' ' + '"' + str(self.paramdict) + '"'
        # print(cmd)
        self.send_command_to_SSHClient(cmd) 
        time.sleep(1)


#############################################################
#                   Thread Class                            #
#############################################################                                                 
class TraceThread(QThread):
    '''
    read data from log file and send data to trace window of Main window class
    '''
    trace_signal = pyqtSignal(str)
    def __init__(self, parent):
        super(TraceThread, self).__init__(parent)
        self._running = True
        self.msgs = []

    def run(self):
        while self._running:
            if len(self.msgs) != 0:
                msg = self.msgs.pop(0)
                self.trace_signal.emit(msg)
            
    def set_message(self, message):
        self.msgs.append(message)

    def stop(self):
        self._running = False
        self.terminate()

class CmdExecution(QThread):
    '''
    ssh execute the command
    '''
    output_signal = pyqtSignal(str)
    def __init__(self, parent, ssh: SSHClient):
        super(CmdExecution, self).__init__(parent)
        self._running = True
        self.ssh = ssh
        self.cmd = ''

    def run(self):
        while self._running:
            if self.cmd:
                try:
                    self._execute_command(self.cmd)
                except Exception as e:
                    self.output_signal.emit(f'ERROR: {e}')
                finally:
                    self.cmd = ''  # Reset command after execution
                    self._running = False  # Stop thread after command execution
    
    def set_command(self, command):
        self.cmd = command

    def _execute_command(self, command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        self._read_stdout(stdin, stdout)
        self._read_stderr(stderr)

    def _read_stdout(self, stdin, stdout):
        try:
            for stdline in iter(stdout.readline, ""):
                self.output_signal.emit(stdline.strip())
                if "going to create filesystem and partitions" in stdline:
                    self.output_signal.emit("Please input size (MB) through Slider or LineEdit and click Assign button (Btrfs can not less than 115 MB): ")
                    self._get_user_size_input(stdin)
        except Exception as e:
            self.output_signal.emit(f'ERROR: {e}')

    def _read_stderr(self, stderr):
        try:
            for errline in iter(stderr.readline, ""):
                self.output_signal.emit(f'WARN: {errline.strip()}')
        except Exception as e:
            self.output_signal.emit(f'ERROR: {e}')
    
    def _get_user_size_input(self, stdin):
        while self._running:  # Keep prompting while the thread is running
            if self.cmd.isdigit():
                size = int(self.cmd)
                stdin.write(f'{size}\n')
                stdin.flush()
                break
    
    def stop(self):
        self._running = False
        self.terminate()

class SSHStatusMonitor(QThread):
    '''
    SSHClient heartbeat thread to check the ssh connection state
    '''
    connection_status_signal = pyqtSignal(bool)
    def __init__(self, parent, ssh_client: SSHClient):
        super(SSHStatusMonitor, self).__init__(parent)
        self._running = False
        self.ssh_client = ssh_client
        #self.i = 0
    def run(self):
        # detective ssh connectio status in while loop like heartbeat
        while True:
            status = self.check_connection()
            self.connection_status_signal.emit(status)
            time.sleep(0.5)
    
    def check_connection(self):
        transport = self.ssh_client.get_transport()
        if transport and transport.is_active():
            return True # ssh connected
        return False # ssh disconnected

    def stop(self):
        self._running = False
        self.terminate()
    
class FSavaiableMonitor(QThread):
    '''
    monitor the mounted mount point free space
    '''
    fs_available_status_signal = pyqtSignal(dict)
    def __init__(self, parent, ssh_client: SSHClient):
        super(FSavaiableMonitor, self).__init__(parent)
        self._running = False
        self.ssh = ssh_client
        self.fs_name = ''
    
    def run(self):
        while self._running:
            self._read_fsused(fs_name=self.fs_name)
            time.sleep(7)
    
    def _read_fsused(self, fs_name):
        try:
            # _, stdout, _ = self.ssh.exec_command(f'lsblk --fs -o FSAVAIL,FSUSE%,MOUNTPOINT | grep -i "/mnt/usb_{fs_name}"') 
            _, stdout, _ = self.ssh.exec_command(f'df -Bm | grep -i "/mnt/usb_{fs_name}"') 
            out = str(stdout.read().decode('ascii', errors='ignore').strip())
            if "part" not in out:
                FSused = int(out.split(' ')[-2].split("%")[0])
                FSavail = float(out.lstrip().split("M")[-2])
                Note = ''
                fs_spacedict = {"FSused": FSused, "FSavail": FSavail, "Note": Note}
            else:
                FSused1 = int(out.split('\n')[0].split(' ')[-2].split("%")[0])
                FSused2 = int(out.split('\n')[1].split(' ')[-2].split("%")[0])
                FSused = FSused1 + FSused2
                FSavail1 = float(out.split('\n')[0].lstrip().split("M")[-2])
                FSavail2 = float(out.split('\n')[1].lstrip().split("M")[-2])
                FSavail = FSavail1 + FSavail2
                Note = f'(p1:{FSavail1} MB free; p2:{FSavail2} MB free)'
                fs_spacedict = {"FSused": FSused, "FSavail": FSavail, "Note": Note}
            self.fs_available_status_signal.emit(fs_spacedict)
        except:
            fs_spacedict = {"FSused": "unknown", "FSavail": "unknown", "Note": ""}
            self.fs_available_status_signal.emit(fs_spacedict)
    
    def set_fsname(self, fsname):
        self.fs_name = fsname
    
    def stop(self):
        self._running = False
        fs_spacedict = {"FSused": "unknown", "FSavail": "unknown", "Note": ""}
        self.fs_available_status_signal.emit(fs_spacedict)
        self.terminate()

#############################################################
#                   Other Helpful Classes                   #
#############################################################
class TabContent(QtWidgets.QWidget):
    '''
    create tab content for Tab ECM  HID and CDC 
    '''
    def __init__(self):
        super(TabContent, self).__init__()

        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)

        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(10, 10, 10, 10)
        self.horizontalLayout.setSpacing(5)

        self.verticalLayout_sup = QtWidgets.QVBoxLayout()
        self.verticalLayout_sup.setSpacing(5)

        #####################
        # supported device  #
        #####################
        # create radiobutton supported
        self.radioButton_sup = QtWidgets.QRadioButton(self)
        self.radioButton_sup.setText("supported")
        self.verticalLayout_sup.addWidget(self.radioButton_sup)
        self.radioButton_sup.toggled.connect(self.radio_button_toggled_event)
        
        self.horizontalLayout_sup = QtWidgets.QHBoxLayout()
        self.horizontalLayout_sup.setSpacing(5)

        # create device info label
        self.label_DeviceInfo = QtWidgets.QLabel(self)
        self.label_DeviceInfo.setText("Device Info")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_DeviceInfo.sizePolicy().hasHeightForWidth())
        self.label_DeviceInfo.setSizePolicy(sizePolicy)
        self.horizontalLayout_sup.addWidget(self.label_DeviceInfo)
        
        # create device comboBox 
        self.comboBox_Device = QtWidgets.QComboBox(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_Device.sizePolicy().hasHeightForWidth())
        self.comboBox_Device.setSizePolicy(sizePolicy)
        self.comboBox_Device.setMinimumSize(QtCore.QSize(150, 20))
        self.horizontalLayout_sup.addWidget(self.comboBox_Device)
        self.verticalLayout_sup.addLayout(self.horizontalLayout_sup)
        self.horizontalLayout.addLayout(self.verticalLayout_sup)

        #####################
        # vertical line     #
        #####################
        # create vertical line
        self.line = QtWidgets.QFrame(self)
        self.line.setObjectName("line")
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout_cus = QtWidgets.QVBoxLayout()
        self.verticalLayout_cus.setSpacing(5)

        #####################
        # customized device #
        #####################
        # create radio button customized
        self.radioButton_cus = QtWidgets.QRadioButton(self)
        self.radioButton_cus.setText("customized")
        self.verticalLayout_cus.addWidget(self.radioButton_cus)
        self.horizontalLayout_cus = QtWidgets.QHBoxLayout()
        self.horizontalLayout_cus.setSpacing(5)
        self.radioButton_cus.toggled.connect(self.radio_button_toggled_event)

        # create PID and VID's label and lineedit
        PIDVIDRegex = QtCore.QRegExp(r"[0-9A-Fa-f]{4}") # VID and PID is a 16-bit vendor number
        self.LB_VID = QtWidgets.QLabel(self)
        self.LB_VID.setText("VID  0x")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_VID.sizePolicy().hasHeightForWidth())
        self.LB_VID.setSizePolicy(sizePolicy)
        self.horizontalLayout_cus.addWidget(self.LB_VID)
        
        self.LE_VID = QtWidgets.QLineEdit(self)
        self.PIDVID_validator = QtGui.QRegExpValidator(PIDVIDRegex, self.LE_VID)
        self.LE_VID.setValidator(self.PIDVID_validator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LE_VID.sizePolicy().hasHeightForWidth())
        self.LE_VID.setSizePolicy(sizePolicy)
        self.LE_VID.setInputMask("HHHH;_")
        self.LE_VID.setMaximumSize(QtCore.QSize(35, 20))
        self.LE_VID.setCursorPosition(0)
        self.LE_VID.setToolTip("Give 16-bit vendor number (Hexadecimal)")
        self.horizontalLayout_cus.addWidget(self.LE_VID)

        self.LB_PID = QtWidgets.QLabel(self)
        self.LB_PID.setText("PID  0x")
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LB_PID.sizePolicy().hasHeightForWidth())
        self.LB_PID.setSizePolicy(sizePolicy)
        self.horizontalLayout_cus.addWidget(self.LB_PID)
        
        self.LE_PID = QtWidgets.QLineEdit(self)
        self.PIDVID_validator = QtGui.QRegExpValidator(PIDVIDRegex, self.LE_PID)
        self.LE_PID.setValidator(self.PIDVID_validator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LE_PID.sizePolicy().hasHeightForWidth())
        self.LE_PID.setSizePolicy(sizePolicy)
        self.LE_PID.setInputMask("HHHH;_")
        self.LE_PID.setCursorPosition(2)
        self.LE_PID.setMaximumSize(QtCore.QSize(35, 20))
        self.LE_PID.setCursorPosition(0)
        self.LE_PID.setToolTip("Give 16-bit product number (Hexadecimal)")

        self.horizontalLayout_cus.addWidget(self.LE_PID)
        
        self.verticalLayout_cus.addLayout(self.horizontalLayout_cus)
        self.horizontalLayout.addLayout(self.verticalLayout_cus)

        self.init_QWidgets_status()

    #####################
    #     functions     #
    #####################
    def radio_button_toggled_event(self):
        '''
        radio button toggled event
        '''
        if self.radioButton_sup.isChecked():
            self.LE_VID.setEnabled(False)
            self.LE_PID.setEnabled(False)
            self.comboBox_Device.setEnabled(True)
        elif self.radioButton_cus.isChecked():
            self.LE_VID.setEnabled(True)
            self.LE_PID.setEnabled(True)
            self.comboBox_Device.setEnabled(False)

    def init_QWidgets_status(self):
        '''
        init QWidgets in tab
        '''
        self.LE_VID.setEnabled(False)                   # QLineEdit
        self.LE_PID.setEnabled(False)                   # QLineEdit
        self.radioButton_sup.setChecked(True)           # QRadioButton
        self.radioButton_cus.setChecked(False)          # QRadioButton
        self.comboBox_Device.setEnabled(True)           # QComboBox

class VLine(QFrame):
    '''
    Setting up a customized status bar like:
    -------------------------------------------------
    |status message       |version: 1.0.1 |Data: Y-M-D|
    -------------------------------------------------
    '''
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    ui = Ui_MainWindow()
    ui.show()
    sys.exit(app.exec_())
