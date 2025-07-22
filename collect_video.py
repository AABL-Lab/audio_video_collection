import cv2
import time
import asyncio
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor

class VideoRecorder:
    def __init__(self, camera_ids, output_files, frame_width=640, frame_height=480, fps=15.0, codec='mp4v'):
        self.camera_ids = camera_ids
        self.output_files = output_files
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        self.codec = codec
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        if len(self.camera_ids) > 0:
            self.latest_frames = {cid: None for cid in self.camera_ids}  # Shared frame buffers
            self.executor = ThreadPoolExecutor(max_workers=len(camera_ids))

    def _record_camera(self, camera_id, output_file_base):
        cap = cv2.VideoCapture(camera_id, cv2.CAP_V4L2) # I set this manually because it wasn't totally working without it, if there are strange things look into this
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        fourcc = cv2.VideoWriter_fourcc(*self.codec)

        def get_timestamped_filename():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"{output_file_base}_{timestamp}.mp4"

        current_writer = cv2.VideoWriter(get_timestamped_filename(), fourcc, self.fps, (self.frame_width, self.frame_height))
        print(f"[INFO] Recording from camera {camera_id} to base '{output_file_base}'")

        start_time = time.time()

        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print(f"[WARN] Failed to read frame from camera {camera_id}")
                break

            current_writer.write(frame)

            with self.lock:
                self.latest_frames[camera_id] = frame.copy()  # safely update frame

            # Rotate file every minute
            if time.time() - start_time >= 60:
                current_writer.release()  # Flush to disk
                current_writer = cv2.VideoWriter(get_timestamped_filename(), fourcc, self.fps, (self.frame_width, self.frame_height))
                start_time = time.time()

            #cv2.imshow(f'Camera {camera_id}', frame)
            #if cv2.waitKey(1) & 0xFF == ord('q'):
            #    self.stop_event.set()
            #    break

        cap.release()
        current_writer.release()
        #cv2.destroyWindow(f'Camera {camera_id}')
        print(f"[INFO] Stopped recording camera {camera_id}")


    async def record(self):
        loop = asyncio.get_running_loop()
        tasks = []

        for cam_id, out_file in zip(self.camera_ids, self.output_files):
            task = loop.run_in_executor(self.executor, self._record_camera, cam_id, out_file)
            tasks.append(task)

        await asyncio.gather(*tasks)

    def stop(self):
        print("[INFO] Stopping all recordings...")
        self.stop_event.set()




if __name__ == "__main__":
    # Honestly this might not work but this class should be used with record_data.py anyways.
    recorder = VideoRecorder
    asyncio.run(recorder.record_video())