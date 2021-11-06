import os
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidget, QPushButton, QVBoxLayout, QComboBox, QTableWidgetItem, \
    QHeaderView, QMessageBox
import json


class FunctionsWindow(QMainWindow):
    def __init__(self, main_window):
        QMainWindow.__init__(self)

        self.main_window = main_window
        # Настройка окна
        self.setMinimumSize(QSize(600, 100))
        self.setWindowTitle("Функции предварительной обработки данных")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(2)
        self.table.setRowCount(1)
        self.table.setHorizontalHeaderLabels(['Функция', 'Параметры'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        func_combobox = QComboBox()
        func_combobox.addItems(["Замена некорректных данных", "Приведение типов", "Фильтрация"])
        self.table.setItem(0, 0, QTableWidgetItem())
        self.table.setCellWidget(0, 0, func_combobox)
        param_combobox = QComboBox()
        param_combobox.addItems(["", "int32", "float32"])
        param_combobox.setEditable(True)
        self.table.setItem(0, 1, QTableWidgetItem())
        self.table.setCellWidget(0, 1, param_combobox)

        add_btn = QPushButton("Добавить", self)
        add_btn.clicked.connect(self.add_function)
        save_btn = QPushButton("Сохранить", self)
        save_btn.clicked.connect(self.save_preset)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.table)
        vertical_layout.addWidget(add_btn)
        vertical_layout.addWidget(save_btn)
        self.central_widget.setLayout(vertical_layout)

    def add_function(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        func_combobox = QComboBox()
        func_combobox.addItems(["Замена некорректных данных", "Приведение типов", "Фильтрация"])
        self.table.setItem(row_position, 0, QTableWidgetItem())
        self.table.setCellWidget(row_position, 0, func_combobox)
        param_combobox = QComboBox()
        param_combobox.addItems(["", "int32", "float32"])
        param_combobox.setEditable(True)
        self.table.setItem(row_position, 1, QTableWidgetItem())
        self.table.setCellWidget(row_position, 1, param_combobox)

    def save_preset(self):
        flag = True
        json_data = {}
        rows = self.table.rowCount()
        for i in range(rows):
            widget = self.table.cellWidget(i, 0)
            if isinstance(widget, QComboBox):
                func = widget.currentText()
            widget = self.table.cellWidget(i, 1)
            if isinstance(widget, QComboBox):
                params = widget.currentText()
            if func == "Замена некорректных данных":
                try:
                    float(params)
                    json_data[i] = {"func": func, "params": params}
                except (TypeError, ValueError):
                    QMessageBox.about(self, "Ошибка", "Для этой функции параметром может быть только число")
                    flag = False
                    break
            elif func == "Приведение типов":
                if params in ["int32", "float32"]:
                    json_data[i] = {"func": func, "params": params}
                else:
                    QMessageBox.about(self, "Ошибка", "Для этой функции параметром может быть один из предложенных "
                                                      "списков")
                    flag = False
                    break
            elif func == "Фильтрация":
                if params == "":
                    json_data[i] = {"func": func, "params": params}
                else:
                    QMessageBox.about(self, "Ошибка", "Для этой функции параметры не нужны")
                    flag = False
                    break
        if flag:
            with open(os.path.join(self.main_window.path, self.main_window.current_project,
                                   self.main_window.current_test, "preset.json"), "w") as write_file:
                json.dump(json_data, write_file, ensure_ascii=False)
            QMessageBox.about(self, "Создание пресета", "Файл успешно создан")
            self.close()
