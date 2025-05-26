# Automated Audio and Video Collection

This package is for collecting simultaneous audio and video data for studies. 

### Getting Set Up
- To begin, make sure that your microphone is connected. If using the lapel audio recorders, connect your computer to the 'M-Track Eight' via usb and select it as your input device.
- Ensure that the lapel audio device is connected to the receiver. See [this](https://assets.sennheiser.com/global-downloads/file/3020/Sennheiser_ewG3_QuickstartGuide.pdf) tutorial. 
- Check that webcams are connected to the computer via usb.

### Begin Recording
- To start the gui, simply run ``record_data.py``
- Hit the 'Record' and 'Stop' buttons to start/stop recordings
- Select the audio/video save location using the `Select Save Location` box. By default, files are saved to the current directory
- Input the number of audio channels in the textbox. (If using the Sennheiser, you'll choose between 1-4 audio channels, depending on how many lapel mics are being used)
- Use the selection box to select the cameras you'd like to use (NOTE: for now, only one camera can be selected at once)





<!-- ### ``people_boxes.py``
Run this file to track the positions of team members over time. 
- Put the path to your desired video in ``vid_path``. 
- The ``keypoints`` variable contains the the team members' keypoints. For instance, the keypoints for Team Member #1 are stored in ``keypoints[0]``.

### ``transcribe.py``
Transcribes audio from a wav file.
- Put the name of your wav file in ``AUDIO_FILE``.
- Uses speech recognition (https://pypi.org/project/SpeechRecognition/) and transcribes the audio into ``transcription.txt``. -->

