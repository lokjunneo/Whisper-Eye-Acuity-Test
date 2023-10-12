from whisper_online import *

src_lan = "en"  # source language
tgt_lan = "en"  # target language  -- same as source for ASR, "en" if translate task is used

asr = FasterWhisperASR(src_lan, "small")

asr.change_original_language("cn")
#asr = FasterWhisperASR(src_lan, "large-v2")  # loads and wraps Whisper model
# set options:
# asr.set_translate_task()  # it will translate from lan into English
asr.use_vad()  # set using VAD 


online = OnlineASRProcessor(tgt_lan, asr)  # create processing object

