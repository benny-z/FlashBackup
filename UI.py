from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from os.path import exists
from controller import add_new_record

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(639, 600)
        MainWindow.setMinimumSize(639, 600)
        MainWindow.setMaximumSize(639, 600)
        self.widget = QWidget(MainWindow)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.label = QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(10, 10, 211, 16))
        self.label.setObjectName(_fromUtf8("label"))

        self.select_drive_label = QLabel(self.widget)
        self.select_drive_label.setGeometry(QtCore.QRect(10, 30, 211, 16))
        self.select_drive_label.setObjectName(_fromUtf8("select_drive_label"))

        self.back_upLbl = QLabel(self.widget)
        self.back_upLbl.setGeometry(QtCore.QRect(10, 290, 61, 16))
        self.back_upLbl.setObjectName(_fromUtf8("back_upLbl"))

        self.okBtn = QPushButton(self.widget)
        self.okBtn.setGeometry(QtCore.QRect(80, 320, 61, 31))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Ampersand"))
        font.setPointSize(18)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.okBtn.setFont(font)
        self.okBtn.setFocusPolicy(QtCore.Qt.TabFocus)
        self.okBtn.setAutoFillBackground(True)
        self.okBtn.setAutoDefault(False)
        self.okBtn.setDefault(False)
        self.okBtn.setFlat(True)
        self.okBtn.setObjectName(_fromUtf8("okBtn"))
        self.backup_pathTxtBx = QLineEdit(self.widget)
        self.backup_pathTxtBx.setGeometry(QtCore.QRect(76, 288, 141, 20))
        self.backup_pathTxtBx.setObjectName(_fromUtf8("backup_pathTxtBx"))
        self.scrollArea = QScrollArea(self.widget)
        self.scrollArea.setGeometry(QtCore.QRect(10, 50, 211, 231))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))

        self.scrollAreaWidgetContentsLayout = QVBoxLayout()
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setLayout(
            self.scrollAreaWidgetContentsLayout)
        self.scrollAreaWidgetContents.setObjectName(
            _fromUtf8("scrollAreaWidgetContents"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.buttonGroup = QButtonGroup()

        for drive in QtCore.QDir.drives():
            drive_name = drive.absoluteFilePath().replace('/', '\\')
            ip = QFileIconProvider()
            my_button = QPushButton(drive_name)
            my_button.setIcon(ip.icon(drive))
            my_button.setCheckable(True)
            my_button.setFlat(True)
            buttonSize = QtCore.QSize(120, 70)
            my_button.setFixedSize(buttonSize)
            my_button.setIconSize(buttonSize)

            self.buttonGroup.addButton(my_button)
            self.scrollAreaWidgetContentsLayout.addWidget(my_button)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.setConnections()

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QApplication.translate(
            "MainWindow", "FlashBackup", None))
        self.label.setText(QApplication.translate(
            "MainWindow", "Make sure your device is connected!", None))
        self.select_drive_label.setText(QApplication.translate(
            "MainWindow", "Please select your removable drive:", None))
        self.back_upLbl.setText(QApplication.translate(
            "MainWindow", "backup path:", None))
        self.okBtn.setText(QApplication.translate(
            "MainWindow", "Ok", None))

    def setConnections(self):
        self.okBtn.clicked.connect(
            lambda: self.okBtnHandler(self.buttonGroup.checkedButton()))
        self.backup_pathTxtBx.mousePressEvent = self.selectBackupDirecotry

    def okBtnHandler(self, selected_button):
        if selected_button is None:
            QMessageBox.warning(
                None, ":(", "You must specify a drive you would like to backup")
            return
        if '' == self.backup_pathTxtBx.text() or not exists(self.backup_pathTxtBx.text()):
            QMessageBox.warning(None, "FUUU", "Please select a valid directory\n\
for the backup to be saved to")
            return
        try:
            add_new_record(
                str(selected_button.text()), str(self.backup_pathTxtBx.text()))
        except Exception as e:
            QMessageBox.warning(None, "Somekinda error", str(e))

    def selectBackupDirecotry(self, event):
        folder = QFileDialog.getExistingDirectory(
            None, "Please select a folder where your backup will be saved")
        if '' != folder:
            self.backup_pathTxtBx.setText(folder)
