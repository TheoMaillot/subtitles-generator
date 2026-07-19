import sys
import os
import shutil
from pathlib import Path

from extraction import extract_audio
from asr import transcribe_audio
from mt import dict_translation
from srt_conversion import dict_to_srt
from languages import LANGUAGE_CODES

sys.stdout.reconfigure(encoding='utf-8')

if getattr(sys, 'frozen', False):
    PARENT_FOLDER = Path(sys._MEIPASS)
else:
    PARENT_FOLDER = Path(__file__).parent
AUDIO_FOLDER    = PARENT_FOLDER / "audio"
SEGMENT_FOLDER  = PARENT_FOLDER / "segments"

def video_translation(video_path: str, subtitles_path: str, video_language: str, target_language: str):

    # Delete temp folders
    if os.path.exists(AUDIO_FOLDER):
        shutil.rmtree(AUDIO_FOLDER)
    if os.path.exists(SEGMENT_FOLDER):
        shutil.rmtree(SEGMENT_FOLDER)

    audio_path = extract_audio(video_path=video_path)
    
    input_dict, output_dict = [], []
    input_dict = transcribe_audio(audio_path=audio_path, audio_language=LANGUAGE_CODES[video_language]["whisper"])
    print(f"\n\n\n\n{input_dict}\n\n\n\n")
    print("-----1-----")
    output_dict = dict_translation(input_dict=input_dict, input_language=LANGUAGE_CODES[video_language]["nllb"], output_language=LANGUAGE_CODES[target_language]["nllb"])
    print("-----2-----")
    
    # Name of the srt file
    srt_name = os.path.splitext(os.path.basename(video_path))[0]
    dict_to_srt(segments=output_dict, output_path=subtitles_path)

    # Delete audio folder
    shutil.rmtree(AUDIO_FOLDER)