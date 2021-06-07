import pandas as pd
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
import mywindow as mw
import graphwindow as gw
from scipy.signal import savgol_filter

y_filtered = {}


class FilterWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Choose graph")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(2)
        self.table.setRowCount(len(mw.y))
        self.table.setHorizontalHeaderLabels(['Name', ''])
        for i in range(len(mw.y)):
            self.table.setItem(i, 0, QTableWidgetItem(str(mw.y[i])))
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 1, item)

        self.filter_btn = QPushButton("Filter", self)
        self.filter_btn.clicked.connect(self.filter_data)

        self.vertical_layout = QVBoxLayout()  # Вертикальная расстановка
        self.vertical_layout.addWidget(self.table)
        self.vertical_layout.addWidget(self.filter_btn)
        self.central_widget.setLayout(self.vertical_layout)

    def filter_data(self):
        global y_filtered

        y_filtered.clear()
        for i in range(self.table.rowCount()):
            if self.table.item(i, 1).checkState() == Qt.Checked:
                win_size = len(mw.data[mw.y[i]])
                if win_size % 2 != 1:
                    win_size = win_size - 1
                y_filtered[self.table.item(i, 0).text()] = savgol_filter(mw.data[mw.y[i]], win_size, 2)
                
        self.graph_win = gw.GraphWindow()
        self.graph_win.show()
        self.close()
