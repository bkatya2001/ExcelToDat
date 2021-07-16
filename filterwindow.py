from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
import start
from scipy.signal import savgol_filter


class FilterWindow(QMainWindow):
    def __init__(self, main_window):
        QMainWindow.__init__(self)

        self.main_window = main_window
        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Выбрать графики для фильтрации")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(2)
        self.table.setRowCount(len(self.main_window.y))
        self.table.setHorizontalHeaderLabels(['Название', ''])
        for i in range(len(self.main_window.y)):
            self.table.setItem(i, 0, QTableWidgetItem(str(self.main_window.y[i])))
            item = QTableWidgetItem()
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            self.table.setItem(i, 1, item)

        # Кнопки
        filter_btn = QPushButton("Фильтровать", self)
        filter_btn.clicked.connect(self.filter_data)

        vertical_layout = QVBoxLayout()  # Вертикальная расстановка
        vertical_layout.addWidget(self.table)
        vertical_layout.addWidget(filter_btn)
        self.central_widget.setLayout(vertical_layout)

    def filter_data(self):
        self.main_window.changed_action.setEnabled(True)
        self.main_window.y_filtered.clear()
        for i in range(self.table.rowCount()):
            if self.table.item(i, 1).checkState() == Qt.Checked:
                win_size = len(self.main_window.data[self.main_window.y[i]])
                if win_size % 2 != 1:
                    win_size = win_size - 1
                self.main_window.y_filtered[self.table.item(i, 0).text()] = \
                    savgol_filter(self.main_window.data[self.main_window.y[i]], win_size, 2)

        self.main_window.update_graph()
        self.close()
