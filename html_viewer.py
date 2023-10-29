import sys
from collections import OrderedDict
from PySide6.QtCore import Qt, QUrl, QTimer, Slot, QFileInfo, QDir
from PySide6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtWebEngineWidgets import QWebEngineView

from eye_acuity_test import EyeAcuityTest, EyeAcuityWrapper

from Flowerchart.flowerchart_node import FlowChartDecisionNode, FlowChartProcessNode, FlowChartNode, FlowChartDelayNode, print_kwargs

# For testing purposes
from threading import Thread
import time
# Audio from https://elevenlabs.io
# Free version does not cover commercial license


        
class HTMLWindow(QMainWindow, EyeAcuityWrapper):
    def __init__(self, main_window):
        super().__init__()
        
        # A boolean used to determine if input should be processed or not
        #   Set to false when audio is playing
        self.enable_process_input = True
        self.main_window = main_window

        self.eyeacuitytest = EyeAcuityTest(self)
        # Create a QWebEngineView widget
        self.webview = QWebEngineView(self)

        # Set the central widget to the web view
        self.setCentralWidget(self.webview)

        # Set window properties
        self.setWindowTitle("Eye Acuity Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Used to stop audio streaming to server, while audio playing instructions is running
        #self.tts_timer = QTimer()
        self.media_player = QMediaPlayer()
        
        self.audioOutput = QAudioOutput()
        self.media_player.setAudioOutput(self.audioOutput)
        
        
        # Attach Main Window's .toggleAudioSocketRunning as listener to playingChanged
        # Change in playing state will call self.main_window.toggle_audio_socket_running
        self.media_player.playingChanged.connect(self.main_window.toggle_audio_socket_running)
        self.media_player.playingChanged.connect(self.toggle_processing)

        with open("eye-acuity-pages/default.html") as f:
            self.html_content = f.read()
        
        # Load an HTML content
        self.load_html_content()
        
        
        self.eyeacuitytest.execute_process()
    
        #self.interact_with_page()

    def load_html_content(self):
        # Define the HTML content

        # Load the HTML content into the web view
        self.webview.setHtml(self.html_content, QUrl("about:blank"))
        
        # wait for page to finish loading before calling js
        self.webview.page().loadFinished.connect(self.interact_with_page)

    def interact_with_page(self):
        pass
        # Code to run Javascript on loaded html page
        # self.webview.page().runJavaScript("document.getElementById('change_this').innerHTML = 'This is an example of chaging content with JS!'")
    
    def run_javascript(self, javascript):
        self.webview.page().runJavaScript(javascript)
    
    
    @Slot(str)
    def processText(self, text):
        print(self.eyeacuitytest.current_node)
        if self.enable_process_input:
            # <!> If audio is playing, ignore
            if isinstance(self.eyeacuitytest.current_node, FlowChartDecisionNode):
                self.eyeacuitytest.execute_decision(text)
    
    @Slot()
    def toggle_processing(self):
        self.enable_process_input = not self.enable_process_input
        if (self.enable_process_input):
            if isinstance(self.eyeacuitytest.current_node, FlowChartDelayNode):
                self.eyeacuitytest.execute_delay()
            
    def play_audio(self, relative_audio_location):
        
        try:
            print("file://" + QDir.currentPath() + relative_audio_location)
            self.media_player.setSource(QUrl.fromLocalFile(QDir.currentPath() + relative_audio_location))
            self.media_player.setPosition(0)
            
            self.media_player.play()
        except:
            print("Audio play failed")

class FakeMainWindow(QMainWindow):
    @Slot()
    def toggle_audio_socket_running(self):
        pass
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    fake_main_window = FakeMainWindow()
    window = HTMLWindow(fake_main_window)
    window.show()
    def gui_loop():
        sys.exit(app.exec())
    def input_loop():
        #time.sleep(2)
        # Wait for window to finish loading
        eat = window.eyeacuitytest
        while eat is None:
            eat = window.eyeacuitytest
        while eat.current_node is not None:
            if isinstance(eat.current_node,FlowChartDecisionNode):
                eat.current_node = eat.current_node.execute(input("Enter input: "))
            '''
            elif isinstance(eat.current_node,FlowChartDelayNode):
                print("<Delay node> Pretending delay has passed")
                eat.current_node = eat.current_node.execute()
            '''
    Thread(target = input_loop).start()
    gui_loop() #Must be called from main thread
        
    
