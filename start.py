from PyQt5.QtWidgets import QApplication
import sys
import os
import filewindow as fw

if __name__ == "__main__":
    app = QApplication(sys.argv)

    try:
        os.mkdir(os.path.join(os.getcwd(), "Projects"))
    except OSError:
        pass

    fw.path = os.path.join(os.getcwd(), "Projects")
    fw.projects = os.listdir(fw.path)
    fw = fw.FileWindow()
    fw.show()
    sys.exit(app.exec())
