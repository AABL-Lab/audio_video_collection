import asyncio
import sounddevice as sd
import soundfile as sf
import threading
import queue
class AudioRecorder:
    def __init__(self, save_location, samplerate=44100, channels=1): 
        self.save_location = save_location
        self.samplerate = samplerate
        self.channels = channels
        self.q = queue.Queue()
        self.stop_event = threading.Event()
        self.thread = None

    def _callback(self, indata, frames, time, status):
        if status:
            print(f"[WARN] Audio status: {status}")
        self.q.put(indata.copy())

    def _record_audio(self):
        # Create one SoundFile per channel
        print(self.save_location)
        files = [
            sf.SoundFile(f"{self.save_location}_ch{ch+1}.wav", mode='w', samplerate=self.samplerate, channels=1)
            for ch in range(self.channels)
        ]

        try:
            print(sd.InputStream())
            with sd.InputStream(samplerate=self.samplerate, channels=self.channels, callback=self._callback):
                print(f"[INFO] Recording audio for each channel...")
                while not self.stop_event.is_set():
                    data = self.q.get()  # shape: (frames, channels)
                    for ch in range(self.channels):
                        files[ch].write(data[:, ch])
        finally:
            for f in files:
                f.close()
        print("[INFO] Audio recording stopped.")


    async def record(self):
        self.thread = threading.Thread(target=self._record_audio)
        self.thread.start()

    def stop(self):
        print("[INFO] Stopping audio recording...")
        self.stop_event.set()
        self.thread.join()
