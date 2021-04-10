from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt5.QtWidgets import QVBoxLayout, QPushButton
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import QSize, pyqtSlot
import pandas as pd
import sys


# Наследуемся от QMainWindow
class MainWindow(QMainWindow):
    # Переопределяем конструктор класса
    def __init__(self):
        # Обязательно нужно вызвать метод супер класса
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(480, 80))
        self.setWindowTitle("Convertor from .xlsx to .dat")
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)

        self.vertical_layout = QVBoxLayout() # Вертикальная расстановка
        self.central_widget.setLayout(self.vertical_layout)
        
        self.table = QTableWidget(self) # Пустая таблица

        # Кнопки
        self.get_btn = QPushButton("Choose file", self)
        self.get_btn.clicked.connect(self.choose_file)
        self.convert_btn = QPushButton("Get .dat", self)
        self.convert_btn.clicked.connect(self.convert_data)
        
        # Добавление компонентов в расстановку
        self.vertical_layout.addWidget(self.get_btn)
        self.vertical_layout.addStretch(1)
        self.vertical_layout.addWidget(self.table)
        self.vertical_layout.addStretch(1)
        self.vertical_layout.addWidget(self.convert_btn)

    @pyqtSlot()
    def choose_file(self):
        filename = QFileDialog.getOpenFileName(self, "Выбрать таблицу",
                                               ".", "Excel Workbook (*.xlsx)")
        self.data = pd.read_excel(filename[0])
        headers = self.data.columns.to_list()
        
        self.table.setColumnCount(len(headers))
        self.table.setRowCount(len(self.data))
        self.table.setHorizontalHeaderLabels(headers)
        
        for i in range(len(headers)):
            for j in range(len(self.data)):
                self.table.setItem(j, i, QTableWidgetItem(str(self.data.iloc[j, i])))
                
        # делаем ресайз колонок по содержимому
        self.table.resizeColumnsToContents()

    def convert_data(self):
        self.data.to_csv('out.dat', header=False, index=False)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
