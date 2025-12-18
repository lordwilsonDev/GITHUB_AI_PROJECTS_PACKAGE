import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os

class Ear:
    def __init__(self):
        print("👂 Loading Cochlea (Whisper Base)...")
        # 'base' is fast enough for M1 real-time
        self.model = whisper.load_model("base", device="cpu") 

    def listen(self, duration=5, fs=16000):
        print("🎤 Listening...")
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
        sd.wait()
        
        # Temp save for Whisper (M1 Memory Mapping)
        wav.write("temp_audio.wav", fs, recording.astype(np.int16))
        
        result = self.model.transcribe("temp_audio.wav", fp16=False)
        text = result['text'].strip()
        print(f"👂 Heard: '{text}'")
        return text
