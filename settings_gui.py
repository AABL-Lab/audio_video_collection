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
import os

class StartGUI:
    def __init__(self):
        num_cameras = self._count_cameras()
        print(f"Number of connected cameras: {num_cameras}")

        self.root = tk.Tk()
        self.root.title("Audio/Video Data Collection")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
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
        self.save_location.grid(row=3, column=0, pady=10)

        

        self.select_save_button = tk.Button(self.root, text="Select Save Location", command=self.select_save_location)
        self.select_save_button.grid(row=3, column=1, pady=10)

        # Audio channel selection
        self.audio_channels = tk.Label(self.root, text="# of audio channels:")
        self.audio_channels.grid(row=4, column=0, pady=10)
        self.num_channels = tk.Entry(self.root)
        self.num_channels.insert(0, "2") # enter default value
        self.num_channels.grid(row=4, column=1, pady=10)
        

        # Camera selection 
        self.camera_label = tk.Label(self.root, text="Select Cameras:")
        self.camera_label.grid(row=5, column=0)
        self.camera_options = [i for i in range(num_cameras)]  # Simulated camera indices
        self.camera_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, height=5)
        for cam in self.camera_options:
            self.camera_listbox.insert(tk.END, f"Camera {cam}")
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

    def _check_file_exists(self, filename):
        filepath = os.path.join(self.SAVE_LOCATION, filename)

        if os.path.isfile(filepath):
            return True
        else:
            return False

    def _check_any_camera_file_exists(self,filename_list):
        for filename in self.CAMERA_OUTPUT_FILES:
            if os.path.isfile(filename):
                print("camera file exists")
                return True
            else:
                print("camera file does NOT exist")
                return False

    def _save_updated_entry_data(self):
        self.SAVE_LOCATION = self.save_location.get()
        selected_indices = self.camera_listbox.curselection() 
        self.CAMERA_IDS = [self.camera_options[i] for i in selected_indices]
        self.CAMERA_OUTPUT_FILES = [f"{self.SAVE_LOCATION}camera{num}.mp4" for num in self.CAMERA_IDS]
        self.NUM_CHANNELS = int(self.num_channels.get())

    def _on_start_wrapper(self):
        # check if we'll be overwriting any files
        self._save_updated_entry_data()
        if self._check_any_camera_file_exists(self.CAMERA_OUTPUT_FILES):
            response = messagebox.askyesno("Confirmation", "This may overwrite an existing file. Continue anyway?")
            if response: # if the user wants to continue anyway
                # start recording
                asyncio.run_coroutine_threadsafe(self._on_start(), self.loop)
        # if we're not overwriting any files, just start the recording
        else: 
            asyncio.run_coroutine_threadsafe(self._on_start(), self.loop)


    async def _on_start(self):
        self._save_updated_entry_data()
        self.toggle_recording(True)
        await self.record_audio_video()


    def _on_stop(self):
        try:
            self.audio_recorder.stop()
            self.video_recorder.stop()
            self.toggle_recording(False)
        except: 
            print("No recording to stop")

    def _on_close(self):
        # when user closes the window
        self._on_stop()
        self.root.destroy()
        

    def run(self):
        self.root.mainloop()

    async def record_audio_video(self):
        print("recording audio video")

        self.audio_recorder = AudioRecorder(save_location=self.SAVE_LOCATION, channels=self.NUM_CHANNELS)
        self.video_recorder = VideoRecorder(
            self.CAMERA_IDS,  
            self.CAMERA_OUTPUT_FILES
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
    
