import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc


APP_NAME = 'Process Monitor'
ORG_NAME = 'Project1'


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
        self.init_ui()

    def init_ui(self):
        pass

    def update_info(self):
        pass


class SettingsTab(Qw.QWidget):

    def __init__(self, parent):
        super().__init__()
        self.main = parent
        self.init_ui()
        self.check = False

    def init_ui(self):
        self.label_fr = Qw.QLabel(self)
        self.label_fr.setText('Update Frequency')
        self.label_fr.move(20, 30)
        self.label_pas = Qw.QLabel(self)
        self.label_pas.setText('Passive update period')
        self.label_pas.move(20, 50)

        self.spin_fr = Qw.QDoubleSpinBox(self)
        self.spin_fr.move(200, 30)
        self.spin_fr.setMaximum(3600.0)
        self.spin_fr.setMinimum(1.0)
        self.spin_fr.setSingleStep(1.0)
        
        self.spin_pas = Qw.QDoubleSpinBox(self)
        self.spin_pas.move(200, 50)
        self.spin_pas.setMaximum(3600.0)
        self.spin_pas.setMinimum(1.0)
        self.spin_pas.setSingleStep(1.0)

        self.check_b = Qw.QCheckBox(self)
        self.check_b.move(20,70)
        self.check_b.setText('Run at startup')

        self.button = Qw.QPushButton(self)
        self.button.setText('Apply')
        self.button.move(100, 100)
        self.button.clicked.connect(self.apply)

    def apply(self):
        self.main.settings.setValue('passive period',self.spin_pas.value())
        self.main.settings.setValue('update frequency',self.spin_fr.value())
        self.check = self.check_b.isChecked()
        self.main.read_settings()

    def update_info(self):
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
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)

        self.tab_ind = 0
        self.tab_widgets = [ProcessTab(), GraphsTab(), SettingsTab(self)]
        self.scroll.setWidget(self.tab_widgets[0])

    def change_tab(self, ind):
        self.tab_ind = ind
        self.layout.removeWidget(self.scroll)
        self.scroll = Qw.QScrollArea(self.main_window)
        self.scroll.setWidgetResizable(True)
        self.layout.addWidget(self.scroll)
        self.tab_widgets[ind].update_info()
        self.scroll.setWidget(self.tab_widgets[ind])

    def update_info(self):
        self.tab_widgets[self.tab_ind].update_info()

    def passive_update(self):
        pass

    def read_settings(self):
        self.settings = Qc.QSettings()
        self.update_frequency = self.settings.value('update frequency', 10)
        self.passive_period = self.settings.value('passive period', 5)
        if self.timing:
            self.kill_timers()
            self.init_timers()
            self.start_timers()

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
