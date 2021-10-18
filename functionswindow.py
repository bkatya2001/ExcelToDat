from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableWidget, QPushButton, QVBoxLayout


class FunctionsWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Настройка окна
        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Функции предварительной обработки данных")

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.table = QTableWidget(self)  # Пустая таблица
        self.table.setColumnCount(3)
        self.table.setRowCount(1)
        self.table.setHorizontalHeaderLabels(['№', 'Функция', 'Параметры'])


        add_btn = QPushButton("Добавить", self)
        add_btn.clicked.connect(self.add_function)
        save_btn = QPushButton("Сохранить", self)
        save_btn.clicked.connect(self.save_preset)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.table)
        vertical_layout.addWidget(add_btn)
        self.central_widget.setLayout(vertical_layout)

    def add_function(self):
        pass

    def save_preset(self):
        pass

