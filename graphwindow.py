import random

from PyQt5.QtWidgets import QMainWindow
import pyqtgraph as pg
import pyqtgraph.exporters
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
        for col in mw.y:
            if col != mw.x_name:
                plt = self.plot(mw.x, list(mw.data[col]), col)

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
