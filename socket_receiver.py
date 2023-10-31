from PySide6.QtCore import QRunnable, Slot, Signal, QThread, QMutex
from PySide6.QtWidgets import QApplication
import time

class SocketReceiver(QThread):

    update_signal = Signal(str)
    #phonemic_signal = Signal(str,str)
    html_update_signal = Signal(str)
    def __init__(self):
        super(SocketReceiver, self).__init__()
        self.socket_recv_data = b''
    
    def setup(self, socket, stateWindow, htmlWindow):
        self.server_socket = socket
        self.stateWindow = stateWindow
        self.htmlWindow = htmlWindow
        self.update_signal.connect(stateWindow.changeLabel)
        self.html_update_signal.connect(htmlWindow.processText)
        #self.phonemic_signal.connect(stateWindow.updatePhonemics)

    def run(self):
        self.running = True
        while True:
            try:
                recv_data = self.server_socket.recv(4098)
                # just in case of unreliable data
                if len(recv_data) < 1:
                    #break
                    continue
                #print(recv_data.decode('utf-8'))
                
                print("<appending>", recv_data.decode('utf-8'), "</appending>")
                self.socket_recv_data += recv_data
            except:
                # Buffer not ready
                continue
            if len(self.socket_recv_data) >= 1:
                decoded_received_data = self.socket_recv_data.decode('utf-8')
                print("I received: ", decoded_received_data)
                #self.stateWindow.changeLabel(decoded_received_data)
                #self.emit(Signal('log1(QString)'), decoded_received_data)
                #self.emit(Signal('log1(QString)'), decoded_received_data)
                self.update_signal.emit(decoded_received_data)
                self.html_update_signal.emit(decoded_received_data)
                
                #self.phonemic_signal.emit(decoded_received_data, "en-us")
                self.socket_recv_data = b''
                
        
if __name__ == '__main__':
    pass
    #worker.valueChanged.connect(print)  # Connect the signal to a slot (e.g., print)

    # Simulate passing an audio buffer to the worker
    #f = open("audio2.wav","r")
    #audio_data = f.read()
    #f.close()
    #audio_buffer = np.frombuffer(audio_data, dtype=np.int16)  # Simulated audio data
    #worker.pass_buffer(audio_buffer)

    #sys.exit(app.exec_())