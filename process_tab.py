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
    def __init__(self, parent=None, proc=None):
        super().__init__(parent)
        layout = Qw.QHBoxLayout(self)
        self.proc = proc
        self.pid_label = Qw.QLabel()
        self.pid_label.setText(str(self.proc.pid))
        layout.addWidget(self.pid_label)
        self.cp_label = Qw.QLabel()
        layout.addWidget(self.cp_label)
        self.memory_label = Qw.QLabel()
        layout.addWidget(self.memory_label)

        self.update_info()

    def update_info(self):
        self.memory_label.setText(self.count_memory())
        self.cp_label.setText('%.3f%%' % (self.count_cp(),))

    def count_memory(self):
        return self.human_read_format(self.proc.memory_info().rss)

    def count_cp(self):
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
        self.lay = Qw.QVBoxLayout(self)
        self.lay.setContentsMargins(5, 5, 5, 5)
        self.header = Qw.QGroupBox(self)
        self.header.setFixedHeight(40)
        self.header.mousePressEvent = lambda *args: self.popup_resize()
        layout = Qw.QHBoxLayout(self.header)
        layout.setContentsMargins(10, 2, 10, 2)
        self.lay.addWidget(self.header)
        # self.setMinimumHeight(self.sizeHint().height())
        self.setFixedHeight(self.sizeHint().height())
        # self.setFixedHeight(60)
        self.setMinimumWidth(300)
        self.setMaximumWidth(700)

        style = 'QLabel {font-size: 16px;}'
        self.header.setStyleSheet(style)
        self.name_label = Qw.QLabel()
        self.name_label.setText(self.proc_name)

        layout.addWidget(self.name_label, 5)
        self.cp_label = Qw.QLabel()
        layout.addWidget(self.cp_label, 1)
        self.memory_label = Qw.QLabel()
        layout.addWidget(self.memory_label, 1)
        self.count_proc_label = Qw.QLabel()
        layout.addWidget(self.count_proc_label, 2)
        self.type_label = Qw.QLabel()
        self.type_label.setText(self.proc_type)
        layout.addWidget(self.type_label, 3)
        self.get_processes()

        self.more_info = Qw.QGroupBox(self)
        self.more_info.hide()
        self.lay.addWidget(self.more_info)
        self.ex_inf_lay = Qw.QVBoxLayout(self.more_info)

        self.more_proc = Qw.QWidget(self.more_info)

        self.lay2 = Qw.QVBoxLayout(self.more_proc)
        self.lay2.setContentsMargins(2, 2, 2, 2)
        self.lay2.setSpacing(2)
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

        self.procs = []

        self.lay2.setAlignment(Qc.Qt.AlignTop)

        for i in range(len(self.processes)):
            self.procs.append(ExtraProcessWidget(proc=self.processes[i]))
            self.procs[i].setFixedHeight(30)
            self.lay2.addWidget(self.procs[i])

        self.count_clicks = 0
        self.get_processes()
        self.memory_list = []
        self.cpu_list = []

        self.graph_cpu = CustomGraph(self.more_info)
        self.graph_cpu.plot(self.cpu_list)
        self.graph_cpu.setFixedHeight(150)
        self.graph_cpu.setXRange(0, -self.x_range)
        self.graph_cpu.setYRange(0, 100)
        self.graph_cpu.setLabel('left','CPU')


        self.ex_inf_lay.addWidget(self.graph_cpu)

        self.graph_mem = CustomGraph(self.more_info)
        self.graph_mem.plot(self.memory_list)
        self.graph_mem.setFixedHeight(150)
        self.graph_mem.setXRange(0, -self.x_range)
        self.graph_mem.setLabel('left','Memory usage')



        self.ex_inf_lay.addWidget(self.graph_mem)

        self.update_info()

    def popup_resize(self):
        if self.expanded:
            self.scroll_area.verticalScrollBar().setValue(0)
            self.more_info.hide()
        else:
            self.more_info.show()
        self.expanded = not self.expanded
        self.setFixedHeight(self.sizeHint().height())
        self.parent().resize(self.parent().size().width(), self.parent().sizeHint().height())

    def get_processes(self):
        self.processes = [e for e in psutil.process_iter() if e.name() == self.proc_name]

    def update_info(self):
        self.delete_dead_proc()
        update_time=time.time()
        self.cp_label.setText('%.1f%%' % (self.count_cp(),))
        self.memory_label.setText('%.1f%%' % (self.count_memory(),))
        self.count_proc_label.setText(str(self.count_proc()))
        self.memory_list.append([update_time, self.count_memory()])
        self.cpu_list.append([update_time,self.count_cp()])
        if self.expanded:
            for i in self.procs:
                i.update_info()

        self.graph_cpu.clear()
        self.graph_cpu.plot([e[0] - update_time for e in self.cpu_list], [e[1] for e in self.cpu_list])
        self.graph_mem.clear()
        self.graph_mem.plot([e[0] - update_time for e in self.memory_list], [e[1] for e in self.memory_list])
        self.clear_garbage(update_time)

    def clear_garbage(self, cur_time):
        self.cpu_list = [e for e in self.cpu_list if e[0] - cur_time >= -self.x_range]
        self.memory_list = [e for e in self.memory_list if e[0] - cur_time >= -self.x_range]


    def passive_update(self):
        self.update_info()

    def count_cp(self):
        return sum([i.cpu_percent() for i in self.processes])

    def count_memory(self):
        return sum([i.memory_percent() for i in self.processes])

    def count_proc(self):
        return len(self.processes)

    def delete_dead_proc(self):
        for i in self.processes:
            if psutil.pid_exists(i.pid) is False:
                self.procs[self.processes.index(i)].hide()
                self.parent().resize(self.parent().size().width(), self.parent().sizeHint().height())
                del self.procs[self.processes.index(i)]
                del self.processes[self.processes.index(i)]





class ProcessTab(Qw.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.init_ui()


    def init_ui(self):

        self.proc_wds=[]
        self.layout = Qw.QVBoxLayout(self)

        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(2)
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
        self.label_type=Qw.QLabel()
        self.label_type.setText('Type')
        self.extralay.addWidget(self.label_type,3)
        self.layout.addWidget(self.widget1)

        for e in range(len(self.get_processes())):
            self.proc_wds.append(ProcessWidget(self,proc_name=self.get_processes()[e]))
            self.layout.addWidget(self.proc_wds[e])
        self.setFixedHeight(self.sizeHint().height())

    def update_info(self):
        self.delete_dead_proc()
        for e in self.proc_wds:
            e.update_info()


    def passive_update(self):
        pass

    def get_processes(self):
        self.processes = list(set(map(lambda e: e.name(),list( psutil.process_iter()))))
        return self.processes

    def delete_dead_proc(self):
        for i in self.get_processes():
            if i not in list(map(lambda e: e.name(),list(psutil.process_iter()))):
                self.proc_wds[self.get_processes().index(i)].hide()
                self.parent().resize(self.parent().size().width(), self.parent().sizeHint().height())
                del self.proc_wds[self.get_processes().index(i)]
                del self.get_processes()[self.get_processes().index(i)]

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


class GraphsTab(Qw.QWidget):

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
        self.main_window.setGeometry(300, 300, 300, 300)
        self.main_window.setMinimumSize(300, 300)
        self.layout = Qw.QVBoxLayout(self.main_window)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

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
