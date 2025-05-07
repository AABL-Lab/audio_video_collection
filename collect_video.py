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

        cap.release()
        out.release()
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


async def wait_for_q_to_quit(recorder):
    print("[INFO] Press 'q' then Enter to stop recording...")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, input, ">> ")
    recorder.stop()

async def record_video():
    camera_ids = [0, 1]
    output_files = ['camera0_output.mp4', 'camera1_output.mp4']
    recorder = VideoRecorder(camera_ids, output_files)

    await asyncio.gather(
        recorder.record(),
        wait_for_q_to_quit(recorder)
    )

if __name__ == "__main__":
    asyncio.run(record_video())
