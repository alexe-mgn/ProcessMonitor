import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc
import pyqtgraph as Pg


class CustomGraph(Pg.PlotWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item = self.getPlotItem()
        self.box = self.item.getViewBox()
        self.setMouseEnabled(False, False)
        self.setMenuEnabled(False)


class ProcessTab(Qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        pass

    def update_info(self):
        pass


class GraphsTab(Qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cpu_info = [1]
        self.mem_info = [1]
        self.init_ui()

    def init_ui(self):
        self.layout = Qw.QGridLayout(self)

        self.cpu_graph = CustomGraph(self)
        self.cpu_graph.setXRange(0, 60)
        self.cpu_graph.setYRange(0, 100)
        self.cpu_graph.setMinimumSize(100, 100)
        self.layout.addWidget(self.cpu_graph, 0, 0)

        self.mem_graph = CustomGraph(self)
        self.mem_graph.setXRange(0, 60)
        self.mem_graph.setYRange(0, 100)
        self.mem_graph.setMinimumSize(100, 100)
        self.layout.addWidget(self.mem_graph, 1, 0)

        self.setMinimumSize(self.sizeHint())

    def update_info(self):
        self.cpu_info.append(psutil.cpu_percent())
        self.mem_info.append(psutil.virtual_memory().percent)

        while len(self.cpu_info) > 60:
            del self.cpu_info[0]

        while len(self.mem_info) > 60:
            del self.mem_info[0]

        self.cpu_graph.clear()
        self.cpu_graph.plot(self.cpu_info)
        self.mem_graph.clear()
        self.mem_graph.plot(self.mem_info)


class SettingsTab(Qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        pass

    def update_info(self):
        pass


class Main:

    def __init__(self):
        self.init_ui()

    def init_ui(self):
        self.main_window = Qw.QWidget()
        self.main_window.setGeometry(300, 300, 300, 300)
        self.layout = Qw.QVBoxLayout(self.main_window)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.tabs = Qw.QTabBar()
        self.tabs.setFixedHeight(20)
        self.tabs.addTab('Processes')
        self.tabs.addTab('Graphs')
        self.tabs.addTab('Settings')
        self.tabs.currentChanged.connect(self.change_tab)
        self.layout.addWidget(self.tabs)

        self.scroll = Qw.QScrollArea(self.main_window)
        self.layout.addWidget(self.scroll)

        self.ind = 0
        self.tab_widgets = [ProcessTab(), GraphsTab(), SettingsTab()]
        self.scroll.setWidget(self.tab_widgets[0])
        self.scroll.setWidgetResizable(True)

        self.timer = Qc.QTimer(self.main_window)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_info)
        self.timer.start()

    def change_tab(self, ind):
        self.ind = ind
        self.layout.removeWidget(self.scroll)
        self.scroll = Qw.QScrollArea(self.main_window)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        self.tab_widgets[ind].update_info()
        self.scroll.setWidget(self.tab_widgets[ind])

    def update_info(self):
        self.tab_widgets[self.ind].update_info()

    def show(self):
        self.main_window.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = Qw.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())
