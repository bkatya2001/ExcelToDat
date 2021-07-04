import os
import shutil
import datetime
import re
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QFormLayout, \
    QLineEdit, QTextEdit, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize
import filewindow as fw


# Окно для создания нового испытания
class AddWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Добавить испытание")
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.vertical_layout = QVBoxLayout()
        self.form_layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.form_layout.addRow(QLabel("Название:"), self.name_edit)
        self.person_edit = QLineEdit()
        self.form_layout.addRow(QLabel("Ф.И.О. сотрудника:"), self.person_edit)
        self.data_edit = QTextEdit()
        self.form_layout.addRow(QLabel("Дополнительная информация:"), self.data_edit)
        self.vertical_layout.addLayout(self.form_layout)

        choose_btn = QPushButton("Выбрать .xlsx файл")
        choose_btn.clicked.connect(self.choose_file)
        self.vertical_layout.addWidget(choose_btn)

        self.file_lbl = QLabel("")
        self.vertical_layout.addWidget(self.file_lbl)

        self.create_btn = QPushButton("Создать испытание")
        self.create_btn.clicked.connect(self.create_test)
        self.create_btn.setEnabled(False)
        self.vertical_layout.addWidget(self.create_btn)

        self.central_widget.setLayout(self.vertical_layout)

    def choose_file(self):  # Выбор файла с таблицей
        file = QFileDialog.getOpenFileName(self, 'Выбрать .xlsx файл', 'C:/', "Excel Workbook (*.xlsx)")[0]
        if file != "":
            self.file_lbl.setText(file)
            self.create_btn.setEnabled(True)
        else:
            self.create_btn.setEnabled(False)

    def create_test(self):  # Создание испытания
        tests = os.listdir(fw.current_project)
        pat = "[A-Za-zА-Яа-я]\\d*"  # Шаблон для названия
        text = self.name_edit.text()
        if re.match(pat, text):
            if not (text in tests):
                path = os.path.join(fw.current_project, text)
                os.mkdir(path)
                shutil.copy(self.file_lbl.text(), path)  # Копируем файл с таблицей

                # Формируем файл с дополнительной информацией
                meta_file = open(path + "\\metadata.txt", "w")
                meta_file.write(str(datetime.datetime.now()) + '\n')
                meta_file.write("Название испытания: " + text + "\n")
                meta_file.write("Ф.И.О. сотрудника: " + self.person_edit.text() + '\n')
                meta_file.write("Дополнительная информация: " + self.data_edit.toPlainText())
                meta_file.close()
                self.close()
                self.fw = fw.FileWindow()
                self.fw.show()
            else:
                QMessageBox.about(self, "Ошибка", "Испытание с таким названием уже существует")
        else:
            QMessageBox.about(self, "Ошибка", "Название должно состоять из букв и может содержать цифры")
