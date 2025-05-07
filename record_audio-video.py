from collect_audio import AudioRecorder
from collect_video import VideoRecorder
from gui import StopRecordingGUI
import asyncio


#--------------------------------------------------------------------
CAMERA_IDS = [0, 1]
CAMERA_OUTPUT_FILES = ['camera0_output.mp4', 'camera1_output.mp4']

AUDIO_OUTPUT_FILE = "output_audio.wav"
NUM_CHANNELS = 2 # use >1 channel when using m-audio
#--------------------------------------------------------------------

# async def wait_for_q_to_quit(audio_recorder, video_recorder):
#     print("[INFO] Press 'q' then Enter to stop recording...")
#     loop = asyncio.get_running_loop()
#     await loop.run_in_executor(None, input, ">> ")
#     audio_recorder.stop()
#     video_recorder.stop()

async def wait_for_q_to_quit(audio_recorder, video_recorder):
    print("[INFO] Press 'q' then Enter to stop recording...")
    loop = asyncio.get_running_loop()
    gui = StopRecordingGUI(audio_recorder, video_recorder)
    gui.start()
    await gui.wait_for_stop()

async def record_audio_video():

    audio_recorder = AudioRecorder(output_file=AUDIO_OUTPUT_FILE, channels=NUM_CHANNELS)
    video_recorder = VideoRecorder(
        CAMERA_IDS,  
        CAMERA_OUTPUT_FILES
    )


    await asyncio.gather(
        audio_recorder.record(),
        video_recorder.record(),
        wait_for_q_to_quit(audio_recorder, video_recorder)
    )

if __name__ == "__main__":
    asyncio.run(record_audio_video())
    