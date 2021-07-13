from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout
import pandas as pd
import datawindow as dw


class ColumnsWindow(QMainWindow):
    def __init__(self, data_window):
        QMainWindow.__init__(self)

        self.old_data_window = data_window
        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Выбрать графики для фильтрации")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(2)
        self.table.setRowCount(len(dw.data.columns))
        self.table.setHorizontalHeaderLabels(['Столбец', 'Порядковый номер'])

        for i in range(len(dw.data.columns)):
            self.table.setItem(i, 0, QTableWidgetItem(str(dw.data.columns[i])))
            self.table.setItem(i, 1, QTableWidgetItem(''))

        set_btn = QPushButton("Установить порядок", self)
        set_btn.clicked.connect(self.set_data)
        return_btn = QPushButton('Назад', self)
        return_btn.clicked.connect(self.return_back)

        vertical_layout = QVBoxLayout()  # Вертикальная расстановка
        vertical_layout.addWidget(self.table)
        vertical_layout.addWidget(set_btn)
        vertical_layout.addWidget(return_btn)
        self.central_widget.setLayout(vertical_layout)

    def set_data(self):
        df = pd.DataFrame(columns=['columns', 'value'])
        for i in range(len(dw.data.columns)):
            df.loc[len(df)] = [self.table.item(i, 0).text(), self.table.item(i, 1).text()]
        df = df.sort_values(by='value')
        dw.data = dw.data.reindex(columns=df['columns'])

        self.old_data_window.create_table()
        self.old_data_window.show()
        self.close()

    def return_back(self):
        self.old_data_window.show()
        self.close()