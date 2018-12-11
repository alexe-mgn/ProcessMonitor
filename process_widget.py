import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc


class ProcessWidget(Qw.QGroupBox):
    def __init__(self, parent=None, proc_name=None, type=''):
        super().__init__(parent)
        self.type = type
        self.proc_name = proc_name
        self.lay = Qw.QVBoxLayout(self)
        self.header = Qw.QWidget(self)
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
        self.type_label.setText(self.type)
        layout.addWidget(self.type_label, 3)
        self.get_processes()
        self.update()

    def mousePressEvent(self, event):
        pass

    def get_processes(self):
        self.processes = [e for e in psutil.process_iter() if e.name() == self.proc_name]

    def update(self):
        self.cp_label.setText(str('%.1f%%' % (self.count_cp(),)))
        self.memory_label.setText('%.1f%%' % (self.count_memory(),))
        self.count_proc_label.setText(str(self.count_proc()))

    def count_cp(self):
        cp = sum([i.cpu_percent() for i in self.processes])
        return cp

    def count_memory(self):
        memory = round(sum([i.memory_percent() for i in self.processes]))
        return memory

    def count_proc(self):
        return len(self.processes)


class Main:
    def __init__(self):
        self.window = Qw.QWidget()
        self.window.setGeometry(0, 0, 300, 300)
        layout = Qw.QVBoxLayout(self.window)
        self.wd = ProcessWidget(proc_name='chrome.exe')
        layout.addWidget(self.wd)

    def show(self):
        self.window.show()


if __name__ == '__main__':
    app = Qw.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())
