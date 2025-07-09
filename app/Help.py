# -*- coding: utf-8 -*-


import os

import Icons
from PyQt5 import QtCore, QtGui, QtWidgets

os.environ["QT_ENABLE_HIGHDPI_SCALING"]   = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ["QT_SCALE_FACTOR"]             = "1"
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons

class Ui_Form(object):
    def setup_ui(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 400)
        Form.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
        Form.setWindowIcon(QtGui.QIcon(":/icon/help.png"))
        self.gridLayout_3 = QtWidgets.QGridLayout(Form)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.LB_Contact = QtWidgets.QLabel(Form)
        self.LB_Contact.setObjectName("LB_Contact")
        self.gridLayout.addWidget(self.LB_Contact, 0, 0, 1, 1)
        self.LB_Name = QtWidgets.QLabel(Form)
        self.LB_Name.setOpenExternalLinks(True)
        self.LB_Name.setObjectName("LB_Name")
        self.gridLayout.addWidget(self.LB_Name, 0, 1, 1, 1)
        self.gridLayout_3.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 321, 178))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textBrowser = QtWidgets.QTextBrowser(self.scrollAreaWidgetContents)
        self.textBrowser.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textBrowser)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout_3.addWidget(self.scrollArea, 1, 0, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setWindowTitle("About USB Tool")
        self.LB_Contact.setText("Contact: ")
        self.LB_Name.setText("<a href='mailto:xiaochuan_lu@yahoo.com'>Xiaochuan Lu</a>")
        self.textBrowser.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
        "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
        "p, li { white-space: pre-wrap; }\n"
        "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
        "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt; font-weight:600; text-decoration: underline;\">Quick User Guide</span></p>\n"
        "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt; font-weight:600; text-decoration: underline;\"><br /></p>\n"
        #### Introduction
        "<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Introduction:</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">\nThe USB Emulator is a tool developed by Software Test Entertainment. It is designed to simplify the testing of supported USB devices and enhance the team's media-device testing capabilities</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"

        #### Precondition #<a href=\"https://github.com/luxc1101/raspi-usb-sim/blob/master/README.md\">Raspi USB Tool</a>
        "<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Precondition:</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">1.</span> Prepare hardware (RaspberryPi zero W, USB Mico-B Cable (OTG), USB Mico-B Cable (Power), micoSD Card, etc.) for more details please read <a href=\"https://github.com/luxc1101/raspi-usb-sim/blob/master/README.md\">Raspi USB Tool</a> </p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">2.</span> Plug in a fully prepared microSD card with the desired OS, necessary scripts, and installed packages</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">3.</span> Power Paspberry Pi Zero W by connecting its PWR port to a PC USB port or an external power supply (of output 5V). Hint: A solid green light indicates a proper connection</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">4.</span> Connect the Rpi device and the DUT through a USB Micro-B to USB A cable</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">5.</span> Plug in a USB WiFi receiver/adapter to the test PC (if your computer cannot receive WiFi without an adapter)</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
        #### Configuration
        "<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Configuration:</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">1.</span> Click on <span style=\" font-weight:600;\">SSH Connect</span> (Raspberry icon) to configure the SSHClient and WiFi parameters and establish an SSH connection</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">2.</span> Click on <span style=\" font-weight:600;\">Project</span> on the menubar to select the desired environment</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
        #### Features:
        "<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Features:</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\">Mass Storage Class (MSC):</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:10px;\"><span style=\" font-weight:600;\">1.</span> The <span style=\" font-weight:600;\">MSC Tab</span> enables the tester to simulate their desired File System (FS), such as exFAT and NTFS, etc. To begin, select your desired FS and click on Mount</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:10px;\"><span style=\" font-weight:600;\">2.</span> If the selected FS exists, the LED will indicate its existence. If not, this file system will first be created first, for which the tester must define parameters such as the disc size in the command window</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
        
        "<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\">USB Peripherals: (Ethernet Control Model, Human Interface Device, Communication Device Class)</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:10px;\"><span style=\" font-weight:600;\">1.</span> The <span style=\" font-weight:600;\">ECM, HID and CDC</span> Tabs enable the user to test whether the DUT supports an emulated USB device. These tabs usually list all devices that could be mounted directly. However, if the tester wants to see if some device from beyond the list is supported, they must input its customized VID and PID numbers</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-weight:600;\"><br /></p>\n"
        #### Hint:
        "<p style=\" margin-top:0px; margin-bottom:5px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-weight:600;\">Hints:</span></p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">1.</span> Inputting value or sending a command to the SSHClent through <span style=\" font-weight:600;\">Command LineEdit</span> is also possible</p>\n"
        "<p style=\" margin-top:0px; margin-bottom:2px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:5px;\"><span style=\" font-weight:600;\">2.</span> Once the <span style=\" font-weight:600;\">POWER OFF RASPI</span> in in command line drop-down has been sent, the Rpi device will be powered off and can only be powered on again by re-plugging USB Micro-B cable</p>\n"
        "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
        "</body></html>")
        self.textBrowser.setOpenExternalLinks(True) # Specifies whether QTextBrowser should automatically open links to external sources
        
# if __name__ == "__main__":
#     import sys
#     app = QtWidgets.QApplication(sys.argv)
#     Form = QtWidgets.QWidget()
#     ui = Ui_Form()
#     ui.setup_ui(Form)
#     Form.show()
#     sys.exit(app.exec_())
