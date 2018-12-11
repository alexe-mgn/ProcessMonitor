import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc


class ProcessTab(Qw.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)


class GraphsTab(Qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        lbl = Qw.QLabel('Some graphs here', self)
        lbl.setFixedSize(100, 100)
        self.setFixedSize(100, 100)


class SettingsTab(Qw.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        self.f_lbl = Qw.QLabel('Frequency here', self)
        self.f_lbl.setFixedSize(100, 100)
        self.setFixedSize(100, 100)


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
        self.scroll.setWidget(self.tab_widgets[2])

    def change_tab(self, ind):
        self.layout.removeWidget(self.scroll)
        self.scroll = Qw.QScrollArea(self.main_window)
        self.layout.addWidget(self.scroll)
        self.scroll.setWidget(self.tab_widgets[ind])

    def show(self):
        self.main_window.show()


if __name__ == '__main__':
    app = Qw.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())
