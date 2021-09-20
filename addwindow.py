import os
import shutil
import datetime
import re
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QFormLayout, \
    QLineEdit, QTextEdit, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize


# Окно для создания нового испытания
class AddWindow(QMainWindow):
    def __init__(self, main_window):
        QMainWindow.__init__(self)

        self.main_window = main_window

        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Добавить испытание")
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        vertical_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.name_edit = QLineEdit()
        form_layout.addRow(QLabel("Название:"), self.name_edit)
        self.person_edit = QLineEdit()
        form_layout.addRow(QLabel("Ф.И.О. сотрудника:"), self.person_edit)
        self.data_edit = QTextEdit()
        form_layout.addRow(QLabel("Дополнительная информация:"), self.data_edit)
        vertical_layout.addLayout(form_layout)

        choose_btn = QPushButton("Выбрать .xlsx файл")
        choose_btn.clicked.connect(self.choose_file)
        vertical_layout.addWidget(choose_btn)

        self.file_lbl = QLabel("")
        vertical_layout.addWidget(self.file_lbl)

        self.create_btn = QPushButton("Создать испытание")
        self.create_btn.clicked.connect(self.create_test)
        self.create_btn.setEnabled(False)
        vertical_layout.addWidget(self.create_btn)

        self.central_widget.setLayout(vertical_layout)

    def choose_file(self):  # Выбор файла с таблицей
        file = QFileDialog.getOpenFileName(self, 'Выбрать .xlsx файл', 'C:/', "Excel Workbook (*.xlsx)")[0]
        if file != "":
            self.file_lbl.setText(file)
            self.create_btn.setEnabled(True)
        else:
            self.create_btn.setEnabled(False)

    def create_test(self):  # Создание испытания
        tests = os.listdir(os.path.join(self.main_window.path, self.main_window.current_project))
        pat = "[\w-]+"  # Шаблон для названия
        text = self.name_edit.text()
        if re.sub(pat, "", text, 1) == "":
            if not (text in tests):
                path = os.path.join(self.main_window.path, self.main_window.current_project, text)
                os.mkdir(path)
                shutil.copy(self.file_lbl.text(), path)  # Копируем файл с таблицей
                os.mkdir(os.path.join(path, "Изменённые_данные"))

                # Формируем файл с дополнительной информацией
                meta_file = open(os.path.join(path, "metadata.txt"), "w")
                meta_file.write(str(datetime.datetime.now()) + '\n')
                meta_file.write("Расположение файла: " + os.path.join(path, "metadata.txt") + '\n')
                meta_file.write("Название испытания: " + text + '\n')
                meta_file.write("Ф.И.О. сотрудника: " + self.person_edit.text() + '\n')
                meta_file.write("Дополнительная информация: " + self.data_edit.toPlainText())
                meta_file.close()
                self.main_window.update_tests_layout()
                self.close()
            else:
                QMessageBox.about(self, "Ошибка", "Испытание с таким названием уже существует")
        else:
            QMessageBox.about(self, 'Ошибка', 'Название проекта может состоять из букв, цифр, а также знаков '
                                              'тире и нижнего подчёркивания.')
