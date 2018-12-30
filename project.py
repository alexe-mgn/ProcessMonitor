import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc
import pyqtgraph as Pg
import time
import sqlite3

APP_NAME = 'Process Monitor'
DATABASE = 'Process_Data.db'
ORG_NAME = 'Project1'
TAB_MINIMUM_SIZE = [275, 275]

db_con = sqlite3.connect(DATABASE)


# Execute function with delay
def delayed(parent, func):
    timer = Qc.QTimer(parent)
    timer.setSingleShot(True)
    timer.timeout.connect(func)
    timer.start(1)


class CustomGraph(Qw.QGroupBox):

    def __init__(self, parent=None, data_path=None):
        super().__init__(parent)

        # Class values
        self.connection = db_con
        self.data_path = data_path
        # min - 60
        # hour - 3600
        # 6 hours - 21600
        # day - 86400
        # Таблица отображения оси абсцисс
        # [max range, unit, tick spacing, axis scale]
        # [60, 900, 3600, 21600, 86400]
        self.ticks = [
            [
                180,
                's',
                10,
                1
            ],
            [
                900,
                'mins',
                1,
                1 / 60
            ],
            [
                4500,
                'mins',
                5,
                1 / 60
            ],
            [
                10800,
                'mins',
                10,
                1 / 60
            ],
            [
                43200,
                'hours',
                1,
                1 / 3600
            ],
            [
                86400,
                'hours',
                2,
                1 / 3600
            ]]
        btn_order = ['Day', '6 hours', 'Hour', '15 mins', 'Current'][::-1]
        btn_count = len(btn_order)

        self.init_storage()

        self.layout = Qw.QGridLayout(self)
        self.layout.setContentsMargins(5, 5, 5, 5)

        # Graph values
        self.graph = Pg.PlotWidget(self)
        self.graph.installEventFilter(self)
        self.item = self.graph.getPlotItem()
        self.box = self.item.getViewBox()
        self.x_axis = self.item.getAxis('bottom')

        # Setting graph options
        self.box.setLimits(xMax=20)
        self.x_axis.enableAutoSIPrefix(False)
        self.graph.setMouseEnabled(True, False)
        self.graph.setMenuEnabled(False)
        self.graph.hideButtons()
        self.graph.showGrid(True, True)

        self.layout.addWidget(self.graph, 0, 0, 1, btn_count)

        for n, i in enumerate(btn_order):
            lbl = Qw.QLabel(i, self)
            lbl.setFixedSize(lbl.sizeHint())
            lbl.mousePressEvent = lambda event, ind=n: self.change_range(ind)
            self.layout.addWidget(lbl, 1, n)

        self.slider = Qw.QSlider(Qc.Qt.Horizontal, self)
        self.slider.setTickPosition(1)
        self.slider.setValue(0)
        self.slider.setRange(0, btn_count - 1)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.ranges = [60, 900, 3600, 21600, 86400]
        self.slider.valueChanged.connect(lambda ind: self.change_range(ind))

        self.layout.addWidget(self.slider, 2, 0, 1, btn_count)

        self.change_range(0)

    def init_storage(self):
        if self.data_path is None:
            self.data = []
        else:
            self.connection.execute(
                'CREATE TABLE if not exists "{0}" (x FLOAT, y FLOAT, group_ind INTEGER)'.format(
                    self.data_path))
            # Table is not empty
            if self.connection.execute(
                    'SELECT count(x) FROM "{}"'.format(
                        self.data_path)
            ).fetchone()[0] > 0:
                # Get current session group
                self.group = self.connection.execute(
                    'SELECT max(group_ind) FROM "{0}"'.format(
                        self.data_path)
                ).fetchone()[0] + 1
            else:
                self.group = 0

    def read_data(self, extra=''):
        if self.data_path is None:
            return self.data
        else:
            return self.connection.execute(
                'SELECT * FROM "{0}"{1}'.format(
                    self.data_path, extra)
            ).fetchall()

    def eventFilter(self, widget, event):
        if event.type() == 31:
            self.adjust_axis()
        event.accept()
        return False

    def change_range(self, ind):
        self.slider.setValue(ind)
        self.graph.setXRange(-self.slider.ranges[ind], 0)
        self.adjust_axis()

    def adjust_axis(self):
        visible_range = self.graph.visibleRange()
        visible_size = visible_range.right() - visible_range.left()
        ind = 0
        ln = len(self.ticks)
        while ind < ln - 1 and visible_size > self.ticks[ind][0]:
            ind += 1
        self.box.setLimits(xMax=visible_size * .1)
        spacing = self.ticks[ind][2]
        self.x_axis.setTickSpacing(spacing, spacing / 2)
        self.x_axis.setScale(self.ticks[ind][3])
        self.x_axis.setLabel('time', units=self.ticks[ind][1])

    def plot(self):
        update_time = time.time()
        self.graph.clear()
        visible_range = self.graph.visibleRange()
        data = self.read_data(
            ' WHERE x >= {0} and x <= {1}'.format(
                update_time + visible_range.left(),
                update_time + visible_range.right()))
        group_datas = {}
        for i in data:
            group = i[2]
            gr_data = group_datas.get(group, None)
            if gr_data is None:
                gr_data = [[], []]
                group_datas[group] = gr_data
            gr_data[0].append(i[0] - update_time)
            gr_data[1].append(i[1])
        for i in group_datas.values():
            self.graph.plot(*i)

    def append(self, dat):
        if self.data_path is None:
            self.data.append([time.time(), dat])
        else:
            self.connection.execute(
                'INSERT INTO "{0}" VALUES ("{1}", {2}, {3})'.format(
                    self.data_path, time.time(), dat, self.group)
            )

    def setLabel(self, *args):
        self.graph.setLabel(*args)

    def setYRange(self, *args):
        self.graph.setYRange(*args)


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
        memory_percent = self.proc.memory_percent()
        self.memory_label.setText(self.count_memory())
        return memory_percent

    def cpu_percent(self):
        cpu_percent = self.proc.cpu_percent()
        self.cp_label.setText('%.3f%%' % (cpu_percent,))
        return cpu_percent

    def exists(self):
        return psutil.pid_exists(self.pid)

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

    def __init__(self, parent=None, proc_name=None):
        super().__init__(parent)
        self.mem_load = 0
        self.cp_load = 0
        self.expanded = False
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
        header_layout = Qw.QHBoxLayout(self.header)
        header_layout.setContentsMargins(10, 2, 10, 2)
        self.layout.addWidget(self.header)
        # Header labels
        self.name_label = Qw.QLabel()
        self.name_label.setText(self.proc_name)
        header_layout.addWidget(self.name_label, 5)
        self.cp_label = Qw.QLabel()
        header_layout.addWidget(self.cp_label, 1)
        self.memory_label = Qw.QLabel()
        header_layout.addWidget(self.memory_label, 1)
        self.count_proc_label = Qw.QLabel()
        header_layout.addWidget(self.count_proc_label, 2)

        # Detailed information popup
        self.more_info = Qw.QWidget(self)
        self.more_info.hide()
        self.layout.addWidget(self.more_info)
        self.more_info.layout = Qw.QVBoxLayout(self.more_info)

        # Processes group box
        self.proc_box = Qw.QWidget(self.more_info)
        self.proc_box.adjust = lambda: self.proc_box.setFixedHeight(self.proc_box.sizeHint().height())
        self.proc_box.layout = Qw.QVBoxLayout(self.proc_box)
        self.proc_box.layout.setContentsMargins(2, 2, 2, 2)
        self.proc_box.layout.setSpacing(2)
        self.proc_box.layout.setAlignment(Qc.Qt.AlignTop)

        # Process group box header
        self.proc_box_header = Qw.QGroupBox()
        proc_header_layout = Qw.QHBoxLayout(self.proc_box_header)
        proc_header_layout.setContentsMargins(5, 2, 5, 2)
        self.proc_box_header.setFixedHeight(30)

        self.label_name = Qw.QLabel()
        self.label_name.setText('PID')
        proc_header_layout.addWidget(self.label_name)
        self.label_cpu = Qw.QLabel()
        self.label_cpu.setText('CPU')
        proc_header_layout.addWidget(self.label_cpu)
        self.label_mem = Qw.QLabel()
        self.label_mem.setText('Mem Usage')
        proc_header_layout.addWidget(self.label_mem)
        self.more_info.layout.addWidget(self.proc_box_header)

        proc_header_layout.insertSpacing(0, 12)
        proc_header_layout.insertSpacing(4, 27)

        # Process group box scroll area
        self.scroll_area = Qw.QScrollArea(self.more_info)
        self.scroll_area.setVerticalScrollBarPolicy(Qc.Qt.ScrollBarAlwaysOn)
        self.scroll_area.setWidget(self.proc_box)
        self.scroll_area.setFixedHeight(200)
        self.scroll_area.setWidgetResizable(True)
        self.more_info.layout.addWidget(self.scroll_area)

        # Initialize subprocesses
        for i in self.get_pids():
            wid = ExtraProcessWidget(pid=i)
            self.proc_box.layout.addWidget(wid)
            self.widgets[i] = wid
        self.proc_box.adjust()
        delayed(self, self.proc_box.adjust)

        self.graph_cpu = CustomGraph(self.more_info, 'PROCESS_CPU.%s' % (self.proc_name,))
        self.graph_cpu.setYRange(0, 100)
        self.graph_cpu.plot()
        self.graph_cpu.setFixedHeight(190)
        self.graph_cpu.setLabel('left', 'CPU')
        self.more_info.layout.addWidget(self.graph_cpu)

        self.graph_mem = CustomGraph(self.more_info, 'PROCESS_MEM.%s' % (self.proc_name,))
        self.graph_mem.setYRange(0, 100)
        self.graph_mem.plot()
        self.graph_mem.setFixedHeight(190)
        self.graph_mem.setLabel('left', 'Memory usage')
        self.more_info.layout.addWidget(self.graph_mem)

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
        self.proc_box.adjust()
        self.adjust()
        self.parent().adjust()

    def get_pids(self):
        return set(e.pid for e in self.process_iter() if psutil.pid_exists(e.pid) and e.name() == self.proc_name)

    def process_iter(self):
        if self.parent() is not None:
            return self.parent().process_iter()
        else:
            return []

    def add_new(self):
        np = self.get_pids()
        if len(np) < 1:
            self.remove()
        new = np - set(self.widgets.keys())
        if len(new) > 0:
            for i in new:
                wid = ExtraProcessWidget(pid=i)
                self.proc_box.layout.addWidget(wid)
                self.widgets[i] = wid
            self.proc_box.adjust()
            delayed(self, self.proc_box.adjust)

    def update_info(self):
        self.count_res_usage()
        self.cp_label.setText('%.1f%%' % (self.cp_load,))
        self.memory_label.setText('%.1f%%' % (self.mem_load,))
        self.count_proc_label.setText(str(self.count_proc_num()))
        self.add_graph_data()

        if self.expanded:
            self.update_graphs()

    def passive_update(self):
        if not self.parent().main.shown or self.parent().main.current_tab() != self.parent():
            self.count_res_usage()
            self.add_graph_data()
        self.add_new()

    def add_graph_data(self):
        self.graph_cpu.append(self.cp_load)
        self.graph_mem.append(self.mem_load)

    def update_graphs(self):
        self.graph_cpu.plot()
        self.graph_mem.plot()

    def count_res_usage(self):
        cp_load, mem_load = 0, 0
        have_subprocs = False
        for k, v in self.widgets.copy().items():
            try:
                cp_load += v.cpu_percent()
                mem_load += v.memory_percent()
                # v.update_info()
                have_subprocs = True
            except psutil._exceptions.NoSuchProcess:
                v.deleteLater()
                self.proc_box.layout.removeWidget(v)
                del self.widgets[k]
                self.proc_box.adjust()
        if not have_subprocs:
            self.remove()
        else:
            self.cp_load = cp_load
            self.mem_load = mem_load

    def count_proc_num(self):
        return len(self.widgets)

    def remove(self):
        if self.parent() is not None:
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
        self.header = Qw.QGroupBox()
        self.header.setMaximumWidth(700)
        header_layout = Qw.QHBoxLayout(self.header)
        header_layout.setContentsMargins(5, 2, 5, 2)
        self.header.setFixedHeight(30)
        self.label_name = Qw.QLabel()
        self.label_name.setText('Name')
        header_layout.addWidget(self.label_name, 5)
        self.label_cpu = Qw.QLabel()
        self.label_cpu.setText('CPU')
        header_layout.addWidget(self.label_cpu, 1)
        self.label_mem = Qw.QLabel()
        self.label_mem.setText('Mem usage')
        header_layout.addWidget(self.label_mem, 1)
        self.label_count = Qw.QLabel()
        self.label_count.setText('proc. count')
        header_layout.addWidget(self.label_count, 2)
        self.layout.addWidget(self.header)

        header_layout.insertSpacing(0, 20)
        header_layout.insertSpacing(5, 20)

        for i in self.processes:
            wid = ProcessWidget(self, proc_name=i)
            self.layout.addWidget(wid)
            self.widgets[i] = wid
        self.adjust()

    def delete_element(self, name):
        if name is self.widgets.keys():
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
            delayed(self, self.adjust)
        self.processes = np

    def passive_update(self):
        self.add_new()
        for k, v in self.widgets.copy().items():
            v.passive_update()

    def get_processes(self):
        return set([e.name() for e in self.process_iter() if psutil.pid_exists(e.pid)])

    def process_iter(self):
        return self.main.process_iter


class GraphsTab(Qw.QGroupBox):

    def __init__(self, parent):
        super().__init__()
        self.main = parent
        # self.setMinimumSize(*TAB_MINIMUM_SIZE)
        self.init_ui()

    def init_ui(self):
        self.layout = Qw.QGridLayout(self)

        self.cpu_graph = CustomGraph(self, 'CPU')
        self.cpu_graph.setYRange(0, 100)
        self.cpu_graph.setMinimumSize(300, 180)
        self.cpu_graph.item.setLabel('left', 'CPU load')
        self.layout.addWidget(self.cpu_graph, 0, 0)

        self.mem_graph = CustomGraph(self, 'MEMORY')
        self.mem_graph.setYRange(0, 100)
        self.mem_graph.setMinimumSize(300, 180)
        self.mem_graph.item.setLabel('left', 'Memory usage')
        self.layout.addWidget(self.mem_graph, 1, 0)

        self.setMinimumSize(self.sizeHint())

    def update_info(self):
        self.cpu_graph.append(psutil.cpu_percent())
        self.mem_graph.append(psutil.virtual_memory().percent)
        self.cpu_graph.plot()
        self.mem_graph.plot()

    def passive_update(self):
        if self.main.current_tab() != self or not self.main.shown:
            self.update_info()


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

        self.graph_label = Qw.QLabel(self)
        self.graph_label.setText('Graph range (mins)')
        self.graph_label.move(20, 70)

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
        self.main.set_graph_range()

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
        self.process_iter = list(psutil.process_iter())
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

        self.update_info()

    def change_tab(self, ind):
        self.scroll.takeWidget()
        self.tab_ind = ind
        self.tab_widgets[ind].update_info()
        self.scroll.setWidget(self.tab_widgets[ind])

    def update_info(self):
        self.current_tab().update_info()

    def passive_update(self):
        self.process_iter = list(psutil.process_iter())
        for i in self.tab_widgets:
            i.passive_update()

    def read_settings(self):
        self.settings = Qc.QSettings()
        self.update_frequency = float(self.settings.value('update frequency', 1))
        self.passive_period = float(self.settings.value('passive period', 5))
        if self.timing:
            self.kill_timers()
            self.init_timers()
            self.start_timers()

    def current_tab(self):
        return self.tab_widgets[self.tab_ind]

    def close_handler(self, event):
        db_con.commit()
        if self.tray is not None:
            self.hide_to_tray()
            event.ignore()
        else:
            event.accept()

    def popup_from_tray(self):
        db_con.commit()
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
        db_con.commit()
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
