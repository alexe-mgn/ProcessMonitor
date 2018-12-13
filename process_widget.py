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
        self.graph_cpu.setFixedHeight(120)
        self.ex_inf_lay.addWidget(self.graph_cpu)

        self.graph_mem = CustomGraph(self.more_info)
        self.graph_mem.plot(self.memory_list)
        self.graph_mem.setFixedHeight(120)

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
        self.cp_label.setText('%.1f%%' % (self.count_cp(),))
        self.memory_label.setText('%.1f%%' % (self.count_memory(),))
        self.count_proc_label.setText(str(self.count_proc()))
        self.memory_list.append(self.count_memory())
        self.cpu_list.append(self.count_cp())
        if self.expanded:
            for i in self.procs:
                i.update_info()

        self.graph_cpu.plot([e for e in self.cpu_list])
        self.graph_mem.clear()
        self.graph_mem.plot([e for e in self.memory_list])

    def passive_update(self):
        self.update_info()

    def count_cp(self):
        return sum([i.cpu_percent() for i in self.processes])

    def count_memory(self):
        return sum([i.memory_percent() for i in self.processes])

    def count_proc(self):
        return len(self.processes)


class Main:
    def __init__(self):
        self.window = Qw.QWidget()
        self.window.setGeometry(0, 0, 300, 300)
        layout = Qw.QVBoxLayout(self.window)
        self.wd = ProcessWidget(proc_name='opera.exe')
        layout.addWidget(self.wd)

    def show(self):
        self.window.show()



if __name__ == '__main__':
    app = Qw.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())
