from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QPlainTextEdit
from PySide6.QtCore import QRunnable, Slot, Signal, QThread, QMutex
from PySide6.QtCore import Slot

import requests
from phonemizer import phonemize
from phonemizer.separator import Separator

class StateWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QPlainTextEdit()
        layout.addWidget(self.label)
        
        self.phonemics_text_edit = QPlainTextEdit()
        layout.addWidget(self.phonemics_text_edit)
        self.setLayout(layout)
        
        # Create a worker thread
        self.worker_thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.worker_thread)
        self.worker.updatePhonemicsSignal.connect(self.updatePhonemics)
        self.worker_thread.started.connect(self.worker.run)
    
    @Slot()
    def changeLabel(self,text):
        if text != "" or text is not None:
            self.label.insertPlainText(text)
            #self.updatePhonemics(text,"en-us")
            language = "en-us"
            self.worker.updatePhonemicsSignal.emit(text, language)
    
    @Slot(str, str)
    def updatePhonemics(self,text,language):
        phn = phonemize(
                    text,
                    language=language,
                    backend='espeak',  # brew install espeak, then add lib to variable PHONEMIZER_ESPEAK_LIBRARY
                    separator=Separator(phone=None, word=' ', syllable='|'),
                    strip=True,
                    preserve_punctuation=True,
                    njobs=1)
        self.phonemics_text_edit.insertPlainText(phn)
        
        pass
    
    
class Worker(QThread):
    updatePhonemicsSignal = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.text = ""

    def run(self):
        while True:
            #text, language = self.updatePhonemicsSignal.emit()
            if self.text is not None or self.text != "":
                    phn = phonemize(
                        self.text,
                        language="en-us ",
                        backend='espeak',  # brew install espeak, then add lib to variable PHONEMIZER_ESPEAK_LIBRARY
                        separator=Separator(phone=None, word=' ', syllable='|'),
                        strip=True,
                        preserve_punctuation=True,
                        njobs=1)
                    self.phonemicsUpdatedSignal.emit(phn)