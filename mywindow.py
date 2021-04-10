from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import QSize, Qt, pyqtSlot
import sys


# Наследуемся от QMainWindow
class MainWindow(QMainWindow):
    # Переопределяем конструктор класса
    def __init__(self):
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Работа с QTableWidget")
        central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(central_widget)

        vertical_layout = QVBoxLayout()
        central_widget.setLayout(vertical_layout)

        get_btn = QPushButton("Choose file", self)
        get_btn.clicked.connect(self.choose_file)
        convert_btn = QPushButton("Get .dat", self)
        convert_btn.clicked.connect(self.convert_data)

        table = QTableWidget(self)  # Создаём таблицу
        table.setColumnCount(3)     # Устанавливаем три колонки
        table.setRowCount(1)        # и одну строку в таблице

        # Устанавливаем заголовки таблицы
        table.setHorizontalHeaderLabels(["Header 1", "Header 2", "Header 3"])

        # Устанавливаем всплывающие подсказки на заголовки
        table.horizontalHeaderItem(0).setToolTip("Column 1 ")
        table.horizontalHeaderItem(1).setToolTip("Column 2 ")
        table.horizontalHeaderItem(2).setToolTip("Column 3 ")

        # Устанавливаем выравнивание на заголовки
        table.horizontalHeaderItem(0).setTextAlignment(Qt.AlignLeft)
        table.horizontalHeaderItem(1).setTextAlignment(Qt.AlignHCenter)
        table.horizontalHeaderItem(2).setTextAlignment(Qt.AlignRight)

        # заполняем первую строку
        table.setItem(0, 0, QTableWidgetItem("Text in column 1"))
        table.setItem(0, 1, QTableWidgetItem("Text in column 2"))
        table.setItem(0, 2, QTableWidgetItem("Text in column 3"))

        # делаем ресайз колонок по содержимому
        table.resizeColumnsToContents()

        vertical_layout.addWidget(get_btn)
        vertical_layout.addStretch(1)
        vertical_layout.addWidget(table)   # Добавляем таблицу в сетку
        vertical_layout.addStretch(1)
        vertical_layout.addWidget(convert_btn)

    @pyqtSlot()
    def choose_file(self):
        print('PyQt5 button click')

    def convert_data(self):
        print('PyQt5 button click')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
