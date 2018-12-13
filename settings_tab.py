import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc


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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.freq = 1.0
        self.pass_freq = 1.0
        self.check = False

    def init_ui(self):
        self.label_fr = Qw.QLabel()
        self.label_fr.setText('Update Frequency')
        self.label_fr.move(20, 50)
        self.label_pas = Qw.QLabel()
        self.label_pas.setText('Passive update period')
        self.label_pas.move(20, 80)

        self.spin_fr = Qw.QDoubleSpinBox()
        self.spin_fr.move(250, 50)
        self.spin_fr.setMaximum(3600.0)
        self.spin_fr.setMinimum(1.0)
        self.spin_fr.setSingleStep(1.0)
        
        self.spin_pas = Qw.QDoubleSpinBox()
        self.spin_pas.move(250, 80)
        self.spin_pas.setMaximum(3600.0)
        self.spin_pas.setMinimum(1.0)
        self.spin_pas.setSingleStep(1.0)

        self.check_b = Qw.QCheckBox()
        self.check_b.setText('Run at startup')

        self.button = Qw.QPushButton()
        self.button.setText('Apply')
        self.button.move(100, 400)
        self.button.clicked.connect(self.apply())

    def apply(self):
        self.pass_freq = self.spin_pas.value()
        self.freq = self.freq.value()
        self.check = self.check_b.isChecked()

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

        self.tab_widgets = [ProcessTab(), GraphsTab(), SettingsTab()]
        self.scroll.setWidget(self.tab_widgets[0])

    def change_tab(self, ind):
        self.layout.removeWidget(self.scroll)
        self.scroll = Qw.QScrollArea(self.main_window)
        self.layout.addWidget(self.scroll)
        self.tab_widgets[ind].update_info()
        self.scroll.setWidget(self.tab_widgets[ind])

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
