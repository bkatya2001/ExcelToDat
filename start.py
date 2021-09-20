from PyQt5.QtWidgets import QApplication
import sys
import os
import mainwindow as mw
from qt_material import apply_stylesheet


if __name__ == "__main__":
    app = QApplication(sys.argv)

    apply_stylesheet(app, theme='dark_lightgreen.xml')
    stylesheet = app.styleSheet()
    with open('custom.css') as file:
        app.setStyleSheet(stylesheet + file.read().format(**os.environ))

    try:
        os.mkdir(os.path.join(os.getcwd(), "Projects"))
    except OSError:
        print('')

    mw = mw.MainWindow()
    mw.showMaximized()
    sys.exit(app.exec())
