import os
import random
import re
import subprocess

import pandas as pd
import pyqtgraph as pg
import pyqtgraph.exporters
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QScrollArea, QGroupBox, QLabel, \
    QSizePolicy, QInputDialog, QMessageBox, QTableWidget, QTableWidgetItem, QTextEdit, QAction, QApplication, \
    QButtonGroup
import addwindow as aw
import columnswindow as cw
import filterwindow as fw


def get_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


# Метод для отрисовки графика
def plot(x, y, plotname, graphWidget):
    color = get_color()
    pen = pg.mkPen(color=(color[0], color[1], color[2]))
    return graphWidget.plot(x, y, name=plotname, pen=pen)


# Удаление всех элементов из Layout для дальнейшего обновления
def clear_layout(layout):
    for i in reversed(range(layout.count())):
        layout.itemAt(i).widget().setParent(None)


def file_pushed(file_path):
    subprocess.run(file_path, shell=True)


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
        self.table.setMaximumWidth(int(QApplication.desktop().availableGeometry().width() * 0.3))
        self.table.cellChanged.connect(self.change_cell)  # Возможность редактирования данных

        # Часть для графиков
        pg.setConfigOption('foreground', pg.mkColor("000000"))
        # Создаём поле для графика
        self.originalGraphWidget = pg.PlotWidget()
        self.originalGraphWidget.setBackground('w')
        self.originalGraphWidget.setTitle("Исходные данные")
        self.originalGraphWidget.setLabel('left', 'Values')
        self.originalGraphWidget.setLabel('bottom', self.x_name)
        self.originalGraphWidget.showGrid(x=True, y=True)
        self.originalGraphWidget.addLegend()  # Описание: цвет - график

        # Создаём поле для изменённого графика
        self.changedGraphWidget = pg.PlotWidget()
        self.changedGraphWidget.setBackground('w')
        self.changedGraphWidget.setTitle("Изменённые данные")
        self.changedGraphWidget.setLabel('left', 'Values')
        self.changedGraphWidget.setLabel('bottom', self.x_name)
        self.changedGraphWidget.showGrid(x=True, y=True)
        self.changedGraphWidget.addLegend()

        self.original_plt = []
        self.changed_plt = []

        # Часть для вывода
        out_text = QTextEdit()
        out_text.setMaximumHeight(int(QApplication.desktop().availableGeometry().height() * 0.3))
        out_text.setReadOnly(True)

        data_layout.addLayout(self.project_layout)
        data_layout.addLayout(self.tests_layout)
        data_layout.addWidget(self.table)
        left_layout.addLayout(data_layout)
        left_layout.addWidget(out_text)
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

        data_menu = menuBar.addMenu("Данные")
        self.conversion_action = QAction("Конвертировать в .data", self)
        self.conversion_action.setEnabled(False)
        self.conversion_action.triggered.connect(self.convert_data)
        self.graph_action = QAction("Построить график", self)
        self.graph_action.setEnabled(False)
        self.graph_action.triggered.connect(self.get_graph)
        data_menu.addAction(self.conversion_action)
        data_menu.addAction(self.graph_action)
        change_menu = data_menu.addMenu("Изменить")
        self.data_action = QAction("Данные в выбранных ячейках", self)
        self.data_action.setEnabled(False)
        self.data_action.triggered.connect(self.change_data_in_chosen_cells)
        self.column_action = QAction("Порядок столбцов", self)
        self.column_action.setEnabled(False)
        self.column_action.triggered.connect(self.enumerate_col)
        change_menu.addAction(self.data_action)
        change_menu.addAction(self.column_action)

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

    def check_data(self):  # Проверка корректности введённых данных в таблицу
        result = []
        for col in range(len(self.data.columns)):
            for i in range(len(self.data)):
                try:
                    self.data.iloc[i, col] = float(self.data.iloc[i, col])
                except (TypeError, ValueError):
                    result.append(col)
                    self.type_flag = False
                    break
        self.type_flag = True
        return result

    def open_data(self):
        # Находим файл с таблицей
        xlsx = os.listdir(os.path.join(self.path, self.current_project, self.current_test))
        xlsx = [i for i in xlsx if '.xlsx' in i]
        self.file_path = os.path.join(self.path, self.current_project, self.current_test, xlsx[0])

        if self.file_path != "":
            self.data = pd.read_excel(self.file_path)
            self.create_table()

    def update_project_layout(self):
        clear_layout(self.project_layout)

        project_lbl = QLabel("Проекты:")
        project_lbl.setStyleSheet('font-size: 11pt')
        self.project_layout.addWidget(project_lbl)

        if len(self.projects) == 0:
            self.project_layout.addStretch(1)
            empty_lbl = QLabel("Нет созданных проектов")
            empty_lbl.setStyleSheet('font-size: 11pt')
            self.project_layout.addWidget(empty_lbl)
            self.project_layout.addStretch(1)
        else:
            box = QGroupBox()
            inner_layout = QVBoxLayout()

            self.buttons = QButtonGroup()
            self.buttons.buttonClicked[int].connect(self.choose_project)
            for folder in range(len(self.projects)):
                button = QPushButton(self.projects[folder], self)
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setStyleSheet('background: transparent; text-align: left; border: none; font-size: 11pt; '
                                     'font-weight: 100')
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
                        button = QPushButton(file)
                        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                        button.setStyleSheet('background: transparent; text-align: center; border: none; font-size: '
                                             '7pt; font-weight: 100')
                        # В обработчик нажатия передаём путь, чтобы определять, что нужно открыть
                        button.clicked.connect(
                            lambda state, file_path=os.path.join(folder_path, tests[test], file):
                            file_pushed(file_path))
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
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 700;')
            else:
                button.setStyleSheet(
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 100;')
        self.test_action.setEnabled(True)
        self.update_tests_layout()

    def test_pushed(self, id):
        for button in self.test_buttons.buttons():
            if self.test_buttons.id(button) == id:
                self.current_test = button.text()
                button.setStyleSheet(
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 700;')
            else:
                button.setStyleSheet(
                    'background: transparent; text-align: left; border: none; font-size: 11pt; font-weight: 100;')
        self.conversion_action.setEnabled(True)
        self.data_action.setEnabled(True)
        self.column_action.setEnabled(True)
        self.open_data()

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
            self.x_name = self.data.columns[0]
            self.type_flag = False
            self.table_ready = False
            headers = self.data.columns.to_list()

            self.clear_table()
            self.table.setColumnCount(len(headers))
            self.table.setRowCount(len(self.data))
            self.table.setHorizontalHeaderLabels(headers)

            for i in range(len(headers)):
                for j in range(len(self.data)):
                    self.table.setItem(j, i, QTableWidgetItem(str(self.data.iloc[j, i])))

            self.table.insertRow(len(self.data))  # Добавляем ряд с checkbox
            for i in range(1, len(headers)):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                self.table.setItem(len(self.data), i, item)

            # делаем ресайз колонок по содержимому
            self.table.resizeColumnsToContents()

            incorrect_columns = self.check_data()
            self.paint_headers(incorrect_columns)
            if len(incorrect_columns) != 0:
                self.conversion_action.setEnabled(False)
                self.graph_action.setEnabled(False)
            else:
                self.conversion_action.setEnabled(True)
                self.graph_action.setEnabled(True)

            self.table_ready = True

    def clear_table(self):
        while self.table.rowCount() > 0:
            self.table.removeRow(0)

    def paint_headers(self, columns):
        for i in range(len(self.data.columns)):
            header = self.table.horizontalHeaderItem(i)
            header.setText(header.text().replace('*', ''))
        if len(columns) != 0:
            for i in columns:
                header = self.table.horizontalHeaderItem(i)
                header.setText('*' + header.text())

    def convert_data(self):
        self.get_checked_columns()
        self.y.insert(0, self.x_name)
        self.data.to_csv(os.path.join(self.path, self.current_project, self.current_test, 'out.data'),
                         sep=' ', columns=self.y, header=False, index=False)
        QMessageBox.about(self, "Конвертация", "Конвертация завершена")
        self.y.remove(self.x_name)

    def get_checked_columns(self):
        self.y.clear()
        for i in range(1, self.table.columnCount()):
            if self.table.item(len(self.data), i).checkState() == Qt.Checked:
                self.y.append(self.data.columns[i])  # Add labels of columns

    def get_graph(self):
        self.x_name = self.data.columns[0]
        self.data = self.data.sort_values(by=self.x_name)  # Сортируем данные по возрастанию x
        self.x = list(self.data[self.data.columns[0]])

        self.filter_action.setEnabled(True)
        self.add_action.setEnabled(True)
        self.original_action.setEnabled(True)
        self.get_checked_columns()
        self.draw_graph()

    def change_cell(self, row, column):
        if row != len(self.data) and self.table_ready:
            self.data.iloc[row, column] = self.table.item(row, column).text()
            try:
                value = float(self.table.item(row, column).text())
                self.data.iloc[row, column] = value
            except (TypeError, ValueError):
                QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
                self.conversion_action.setEnabled(False)
                self.graph_action.setEnabled(False)

            incorrect_columns = self.check_data()
            self.paint_headers(incorrect_columns)
            if len(incorrect_columns) == 0:
                self.conversion_action.setEnabled(True)
                self.graph_action.setEnabled(True)

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
                    for cell in cells:
                        row = cell.row()
                        column = cell.column()
                        self.data.iloc[row, column] = value
                        item = QTableWidgetItem()
                        item.setText(text)
                        self.table.setItem(row, column, item)
                except (TypeError, ValueError):
                    QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
                    self.conversion_action.setEnabled(False)
                    self.graph_action.setEnabled(False)

                incorrect_columns = self.check_data()
                self.paint_headers(incorrect_columns)
                if len(incorrect_columns) == 0:
                    self.conversion_action.setEnabled(True)
                    self.graph_action.setEnabled(True)

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
        for col in self.y:
            if col != self.x_name:
                self.changed_plt.append(plot([0], [0], col, self.changedGraphWidget))
                self.original_plt.append(plot(self.x, list(self.data[col]), col, self.originalGraphWidget))

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
