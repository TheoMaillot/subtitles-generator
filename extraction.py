import subprocess
import os
import time
import imageio_ffmpeg

def extract_audio(video_path: str):
    os.makedirs("audio", exist_ok=True)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    output_path = os.path.join("audio", f"{video_name}_{int(time.time())}.wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path