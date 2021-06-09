from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QScrollArea, QGroupBox
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize
import os
import graphwindow as gw

path = os.getcwd() + "\\Tests"
files = os.listdir(path)


class FileWindow(QMainWindow):
    def __init__(self):
        global path
        global files

        QMainWindow.__init__(self)

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
            for i in range(len(files)):
                self.button = QPushButton(files[i])
                self.button.setStyleSheet('background: transparent; text-align: left')
                self.button.clicked.connect(
                    lambda state, file_path=(path + '\\' + files[i]): self.button_pushed(file_path))
                self.inner_layout.addWidget(self.button)
                inner_files = os.listdir(path + "\\" + files[i])
                for j in range(len(inner_files)):
                    self.button = QPushButton(inner_files[j])
                    self.button.setContentsMargins(20, 11, 11, 11)
                    self.button.setStyleSheet('background: transparent')
                    self.button.clicked.connect(
                        lambda state, file_path=(path + '\\' + files[i] + '\\' + inner_files[j]): self.button_pushed(file_path))
                    self.inner_layout.addWidget(self.button)

            self.box.setLayout(self.inner_layout)
            self.scroll = QScrollArea()
            self.scroll.setWidget(self.box)
            self.scroll.setWidgetResizable(True)
            self.vertical_layout.addWidget(self.scroll)

        self.central_widget.setLayout(self.vertical_layout)

    def button_pushed(self, file_path):
        folders = file_path.split('\\')
        if folders[len(folders) - 2] == 'Tests':
            self.gw = gw.GraphWindow()
            self.gw.file_path = file_path
            self.gw.show()
            print(self.gw.file_path)
        else:
            os.system(file_path)
