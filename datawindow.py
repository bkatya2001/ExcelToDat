import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton, \
    QTableWidgetItem, QMessageBox
import pandas as pd
import graphwindow as gw
import filewindow as fw

data = pd.DataFrame()  # Data from excel
x = []  # Data for x
x_name = ""
y = []  # Chosen columns
type_flag = False  # Необходимо для проверки данных на соответствие типу данных (число)
table_ready = False
file_path = ""  # Отвечает за путь к .xlsx файлу


def check_data():  # Проверка корректности введённых данных в таблицу
    global type_flag

    for col in data.columns:
        for i in range(len(data)):
            try:
                data[col][i] = float(data[col][i])
            except (TypeError, ValueError):
                type_flag = False
                return False
    type_flag = True
    return True


class DataWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        global file_path

        # Находим файл с таблицей
        xlsx = os.listdir(os.path.join(fw.path, fw.current_project, fw.current_test))
        for i in xlsx:
            if ".xlsx" not in i:
                xlsx.remove(i)
        file_path = os.path.join(fw.path, fw.current_project, fw.current_test, xlsx[0])

        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Конвертация из .xlsx в .data")
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        vertical_layout = QVBoxLayout()  # Вертикальная расстановка
        self.central_widget.setLayout(vertical_layout)

        horizontal_layout = QHBoxLayout()  # Горизонтальная расстановка

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.cellChanged.connect(self.change_cell)  # Возможность редактирования данных

        # Кнопки
        self.convert_btn = QPushButton("Конвертировать в .data", self)
        self.convert_btn.clicked.connect(self.convert_data)
        self.graph_btn = QPushButton("Построить график", self)
        self.graph_btn.clicked.connect(self.get_graph)
        return_btn = QPushButton("Назад", self)
        return_btn.clicked.connect(self.return_page)
        self.convert_btn.setEnabled(False)
        self.graph_btn.setEnabled(False)

        # Добавление компонентов в расстановку
        vertical_layout.addWidget(self.table)
        horizontal_layout.addWidget(self.convert_btn)
        horizontal_layout.addWidget(self.graph_btn)
        vertical_layout.addLayout(horizontal_layout)
        vertical_layout.addWidget(return_btn)

        self.create_table()

    def create_table(self):
        global data
        global x
        global x_name
        global type_flag
        global table_ready
        global file_path

        if file_path != "":
            type_flag = False
            table_ready = False
            data = pd.read_excel(file_path)
            headers = data.columns.to_list()

            self.table.setColumnCount(len(headers))
            self.table.setRowCount(len(data))
            self.table.setHorizontalHeaderLabels(headers)

            for i in range(len(headers)):
                for j in range(len(data)):
                    self.table.setItem(j, i, QTableWidgetItem(str(data.iloc[j, i])))

            self.table.insertRow(len(data))  # Добавляем ряд с checkbox
            for i in range(1, len(headers)):
                item = QTableWidgetItem()
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                self.table.setItem(len(data), i, item)

            # делаем ресайз колонок по содержимому
            self.table.resizeColumnsToContents()

            if not check_data():
                QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
                self.convert_btn.setEnabled(False)
                self.graph_btn.setEnabled(False)
            else:
                self.convert_btn.setEnabled(True)
                self.graph_btn.setEnabled(True)

            table_ready = True

    def convert_data(self):
        global data
        global file_path

        data.to_csv(os.path.join(fw.path, fw.current_project, fw.current_test, 'out.data'), sep=' ', header=False, index=False)
        QMessageBox.about(self, "Конвертация", "Конвертация завершена")

    def get_graph(self):
        global data
        global y
        global x
        global x_name

        x_name = data.columns[0]
        data = data.sort_values(by=x_name)  # Сортируем данные по возрастанию x
        x = list(data[data.columns[0]])

        y.clear()
        for i in range(1, self.table.columnCount()):
            if self.table.item(len(data), i).checkState() == Qt.Checked:
                y.append(data.columns[i])  # Add labels of columns

        self.graph_win = gw.GraphWindow()
        self.graph_win.show()
        self.close()

    def change_cell(self, row, column):
        global type_flag
        global table_ready

        if row != len(data) and table_ready:
            data.iloc[row, column] = self.table.item(row, column).text()
            try:
                value = float(self.table.item(row, column).text())
                data.iloc[row, column] = value
            except (TypeError, ValueError):
                QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
                self.convert_btn.setEnabled(False)
                self.graph_btn.setEnabled(False)

            if check_data():
                self.convert_btn.setEnabled(True)
                self.graph_btn.setEnabled(True)

    def return_page(self):
        self.fw = fw.FileWindow()
        self.fw.show()
        self.close()
