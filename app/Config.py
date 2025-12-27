# -*- coding: utf-8 -*-
#*****************************************************
# Project:   Raspberrypi Zero USB filesystem simulator
# Autor:     Xiaochuan Lu
# Abteilung: SWTE
#*****************************************************

import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET

import Icons
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QMessageBox

os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"]             = "1"
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

class ComboBox(QtWidgets.QComboBox):
    combobox_click_event = pyqtSignal()

    def showPopup(self):
        self.combobox_click_event.emit()
        super(ComboBox, self).showPopup()

class Ui_SSHHelper(object):
    def setup_ui(self, Form):
        Form.setWindowTitle("SSH Login Help")
        Form.resize(300, 400)
        Form.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        Form.setWindowIcon(QtGui.QIcon(":/icon/ssh-raspi.png"))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout_1 = QtWidgets.QGridLayout()
        self.gridLayout.addLayout(self.gridLayout_1, 0, 0, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 321, 178))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.textEdit = QtWidgets.QTextEdit(self.scrollAreaWidgetContents)
        self.textEdit.setReadOnly(True)
        self.verticalLayout.addWidget(self.textEdit)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 1, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(Form)

        self.textEdit.setMarkdown("## Rpi SSH Connection")
        self.appendMarkdown("`==========================`  ")
        self.appendMarkdown("## SSH Config:")
        self.appendMarkdown("**IP**: Rpi host IP address, which could be checked in router, please check `readme.txt`")
        self.appendMarkdown("**Port**: 22")
        self.appendMarkdown("**User**: pi")
        self.appendMarkdown("**Key**: pass")
        self.appendMarkdown("**Log**: `*.log`")
        self.appendMarkdown("`---------------`")
        self.appendMarkdown("## WiFi:")
        self.appendMarkdown("**SSID**: all visible WiFi network name on current machine")
        self.appendMarkdown("**Password**: WiFi password")
        self.appendMarkdown("`---------------`")
        self.appendMarkdown("## Buttons:")
        self.appendMarkdown("**Apply**: validate the input if all inputs are OK, save the current parameter on configuration dialog and validate the input")
        self.appendMarkdown("**Cancel**: close the Rpi SSH Connection without saving parameter")
        self.appendMarkdown("**Connect**: connect WiFi and try to build SSH Client connection")
    
    def appendMarkdown(self, new_markdown):
        '''
        append new markdown line content
        '''
        current_markdown = self.textEdit.toMarkdown()
        combined_markdown = current_markdown + new_markdown
        self.textEdit.setMarkdown(combined_markdown)


class Ui_RaspiSshConnection(QMainWindow):

    SSHConnection_signal = pyqtSignal(dict)

    def confighelp(self):
        '''
        show info about this tool and quick user guide
        '''
        self.DialoghelpWin = QtWidgets.QDialog()
        self.ui            = Ui_SSHHelper()
        self.ui.setup_ui(self.DialoghelpWin)
        self.DialoghelpWin.show()

    def setup_ui(self, RaspiSshConnection:QtWidgets.QDialog):
        RaspiSshConnection.resize(300, 280)
        RaspiSshConnection.setWindowIcon(QtGui.QIcon(":/icon/ssh-raspi.png"))
        RaspiSshConnection.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        self.gridLayout_3 = QtWidgets.QGridLayout(RaspiSshConnection)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.groupBox_SSH = QtWidgets.QGroupBox(RaspiSshConnection)
        # self.groupBox_SSH.setStyleSheet("background-color: white")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_SSH)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.LB_IP = QtWidgets.QLabel(self.groupBox_SSH)
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.LB_IP)
        
        self.LE_IP = QtWidgets.QLineEdit(self.groupBox_SSH)
        # https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch07s16.html
        IPV4Regex = QtCore.QRegExp(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        self.IP_validator = QtGui.QRegExpValidator(IPV4Regex, self.LE_IP)
        self.LE_IP.setValidator(self.IP_validator)
        font = QtGui.QFont("Courier New", 10)
        self.LE_IP.setFont(font)
        self.LE_IP.setInputMask("000.000.000.000;_")
        self.LE_IP.installEventFilter(self)

        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.LE_IP)
        self.LB_Port = QtWidgets.QLabel(self.groupBox_SSH)
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.LB_Port)
        
        self.LE_Port = QtWidgets.QLineEdit(self.groupBox_SSH)
        PortRegex = QtCore.QRegExp(r"^[0-9][0-9]$")
        self.Port_validator = QtGui.QRegExpValidator(PortRegex, self.LE_Port)
        self.LE_Port.setValidator(self.Port_validator)
        self.LE_Port.setFont(font)

        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.LE_Port)
        self.LB_User = QtWidgets.QLabel(self.groupBox_SSH)
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.LB_User)
        
        self.LE_User = QtWidgets.QLineEdit(self.groupBox_SSH)
        UserRegex = QtCore.QRegExp(r"[p][i]")
        self.User_validator = QtGui.QRegExpValidator(UserRegex, self.LE_Port)
        self.LE_User.setValidator(self.User_validator)
        self.LE_User.setFont(font)

        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.LE_User)
        self.LB_Key = QtWidgets.QLabel(self.groupBox_SSH)
        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.LB_Key)
        
        self.LE_Key = QtWidgets.QLineEdit(self.groupBox_SSH)
        KeyRegex = QtCore.QRegExp(r"^.+") # any string that has at least one characte
        self.Key_validator = QtGui.QRegExpValidator(KeyRegex, self.LE_Key)
        self.LE_Key.setValidator(self.Key_validator)
        self.LE_Key.setFont(font)

        self.formLayout_2.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.LE_Key)
        self.LB_Log = QtWidgets.QLabel(self.groupBox_SSH)
        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.LB_Log)
        self.LE_LogPath = QtWidgets.QLineEdit(self.groupBox_SSH)
        
        LogRegex = QtCore.QRegExp(r"^.*\.log$") # for any sequence of characters (including none) before the literal ".log"
        self.Log_validator = QtGui.QRegExpValidator(LogRegex, self.LE_LogPath)
        self.LE_LogPath.setValidator(self.Log_validator)
        self.LE_LogPath.setFont(font)

        self.formLayout_2.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.LE_LogPath)
        self.gridLayout.addLayout(self.formLayout_2, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_SSH)

        self.groupBox_WiFi = QtWidgets.QGroupBox(RaspiSshConnection)
        # self.groupBox_WiFi.setStyleSheet("background-color: white")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_WiFi)
        self.formLayout_3 = QtWidgets.QFormLayout()
        self.LB_ssid = QtWidgets.QLabel(self.groupBox_WiFi)
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.LB_ssid)

        self.CB_ssid = ComboBox(self.groupBox_WiFi)
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.CB_ssid)
        self.CB_ssid.setFont(font)

        self.LB_psk = QtWidgets.QLabel(self.groupBox_WiFi)
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.LB_psk)
        self.LE_psk = QtWidgets.QLineEdit(self.groupBox_WiFi)
        
        PSKRegex = QtCore.QRegExp("^\S{8,}$") #  any character but not a whitespace at least 8 times
        self.PSK_validator = QtGui.QRegExpValidator(PSKRegex, self.LE_psk)
        self.LE_psk.setValidator(self.PSK_validator)
        self.LE_psk.setFont(font)

        self.LE_psk.setEchoMode(QtWidgets.QLineEdit.Password)

        # Action for toggling the visibility of the password
        self.toggleAction = QtWidgets.QAction(self)
        self.toggleAction.setIcon(QtGui.QIcon(':/icon/eye.png')) 
        self.toggleAction.setCheckable(True)
        self.LE_psk.addAction(self.toggleAction, QtWidgets.QLineEdit.TrailingPosition)
        self.toggleAction.triggered.connect(self.toggle_PW_visibility)

        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.LE_psk)
        self.verticalLayout_2.addLayout(self.formLayout_3)
        self.verticalLayout.addWidget(self.groupBox_WiFi)

        spacerItem = QtWidgets.QSpacerItem(13, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox_Conf = QtWidgets.QDialogButtonBox(RaspiSshConnection)
        self.buttonBox_Conf.setOrientation(QtCore.Qt.Horizontal)
        connectiondialogbuttons = QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Help|QtWidgets.QDialogButtonBox.Cancel
        self.buttonBox_Conf.setStandardButtons(connectiondialogbuttons)
        self.buttonBox_Conf.button(QtWidgets.QDialogButtonBox.Ok).setText("Connect")
        self.verticalLayout.addWidget(self.buttonBox_Conf)
        self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.msg = QMessageBox()
        self.msg.setWindowTitle("SSH Connection")
        self.msg.setStandardButtons(QMessageBox.NoButton)
        self.msg.setWindowIcon(QtGui.QIcon(":/icon/ssh-raspi.png"))
        

        with open(os.path.join(os.getcwd(), "./config/Config.json"),'r',encoding="utf8") as f:
            self.setup_dict = json.load(f)
            f.close()
        
        RaspiSshConnection.setWindowTitle("Rpi SSH Connection")
        self.groupBox_SSH.setTitle("SSH Config")
        self.LB_IP.setText("IP Address")
        self.LE_IP.setPlaceholderText("Rpi device IP")
        self.LE_IP.setText(self.setup_dict["SSHConf"]["IPAddress"])
        self.LE_IP.setCursorPosition(0) # holds the current cursor position e.g. 0 for line edit
        self.LB_Port.setText("Port")
        self.LE_Port.setPlaceholderText("SSH Default Port: 22")
        self.LE_Port.setText(self.setup_dict["SSHConf"]["Port"])
        self.LB_User.setText("User")
        self.LE_User.setPlaceholderText("Rpi Username: pi")
        self.LE_User.setText(self.setup_dict["SSHConf"]["User"])
        self.LB_Key.setText("Key")
        self.LE_Key.setPlaceholderText("Rpi login password: pass")
        self.LE_Key.setText(self.setup_dict["SSHConf"]["Key"])
        self.LB_Log.setText("Log")
        self.LE_LogPath.setPlaceholderText("Save command and output in e.g. logging.log")
        self.LE_LogPath.setText(self.setup_dict["SSHConf"]["Log"])
        self.groupBox_WiFi.setTitle("WiFi")
        self.LB_ssid.setText("SSID")
        self.LB_psk.setText("Password")
        self.LB_psk.setOpenExternalLinks(True)
        self.LE_psk.setPlaceholderText("WiFi network password")
        self.LE_psk.setText(self.setup_dict["WiFi"]["psk"])

#############################
# event signal
#############################

        #self.retranslateUi(RaspiSshConnection)
        self.buttonBox_Conf.accepted.connect(RaspiSshConnection.accept) # type: ignore
        self.buttonBox_Conf.rejected.connect(RaspiSshConnection.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(RaspiSshConnection)
 
        self.find_ssid() # find visable ssid
        # self.B_ImgPath.clicked.connect(self.OCfolder)
        self.buttonBox_Conf.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.save_param_validate_input_connect_wifi)
        self.buttonBox_Conf.button(QtWidgets.QDialogButtonBox.Help).clicked.connect(self.confighelp)
        self.buttonBox_Conf.button(QtWidgets.QDialogButtonBox.Apply).clicked.connect(lambda: self.validate_input_save_parma(validate=True))
        self.CB_ssid.combobox_click_event.connect(self.find_ssid)


#############################
# Functions
#############################
    def eventFilter(self, obj, event):
        '''
        BackSpace key press event for object iP LineEdit
        '''
        # Check if the event is for the LE_IP QLineEdit and is a key press
        if obj == self.LE_IP and event.type() == QtCore.QEvent.KeyPress:
            # Check for Delete key press
            if event.key() == QtCore.Qt.Key.Key_Backspace:
                cursor_position = self.LE_IP.cursorPosition()
                ip_text = self.LE_IP.displayText()

                if cursor_position>0 and ip_text[cursor_position - 1].isdigit():                                     
                    new_ip_text = ip_text[:cursor_position-1] + "_" + ip_text[cursor_position:]
                    self.LE_IP.setText(new_ip_text)
                    self.LE_IP.setCursorPosition(cursor_position - 1)  # Move cursor left

        # Call the base class event filter for any other events
        return super(Ui_RaspiSshConnection, self).eventFilter(obj, event)

    def toggle_PW_visibility(self):
        '''
        toggle to change wifi password visibility
        '''
        if self.toggleAction.isChecked(): # Check if the toggle action is checked
            self.LE_psk.setEchoMode(QtWidgets.QLineEdit.Normal) # Show password
        else:
            self.LE_psk.setEchoMode(QtWidgets.QLineEdit.Password) # Hide password

    def find_ssid(self):
        '''
        find visiable WiFi networkname and add ssid into combobox
        if the ssid, which was saved in config.json, is visiable, this ssid will be move up to the first index 
        '''
        try:
            WiFivisible = subprocess.check_output('netsh wlan show networks', shell=True).decode('ascii', errors='ignore').strip()
            SSIDlist = [line for line in WiFivisible.splitlines() if 'ssid' in line.lower()] # save ssid info in list
            self.CB_ssid.clear() # clear all items in combobox
            if len(SSIDlist) != 0:
                for SSID in SSIDlist:
                    if SSID.split(':')[-1][1:]:
                        self.CB_ssid.addItem(SSID.split(':')[-1][1:]) # add detected ssid to combobox 
                index = self.CB_ssid.findText(self.setup_dict["WiFi"]["ssid"]) # get index of specific ssid return the index or -1 (not find)
                if index > 0 : # if index > 0
                    item_text = self.CB_ssid.itemText(index) # get ssid by index
                    self.CB_ssid.removeItem(index) # remove time by index
                    self.CB_ssid.insertItem(0, item_text) # insert item at index 0
                    self.CB_ssid.setCurrentIndex(0) # holds the index 0 of the current item in the combobox
        except Exception as e:
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.setText(f"{e} Please check WiFi setup on your PC!")
            QTimer.singleShot(3000, lambda : self.msg.done(0))
            self.msg.show()
            
    def create_wifi_profile_xml(self, ssid, password) -> None:
        '''
        create wifi profile xml file
        '''

        WLANProfile = ET.Element("WLANProfile", xmlns="http://www.microsoft.com/networking/WLAN/profile/v1") # Create root element

        name = ET.SubElement(WLANProfile, "name") # Create child elements
        name.text = ssid

        SSIDConfig = ET.SubElement(WLANProfile, "SSIDConfig")
        SSID = ET.SubElement(SSIDConfig, "SSID")
        SSID_name = ET.SubElement(SSID, "name")
        SSID_name.text = ssid

        connectionType = ET.SubElement(WLANProfile, "connectionType")
        connectionType.text = "ESS"

        connectionMode = ET.SubElement(WLANProfile, "connectionMode")
        connectionMode.text = "manual"

        MSM = ET.SubElement(WLANProfile, "MSM")
        security = ET.SubElement(MSM, "security")
        authEncryption = ET.SubElement(security, "authEncryption")
        authentication = ET.SubElement(authEncryption, "authentication")
        authentication.text = "WPA2PSK"
        encryption = ET.SubElement(authEncryption, "encryption")
        encryption.text = "AES"
        useOneX = ET.SubElement(authEncryption, "useOneX")
        useOneX.text = "false"

        sharedKey = ET.SubElement(security, "sharedKey")
        keyType = ET.SubElement(sharedKey, "keyType")
        keyType.text = "passPhrase"
        protected = ET.SubElement(sharedKey, "protected")
        protected.text = "false"
        keyMaterial = ET.SubElement(sharedKey, "keyMaterial")
        keyMaterial.text = password

        tree = ET.ElementTree(WLANProfile) # Create XML tree

        with open("WiFiProfile.xml", "wb") as f: # Write to file
            tree.write(f, encoding="utf-8", xml_declaration=True)


    def delete_file(self, filename) -> None:
        '''
        delete temporary file by path
        '''
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass
        except Exception as e:
            pass

    def wificonnect(self) -> bool:
        '''
        connect specific wifi network by ssid and password
        '''
        ssid = self.CB_ssid.currentText() # read ssid frome Combobox 
        psk = self.LE_psk.text() # read psk frome LineEditor 
        wifimsg = QMessageBox()
        wifimsg.setWindowTitle("Configuration")
        wifimsg.setStandardButtons(QMessageBox.NoButton)
        wifimsg.setWindowIcon(QtGui.QIcon(":/icon/ssh-raspi.png"))
        wifimsg.setWindowTitle("WiFi Status")

        self.create_wifi_profile_xml(ssid, psk) # create WiFiProfile.xml within ssid and psk 
        WiFiexist = subprocess.getoutput(f' netsh wlan show networks | findstr "\<{ssid}\>"') # check if ssid exist
        # if ssid exits
        if ssid in WiFiexist:
            current_connected_ssid = subprocess.getoutput('netsh wlan show interfaces | Findstr "\<SSID\>"').split(':')[-1].strip() # check if this ssid already connected
            wifimsg.setIcon(QMessageBox.Information)
            if ssid != current_connected_ssid: # if ssid is not connected
                subprocess.check_output('netsh wlan add profile filename=WiFiProfile.xml', shell=True) # add wifi profile 
                # connect wifi with ssid
                subprocess.check_output(f'netsh wlan connect name="{ssid}"', shell=True)
                # wait secs wilfi connect to build needs time, Recommended waiting time >=8s
                wifimsg.setText("WiFi {} is connecting...".format(ssid))
                QTimer.singleShot(8000, lambda : wifimsg.done(0))
                wifimsg.exec()

            if 'Online' in subprocess.getoutput('netsh wlan show interfaces | Findstr /c:"Signal" && Echo Online || Echo Offline'):
                wifimsg.setText("WiFi {} connected".format(ssid))
                QTimer.singleShot(1000, lambda : wifimsg.done(0))
                wifimsg.exec()
                self.delete_file('WiFiProfile.xml')
                return True
                
            wifimsg.setIcon(QMessageBox.Critical)
            wifimsg.setText("WiFi {} connection failed, please check SSID and Key".format(ssid))
            QTimer.singleShot(1500, lambda : wifimsg.done(0))
            wifimsg.show()
            return False

        wifimsg.setIcon(QMessageBox.Critical)
        wifimsg.setText("WiFi {} not available, please check network connection".format(ssid))
        QTimer.singleShot(1500, lambda : wifimsg.done(0))
        wifimsg.show()
        self.delete_file('WiFiProfile.xml')
        return False          

    def validate_input(self)-> bool:
        '''
        validate the input parameter by QValidator, if all fields are valid, it return true otherweise return false 
        '''
        self.msg.setIcon(QMessageBox.Critical)
        IPState = self.IP_validator.validate(self.LE_IP.text(), 0)[0]
        PortState = self.Port_validator.validate(self.LE_Port.text(), 0)[0]
        UserState = self.User_validator.validate(self.LE_User.text(), 0)[0]
        KeyState = self.Key_validator.validate(self.LE_Key.text(), 0)[0]
        PSKState = self.PSK_validator.validate(self.LE_psk.text(), 0)[0]
        LogState = self.Log_validator.validate(self.LE_LogPath.text(), 0)[0]
        # IP
        if IPState != QtGui.QValidator.Acceptable:
            self.msg.setText(f"IP {self.LE_IP.text()} is unvalid")
            QTimer.singleShot(1500, lambda : self.msg.done(0))
            self.msg.show()
            return False
        # Port
        elif PortState != QtGui.QValidator.Acceptable:
            self.msg.setText(f"Port {self.LE_Port.text()} is unvalid")
            QTimer.singleShot(1500, lambda : self.msg.done(0))
            self.msg.show()
            return False
        # User
        elif UserState != QtGui.QValidator.Acceptable:
            self.msg.setText(f"User {self.LE_User.text()} is unvalid")
            QTimer.singleShot(1500, lambda : self.msg.done(0))
            self.msg.show()
            return False
        # Key
        elif KeyState != QtGui.QValidator.Acceptable:
            self.msg.setText(f"Key {self.LE_Key.text()} is unvalid")
            QTimer.singleShot(1500, lambda : self.msg.done(0))
            self.msg.show()
            return False
        # Log
        elif LogState != QtGui.QValidator.Acceptable:
            self.msg.setText(f"Log {self.LE_LogPath.text()} extension is unvalid")
            QTimer.singleShot(1500, lambda : self.msg.done(0))
            self.msg.show()
            return False
        # SSID
        elif len(self.CB_ssid.currentText()) == 0:
            self.msg.setText(f"SSID {self.CB_ssid.currentText()} is unvalid")
            QTimer.singleShot(1500, lambda : self.msg.done(0))
            self.msg.show()
            return False
        # Psk
        elif PSKState != QtGui.QValidator.Acceptable:
            self.msg.setText(f"password {self.LE_psk.text()} is unvalid")
            QTimer.singleShot(1500, lambda : self.msg.done(0))
            self.msg.show()
            return False

        return True

    def validate_input_save_parma(self, validate:bool) -> None:
        '''
        validate input paramter through QValidator for each field and save them in Config.json file 
        '''

        self.setup_dict['SSHConf']['User'] = self.LE_User.text()
        self.setup_dict['SSHConf']['Port'] = self.LE_Port.text()
        self.setup_dict['SSHConf']['IPAddress'] = self.LE_IP.text()
        self.setup_dict['SSHConf']['Key'] = self.LE_Key.text()
        self.setup_dict['SSHConf']['Log'] = self.LE_LogPath.text()
        self.setup_dict['WiFi']['ssid'] = self.CB_ssid.currentText()
        self.setup_dict['WiFi']['psk'] = self.LE_psk.text()

        if validate:
            if self.validate_input():
                with open(os.path.join(os.getcwd(), "Config.json"), 'w') as f:
                    json.dump(self.setup_dict, f)
                    f.close()

                self.msg.setIcon(QMessageBox.Information)
                self.msg.setText(f"configuration saved")
                QTimer.singleShot(1000, lambda : self.msg.done(0))
                return self.msg.show()
        else:
            with open(os.path.join(os.getcwd(), "./config/Config.json"), 'w') as f:
                json.dump(self.setup_dict, f)
                f.close()
            
    def remove_zeros_from_ip(self, ip_add) -> str:
        '''
        split the IP address into its octets and convert each octet to an integer with no leading zeros
        return the new IP address with no leading zeros
        '''
        new_ip_add = ".".join([str(int(i)) for i in ip_add.split(".")])  
        return new_ip_add

    def save_param_validate_input_connect_wifi(self):
        '''
        validate input parameter and connect wifi, if wifi is connected scusessfully, pass the parameter to slots
        '''
        self.validate_input_save_parma(validate=False)
        self.Confwin = QtWidgets.QDialog()
        self.ui = Ui_RaspiSshConnection()
        self.ui.setup_ui(self.Confwin)

        if self.validate_input() and self.wificonnect():
            User = self.LE_User.text()
            Port = self.LE_Port.text()
            IP = self.remove_zeros_from_ip(self.LE_IP.text())
            Key = self.LE_Key.text()
            Log = self.LE_LogPath.text()
                   
            paramdict = {"Port": Port, "IP": IP, "User": User,
            "Key": Key, "Log": Log}
            
            self.SSHConnection_signal.emit(paramdict) # pass parameter dict to slot
            return self.Confwin.accept
        
        return self.Confwin.show()


if __name__ == "__main__":
    dialogapp = QtWidgets.QApplication(sys.argv)
    RaspiSshConnection = QtWidgets.QDialog()
    connectiondialogui = Ui_RaspiSshConnection()
    connectiondialogui.setup_ui(RaspiSshConnection)
    RaspiSshConnection.show()
    sys.exit(dialogapp.exec_())
