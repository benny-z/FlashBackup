from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from UI import Ui_MainWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QDialog()
    ui = Ui_MainWindow()
    ui.setupUi(window)

    window.show()
    sys.exit(app.exec_())
