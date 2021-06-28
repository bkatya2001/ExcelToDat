from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
import graphwindow as gw
import datawindow as dw
from scipy.signal import savgol_filter

y_filtered = {}  # Фильтрованные данные (y)


class FilterWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Выбрать графики для фильтрации")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(2)
        self.table.setRowCount(len(dw.y))
        self.table.setHorizontalHeaderLabels(['Название', ''])
        for i in range(len(dw.y)):
            self.table.setItem(i, 0, QTableWidgetItem(str(dw.y[i])))
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 1, item)

        # Кнопки
        self.filter_btn = QPushButton("Фильтровать", self)
        self.filter_btn.clicked.connect(self.filter_data)
        self.return_btn = QPushButton('Назад', self)
        self.return_btn.clicked.connect(self.return_back)

        self.vertical_layout = QVBoxLayout()  # Вертикальная расстановка
        self.vertical_layout.addWidget(self.table)
        self.vertical_layout.addWidget(self.filter_btn)
        self.vertical_layout.addWidget(self.return_btn)
        self.central_widget.setLayout(self.vertical_layout)

    def filter_data(self):
        global y_filtered

        y_filtered.clear()
        for i in range(self.table.rowCount()):
            if self.table.item(i, 1).checkState() == Qt.Checked:
                win_size = len(dw.data[dw.y[i]])
                if win_size % 2 != 1:
                    win_size = win_size - 1
                y_filtered[self.table.item(i, 0).text()] = savgol_filter(dw.data[dw.y[i]], win_size, 2)
                
        self.graph_win = gw.GraphWindow()
        self.graph_win.show()
        self.graph_win.update_graph()
        self.close()

    def return_back(self):
        self.graph_win = gw.GraphWindow()
        self.graph_win.show()
        self.graph_win.update_graph()
        self.close()