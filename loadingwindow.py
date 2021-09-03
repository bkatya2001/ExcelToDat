from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout


# Окно для отображения загрузки
class LoadingWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        label = QLabel(self)
        label.setText("Подождите.\nИдёт загрузка данных...")
        label.setFont(QFont("Arial", 15))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.central_widget.setLayout(layout)
