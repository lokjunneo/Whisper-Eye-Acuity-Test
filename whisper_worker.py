from PySide6.QtCore import QRunnable, Slot, Signal, QThread, QMutex
from PySide6.QtWidgets import QApplication
import time
from whisper_online import *
import multiprocessing

asr = FasterWhisperASR("en", "small")
a = load_audio_chunk("audio.wav",0,1)
asr.use_vad()
asr.change_original_language("en")
asr.transcribe(a)
online = OnlineASRProcessor(asr, "en")
stored_buffer = np.array([], dtype=np.float32)

def transcription(audio):
    print("<<< TRANSCRIPTION >>>")
    online.insert_audio_chunk(audio)
    result = online.process_iter()
    #valueChanged.emit(result)  # Emit the result
    print(result)
    return result

class WhisperWorker(QThread):
    valueChanged = Signal(str)  # Signal to emit the result

    def __init__(self):
        super(WhisperWorker, self).__init__()

        self.running = False
        self.mutex = QMutex()

        src_lan = "cn"  # source language
        tgt_lan = "en"  # target language

        self.asr = FasterWhisperASR(src_lan, "small")
        self.asr.use_vad()
        self.asr.change_original_language("en")

        self.online = OnlineASRProcessor(self.asr, tgt_lan)

        self.stored_buffer = np.array([], dtype=np.float32)

    @Slot(np.ndarray)
    def pass_buffer(self, audio_buffer):
        #print("Data passed")
        self.mutex.lock()
        self.stored_buffer = np.append(self.stored_buffer, audio_buffer)
        self.mutex.unlock()
            #self.transcription(self.stored_buffer)

    def run(self):
        self.running = True
        while (self.running):
            
            #print("<<< RUNNING >>> ")
            if (self.stored_buffer.size > 1):
                self.mutex.lock()
                copied_audio_buffer = self.stored_buffer.copy()
                self.stored_buffer = np.array([], dtype=np.float32)
                self.mutex.unlock()
                
                process = multiprocessing.Process(target=transcription, args=(copied_audio_buffer,))
                #self.transcription()
                process.start()

                print("Process joining")
                print(process.join())

    def transcription(self,audio):
        if (self.stored_buffer.size > 1024):
            print("<<< TRANSCRIPTION >>>")
            self.online.insert_audio_chunk(audio)
            result = self.online.process_iter()
            self.valueChanged.emit(result)  # Emit the result
            print(result)
            return result
'''
    def transcription(self, audio_array):
        self.parsing = True
        self.online.insert_audio_chunk(audio_array)
        o = self.online.process_iter()
        print(o)
        self.parsing = False
'''
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)

    worker = WhisperWorker()
    #worker.valueChanged.connect(print)  # Connect the signal to a slot (e.g., print)

    # Simulate passing an audio buffer to the worker
    #f = open("audio2.wav","r")
    #audio_data = f.read()
    #f.close()
    #audio_buffer = np.frombuffer(audio_data, dtype=np.int16)  # Simulated audio data
    #worker.pass_buffer(audio_buffer)

    sys.exit(app.exec_())