from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QPlainTextEdit
from PySide6.QtCore import QRunnable, Slot, Signal, QThread, QMutex, Qt, Q_ARG
from PySide6.QtGui import QTextCursor
from PySide6.QtCore import Slot, QMetaObject

import requests

import eng_to_ipa as p

class StateWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Transcription Viewer")
        
        layout = QVBoxLayout()
        self.label = QPlainTextEdit()
        layout.addWidget(self.label)
        
        self.phonemics_text_edit = QPlainTextEdit()
        layout.addWidget(self.phonemics_text_edit)
        self.setLayout(layout)
        
    
    @Slot()
    def changeLabel(self,text):
        if text != "" or text is not None:
            self.label.insertPlainText(text)
            
            self.label.moveCursor(QTextCursor.End)
            self.phonemics_text_edit.insertPlainText(p.convert(text) +"\n")
            
            self.phonemics_text_edit.moveCursor(QTextCursor.End)