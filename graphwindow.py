import os
import random

from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QApplication, \
    QInputDialog, QMessageBox
import pyqtgraph as pg
import pyqtgraph.exporters
import datawindow as dw
import filterwindow as fw
import filewindow as filew

additional_data_flag = False  # Флаг, обозначающий, что данные нужно дополнить
x_min = 0  # Нижняя граница дополнения
x_max = 0  # Верхняя граница дополнения
changed_flag = False


def get_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return r, g, b


# Метод для отрисовки графика
def plot(x, y, plotname, graphWidget):
    color = get_color()
    pen = pg.mkPen(color=(color[0], color[1], color[2]))
    return graphWidget.plot(x, y, name=plotname, pen=pen)


class GraphWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        # Создаём поле для графика
        self.originalGraphWidget = pg.PlotWidget()
        self.originalGraphWidget.setBackground('w')
        self.originalGraphWidget.setTitle("Исходные данные")
        self.originalGraphWidget.setLabel('left', 'Values')
        self.originalGraphWidget.setLabel('bottom', dw.x_name)
        self.originalGraphWidget.showGrid(x=True, y=True)
        self.originalGraphWidget.addLegend()  # Описание: цвет - график

        # Создаём поле для изменённого графика
        self.changedGraphWidget = pg.PlotWidget()
        self.changedGraphWidget.setBackground('w')
        self.changedGraphWidget.setTitle("Изменённые данные")
        self.changedGraphWidget.setLabel('left', 'Values')
        self.changedGraphWidget.setLabel('bottom', dw.x_name)
        self.changedGraphWidget.showGrid(x=True, y=True)
        self.changedGraphWidget.addLegend()

        # Кнопки
        return_files_btn = QPushButton("Выбрать другое испытание", self)
        return_files_btn.clicked.connect(self.return_files)
        return_data_btn = QPushButton("Выбрать другие зависимости", self)
        return_data_btn.clicked.connect(self.return_data)
        filter_btn = QPushButton("Отфильтровать", self)
        filter_btn.clicked.connect(self.filter_data)
        addData_btn = QPushButton("Дополнить", self)
        addData_btn.clicked.connect(self.add_data)
        saveOrig_btn = QPushButton("Сохранить исходное изображение", self)
        saveOrig_btn.clicked.connect(
            lambda state, graphWidget=self.originalGraphWidget: self.save_graph(graphWidget))
        saveChanged_btn = QPushButton("Сохранить изменённое изображение", self)
        saveChanged_btn.clicked.connect(
            lambda state, graphWidget=self.changedGraphWidget: self.save_graph(graphWidget))

        vertical_layout = QVBoxLayout()
        graph_layout = QHBoxLayout()
        graph_layout.addWidget(self.originalGraphWidget)
        graph_layout.addWidget(self.changedGraphWidget)
        vertical_layout.addLayout(graph_layout)
        func_layout = QVBoxLayout()
        func_layout.addWidget(filter_btn)
        func_layout.addWidget(addData_btn)
        save_layout = QVBoxLayout()
        save_layout.addWidget(saveOrig_btn)
        save_layout.addWidget(saveChanged_btn)
        button_layout = QHBoxLayout()
        button_layout.addLayout(func_layout)
        button_layout.addLayout(save_layout)
        back_button_layout = QHBoxLayout()
        back_button_layout.addWidget(return_data_btn)
        back_button_layout.addWidget(return_files_btn)
        vertical_layout.addLayout(button_layout)
        vertical_layout.addLayout(back_button_layout)

        self.central_widget = QWidget(self)  # Создаём центральный виджет
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(vertical_layout)

        self.original_plt = []
        self.changed_plt = []
        self.draw_graph()

        # self.location_on_the_screen()

    def return_files(self):
        self.file_win = filew.FileWindow()
        self.file_win.show()
        self.close()

    def return_data(self):
        self.data_win = dw.DataWindow()
        self.data_win.show()
        self.close()

    # Метод для сохранения картинок графиков
    def save_graph(self, graphWidget):
        exporter = pg.exporters.ImageExporter(graphWidget.plotItem)
        exporter.params.param('width').setValue(graphWidget.range.width(), blockSignal=exporter.widthChanged)
        exporter.params.param('height').setValue(graphWidget.range.height(), blockSignal=exporter.heightChanged)

        text, ok = QInputDialog.getText(self, 'Сохранение',
                                        'Введите название файла:')
        if ok:
            # save to file
            exporter.export(os.path.join(filew.path, filew.current_project, filew.current_test, text + '.png'))

    # Метод для отрисовки графиков в первый раз
    def draw_graph(self):
        for col in dw.y:
            if col != dw.x_name:
                self.changed_plt.append(plot([0], [0], col, self.changedGraphWidget))
                self.original_plt.append(plot(dw.x, list(dw.data[col]), col, self.originalGraphWidget))

    # Метод для обновления данных на графиках
    def update_graph(self):
        global additional_data_flag
        global changed_flag
        global x_min
        global x_max
        # plot data: x, y values
        changed_flag = False
        for col in range(len(dw.y)):
            if dw.y[col] != dw.x_name:
                flag = False
                for fc in fw.y_filtered.keys():
                    if fc == dw.y[col]:
                        flag = True
                        break
                if flag:  # Если эти данные были отфильтрованы
                    values = list(fw.y_filtered.get(dw.y[col]))
                    changed_flag = True
                else:
                    values = list(dw.data[dw.y[col]])
                if additional_data_flag:  # Если есть дополнения к графику
                    changed_flag = True
                    x = list(enumerate(dw.x, 0))
                    min_value = min(x, key=lambda j: j[1])
                    max_value = max(x, key=lambda j: j[1])
                    new_x = []
                    new_y = []
                    for i in range(len(dw.x)):
                        if x_min <= dw.x[i] <= x_max:
                            new_x.append(dw.x[i])
                            new_y.append(values[i])
                    if min_value[1] > x_min:
                        new_x.insert(0, x_min)
                        new_y.insert(0, values[min_value[0]])
                    if max_value[1] < x_max:
                        new_x.insert(len(new_x), x_max)
                        new_y.insert(len(new_x), values[max_value[0]])
                    self.changed_plt[col].setData(new_x, new_y)
                elif changed_flag:
                    self.changed_plt[col].setData(dw.x, values)
                self.original_plt[col].setData(dw.x, list(dw.data[dw.y[col]]))

    # Дополнения к графику
    def add_data(self):
        global x_min
        global x_max
        global additional_data_flag

        begin, ok = QInputDialog.getText(self, 'Начальное значение',
                                         'Введите начальное значение:')
        if ok:
            try:
                x_min = int(begin)
                end, ok = QInputDialog.getText(self, 'Конечное значение',
                                               'Введите конечное значение:')
                if ok:
                    try:
                        x_max = int(end)
                        additional_data_flag = True
                        self.update_graph()
                    except ValueError:
                        QMessageBox.about(self, "Ошибка", "Введены некорректные данные")
            except ValueError:
                QMessageBox.about(self, "Ошибка", "Введены некорректные данные")

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
