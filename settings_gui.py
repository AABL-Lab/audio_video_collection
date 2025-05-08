import tkinter as tk
from tkinter import messagebox
import asyncio
import threading
from collect_audio import AudioRecorder
from collect_video import VideoRecorder
import cv2
import sounddevice as sd

class StartGUI:
    def __init__(self):
        num_cameras = self._count_cameras()
        print(f"Number of connected cameras: {num_cameras}")

        self.root = tk.Tk()
        self.root.title("Multi-Camera Selector")
        self.root.geometry("300x250")

        # Start button
        self.start_button = tk.Button(self.root, text="Start", command=self._on_start_wrapper)
        self.start_button.pack(pady=10)

        # Stop Recording button
        stop_btn = tk.Button(self.root, text="Stop Recording", command=self._on_stop)
        stop_btn.pack(side="top", pady=5)

        # Audio channel selection
        self.audio_channels = tk.Label(self.root, text="Enter number of audio channels:")
        self.audio_channels.pack()
        self.num_channels = tk.Entry(self.root)
        self.num_channels.insert(0, "2") # enter default value
        self.num_channels.pack(pady=5)
        


        # Camera selection label
        self.camera_label = tk.Label(self.root, text="Select Cameras:")
        self.camera_label.pack()

        # Multi-selection Listbox for cameras
        self.camera_options = [i for i in range(num_cameras)]  # Simulated camera indices
        self.camera_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, height=5)
        for cam in self.camera_options:
            self.camera_listbox.insert(tk.END, f"Camera {cam}")
        self.camera_listbox.pack(pady=5)

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_asyncio_loop, daemon=True).start()

    def _count_cameras(self):
        """
        Counts the number of connected cameras.
        """
        max_tested = 10
        count = 0
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                count += 1
                cap.release()
        return count


    def _run_asyncio_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _on_start_wrapper(self):
        asyncio.run_coroutine_threadsafe(self._on_start(), self.loop)

    async def _on_start(self):
        selected_indices = self.camera_listbox.curselection()
        self.CAMERA_IDS = [self.camera_options[i] for i in selected_indices]
        self.NUM_CHANNELS = int(self.num_channels.get())
        
        print("Async Start button clicked!")
        await self.record_audio_video()
        self.root.quit()
        self.root.destroy() 
        print("Async task completed!")

    def _on_stop(self):
        self.audio_recorder.stop()
        self.video_recorder.stop()
        self.root.quit()
        self.root.destroy()    
        

    def run(self):
        self.root.mainloop()

    async def record_audio_video(self):
        print("recording audio video")
        CAMERA_OUTPUT_FILES = [f"camera{num}.mp4" for num in self.CAMERA_IDS]

        AUDIO_OUTPUT_FILE = "output_audio"

        self.audio_recorder = AudioRecorder(output_file=AUDIO_OUTPUT_FILE, channels=self.NUM_CHANNELS)
        self.video_recorder = VideoRecorder(
            self.CAMERA_IDS,  
            CAMERA_OUTPUT_FILES
        )
        print("awaiting")
        await asyncio.gather(
            self.audio_recorder.record(),
            self.video_recorder.record()
        )

# To run the GUI
if __name__ == "__main__":
    app = StartGUI()
    app.run()
    
