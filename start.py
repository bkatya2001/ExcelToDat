from PyQt5.QtWidgets import QApplication
import sys
import mywindow as mw

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = mw.MainWindow()
    mw.show()
    sys.exit(app.exec())
