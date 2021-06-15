from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QScrollArea, QGroupBox
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize
import os
import addwindow as aw
import datawindow as dw

# Путь к папке с испытаниями и директории оттуда
path = os.getcwd() + "\\Tests"
files = os.listdir(path)
fpath = ""

# Окно-проводник по существующим испытаниям
class FileWindow(QMainWindow):
    def __init__(self):
        global path
        global files

        QMainWindow.__init__(self)

        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Испытания")
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.vertical_layout = QVBoxLayout()
        self.main_lbl = QLabel("Испытания")
        self.vertical_layout.addWidget(self.main_lbl)

        # Добавляем кнопки для всех файлов, лежащих в папке
        # Добавляем ScrollArea, чтобы можно было прокручивать вниз,
        # если файлов очень много
        if len(files) == 0:
            self.empty_lbl = QLabel("Нет созданных испытаний")
            self.vertical_layout.addWidget(self.empty_lbl)
        else:
            self.box = QGroupBox()
            self.inner_layout = QVBoxLayout()
            for i in range(len(files)):  # Добавляем каждую внутреннюю директорию
                self.button = QPushButton(files[i])
                self.button.setStyleSheet('background: transparent; text-align: left')
                # В обработчик нажатия передаём путь, чтобы определять, что нужно открыть
                self.button.clicked.connect(
                    lambda state, file_path=(path + '\\' + files[i]): self.button_pushed(file_path))
                self.inner_layout.addWidget(self.button)
                inner_files = os.listdir(path + "\\" + files[i])
                for j in range(len(inner_files)):  # Добавляем каждый файл из внутренних директорий
                    self.button = QPushButton(inner_files[j])
                    self.button.setContentsMargins(20, 11, 11, 11)
                    self.button.setStyleSheet('background: transparent')
                    # В обработчик нажатия передаём путь, чтобы определять, что нужно открыть
                    self.button.clicked.connect(
                        lambda state, file_path=(path + '\\' + files[i] + '\\' + inner_files[j]): self.button_pushed(file_path))
                    self.inner_layout.addWidget(self.button)

            self.box.setLayout(self.inner_layout)
            self.scroll = QScrollArea()
            self.scroll.setWidget(self.box)
            self.scroll.setWidgetResizable(True)
            self.vertical_layout.addWidget(self.scroll)
            self.add_btn = QPushButton("Создать испытание", self)
            self.add_btn.clicked.connect(self.add_test)
            self.vertical_layout.addWidget(self.add_btn)

        self.central_widget.setLayout(self.vertical_layout)

    def button_pushed(self, file_path):
        global fpath
        folders = file_path.split('\\')
        # Файлы открываем, испытания - вызываем другое окно
        if folders[len(folders) - 2] == 'Tests':
            xlsx = os.listdir(file_path)
            for i in xlsx:
                if ".xlsx" not in i:
                    xlsx.remove(i)
            fpath = file_path + "\\" + xlsx[0]
            self.dw = dw.DataWindow()
            self.dw.show()
        else:
            os.system(file_path)

    def add_test(self):
        self.aw = aw.AddWindow()
        self.aw.show()
        self.close()
