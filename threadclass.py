import os
import pandas as pd

from PyQt5.QtCore import QThread, pyqtSignal


class ThreadClass(QThread):
    startSignal = pyqtSignal(int)
    finishSignal = pyqtSignal(str)

    def __init__(self, main_window, parent=None):
        super(ThreadClass, self).__init__(parent)
        self.main_window = main_window

    def run(self):
        if '.data' in self.main_window.file_path:
            self.main_window.data = pd.read_csv(self.main_window.file_path, ' ', index_col=False)
        else:
            if self.main_window.file_path != "":
                self.main_window.data = pd.read_excel(self.main_window.file_path)

        self.finishSignal.emit("Готово!")
