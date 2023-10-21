import sys
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import QPointF, Slot, QThreadPool, QThread
from PySide6.QtMultimedia import QAudioFormat, QAudioSource, QMediaDevices
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QWidget, QStackedWidget, QHBoxLayout, QVBoxLayout
from VAD import VAD
import numpy as np

from whisper_worker import WhisperWorker

import socket

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 43007

SAMPLE_COUNT = 2048


RESOLUTION = 8
    
class MainWindow(QMainWindow):
    def __init__(self, device):
        super().__init__()
        
        self.audio_sample_rate = 16000
        self.VAD = VAD(sampleRate=self.audio_sample_rate)
        self.vad_buffer = []
        
        #socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.connect((SERVER_HOST, SERVER_PORT))
        
        # Create chart
        self._series = QLineSeries()
        self._chart = QChart()
        self._chart.addSeries(self._series)
        self._axis_x = QValueAxis()
        self._axis_x.setRange(0, SAMPLE_COUNT)
        self._axis_x.setLabelFormat("%g")
        self._axis_x.setTitleText("Samples")
        self._axis_y = QValueAxis()
        self._axis_y.setRange(-1, 1)
        self._axis_y.setTitleText("Audio level")
        self._chart.setAxisX(self._axis_x, self._series)
        self._chart.setAxisY(self._axis_y, self._series)
        self._chart.legend().hide()
        name = device.description()
        self._chart.setTitle(f"Data from the microphone ({name})")
        self.label = QLabel(self)
        self.label.setText("VAD: No speech detected")
        
        self.textoutput = QLabel(self)
        self.label.setText("Text will show up here")

        # Audio Format
        format_audio = QAudioFormat()
        format_audio.setSampleRate(self.audio_sample_rate)
        format_audio.setChannelCount(1)
        format_audio.setSampleFormat(QAudioFormat.Int16)

        # Set audio source
        self._audio_input = QAudioSource(device, format_audio, self)
        self._io_device = self._audio_input.start()
        self._io_device.readyRead.connect(self._readyRead)

        self._chart_view = QChartView(self._chart)
        
        # Main widget
        self.widget = QWidget(self)
        
        self.layout = QVBoxLayout(self.widget)
        
        self.layout.addWidget(self._chart_view)
        self.layout.addWidget(self.label)
        self.setCentralWidget(self.widget)

        self._buffer = [QPointF(x, 0) for x in range(SAMPLE_COUNT)]
        self._series.append(self._buffer) 
        

    def closeEvent(self, event):
        if self._audio_input is not None:
            self._audio_input.stop()
        if self.server_socket:
            self.server_socket.close()
        event.accept()

    def valuechange(self):
        print("change")
    @Slot()
    def _readyRead(self):
        data = self._io_device.readAll()
        
        # Convert bytes to NumPy array
        numpy_array = np.frombuffer(data.data(), dtype=np.int16)
        
        # Send audio data to the server
        try:
            self.server_socket.sendall(data.data())
        except Exception as e:
            print(f"Error sending data: {e}")
        
        if numpy_array.size == 0:
            pass
        else:
            vad_state = self.VAD.processFrame(numpy_array.tolist())
            #print(self.VAD.activeFrameCount)
            #if (self.VAD.activeFrameCount > 0):
            if (vad_state):
                #print(vad_state)
                self.label.setText("VAD: Speech detected")
            else:
                self.label.setText("VAD: No speech detected")

        try:
        # Not done properly
            for i in range(0, numpy_array.size, 1):
                self._buffer[i].setY(numpy_array[i] / 32768)
                #print(self._buffer[i].y())
        except:
            pass
            
        self._series.replace(self._buffer)
    



if __name__ == '__main__':
    app = QApplication(sys.argv)

    input_devices = QMediaDevices.audioInputs()
    if not input_devices:
        QMessageBox.warning(None, "audio", "There is no audio input device available.")
        sys.exit(-1)
    main_win = MainWindow(input_devices[0])
    main_win.setWindowTitle("audio")
    available_geometry = main_win.screen().availableGeometry()
    size = available_geometry.height() * 3 / 4
    main_win.resize(size, size)
    main_win.show()
    sys.exit(app.exec())