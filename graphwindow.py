import random

import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QDesktopWidget, QApplication
import pyqtgraph as pg
import pyqtgraph.exporters
import datawindow as dw
import filterwindow as fw


def get_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


class GraphWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Создаём поле для графика
        self.originalGraphWidget = pg.PlotWidget()
        self.originalGraphWidget.setBackground('w')
        self.originalGraphWidget.setTitle("Original graph")
        self.originalGraphWidget.setLabel('left', 'Values')
        self.originalGraphWidget.setLabel('bottom', dw.x_name)
        self.originalGraphWidget.showGrid(x=True, y=True)
        self.originalGraphWidget.addLegend()  # Описание: цвет - график

        self.changedGraphWidget = pg.PlotWidget()
        self.changedGraphWidget.setBackground('w')
        self.changedGraphWidget.setTitle("Changed graph")
        self.changedGraphWidget.setLabel('left', 'Values')
        self.changedGraphWidget.setLabel('bottom', dw.x_name)
        self.changedGraphWidget.showGrid(x=True, y=True)
        self.changedGraphWidget.addLegend()

        # Кнопки
        self.filter_btn = QPushButton("Filter", self)
        self.filter_btn.clicked.connect(self.filter_data)
        self.addData_btn = QPushButton("Дополнить", self)
        self.addData_btn.clicked.connect(self.add_data)

        self.vertical_layout = QVBoxLayout()
        self.graph_layout = QHBoxLayout()
        self.graph_layout.addWidget(self.originalGraphWidget)
        self.graph_layout.addWidget(self.changedGraphWidget)
        self.vertical_layout.addLayout(self.graph_layout)
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.filter_btn)
        self.button_layout.addWidget(self.addData_btn)
        self.vertical_layout.addLayout(self.button_layout)

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.vertical_layout)

        self.draw_graph()

        self.save_graph("Graph")

        #self.location_on_the_screen()

    def plot(self, x, y, plotname):
        color = get_color()
        pen = pg.mkPen(color=(color[0], color[1], color[2]))
        return self.originalGraphWidget.plot(x, y, name=plotname, pen=pen)

    def save_graph(self, filename):
        exporter = pg.exporters.ImageExporter(self.originalGraphWidget.plotItem)
        exporter.params.param('width').setValue(self.originalGraphWidget.range.width(), blockSignal=exporter.widthChanged)
        exporter.params.param('height').setValue(self.originalGraphWidget.range.height(), blockSignal=exporter.heightChanged)

        # save to file
        exporter.export(filename + '.png')

    def draw_graph(self):
        # plot data: x, y values
        for col in dw.y:
            if col != dw.x_name:
                flag = False
                for fc in fw.y_filtered.keys():
                    if fc == col:
                        flag = True
                        break
                if flag:
                    plt = self.plot(dw.x, list(fw.y_filtered.get(col)), col)
                else:
                    plt = self.plot(dw.x, list(dw.data[col]), col)

    def add_data(self):
        print(0)

    def filter_data(self):
        self.filter_win = fw.FilterWindow()
        self.filter_win.show()
        self.close()

    def location_on_the_screen(self):
        screen_geometry = QApplication.desktop().availableGeometry()
        screen_size = (screen_geometry.width(), screen_geometry.height())
        win_size = (self.frameSize().width(), self.frameSize().height())
        x = int(screen_size[0] / 2 - win_size[0] / 2)
        y = int(screen_size[1] / 2 - win_size[1] / 2)
        self.move(x, y)
