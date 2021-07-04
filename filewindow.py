import re

from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QScrollArea, QGroupBox, QHBoxLayout, QInputDialog, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtCore import QSize
import os
import addwindow as aw
import datawindow as dw

# Путь к папке с проектами и директории оттуда
path = os.path.join(os.getcwd(), "Projects")
projects = os.listdir(path)
current_project = ""  # Имя проекта
current_test = ""  # Имя испытания


# Окно-проводник по существующим испытаниям
class FileWindow(QMainWindow):
    def __init__(self):
        global path
        global projects

        QMainWindow.__init__(self)

        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("ExcelToData")
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.project_layout = QVBoxLayout()
        self.tests_layout = QVBoxLayout()

        self.main_layout.addLayout(self.project_layout)
        self.main_layout.addLayout(self.tests_layout)
        self.central_widget.setLayout(self.main_layout)

        self.update_project_layout()
        self.update_tests_layout()

    # Удаление всех элементов из Layout для дальнейшего обновления
    def clear_layout(self, layout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().setParent(None)

    # Обновление Layout (Проекты)
    def update_project_layout(self):
        self.clear_layout(self.project_layout)

        project_lbl = QLabel("Проекты:")
        self.project_layout.addWidget(project_lbl)

        if len(projects) == 0:
            empty_lbl = QLabel("Нет созданных проектов")
            self.project_layout.addWidget(empty_lbl)
        else:
            box = QGroupBox()
            inner_layout = QVBoxLayout()
            for folder in projects:
                button = QPushButton(folder)
                button.setStyleSheet('background: transparent; text-align: left')
                button.clicked.connect(
                    lambda state, project_name=folder: self.choose_project(project_name))
                inner_layout.addWidget(button)
            box.setLayout(inner_layout)
            scroll = QScrollArea()
            scroll.setWidget(box)
            scroll.setWidgetResizable(True)
            self.project_layout.addWidget(scroll)

        create_prj_btn = QPushButton("Создать проект", self)
        create_prj_btn.clicked.connect(self.create_project)
        self.project_layout.addWidget(create_prj_btn)

    # Обновление Layout (Испытания)
    def update_tests_layout(self):
        self.clear_layout(self.tests_layout)

        global path
        global current_project

        if current_project == '':
            start_lbl = QLabel('Проект не выбран')
            self.tests_layout.addWidget(start_lbl)
        else:
            folder_path = os.path.join(path, current_project)
            tests = os.listdir(folder_path)

            test_lbl = QLabel(current_project)
            self.tests_layout.addWidget(test_lbl)

            # Добавляем кнопки для всех файлов, лежащих в папке
            # Добавляем ScrollArea, чтобы можно было прокручивать вниз,
            # если файлов очень много
            if len(tests) == 0:
                empty_lbl = QLabel("Нет созданных испытаний")
                self.tests_layout.addWidget(empty_lbl)
            else:
                box = QGroupBox()  # Необходимо для ScrollArea
                inner_layout = QVBoxLayout()
                for test in tests:  # Добавляем каждую внутреннюю директорию
                    button = QPushButton(test)
                    button.setStyleSheet('background: transparent; text-align: left')
                    # В обработчик нажатия передаём путь, чтобы определять, что нужно открыть
                    button.clicked.connect(
                        lambda state, test_folder=test: self.test_pushed(test_folder))
                    inner_layout.addWidget(button)
                    inner_files = os.listdir(os.path.join(folder_path, test))
                    for file in inner_files:  # Добавляем каждый файл из внутренних директорий
                        button = QPushButton(file)
                        button.setContentsMargins(20, 11, 11, 11)
                        button.setStyleSheet('background: transparent')
                        # В обработчик нажатия передаём путь, чтобы определять, что нужно открыть
                        button.clicked.connect(
                            lambda state, file_path=os.path.join(folder_path, test, file):
                            self.file_pushed(file_path))
                        inner_layout.addWidget(button)

                box.setLayout(inner_layout)
                scroll = QScrollArea()
                scroll.setWidget(box)
                scroll.setWidgetResizable(True)
                self.tests_layout.addWidget(scroll)

            add_test_btn = QPushButton("Добавить испытание", self)
            add_test_btn.clicked.connect(self.add_test)
            self.tests_layout.addWidget(add_test_btn)

    def choose_project(self, project_name):
        global current_project
        current_project = project_name
        self.update_tests_layout()

    def file_pushed(self, file_path):
        os.system(file_path)

    def test_pushed(self, test):
        global current_test
        current_test = test
        self.dw = dw.DataWindow()
        self.dw.show()
        self.close()

    def create_project(self):
        global projects
        global path
        name, ok = QInputDialog.getText(self, 'Создание проекта',
                                        'Введите название нового проекта:')
        if ok:
            if name in projects:
                QMessageBox.about(self, 'Ошибка', 'Проект с таким именем уже существует.')
            else:
                pat = "[A-Za-zА-Яа-я0-9_-]"  # Шаблон для названия
                if re.sub(pat, "", name, 1) == "":
                    os.mkdir(os.path.join(path, name))
                    projects.append(name)
                else:
                    QMessageBox.about(self, 'Ошибка', 'Название проекта может состоять из букв, цифр, а также знаков '
                                                      'тире и нижнего подчёркивания.')

        self.update_project_layout()

    def add_test(self):
        global path
        global current_project
        self.aw = aw.AddWindow()
        self.aw.show()
        self.close()
