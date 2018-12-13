import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc
import pyqtgraph as Pg
import time


APP_NAME = 'Process Monitor'
ORG_NAME = 'Project1'
TAB_MINIMUM_SIZE = [300, 300]


class CustomGraph(Pg.PlotWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item = self.getPlotItem()
        self.box = self.item.getViewBox()
        self.setMouseEnabled(False, False)
        self.setMenuEnabled(False)
        self.hideButtons()
        self.item.showGrid(True, True)


class ProcessTab(Qw.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        pass

    def update_info(self):
        pass

    def passive_update(self):
        pass


class GraphsTab(Qw.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.main = parent
        self.x_range = 60
        self.x_values = list(range(-self.x_range, 1))
        self.cpu_data = []
        self.mem_info = []
        self.init_ui()

    def init_ui(self):
        self.layout = Qw.QGridLayout(self)

        self.cpu_graph = CustomGraph(self)
        self.cpu_graph.setXRange(0, -self.x_range)
        self.cpu_graph.setYRange(0, 100)
        self.cpu_graph.setMinimumSize(100, 100)
        self.layout.addWidget(self.cpu_graph, 0, 0)

        self.mem_graph = CustomGraph(self)
        self.mem_graph.setXRange(0, -self.x_range)
        self.mem_graph.setYRange(0, 100)
        self.mem_graph.setMinimumSize(100, 100)
        self.layout.addWidget(self.mem_graph, 1, 0)

        self.setMinimumSize(self.sizeHint())

    def update_info(self):
        update_time = time.time()
        self.cpu_data.append([update_time, psutil.cpu_percent()])
        self.mem_info.append([update_time, psutil.virtual_memory().percent])

        self.cpu_graph.clear()
        self.cpu_graph.plot([e[0] - update_time for e in self.cpu_data], [e[1] for e in self.cpu_data])
        self.mem_graph.clear()
        self.mem_graph.plot([e[0] - update_time for e in self.mem_info], [e[1] for e in self.mem_info])
        self.clear_garbage(update_time)

    def passive_update(self):
        self.update_info()

    def clear_garbage(self, cur_time):
        self.cpu_data = [e for e in self.cpu_data if e[0] - cur_time >= -self.x_range]
        self.mem_info = [e for e in self.mem_info if e[0] - cur_time >= -self.x_range]


class SettingsTab(Qw.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        pass

    def update_info(self):
        pass

    def passive_update(self):
        pass


class Main:

    def __init__(self):
        self.read_settings()
        self.init_ui()
        self.init_timers()
        self.start_timers()

    def init_timers(self):
        self.timer = Qc.QTimer(self.main_window)
        self.timer.setInterval(1000 / self.update_frequency)
        self.timer.timeout.connect(self.update_info)
        self.passive_timer = Qc.QTimer(self.main_window)
        self.passive_timer.setInterval(self.passive_period * 1000)
        self.passive_timer.timeout.connect(self.passive_update)

    def start_timers(self):
        self.timer.start()
        self.passive_timer.start()

    def stop_timers(self):
        self.timer.stop()
        self.passive_timer.stop()

    def init_ui(self):
        self.main_window = Qw.QWidget()
        self.main_window.setWindowTitle(APP_NAME)
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
        self.scroll.setMinimumSize(*TAB_MINIMUM_SIZE)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.tab_ind = 0
        self.tab_widgets = [ProcessTab(self), GraphsTab(self), SettingsTab(self)]
        self.scroll.setWidget(self.tab_widgets[0])

    def change_tab(self, ind):
        self.tab_ind = ind
        self.layout.removeWidget(self.scroll)
        self.scroll = Qw.QScrollArea(self.main_window)
        self.scroll.setMinimumSize(*TAB_MINIMUM_SIZE)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        self.tab_widgets[ind].update_info()
        self.scroll.setWidget(self.tab_widgets[ind])

    def update_info(self):
        self.tab_widgets[self.tab_ind].update_info()

    def passive_update(self):
        for i in self.tab_widgets:
            i.passive_update()

    def read_settings(self):
        self.settings = Qc.QSettings()
        self.update_frequency = float(self.settings.value('update frequency', 10))
        self.passive_period = float(self.settings.value('passive period', 5))

    def show(self):
        self.main_window.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    sys.excepthook = except_hook
    app = Qw.QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    main = Main()
    main.show()
    sys.exit(app.exec())
