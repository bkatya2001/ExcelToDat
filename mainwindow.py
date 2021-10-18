import os
import random
import re
import shutil
import subprocess

import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QScrollArea, QGroupBox, QLabel, \
    QSizePolicy, QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem, QTextEdit, QAction, QApplication, \
    QButtonGroup, QFileDialog, QMenu
import addwindow as aw
import columnswindow as cw
import filterwindow as fw
import functionswindow as funcwin
import threadclass as thread


def get_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


# Метод для отрисовки графика
def plot(x, y, plotname, graphWidget):
    color = get_color()
    pen = pg.mkPen(color=(color[0], color[1], color[2]), width=3)
    return graphWidget.plot(x, y, name=plotname, pen=pen)


# Удаление всех элементов из Layout для дальнейшего обновления
def clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.path = os.path.join(os.getcwd(), "Projects")  # Путь к папке с проектами
        self.projects = os.listdir(self.path)  # Проекты
        self.current_project = ""  # Имя проекта
        self.current_test = ""  # Имя испытания
        self.data = pd.DataFrame()  # Data from excel
        self.x = []  # Data for x
        self.x_name = ""  # Имя столбца по оси X
        self.y = []  # Chosen columns
        self.type_flag = False  # Необходимо для проверки данных на соответствие типу данных (число)
        self.table_ready = False
        self.file_path = ""  # Отвечает за путь к .xlsx файлу
        self.additional_data_flag = False  # Флаг, обозначающий, что данные нужно дополнить
        self.x_min = 0  # Нижняя граница дополнения
        self.x_max = 0  # Верхняя граница дополнения
        self.changed_flag = False
        self.y_filtered = {}  # Фильтрованные данные (y)
        self.incorrect_data = {}  # Данные с ошибками
        self.many_cells = False  # Флаг для метода изменения значений в нескольких ячейках
        self.is_loading = False  # Флаг текущей загрузки

        self.setWindowTitle("Excel to data")
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        # Создаём все расположения
        main_layout = QHBoxLayout()  # Главное
        left_layout = QVBoxLayout()  # Для проектов, испытаний и вывода данных и .data
        self.project_layout = QVBoxLayout()  # Для проектов
        self.tests_layout = QVBoxLayout()  # Для испытаний
        data_layout = QHBoxLayout()  # Для представления данных
        graph_layout = QVBoxLayout()  # Для графиков

        # Часть для окна с данными
        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setMinimumWidth(int(QApplication.desktop().availableGeometry().width() * 0.3))
        self.table.cellChanged.connect(self.change_cell)  # Возможность редактирования данных

        # Часть для графиков
        pg.setConfigOption('foreground', pg.mkColor("000000"))
        # Создаём поле для графика
        self.originalGraphWidget = pg.PlotWidget()
        self.originalGraphWidget.setBackground('w')
        self.originalGraphWidget.setTitle("Исходные данные")
        self.originalGraphWidget.setLabel('left', 'Values')
        self.originalGraphWidget.setLabel('bottom', 'X')
        self.originalGraphWidget.showGrid(x=True, y=True)
        self.originalGraphWidget.addLegend()  # Описание: цвет - график

        # Создаём поле для изменённого графика
        self.changedGraphWidget = pg.PlotWidget()
        self.changedGraphWidget.setBackground('w')
        self.changedGraphWidget.setTitle("Изменённые данные")
        self.changedGraphWidget.setLabel('left', 'Values')
        self.changedGraphWidget.setLabel('bottom', 'X')
        self.changedGraphWidget.showGrid(x=True, y=True)
        self.changedGraphWidget.addLegend()

        self.original_plt = []
        self.changed_plt = []

        # Часть для вывода
        self.out_text = QTextEdit()
        self.out_text.setMaximumHeight(int(QApplication.desktop().availableGeometry().height() * 0.3))
        self.out_text.setReadOnly(True)

        # Второй поток
        self.threadclass = thread.ThreadClass(self)
        self.threadclass.finishSignal.connect(self.finishSignal_process)

        data_layout.addLayout(self.project_layout)
        data_layout.addLayout(self.tests_layout)
        data_layout.addWidget(self.table)
        left_layout.addLayout(data_layout)
        left_layout.addWidget(self.out_text)
        graph_layout.addWidget(self.originalGraphWidget)
        graph_layout.addWidget(self.changedGraphWidget)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(graph_layout)
        self.central_widget.setLayout(main_layout)

        self.create_menuBar()
        self.update_project_layout()
        self.update_tests_layout()

    def create_menuBar(self):
        menuBar = self.menuBar()

        file_menu = menuBar.addMenu("Файл")
        create_menu = file_menu.addMenu("Создать")
        self.project_action = QAction("Проект", self)
        self.project_action.triggered.connect(self.create_project)
        self.test_action = QAction("Данные испытаний", self)
        self.test_action.setEnabled(False)
        self.test_action.triggered.connect(self.add_test)
        create_menu.addAction(self.project_action)
        create_menu.addAction(self.test_action)
        delete_menu = file_menu.addMenu("Удалить")
        self.delete_prj_action = QAction("Проект", self)
        self.delete_prj_action.triggered.connect(self.delete_prj_folder)
        self.delete_test_action = QAction("Данные испытаний", self)
        self.delete_test_action.triggered.connect(self.delete_test_folder)
        delete_menu.addAction(self.delete_prj_action)
        delete_menu.addAction(self.delete_test_action)

        data_menu = menuBar.addMenu("Данные")
        self.conversion_action = QAction("Конвертировать в .data", self)
        self.conversion_action.setEnabled(False)
        self.conversion_action.triggered.connect(self.convert_data)
        self.set_x_action = QAction("Назначить ось абсцисс", self)
        self.set_x_action.setEnabled(False)
        self.set_x_action.triggered.connect(self.set_x)
        self.graph_action = QAction("Построить график", self)
        self.graph_action.setEnabled(False)
        self.graph_action.triggered.connect(self.get_graph)
        self.copy_action = QAction("Копировать данные", self)
        self.copy_action.setEnabled(False)
        self.copy_action.triggered.connect(self.copy_test)
        data_menu.addAction(self.graph_action)
        data_menu.addAction(self.conversion_action)
        data_menu.addAction(self.set_x_action)
        data_menu.addAction(self.copy_action)
        change_menu = data_menu.addMenu("Изменить")
        self.data_action = QAction("Данные в выбранных ячейках", self)
        self.data_action.setEnabled(False)
        self.data_action.triggered.connect(self.change_data_in_chosen_cells)
        self.column_action = QAction("Порядок столбцов", self)
        self.column_action.setEnabled(False)
        self.column_action.triggered.connect(self.enumerate_col)
        change_menu.addAction(self.data_action)
        change_menu.addAction(self.column_action)
        self.delete_action = QAction("Удалить столбцы", self)
        self.delete_action.setEnabled(False)
        self.delete_action.triggered.connect(self.delete_column)
        data_menu.addAction(self.delete_action)

        function_menu = menuBar.addMenu("Функции")
        self.create_func_action = QAction("Создать", self)
        self.create_func_action.setEnabled(False)
        self.create_func_action.triggered.connect(self.create_functions)
        self.assign_func_action = QAction("Назначить", self)
        self.assign_func_action.setEnabled(False)
        self.assign_func_action.triggered.connect(self.assign_functions)
        function_menu.addAction(self.create_func_action)
        function_menu.addAction(self.assign_func_action)

        graph_menu = menuBar.addMenu("График")
        self.filter_action = QAction("Фильтровать", self)
        self.filter_action.setEnabled(False)
        self.filter_action.triggered.connect(self.filter_data)
        self.add_action = QAction("Изменить диапозон Х", self)
        self.add_action.setEnabled(False)
        self.add_action.triggered.connect(self.add_data)
        graph_menu.addAction(self.filter_action)
        graph_menu.addAction(self.add_action)
        save_menu = graph_menu.addMenu("Сохранить")
        self.original_action = QAction("Исходное изображение", self)
        self.original_action.setEnabled(False)
        self.original_action.triggered.connect(
            lambda state, graphWidget=self.originalGraphWidget: self.save_graph(graphWidget))
        self.changed_action = QAction("Изменённое изображение", self)
        self.changed_action.setEnabled(False)
        self.changed_action.triggered.connect(
            lambda state, graphWidget=self.changedGraphWidget: self.save_graph(graphWidget))
        save_menu.addAction(self.original_action)
        save_menu.addAction(self.changed_action)

    def init_prj_context_menu(self, name):
        self.current_project = name
        context_menu = QMenu(self)
        add_data = QAction("Добавить данные испытаний", self)
        add_data.triggered.connect(self.add_test)
        delete_project = QAction("Удалить проект", self)
        delete_project.triggered.connect(lambda state: self.delete_prj_folder(name))
        context_menu.addAction(add_data)
        context_menu.addAction(delete_project)
        context_menu.exec_(QCursor.pos())

    def set_x(self):
        items = self.data.columns.to_list()
        item, ok = QInputDialog().getItem(self, "Назначение оси абсцисс", "Выберите:", items, 0, False)
        if ok and item != '':
            self.x_name = item

    def loading_data(self):
        self.out_text.clear()
        self.out_text.setText("Подождите. Идёт загрузка данных...")

    def update_project_layout(self):
        clear_layout(self.project_layout)
        self.projects = os.listdir(self.path)
        if len(self.projects) == 0:
            empty_lbl = QLabel("Нет созданных проектов")
            empty_lbl.setStyleSheet('font-size: 11pt')
            self.project_layout.addWidget(empty_lbl)
        else:
            box = QGroupBox()
            inner_layout = QVBoxLayout()

            project_lbl = QLabel("Проекты:")
            project_lbl.setStyleSheet('font-size: 11pt')
            self.project_layout.addWidget(project_lbl)

            self.buttons = QButtonGroup()
            self.buttons.buttonClicked[int].connect(self.choose_project)
            for folder in range(len(self.projects)):
                button = QPushButton(self.projects[folder], self)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setStyleSheet('background: transparent; text-align: left; border: none; font-size: 11pt; '
                                     'font-weight: 100')
                button.setContextMenuPolicy(Qt.CustomContextMenu)
                button.customContextMenuRequested.connect(lambda state, name=self.projects[folder]:
                                                          self.init_prj_context_menu(name))
                self.buttons.addButton(button, folder)
                inner_layout.addWidget(button)

            inner_layout.addStretch(1)
            box.setLayout(inner_layout)
            scroll = QScrollArea()
            scroll.setWidget(box)
            scroll.setWidgetResizable(True)
            self.project_layout.addWidget(scroll)

    def update_tests_layout(self):
        clear_layout(self.tests_layout)

        if self.current_project != '':
            folder_path = os.path.join(self.path, self.current_project)
            tests = os.listdir(folder_path)

            # Добавляем кнопки для всех файлов, лежащих в папке
            # Добавляем ScrollArea, чтобы можно было прокручивать вниз, если файлов очень много
            if len(tests) == 0:
                empty_lbl = QLabel("Нет созданных испытаний")
                empty_lbl.setStyleSheet('font-size: 11pt')
                self.tests_layout.addWidget(empty_lbl)
            else:
                test_lbl = QLabel(self.current_project + ':')
                test_lbl.setStyleSheet('font-size: 11pt')
                self.tests_layout.addWidget(test_lbl)
                self.test_buttons = QButtonGroup()
                self.test_buttons.buttonClicked[int].connect(self.test_pushed)
                box = QGroupBox()  # Необходимо для ScrollArea
                inner_layout = QVBoxLayout()
                for test in range(len(tests)):  # Добавляем каждую внутреннюю директорию
                    button = QPushButton(tests[test], self)
                    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    button.setStyleSheet('background: transparent; text-align: left; border: none; font-size: 11pt; '
                                         'font-weight: 100')
                    # В обработчик нажатия передаём путь, чтобы определять, что нужно открыть
                    self.test_buttons.addButton(button, test)
                    inner_layout.addWidget(button)
                    inner_files = os.listdir(os.path.join(folder_path, tests[test]))
                    for file in inner_files:  # Добавляем каждый файл из внутренних директорий
                        button = QPushButton('- ' + file)
                        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        button.setStyleSheet('background: transparent; text-align: left; border: none; font-size: '
                                             '9pt; font-weight: 100; margin-left: 20px')
                        # В обработчик нажатия передаём путь, чтобы определять, что нужно открыть
                        button.clicked.connect(
                            lambda state, file_path=os.path.join(folder_path, tests[test], file):
                            self.file_pushed(file_path))
                        inner_layout.addWidget(button)
                        if os.path.isdir(os.path.join(folder_path, tests[test], file)):
                            data_files = os.listdir(os.path.join(folder_path, tests[test], file))
                            for df in data_files:
                                button = QPushButton('> ' + df)
                                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                                button.setStyleSheet(
                                    'background: transparent; text-align: left; border: none; font-size: '
                                    '7pt; font-weight: 100; margin-left: 40px')
                                button.clicked.connect(
                                    lambda state, file_path=os.path.join(folder_path, tests[test], file, df):
                                    self.file_pushed(file_path))
                                inner_layout.addWidget(button)

                box.setLayout(inner_layout)
                scroll = QScrollArea()
                scroll.setWidget(box)
                scroll.setWidgetResizable(True)
                self.tests_layout.addWidget(scroll)

    def choose_project(self, id):
        for button in self.buttons.buttons():
            if self.buttons.id(button) == id:
                self.current_project = button.text()
                button.setStyleSheet(
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 700; '
                    'color: yellow')
            else:
                button.setStyleSheet(
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 100;')
        self.test_action.setEnabled(True)
        self.copy_action.setEnabled(False)
        self.update_tests_layout()

    def test_pushed(self, id):
        self.incorrect_data = dict.fromkeys(self.data.columns, 0)
        for button in self.test_buttons.buttons():
            if self.test_buttons.id(button) == id:
                self.current_test = button.text()
                button.setStyleSheet(
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 700; '
                    'color: yellow')
            else:
                button.setStyleSheet(
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 100;')
        self.conversion_action.setEnabled(True)
        self.data_action.setEnabled(True)
        self.column_action.setEnabled(True)
        self.copy_action.setEnabled(True)
        self.delete_action.setEnabled(True)
        self.set_x_action.setEnabled(True)

        # Находим файл с таблицей
        xlsx = os.listdir(os.path.join(self.path, self.current_project, self.current_test))
        xlsx = [i for i in xlsx if ('.xlsx' in i) and i != 'out.xlsx']
        self.file_path = os.path.join(self.path, self.current_project, self.current_test, xlsx[0])

        self.loading_data()
        self.threadclass.start()

    def finishSignal_process(self):
        self.create_table()
        if '.data' in self.file_path:
            self.draw_data_graph()

    def copy_test(self):
        item, ok = QInputDialog.getItem(self, "Выбор проекта", "Проект", tuple(self.projects), 0, False)
        if ok and item:
            cur_path = os.path.join(self.path, self.current_project, self.current_test)
            new_path = os.path.join(self.path, item, self.current_test + "-copy")
            try:
                os.mkdir(new_path)
                paths = [i for i in os.listdir(os.path.join(self.path, self.current_project, self.current_test))
                         if ('.xlsx' in i) or ('.data' in i)]
                for p in paths:
                    shutil.copy(os.path.join(cur_path, p), new_path)
            except FileExistsError:
                QMessageBox.about(self, "Предупреждение", "Копия уже была создана")

    def create_project(self):
        name, ok = QInputDialog.getText(self, 'Создание проекта',
                                        'Введите название нового проекта:')
        if ok:
            if name in self.projects:
                QMessageBox.about(self, 'Ошибка', 'Проект с таким именем уже существует.')
            else:
                pat = "[\w-]+"  # Шаблон для названия
                if re.sub(pat, "", name, 1) == "":
                    os.mkdir(os.path.join(self.path, name))
                    self.projects.append(name)
                    self.update_project_layout()
                else:
                    QMessageBox.about(self, 'Ошибка', 'Название проекта может состоять из букв, цифр, а также знаков '
                                                      'тире и нижнего подчёркивания.')

    def add_test(self):
        self.aw = aw.AddWindow(self)
        self.aw.show()

    def enumerate_col(self):
        self.cw = cw.ColumnsWindow(self)
        self.cw.show()

    def create_table(self):
        if self.file_path != "":

            if len(self.data) > 20:
                length = 20
                table_data = pd.concat([self.data.head(10), self.data.tail(10)], ignore_index=True)
            else:
                length = len(self.data)
                table_data = self.data

            self.x_name = self.data.columns[0]
            self.x = list(self.data[self.x_name])
            self.type_flag = False
            self.table_ready = False
            headers = self.data.columns.to_list()

            self.clear_table()
            self.table.setColumnCount(len(headers))
            self.table.setRowCount(length)
            self.table.setHorizontalHeaderLabels(headers)
            self.incorrect_data = dict.fromkeys(headers, 0)

            for i in range(len(headers)):
                for j in range(length):
                    self.table.setItem(j, i, QTableWidgetItem(str(table_data.iloc[j, i])))

            self.table_ready = True

            self.table.insertRow(0)  # Добавляем ряд с checkbox
            for i in range(0, len(headers)):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                self.table.setItem(0, i, item)

            # делаем ресайз колонок по содержимому
            self.table.resizeColumnsToContents()

            incorrect_columns = [key for key, value in self.incorrect_data.items() if value != 0]
            self.paint_headers(incorrect_columns)
            if len(incorrect_columns) != 0:
                self.conversion_action.setEnabled(False)
                self.graph_action.setEnabled(False)
            else:
                self.conversion_action.setEnabled(True)
                self.graph_action.setEnabled(True)
            self.create_func_action.setEnabled(True)
            self.assign_func_action.setEnabled(True)

    def clear_table(self):
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

    def paint_headers(self, columns):
        message = "Некорректные данные в столбцах: \n"
        for i in range(len(self.data.columns)):
            header = self.table.horizontalHeaderItem(i)
            header.setText(header.text().replace('*', ''))

            if self.data.columns[i] in columns:
                message += header.text() + "\n"
                header.setText('*' + header.text())

        if message == "Некорректные данные в столбцах: \n":
            message = "Все данные в верном формате"
        else:
            message += "\nДанные могут быть представлены только в числовом формате.\n" \
                       "Для изменения значений выделите нужные ячейки и нажмите " \
                       "'Данные' - 'Изменить' - 'Данные в выбранных ячейках'."
        self.out_text.clear()
        self.out_text.setText(message)

    def convert_data(self):
        self.get_checked_columns()
        text, ok = QInputDialog.getText(self, 'Конвертация данных',
                                        'Введите название файла:')
        files = os.listdir(os.path.join(self.path, self.current_project, self.current_test, "Изменённые_данные"))
        if ok:
            pat = "[\w-]+"  # Шаблон для названия
            if re.sub(pat, "", text, 1) == "":
                if not ((text + '.data') in files):
                    self.data.to_excel(os.path.join(self.path, self.current_project, self.current_test,
                                                    "Изменённые_данные", text + '.xlsx'), columns=self.y, index=False)
                    self.data.to_csv(os.path.join(self.path, self.current_project, self.current_test,
                                                  "Изменённые_данные", text + '.data'), sep=' ', columns=self.y,
                                     header=True, index=False)
                    QMessageBox.about(self, "Конвертация", "Конвертация завершена")
                    self.update_tests_layout()
                else:
                    QMessageBox.about(self, "Ошибка", "Файлы с такими названиями уже существуют")
            else:
                QMessageBox.about(self, 'Ошибка', 'Название проекта может состоять из букв, цифр, а также знаков '
                                                  'тире и нижнего подчёркивания.')

    def get_checked_columns(self):
        self.y.clear()
        for i in range(0, self.table.columnCount()):
            if self.table.item(0, i).checkState() == Qt.Checked:
                self.y.append(self.data.columns[i])  # Add labels of columns

    def get_graph(self):
        self.data = self.data.sort_values(by=self.x_name)  # Сортируем данные по возрастанию x
        self.x = list(self.data[self.x_name])

        self.filter_action.setEnabled(True)
        self.add_action.setEnabled(True)
        self.original_action.setEnabled(True)
        self.get_checked_columns()
        self.draw_graph()

    def change_cell(self, row, column):
        if self.table_ready:
            if row != 0:
                t = str(type(self.data.iloc[row - 1, column]))
                self.data.iloc[row - 1, column] = self.table.item(row, column).text()
                try:
                    value = float(self.table.item(row, column).text())
                    self.data.iloc[row - 1, column] = value
                    if not ('float' in t) and not ('int' in t):
                        self.incorrect_data[self.data.columns[column]] -= 1
                except (TypeError, ValueError):
                    if not self.many_cells:
                        QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
                    self.conversion_action.setEnabled(False)
                    self.graph_action.setEnabled(False)
                    if 'float' in t or 'int' in t:
                        self.incorrect_data[self.data.columns[column]] += 1

                incorrect_columns = [key for key, value in self.incorrect_data.items() if value != 0]
                self.paint_headers(incorrect_columns)
                if len(incorrect_columns) != 0:
                    self.conversion_action.setEnabled(False)
                    self.graph_action.setEnabled(False)
                else:
                    self.conversion_action.setEnabled(True)
                    self.graph_action.setEnabled(True)
        else:
            t = str(type(self.data.iloc[row - 1, column]))
            if not ('float' in t) and not ('int' in t):
                self.incorrect_data[self.data.columns[column]] += 1

    def change_data_in_chosen_cells(self):
        cells = self.table.selectedIndexes()
        if len(cells) == 0:
            QMessageBox.about(self, "Ошибка", "Ни одна ячейка не была выбрана")
        else:
            text, ok = QInputDialog.getText(self, 'Изменение данных',
                                            'Введите число:')
            if ok:
                try:
                    value = float(text)
                except (TypeError, ValueError):
                    QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
                self.many_cells = True
                for cell in cells:
                    row = cell.row()
                    column = cell.column()
                    item = QTableWidgetItem()
                    item.setText(text)
                    self.table.setItem(row, column, item)
                self.many_cells = False

    # Метод для сохранения картинок графиков
    def save_graph(self, graphWidget):
        exporter = pg.exporters.ImageExporter(graphWidget.plotItem)
        exporter.params.param('width').setValue(graphWidget.range.width(), blockSignal=exporter.widthChanged)
        exporter.params.param('height').setValue(graphWidget.range.height(), blockSignal=exporter.heightChanged)

        text, ok = QInputDialog.getText(self, 'Сохранение',
                                        'Введите название файла:')
        if ok:
            # save to file
            exporter.export(os.path.join(self.path, self.current_project, self.current_test, text + '.png'))

    # Метод для отрисовки графиков в первый раз
    def draw_graph(self):
        self.originalGraphWidget.clear()
        self.changedGraphWidget.clear()
        self.changed_plt.clear()
        self.original_plt.clear()
        for col in self.y:
            if col != self.x_name:
                self.changed_plt.append(plot([0], [0], col, self.changedGraphWidget))
                self.original_plt.append(plot(self.x, list(self.data[col]), col, self.originalGraphWidget))

    # Метод для отрисовки данных по .data
    def draw_data_graph(self):
        self.originalGraphWidget.clear()
        self.changedGraphWidget.clear()
        self.changed_plt.clear()
        self.original_plt.clear()
        for col in self.data.columns:
            if col != self.x_name:
                self.original_plt.append(plot(self.x, list(self.data[col]), col, self.originalGraphWidget))
                self.changed_plt.append(plot([0], [0], col, self.changedGraphWidget))

    # Метод для обновления данных на графиках
    def update_graph(self):
        # plot data: x, y values
        self.changed_flag = False
        for col in range(len(self.y)):
            if self.y[col] != self.x_name:
                flag = False
                for fc in self.y_filtered.keys():
                    if fc == self.y[col]:
                        flag = True
                        break
                if flag:  # Если эти данные были отфильтрованы
                    values = list(self.y_filtered.get(self.y[col]))
                    self.changed_flag = True
                else:
                    values = list(self.data[self.y[col]])
                if self.additional_data_flag:  # Если есть дополнения к графику
                    self.changed_flag = True
                    x = list(enumerate(self.x, 0))
                    min_value = min(x, key=lambda j: j[1])
                    max_value = max(x, key=lambda j: j[1])
                    new_x = []
                    new_y = []
                    for i in range(len(self.x)):
                        if self.x_min <= self.x[i] <= self.x_max:
                            new_x.append(self.x[i])
                            new_y.append(values[i])
                    if min_value[1] > self.x_min:
                        new_x.insert(0, self.x_min)
                        new_y.insert(0, values[min_value[0]])
                    if max_value[1] < self.x_max:
                        new_x.insert(len(new_x), self.x_max)
                        new_y.insert(len(new_x), values[max_value[0]])
                    self.changed_plt[col].setData(new_x, new_y)
                elif self.changed_flag:
                    self.changed_plt[col].setData(self.x, values)
                self.original_plt[col].setData(self.x, list(self.data[self.y[col]]))

    # Дополнения к графику
    def add_data(self):
        begin, ok = QInputDialog.getText(self, 'Начальное значение',
                                         'Введите начальное значение:')
        if ok:
            try:
                self.x_min = int(begin)
                end, ok = QInputDialog.getText(self, 'Конечное значение',
                                               'Введите конечное значение:')
                if ok:
                    try:
                        self.x_max = int(end)
                        self.additional_data_flag = True
                        self.changed_action.setEnabled(True)
                        self.update_graph()
                    except ValueError:
                        QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
            except ValueError:
                QMessageBox.about(self, "Ошибка", "Введены некорректные данные")

    def filter_data(self):
        self.filter_win = fw.FilterWindow(self)
        self.filter_win.show()

    def file_pushed(self, file_path):
        if '.txt' in file_path:
            f = open(file_path)
            self.out_text.setText(f.read())
        elif '.data' in file_path:
            self.file_path = file_path
            self.conversion_action.setEnabled(True)
            self.data_action.setEnabled(True)
            self.column_action.setEnabled(True)
            self.copy_action.setEnabled(True)
            self.delete_action.setEnabled(True)
            self.set_x_action.setEnabled(True)
            f = open(file_path)
            self.out_text.setText(f.read())
            self.loading_data()
            self.threadclass.start()
        elif '.' in file_path:
            subprocess.run(file_path, shell=True)

    def delete_column(self):
        self.get_checked_columns()
        self.data = self.data.drop(columns=self.y)
        self.create_table()

    def delete_prj_folder(self, name=""):
        self.current_project = ""
        if name == "":
            path = os.path.normpath(os.path.join(os.getcwd(), "Projects"))
            prj = QFileDialog.getExistingDirectory(self, "Выберите проект", path, QFileDialog.ShowDirsOnly)
            if prj != "" and (path in os.path.normpath(prj)):
                shutil.rmtree(prj, ignore_errors=True)
                self.update_project_layout()
                self.update_tests_layout()
        else:
            shutil.rmtree(os.path.join(self.path, name), ignore_errors=True)
            self.update_project_layout()
            self.update_tests_layout()

    def delete_test_folder(self):
        path = os.path.normpath(os.path.join(os.getcwd(), "Projects"))
        prj = QFileDialog.getExistingDirectory(self, "Выберите испытание", path, QFileDialog.ShowDirsOnly)
        if prj != "":
            h, t = os.path.split(os.path.normpath(prj))
            h, t = os.path.split(h)
            if path == h:
                os.rmdir(prj)

    def create_functions(self):
        self.funcwin = funcwin.FunctionsWindow()
        self.funcwin.show()

    def assign_functions(self):
        pass