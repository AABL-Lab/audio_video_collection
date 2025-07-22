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
from PIL import Image, ImageTk
import numpy as np

class StartGUI:
    def __init__(self):
        #num_cameras = self._count_cameras()
        self.camera_options = self._get_working_cameras()
        print(f"Number of connected cameras: {len(self.camera_options)}")

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
        #self.camera_options = [i for i in range(num_cameras)]  # Simulated camera indices
        self.camera_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, height=5)
        for idx, dev in self.camera_options:
            self.camera_listbox.insert(tk.END, f"/dev/video{dev}")
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

    def create_camera_windows(self):
        self.camera_windows = {}
        for cam_id in self.CAMERA_IDS:
            win = tk.Toplevel(self.root)
            win.title(f"Camera {cam_id}")

            # Create a black placeholder image (640x480 or your desired size)
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            img = Image.fromarray(blank)
            imgtk = ImageTk.PhotoImage(image=img)

            label = tk.Label(win, image=imgtk)
            label.imgtk = imgtk  # prevent GC
            label.pack()

            self.camera_windows[cam_id] = (win, label)

    def update_camera_previews(self):
        if hasattr(self, 'video_recorder') and hasattr(self, 'camera_windows'):
            with self.video_recorder.lock:
                for cam_id, (win, label) in self.camera_windows.items():
                    frame = self.video_recorder.latest_frames.get(cam_id)
                    if frame is not None:
                        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        img = Image.fromarray(frame_rgb)
                        imgtk = ImageTk.PhotoImage(image=img)

                        label.imgtk = imgtk  # prevent GC
                        label.config(image=imgtk)

        self.root.after(30, self.update_camera_previews)

    def _get_working_cameras(self):
        working = []
        for i in range(10):
            cap = cv2.VideoCapture(i)  # Use simpler OpenCV capture without GStreamer
            if cap.isOpened():
                working.append((len(working), i))  # logical index, actual device number
                cap.release()
        return working

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
        self.CAMERA_IDS = [self.camera_options[i][1] for i in selected_indices]  # actual /dev/videoX
        self.CAMERA_OUTPUT_FILES = [f"{self.SAVE_LOCATION}camera{num}" for num in self.CAMERA_IDS]
        self.NUM_CHANNELS = int(self.num_channels.get())

    def _on_start_wrapper(self):
        # check if we'll be overwriting any files
        self._save_updated_entry_data()
        if self._check_any_camera_file_exists(self.CAMERA_OUTPUT_FILES):
            response = messagebox.askyesno("Confirmation", "This may overwrite an existing file. Continue anyway?")
            if not response: # if the user DOES NOT want to continue anyway then return 
                return
        # Start recording
        asyncio.run_coroutine_threadsafe(self._on_start(), self.loop)
        if len(self.CAMERA_IDS) > 0:
            self.create_camera_windows()
            self.update_camera_previews()


    async def _on_start(self):
        self._save_updated_entry_data()
        self.toggle_recording(True)
        await self.record_audio_video()


    def _on_stop(self):
        try:
            self.audio_recorder.stop()
            self.video_recorder.stop()
            self.toggle_recording(False)

            if len(self.CAMERA_IDS) > 0:
                for win, _ in self.camera_windows.values():
                    win.destroy()
                self.camera_windows = {}

        except Exception as e:
            print(f"No recording to stop: {e}")

    def _on_close(self):
        # when user closes the window
        self._on_stop()
        self.root.destroy()
        

    def run(self):
        self.root.mainloop()

    async def record_audio_video(self):

        self.audio_recorder = AudioRecorder(save_location=self.SAVE_LOCATION, channels=self.NUM_CHANNELS)
        self.video_recorder = VideoRecorder(
            self.CAMERA_IDS,  
            self.CAMERA_OUTPUT_FILES
        )

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
    
