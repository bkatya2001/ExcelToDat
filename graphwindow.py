import random

import pandas as pd
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget
import pyqtgraph as pg
import pyqtgraph.exporters
import mywindow as mw
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
        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Graph")
        self.graphWidget.setLabel('left', 'Values')
        self.graphWidget.setLabel('bottom', mw.x_name)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.addLegend()  # Описание: цвет - график

        # Кнопки
        self.filter_btn = QPushButton("Filter", self)
        self.filter_btn.clicked.connect(self.filter_data)

        self.vertical_layout = QVBoxLayout()
        self.vertical_layout.addWidget(self.graphWidget)
        self.vertical_layout.addWidget(self.filter_btn)

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(self.vertical_layout)

        self.draw_graph()

        self.save_graph("Graph")

    def plot(self, x, y, plotname):
        color = get_color()
        pen = pg.mkPen(color=(color[0], color[1], color[2]))
        return self.graphWidget.plot(x, y, name=plotname, pen=pen)

    def save_graph(self, filename):
        exporter = pg.exporters.ImageExporter(self.graphWidget.plotItem)
        exporter.params.param('width').setValue(self.graphWidget.range.width(), blockSignal=exporter.widthChanged)
        exporter.params.param('height').setValue(self.graphWidget.range.height(), blockSignal=exporter.heightChanged)

        # save to file
        exporter.export(filename + '.png')

    def draw_graph(self):
        # plot data: x, y values
        for col in mw.y:
            if col != mw.x_name:
                flag = False
                for fc in fw.y_filtered.keys():
                    if fc == col:
                        flag = True
                        break
                if flag:
                    plt = self.plot(mw.x, list(fw.y_filtered.get(col)), col)
                else:
                    plt = self.plot(mw.x, list(mw.data[col]), col)

    def filter_data(self):
        self.filter_win = fw.FilterWindow()
        self.filter_win.show()
        self.close()
