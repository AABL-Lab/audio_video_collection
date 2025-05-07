# Groups-Graphs

### Getting Set Up
- To begin, make sure that your microphone is connected. If using the lapel audio recorders, connect your computer to the 'M-Track Eight' via usb and select it as your input device.
- Ensure that the lapel audio device is connected to the receiver. See [this](https://assets.sennheiser.com/global-downloads/file/3020/Sennheiser_ewG3_QuickstartGuide.pdf) tutorial. 
- Check that webcams are connected to the computer via usb.

### Begin Recording
- To begin audio and video recording, simply run ``record_audio-video.py``

- Audio and video recording will continue until you enter ``q`` into terminal
- Video data can be collected from multiple cameras simultaneously. To add/remove cameras, modify the ``CAMERA_IDS`` and ``CAMERA_OUTPUT_FILES`` lists in ``record_audio-video.py``. 
- To change the file name for audio, modify ``AUDIO_OUTPUT_FILE``.
- Modify the number of audio channels by editing ``NUM_CHANNELS``.


<!-- ### ``people_boxes.py``
Run this file to track the positions of team members over time. 
- Put the path to your desired video in ``vid_path``. 
- The ``keypoints`` variable contains the the team members' keypoints. For instance, the keypoints for Team Member #1 are stored in ``keypoints[0]``.

### ``transcribe.py``
Transcribes audio from a wav file.
- Put the name of your wav file in ``AUDIO_FILE``.
- Uses speech recognition (https://pypi.org/project/SpeechRecognition/) and transcribes the audio into ``transcription.txt``. -->

