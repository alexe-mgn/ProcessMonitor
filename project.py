import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc
import pyqtgraph as Pg
import time

APP_NAME = 'Process Monitor'
ORG_NAME = 'Project1'
TAB_MINIMUM_SIZE = [275, 275]


class CustomGraph(Pg.PlotWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.item = self.getPlotItem()
        self.box = self.item.getViewBox()
        self.setMouseEnabled(False, False)
        self.setMenuEnabled(False)
        self.hideButtons()
        self.item.showGrid(True, True)


class ProcessTab(Qw.QGroupBox):

    def __init__(self, parent):
        super().__init__()
        self.setMinimumSize(*TAB_MINIMUM_SIZE)
        self.init_ui()

    def init_ui(self):
        pass

    def update_info(self):
        pass

    def passive_update(self):
        pass


class GraphsTab(Qw.QGroupBox):

    def __init__(self, parent):
        super().__init__()
        self.main = parent
        self.x_range = 60
        self.cpu_data = []
        self.mem_data = []
        self.setMinimumSize(*TAB_MINIMUM_SIZE)
        self.init_ui()

    def init_ui(self):
        self.layout = Qw.QGridLayout(self)

        self.cpu_graph = CustomGraph(self)
        self.cpu_graph.setXRange(0, -self.x_range)
        self.cpu_graph.setYRange(0, 100)
        self.cpu_graph.setMinimumSize(100, 100)
        self.cpu_graph.item.setLabel('left', 'CPU load')
        self.layout.addWidget(self.cpu_graph, 0, 0)

        self.mem_graph = CustomGraph(self)
        self.mem_graph.setXRange(0, -self.x_range)
        self.mem_graph.setYRange(0, 100)
        self.mem_graph.setMinimumSize(100, 100)
        self.mem_graph.item.setLabel('left', 'Memory usage')
        self.layout.addWidget(self.mem_graph, 1, 0)

    def update_info(self):
        update_time = time.time()
        self.cpu_data.append([update_time, psutil.cpu_percent()])
        self.mem_data.append([update_time, psutil.virtual_memory().percent])

        self.cpu_graph.clear()
        self.cpu_graph.plot([e[0] - update_time for e in self.cpu_data], [e[1] for e in self.cpu_data])
        self.mem_graph.clear()
        self.mem_graph.plot([e[0] - update_time for e in self.mem_data], [e[1] for e in self.mem_data])
        self.clear_old_data(update_time)

    def passive_update(self):
        if self.main.current_tab() != self:
            update_time = time.time()
            self.cpu_data.append([update_time, psutil.cpu_percent()])
            self.mem_data.append([update_time, psutil.virtual_memory().percent])
            self.clear_old_data(update_time)

    def clear_old_data(self, cur_time):
        self.cpu_data = [e for e in self.cpu_data if e[0] - cur_time >= -self.x_range]
        self.mem_data = [e for e in self.mem_data if e[0] - cur_time >= -self.x_range]


class SettingsTab(Qw.QGroupBox):

    def __init__(self, parent):
        super().__init__()
        self.main = parent
        self.setMinimumSize(*TAB_MINIMUM_SIZE)
        self.init_ui()
        self.check = False

    def init_ui(self):
        # Labels
        self.label_fr = Qw.QLabel(self)
        self.label_fr.setText('Update Frequency')
        self.label_fr.move(20, 30)

        self.label_pas = Qw.QLabel(self)
        self.label_pas.setText('Passive update period')
        self.label_pas.move(20, 50)

        # Frequency input
        self.spin_fr = Qw.QDoubleSpinBox(self)
        self.spin_fr.move(150, 30)
        self.spin_fr.setDecimals(3)
        self.spin_fr.setMaximum(10000.0)
        self.spin_fr.setMinimum(0.1)
        self.spin_fr.setSingleStep(1.0)
        self.spin_fr.setValue(self.main.update_frequency)

        # Passive update period input
        self.spin_pas = Qw.QDoubleSpinBox(self)
        self.spin_pas.move(150, 50)
        self.spin_pas.setDecimals(3)
        self.spin_pas.setMaximum(1800.0)
        self.spin_pas.setMinimum(0.001)
        self.spin_pas.setSingleStep(1.0)
        self.spin_pas.setValue(self.main.passive_period)

        self.button = Qw.QPushButton(self)
        self.button.setText('Apply')
        self.button.move(100, 100)
        self.button.clicked.connect(self.apply)

    def apply(self):
        self.main.settings.setValue('passive period', self.spin_pas.value())
        self.main.settings.setValue('update frequency', self.spin_fr.value())
        self.main.read_settings()

    def update_info(self):
        pass

    def passive_update(self):
        pass


class TrayMenu(Qw.QMenu):

    def __init__(self, parent):
        super().__init__()
        self.main = parent
        self.actions = {'Open': self.main.popup_from_tray,
                        'Exit': self.main.exit}
        self.addAction('Open')
        self.addAction('Exit')
        self.triggered.connect(lambda action: self.actions[action.text()]())


class Main:

    def __init__(self):
        self.timing = False
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
        self.timing = True
        self.timer.start()
        self.passive_timer.start()

    def stop_timers(self):
        self.timing = False
        self.timer.stop()
        self.passive_timer.stop()

    def kill_timers(self):
        self.timer.killTimer(self.timer.timerId())
        self.passive_timer.killTimer(self.passive_timer.timerId())

    def init_ui(self):
        # Main window
        self.main_window = Qw.QWidget()
        self.main_window.setWindowTitle(APP_NAME)
        self.main_window.setWindowIcon(Qg.QIcon(APP_NAME + '.ico'))
        self.main_window.closeEvent = self.close_handler
        self.main_window.setGeometry(300, 300, 300, 300)
        self.main_window.setMinimumSize(300, 300)
        self.layout = Qw.QVBoxLayout(self.main_window)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Tray icon
        self.tray = None
        if Qw.QSystemTrayIcon.isSystemTrayAvailable():
            self.tray = Qw.QSystemTrayIcon()
            self.tray.activated.connect(lambda reason: self.popup_from_tray() if reason == 2 else None)
            self.tray.setIcon(Qg.QIcon(APP_NAME + '.ico'))
            self.tray.setContextMenu(TrayMenu(self))
            self.tray.show()

        # Tabs bar
        self.tabs = Qw.QTabBar()
        self.tabs.setFixedHeight(20)
        self.tabs.addTab('Processes')
        self.tabs.addTab('Graphs')
        self.tabs.addTab('Settings')
        self.tabs.currentChanged.connect(self.change_tab)
        self.layout.addWidget(self.tabs)

        # Tab scroll area
        self.scroll = Qw.QScrollArea(self.main_window)
        self.scroll.layout = Qw.QVBoxLayout(self.scroll)
        self.scroll.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.scroll)

        # Tabs init
        self.tab_ind = 0
        self.tab_widgets = [ProcessTab(self), GraphsTab(self), SettingsTab(self)]
        self.scroll.layout.addWidget(self.tab_widgets[0])

    def change_tab(self, ind):
        self.current_tab().setParent(None)
        self.tab_ind = ind
        self.tab_widgets[ind].update_info()
        self.scroll.layout.addWidget(self.tab_widgets[ind])

    def update_info(self):
        self.current_tab().update_info()

    def passive_update(self):
        for i in self.tab_widgets:
            i.passive_update()

    def read_settings(self):
        self.settings = Qc.QSettings()
        self.update_frequency = float(self.settings.value('update frequency', 10))
        self.passive_period = float(self.settings.value('passive period', 5))
        if self.timing:
            self.kill_timers()
            self.init_timers()
            self.start_timers()

    def current_tab(self):
        return self.tab_widgets[self.tab_ind]

    def close_handler(self, event):
        if self.tray is not None:
            self.hide_to_tray()
            event.ignore()
        else:
            event.accept()

    def popup_from_tray(self):
        if not self.shown:
            self.update_info()
            self.timer.start()
            self.show()

    def hide_to_tray(self):
        if self.shown:
            self.timer.stop()
            self.hide()

    def show(self):
        self.shown = True
        self.main_window.show()

    def hide(self):
        self.shown = False
        self.main_window.hide()

    def exit(self):
        self.shown = False
        self.kill_timers()
        sys.exit()


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
