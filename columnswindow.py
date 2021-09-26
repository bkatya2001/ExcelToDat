from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout
import pandas as pd


class ColumnsWindow(QMainWindow):
    def __init__(self, main_window):
        QMainWindow.__init__(self)

        self.main_window = main_window
        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Изменение порядка столбцов")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(2)
        self.table.setRowCount(len(self.main_window.data.columns))
        self.table.setHorizontalHeaderLabels(['Столбец', 'Порядковый номер'])

        for i in range(len(self.main_window.data.columns)):
            item = QTableWidgetItem(str(self.main_window.data.columns[i]))
            item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.table.setItem(i, 0, item)
            self.table.setItem(i, 1, QTableWidgetItem(''))

        set_btn = QPushButton("Установить порядок", self)
        set_btn.clicked.connect(self.set_data)

        vertical_layout = QVBoxLayout()  # Вертикальная расстановка
        vertical_layout.addWidget(self.table)
        vertical_layout.addWidget(set_btn)
        self.central_widget.setLayout(vertical_layout)

    def set_data(self):
        df = pd.DataFrame(columns=['column', 'value'])
        for i in range(len(self.main_window.data.columns)):
            if (self.table.item(i, 1).text()).isdigit():
                if int(self.table.item(i, 1).text()) - 1 >= 0:
                    df.loc[len(df)] = [self.table.item(i, 0).text(), int(self.table.item(i, 1).text()) - 1]
        df = df.sort_values(by='value')
        columns = self.main_window.data.columns.to_list()
        for i in df['column']:
            columns.remove(i)
        for i in range(len(df)):
            columns.insert(df.loc[i, 'value'], df.loc[i, 'column'])
        self.main_window.data = self.main_window.data.reindex(columns=columns)

        self.main_window.create_table()
        self.close()