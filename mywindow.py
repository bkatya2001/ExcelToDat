from PyQt5.QtWidgets import QMainWindow, QWidget, QMessageBox
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QFileDialog
from PyQt5.QtCore import QSize, pyqtSlot
import pandas as pd

data = pd.DataFrame()

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
        
        self.horizontal_layout = QHBoxLayout() # Горизонтальная расстановка
        
        self.table = QTableWidget(self) # Пустая таблица

        # Кнопки
        self.get_btn = QPushButton("Choose file", self)
        self.get_btn.clicked.connect(self.choose_file)
        self.convert_btn = QPushButton("Get .data", self)
        self.convert_btn.clicked.connect(self.convert_data)
        self.graph_btn = QPushButton("Get graph", self)
        self.graph_btn.clicked.connect(self.get_graph)
        
        # Добавление компонентов в расстановку
        self.vertical_layout.addWidget(self.get_btn)
        self.vertical_layout.addWidget(self.table)
        self.horizontal_layout.addWidget(self.convert_btn)
        self.horizontal_layout.addWidget(self.graph_btn)
        self.vertical_layout.addLayout(self.horizontal_layout)
        
        # Возможность редактирования данных
        self.table.cellChanged.connect(self.change_cell)

    @pyqtSlot()
    def choose_file(self):
        global data
        
        filename = QFileDialog.getOpenFileName(self, "Выбрать таблицу",
                                               ".", "Excel Workbook (*.xlsx)")
        data = pd.read_excel(filename[0])
        headers = data.columns.to_list()
        
        self.table.setColumnCount(len(headers))
        self.table.setRowCount(len(data))
        self.table.setHorizontalHeaderLabels(headers)
        
        for i in range(len(headers)):
            for j in range(len(data)):
                self.table.setItem(j, i, QTableWidgetItem(str(data.iloc[j, i])))
                
        # делаем ресайз колонок по содержимому
        self.table.resizeColumnsToContents()

    def convert_data(self):
        global data
        data.to_csv('out.data', header=False, index=False)
        QMessageBox.about(self, "Conversion", "Conversion completed")
        
    def get_graph(self):
        global data
        print(data)
        
    def change_cell(self, row, column):
        data.loc[row, data.columns[column]] = self.table.item(row, column).text()
        