import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import asyncio
import threading
from collect_audio import AudioRecorder
from collect_video import VideoRecorder
import cv2
import sounddevice as sd
from tkinter import ttk
from tkinter import font

class StartGUI:
    def __init__(self):
        num_cameras = self._count_cameras()
        print(f"Number of connected cameras: {num_cameras}")

        self.root = tk.Tk()
        self.root.title("Audio/Video Data Collection")
        self.root.geometry("330x400")

        # Start button
        self.start_button = tk.Button(self.root, text="Record ▶", command=self._on_start_wrapper, width=30, bg="skyblue", fg="black", activebackground="deepskyblue",  activeforeground="black")
        self.start_button.grid(row=0, column=0, columnspan=2, pady=10)

        # Stop Recording button
        stop_btn = tk.Button(self.root, text="Stop \u274C", command=self._on_stop, width=30, bg="salmon", fg="black", activebackground="tomato",  activeforeground="black")
        stop_btn.grid(row=1, column=0, columnspan=2, pady=10)

        separator = ttk.Separator(self.root, orient='horizontal')
        separator.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=5)

        # Save Location
        self.save_location = ttk.Entry(self.root, width=15)
        # self.save_location.pack(side="left", padx=10, pady=10)
        self.save_location.grid(row=3, column=0, pady=10)

        

        self.select_save_button = tk.Button(self.root, text="Select Save Location", command=self.select_save_location)
        # self.select_save_button.pack(side="right", padx=10, pady=10)
        self.select_save_button.grid(row=3, column=1, pady=10)

        # Audio channel selection
        self.audio_channels = tk.Label(self.root, text="# of audio channels:")
        # self.audio_channels.pack(side="left")
        self.audio_channels.grid(row=4, column=0, pady=10)
        self.num_channels = tk.Entry(self.root)
        self.num_channels.insert(0, "2") # enter default value
        # self.num_channels.pack(side="left", pady=5)
        self.num_channels.grid(row=4, column=1, pady=10)
        

        # Camera selection 
        self.camera_label = tk.Label(self.root, text="Select Cameras:")
        # self.camera_label.pack(side="left")
        self.camera_label.grid(row=5, column=0)
        self.camera_options = [i for i in range(num_cameras)]  # Simulated camera indices
        self.camera_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, height=5)
        for cam in self.camera_options:
            self.camera_listbox.insert(tk.END, f"Camera {cam}")
        # self.camera_listbox.pack(side="left", pady=5)
        self.camera_listbox.grid(row=5, column=1, pady=10)

        # Recording indicator label
        self.record_label = tk.Label(
            self.root,
            text="● Not Recording",
            fg="gray",
            font=("Arial", 12, "bold")
        )
        self.record_label.grid(row=6, column=1, pady=10)

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_asyncio_loop, daemon=True).start()

    def _count_cameras(self):
        max_tested = 10
        count = 0
        for i in range(max_tested):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                count += 1
                cap.release()
        return count

    def select_save_location(self):
        folder_path = filedialog.askdirectory(title="Select Folder to Save")
        if folder_path:
            self.save_location.delete(0, tk.END)
            self.save_location.insert(0, folder_path+"/")

    def _run_asyncio_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _on_start_wrapper(self):
        asyncio.run_coroutine_threadsafe(self._on_start(), self.loop)

    async def _on_start(self):
        self.SAVE_LOCATION = self.save_location.get()
        selected_indices = self.camera_listbox.curselection()
        self.CAMERA_IDS = [self.camera_options[i] for i in selected_indices]
        self.NUM_CHANNELS = int(self.num_channels.get())
        
        print("Async Start button clicked!")
        self.toggle_recording(True)
        await self.record_audio_video()
        self.root.quit()
        self.root.destroy() 
        print("Async task completed!")

    def _on_stop(self):
        self.audio_recorder.stop()
        self.video_recorder.stop()
        self.toggle_recording(False)
        # self.root.quit()
        # self.root.destroy()    
        

    def run(self):
        self.root.mainloop()

    async def record_audio_video(self):
        print("recording audio video")
        CAMERA_OUTPUT_FILES = [f"{self.SAVE_LOCATION}camera{num}.mp4" for num in self.CAMERA_IDS]

        self.audio_recorder = AudioRecorder(save_location=self.SAVE_LOCATION, channels=self.NUM_CHANNELS)
        print("audio recorded")
        self.video_recorder = VideoRecorder(
            self.CAMERA_IDS,  
            CAMERA_OUTPUT_FILES
        )
        print("awaiting")
        await asyncio.gather(
            self.audio_recorder.record(),
            self.video_recorder.record()
        )

    def toggle_recording(self, isRecording):
        if isRecording:
            self.record_label.config(text="● Recording", fg="red")
        else:
            self.record_label.config(text="● Not Recording", fg="gray")

# To run the GUI
if __name__ == "__main__":
    app = StartGUI()
    app.run()
    
