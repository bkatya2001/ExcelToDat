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
        # Находим файл с таблицей
        xlsx = os.listdir(os.path.join(self.main_window.path, self.main_window.current_project,
                                       self.main_window.current_test))
        xlsx = [i for i in xlsx if ('.xlsx' in i) and i != 'out.xlsx']
        self.main_window.file_path = os.path.join(self.main_window.path, self.main_window.current_project,
                                                  self.main_window.current_test, xlsx[0])

        if self.main_window.file_path != "":
            self.main_window.data = pd.read_excel(self.main_window.file_path)

        self.finishSignal.emit("Готово!")
