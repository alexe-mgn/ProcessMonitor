import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc


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
        self.cp_label.setText('%.3f' % (self.count_cp(),))

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
        self.proc_type = proc_type
        self.proc_name = proc_name
        self.lay = Qw.QVBoxLayout(self)

        # Заголовок
        self.header = Qw.QWidget(self)
        self.header.setFixedHeight(70)
        layout = Qw.QHBoxLayout(self.header)
        self.lay.addWidget(self.header)
        self.setFixedHeight(70)
        self.setMinimumWidth(200)

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

        # Дополнительная информация.
        self.more_info = Qw.QGroupBox(self)
        self.more_info.hide()
        layout = Qw.QVBoxLayout(self.more_info)
        self.lay.addWidget(self.more_info)

        self.more_proc = Qw.QGroupBox(self.more_info)
        self.more_proc.setMaximumWidth(500)
        layout.addWidget(self.more_proc)

        self.lay2 = Qw.QVBoxLayout(self.more_proc)

        self.get_processes()
        self.procs = []
        self.lay2.setSpacing(10)
        for i in range(len(self.processes)):
            self.procs.append(ExtraProcessWidget(proc=self.processes[i]))
            self.lay2.addWidget(self.procs[i])

        self.count_clicks = 0
        self.update_info()


    def mousePressEvent(self, event):
        self.count_clicks += 1
        if self.count_clicks % 2 == 1:
            self.more_info.show()
            self.setFixedHeight(800)
        else:
            self.more_info.hide()
            self.setFixedHeight(80)


    def get_processes(self):
        self.processes = [e for e in psutil.process_iter() if e.name() == self.proc_name]

    def update_info(self):
        self.cp_label.setText('%.1f%%' % (self.count_cp(),))
        self.memory_label.setText('%.1f%%' % (self.count_memory(),))
        self.count_proc_label.setText(str(self.count_proc()))

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
