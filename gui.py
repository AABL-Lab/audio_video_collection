import asyncio
import threading
import tkinter as tk

class StopRecordingGUI:
    def __init__(self, audio, video):
        self.audio = audio
        self.video = video
        self.stop_event = asyncio.Event()    
        
    def start(self):
        # Run the GUI in a separate thread
        thread = threading.Thread(target=self._run_tkinter)
        thread.daemon = True
        thread.start()    
        
    def _run_tkinter(self):
        self.root = tk.Tk()
        self.root.title("Recording")
        self.root.geometry("300x100")        
        btn = tk.Button(self.root, text="Stop Recording", command=self._on_stop)
        btn.pack(expand=True)        
        self.root.mainloop()    
        
    def _on_stop(self):
        self.audio.stop()
        self.video.stop()
        self.stop_event.set()
        self.root.quit()
        self.root.destroy()    
        
    async def wait_for_stop(self):
        await self.stop_event.wait()# Example usage in your async code
