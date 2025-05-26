import cv2
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

class VideoRecorder:
    def __init__(self, camera_ids, output_files, frame_width=640, frame_height=480, fps=20.0, codec='mp4v'):
        self.camera_ids = camera_ids
        self.output_files = output_files
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.fps = fps
        self.codec = codec
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=len(camera_ids))

    def _record_camera(self, camera_id, output_file):
        cap = cv2.VideoCapture(camera_id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        out = cv2.VideoWriter(output_file, fourcc, self.fps, (self.frame_width, self.frame_height))

        print(f"[INFO] Recording from camera {camera_id} to '{output_file}'")

        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                print(f"[WARN] Failed to read frame from camera {camera_id}")
                break

            out.write(frame)

            # Display the frame in a window
            cv2.imshow(f'Camera {camera_id}', frame)

            # Allow early termination by pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_event.set()
                break

        cap.release()
        out.release()
        cv2.destroyWindow(f'Camera {camera_id}')
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
    asyncio.run(record_video())