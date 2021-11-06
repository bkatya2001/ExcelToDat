import json
import os

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem


class AssignWindow(QMainWindow):
    def __init__(self, main_window):
        QMainWindow.__init__(self)

        self.main_window = main_window
        # Настройка окна
        self.setMinimumSize(QSize(600, 100))
        self.setWindowTitle("Выбор столбцов")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(2)
        columns = self.main_window.data.columns.to_list()
        self.table.setRowCount(len(columns))
        self.table.setHorizontalHeaderLabels(['Название', ''])
        for i in range(len(self.main_window.data.columns)):
            self.table.setItem(i, 0, QTableWidgetItem(str(columns[i])))
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 1, item)

        # Кнопки
        assign_btn = QPushButton("Применить функции", self)
        assign_btn.clicked.connect(self.assign_func)

        vertical_layout = QVBoxLayout()  # Вертикальная расстановка
        vertical_layout.addWidget(self.table)
        vertical_layout.addWidget(assign_btn)
        self.central_widget.setLayout(vertical_layout)

    def assign_func(self):
        checked_columns = []
        with open(os.path.join(self.main_window.path, self.main_window.current_project,
                               self.main_window.current_test, "preset.json"), "r") as read_file:
            data = json.load(read_file)

        for i in range(self.table.rowCount()):
            if self.table.item(i, 1).checkState() == Qt.Checked:
                checked_columns.append(self.table.item(i, 0).text())

        for key in data:
            if data[key]["func"] == "Замена некорректных данных":
                self.change_data(checked_columns, float(data[key]["params"]))
            if data[key]["func"] == "Приведение типов":
                self.convert_types(checked_columns, data[key]["params"])
            if data[key]["func"] == "Фильтрация":
                self.filter_data(checked_columns)

    def change_data(self, columns, param):
        for col in columns:
            self.main_window.data[col] = self.main_window.data[col].replace(to_replace=self.main_window.data[col].to_list(), value=param)
        self.main_window.create_table()
        self.close()

    def convert_types(self, columns, param):
        pass

    def filter_data(self, columns):
        pass
