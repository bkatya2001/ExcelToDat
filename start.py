from PyQt5.QtWidgets import QApplication
import sys
import os
import filewindow as fw

if __name__ == "__main__":
    app = QApplication(sys.argv)

    fw = fw.FileWindow()
    fw.show()
    sys.exit(app.exec())
