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


class ExtraProcessWidget(Qw.QGroupBox):

    def __init__(self, pid, parent=None):
        super().__init__(parent)
        layout = Qw.QHBoxLayout(self)
        self.proc = psutil.Process(pid)
        self.pid = pid
        self.pid_label = Qw.QLabel()
        self.pid_label.setText(str(pid))
        layout.addWidget(self.pid_label)
        self.cp_label = Qw.QLabel()
        layout.addWidget(self.cp_label)
        self.memory_label = Qw.QLabel()
        layout.addWidget(self.memory_label)
        self.setFixedHeight(40)

        self.update_info()

    def update_info(self):
        self.memory_label.setText(self.count_memory())
        self.cp_label.setText('%.3f%%' % (self.cpu_percent(),))

    def count_memory(self):
        return self.human_read_format(self.proc.memory_info().rss)

    def memory_percent(self):
        return self.proc.memory_percent()

    def cpu_percent(self):
        return self.proc.cpu_percent()

    @staticmethod
    def human_read_format(size):
        levels = ['Б', 'КБ', 'МБ', 'ГБ']
        lvl = 0
        cr = size
        while cr // 1024 > 0:
            cr = cr // 1024
            lvl += 1
        return str(round(size / 1024 ** lvl)) + levels[lvl]


class ProcessWidget(Qw.QGroupBox):

    def __init__(self, parent=None, proc_name=None, proc_type=''):
        super().__init__(parent)
        self.x_range = 60
        self.expanded = False
        self.proc_type = proc_type
        self.proc_name = proc_name
        style = 'QLabel {font-size: 16px;}'

        self.widgets = {}

        self.setMinimumWidth(300)
        self.setMaximumWidth(700)
        self.layout = Qw.QVBoxLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Header
        self.header = Qw.QGroupBox(self)
        self.header.setStyleSheet(style)
        self.header.setFixedHeight(40)
        self.header.mousePressEvent = lambda *args: self.popup_resize()
        layout = Qw.QHBoxLayout(self.header)
        layout.setContentsMargins(10, 2, 10, 2)
        self.layout.addWidget(self.header)

        self.name_label = Qw.QLabel()
        self.name_label.setText(self.proc_name)

        layout.addWidget(self.name_label, 5)
        self.cp_label = Qw.QLabel()
        layout.addWidget(self.cp_label, 1)
        self.memory_label = Qw.QLabel()
        layout.addWidget(self.memory_label, 1)
        self.count_proc_label = Qw.QLabel()
        layout.addWidget(self.count_proc_label, 2)




        self.more_info = Qw.QGroupBox(self)
        self.more_info.hide()
        self.layout.addWidget(self.more_info)
        self.ex_inf_lay = Qw.QVBoxLayout(self.more_info)

        self.more_proc = Qw.QWidget(self.more_info)
        self.more_proc.adjust = lambda: self.more_proc.setFixedHeight(self.more_proc.sizeHint().height())

        self.layout2 = Qw.QVBoxLayout(self.more_proc)
        self.layout2.setContentsMargins(2, 2, 2, 2)
        self.layout2.setSpacing(2)
        self.widget1 = Qw.QGroupBox()
        self.extralay = Qw.QHBoxLayout(self.widget1)
        self.extralay.setContentsMargins(5, 2, 5, 2)
        self.widget1.setFixedHeight(30)
        self.label_name = Qw.QLabel()
        self.label_name.setText('PID')
        self.extralay.addWidget(self.label_name)
        self.label_cpu = Qw.QLabel()
        self.label_cpu.setText('CPU')
        self.extralay.addWidget(self.label_cpu)
        self.label_mem = Qw.QLabel()
        self.label_mem.setText('Mem Usage')
        self.extralay.addWidget(self.label_mem)
        self.ex_inf_lay.addWidget(self.widget1)

        self.scroll_area = Qw.QScrollArea(self.more_info)
        self.scroll_area.setVerticalScrollBarPolicy(Qc.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidget(self.more_proc)
        self.scroll_area.setFixedHeight(200)
        self.scroll_area.setWidgetResizable(True)

        self.extralay.insertSpacing(0, 12)
        self.extralay.insertSpacing(4, 27)

        self.ex_inf_lay.addWidget(self.scroll_area)


        self.layout2.setAlignment(Qc.Qt.AlignTop)

        self.add_new()

        self.count_clicks = 0
        self.memory_list = []
        self.cpu_list = []

        self.graph_cpu = CustomGraph(self.more_info)
        self.graph_cpu.plot(self.cpu_list)
        self.graph_cpu.setFixedHeight(150)
        self.graph_cpu.setXRange(0, -self.x_range)
        self.graph_cpu.setYRange(0, 100)
        self.graph_cpu.setLabel('left', 'CPU')

        self.ex_inf_lay.addWidget(self.graph_cpu)

        self.graph_mem = CustomGraph(self.more_info)
        self.graph_mem.plot(self.memory_list)
        self.graph_mem.setFixedHeight(150)
        self.graph_mem.setXRange(0, -self.x_range)
        self.graph_mem.setLabel('left', 'Memory usage')

        self.ex_inf_lay.addWidget(self.graph_mem)

        self.update_info()
        self.adjust()

    def adjust(self):
        self.setFixedHeight(self.sizeHint().height())

    def popup_resize(self):
        if self.expanded:
            self.scroll_area.verticalScrollBar().setValue(0)
            self.more_info.hide()
        else:
            self.more_info.show()
        self.expanded = not self.expanded
        self.more_proc.adjust()
        self.adjust()
        self.parent().adjust()

    def get_pids(self):
        return set(e.pid for e in psutil.process_iter() if e.name() == self.proc_name)

    def add_new(self):
        np = self.get_pids()
        if len(np) < 1:
            self.remove()
        new = np - set(self.widgets.keys())
        if len(new) > 0:
            lst = [psutil.Process(e).name() for e in new]
            for i in new:
                wid = ExtraProcessWidget(pid=i)
                self.layout2.addWidget(wid)
                self.widgets[i] = wid
            self.more_proc.adjust()

    def update_info(self):
        if self.expanded:
            self.update_children()
        self.count_res()
        self.cp_label.setText('%.1f%%' % (self.mem_load,))
        self.memory_label.setText('%.1f%%' % (self.cp_load,))
        self.count_proc_label.setText(str(self.count_proc_num()))
        self.save_graph_data()

        if self.expanded:
            self.update_graphs()

    def update_children(self):
        for k, v in self.widgets.copy().items():
            if psutil.pid_exists(k):
                v.update_info()
            else:
                self.layout2.removeWidget(v)
                v.deleteLater()
                del self.widgets[k]
                self.more_proc.setFixedHeight(self.more_proc.sizeHint().height())

    def passive_update(self):
        self.add_new()
        self.save_graph_data()

    def save_graph_data(self):
        update_time = time.time()
        self.memory_list.append([update_time, self.cp_load])
        self.cpu_list.append([update_time, self.mem_load])
        self.clear_garbage(update_time)

    def update_graphs(self):
        update_time = time.time()
        self.graph_cpu.clear()
        self.graph_cpu.plot([e[0] - update_time for e in self.cpu_list], [e[1] for e in self.cpu_list])
        self.graph_mem.clear()
        self.graph_mem.plot([e[0] - update_time for e in self.memory_list], [e[1] for e in self.memory_list])

    def clear_garbage(self, cur_time):
        self.cpu_list = [e for e in self.cpu_list if e[0] - cur_time >= -self.x_range]
        self.memory_list = [e for e in self.memory_list if e[0] - cur_time >= -self.x_range]

    def count_res(self):
        cp_load, mem_load = 0, 0
        have_subprocs = False
        for i in self.widgets.values():
            if psutil.pid_exists(i.pid):
                have_subprocs = True
                cp_load += i.cpu_percent()
                mem_load += i.memory_percent()
        if not have_subprocs:
            self.remove()
        else:
            self.cp_load = cp_load
            self.mem_load = mem_load

    def count_proc_num(self):
        return len(self.widgets)

    def remove(self):
        self.parent().delete_element(self.proc_name)

class ProcessTab(Qw.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.main = parent
        self.init_ui()

    def init_ui(self):
        self.layout = Qw.QVBoxLayout(self)
        self.processes = self.get_processes()
        self.widgets = {}

         # Widget for Names of columns
        self.widget1 = Qw.QGroupBox()
        self.widget1.setMaximumWidth(700)
        self.extralay = Qw.QHBoxLayout(self.widget1)
        self.extralay.setContentsMargins(5, 2, 5, 2)
        self.widget1.setFixedHeight(30)
        self.label_name = Qw.QLabel()
        self.label_name.setText('Name')
        self.extralay.addWidget(self.label_name,5)
        self.label_cpu = Qw.QLabel()
        self.label_cpu.setText('CPU')
        self.extralay.addWidget(self.label_cpu,1)
        self.label_mem = Qw.QLabel()
        self.label_mem.setText('Mem Usage')
        self.extralay.addWidget(self.label_mem,1)
        self.label_count = Qw.QLabel()
        self.label_count.setText('Count of processes')
        self.extralay.addWidget(self.label_count,2)
        self.layout.addWidget(self.widget1)

        for i in self.processes:
            wid = ProcessWidget(self, proc_name=i)
            self.layout.addWidget(wid)
            self.widgets[i] = wid
        self.adjust()

    def delete_element(self, name):
        self.widgets[name].deleteLater()
        self.layout.removeWidget(self.widgets[name])
        del self.widgets[name]
        self.adjust()

    def adjust(self):
        self.setFixedHeight(self.sizeHint().height())

    def update_info(self):
        for k, v in self.widgets.copy().items():
            v.update_info()

    def add_new(self):
        np = self.get_processes()
        new = np - self.processes
        if len(new) > 0:
            for i in new:
                wid = ProcessWidget(proc_name=i)
                self.layout.addWidget(wid)
                self.widgets[i] = wid
            self.adjust()
            timer = Qc.QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self.adjust)
            timer.start(1)
        self.processes = np

    def passive_update(self):
        self.add_new()
        for k, v in self.widgets.copy().items():
            v.passive_update()

    @staticmethod
    def get_processes():
        return set(map(lambda e: e.name(), list(psutil.process_iter())))


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
        if self.main.current_tab() != self or not self.main.shown:
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
        self.icon = Qg.QIcon(APP_NAME + '.ico')
        # Main window
        self.main_window = Qw.QWidget()
        self.main_window.setWindowTitle(APP_NAME)
        self.main_window.setWindowIcon(self.icon)
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
            self.tray.setIcon(self.icon)
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
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        # Tabs init
        self.tab_ind = 0
        self.tab_widgets = [ProcessTab(self), GraphsTab(self), SettingsTab(self)]
        self.scroll.setWidget(self.tab_widgets[0])

    def change_tab(self, ind):
        self.scroll.takeWidget()
        self.tab_ind = ind
        self.tab_widgets[ind].update_info()
        self.scroll.setWidget(self.tab_widgets[ind])

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
            self.tray.showMessage('Notification', 'Application minimized to tray', self.icon, 1000)

    def show(self):
        self.shown = True
        self.main_window.show()

    def hide(self):
        self.shown = False
        self.main_window.hide()

    def exit(self):
        self.shown = False
        self.kill_timers()
        if self.tray is not None:
            self.tray.hide()
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
