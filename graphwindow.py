import random

from PyQt5.QtWidgets import QMainWindow
import pyqtgraph as pg
import mywindow as mw


def get_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


class GraphWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("Graph")
        self.graphWidget.setLabel('left', 'Values')
        self.graphWidget.setLabel('bottom', mw.x_name)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.addLegend()
        self.setCentralWidget(self.graphWidget)

        # plot data: x, y values
        for col in mw.data.columns:
            if col != mw.x_name:
                self.plot(mw.x, list(mw.data[col]), col)

    def plot(self, x, y, plotname):
        color = get_color()
        pen = pg.mkPen(color=(color[0], color[1], color[2]))
        self.graphWidget.plot(x, y, name=plotname, pen=pen)
