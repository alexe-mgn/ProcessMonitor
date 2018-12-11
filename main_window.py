import sys
import psutil
import PyQt5.QtWidgets as Qw
import PyQt5.QtGui as Qg
import PyQt5.QtCore as Qc


class ProcessTab(Qw.QWidget):

    def __init__(self):
        super().__init__()


class GraphsTab(Qw.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)


class SettingsTab(Qw.QGroupBox):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = Qw.QVBoxLayout(self)
        self.lbl = Qw.QLabel()
        self.lbl.setText('612612638262u8346347834723734758346458347654845')
        self.lbl.setFixedSize(self.lbl.sizeHint())
        self.setMinimumSize(self.lbl.sizeHint())


class Main:

    def __init__(self):
        self.init_ui()

    def init_ui(self):
        self.main_window = Qw.QWidget()
        self.main_window.setGeometry(300, 300, 300, 300)
        layout = Qw.QVBoxLayout(self.main_window)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs = Qw.QTabBar()
        self.tabs.setFixedHeight(20)
        self.tabs.addTab('Processes')
        self.tabs.addTab('Graphs')
        self.tabs.addTab('settings')
        layout.addWidget(self.tabs)

        self.scroll = Qw.QScrollArea(self.main_window)
        layout.addWidget(self.scroll)

        self.settings_tab = SettingsTab()
        self.scroll.setWidget(self.settings_tab)

    def show(self):
        self.main_window.show()


if __name__ == '__main__':
    app = Qw.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec())
