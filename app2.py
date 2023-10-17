import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PySide6 import QtCore
from whisper_online import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        label = QLabel("Centered Label")
        title_label = QLabel("Please read the following text:")
        footer_label = QLabel("Footer Label")
        label.setAlignment(QtCore.Qt.AlignCenter)  # Center the label's text
        layout.addWidget(title_label, alignment=QtCore.Qt.AlignAbsolute)
        layout.addWidget(label, alignment=QtCore.Qt.AlignCenter)
        label.setStyleSheet("font-size: 100cm;")
        layout.addWidget(footer_label, alignment=QtCore.Qt.AlignCenter)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyWindow()
    window.setGeometry(100, 100, 400, 300)
    window.show()
    sys.exit(app.exec_())
