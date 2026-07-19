import silero_vad as vad
import soundfile as sf
from faster_whisper import WhisperModel

import os 
import shutil

vad_model = vad.load_silero_vad()
whisper = WhisperModel(model_size_or_path="medium", device="cpu", compute_type="int8")

SUBTITLE_MAX_CHARS = 80        # ~2 lignes de sous-titre classique
SUBTITLE_MAX_DURATION = 6.0    # secondes, au-delà un sous-titre devient illisible
SUBTITLE_END_PUNCT = ".!?"     # coupure préférée en fin de phrase
SUBTITLE_SOFT_PUNCT = ",;:"    # coupure de secours si la limite est atteinte en plein milieu
 
 
def _split_words_into_subtitles(words):
    """
    Contains a list of timestamped words (a dictionary with 'word', 'start', 'end')
    divided into segments suitable for subtitles: with fixed length and duration,
    with a preference for splitting at punctuation marks.s
    """
    subtitles = []
    current = []
 
    def flush():
        if not current:
            return
        text = "".join(w["word"] for w in current).strip()
        subtitles.append({
            "start": current[0]["start"],
            "end": current[-1]["end"],
            "text": text
        })
        current.clear()
 
    for w in words:
        current.append(w)
        text_so_far = "".join(x["word"] for x in current).strip()
        duration_so_far = current[-1]["end"] - current[0]["start"]
        stripped_word = w["word"].strip()
 
        ends_sentence = stripped_word.endswith(tuple(SUBTITLE_END_PUNCT))
        ends_clause = stripped_word.endswith(tuple(SUBTITLE_SOFT_PUNCT))
        over_limit = len(text_so_far) >= SUBTITLE_MAX_CHARS or duration_so_far >= SUBTITLE_MAX_DURATION
 
        if ends_sentence and len(text_so_far) > 20:
            flush()
        elif over_limit and ends_clause:
            flush()
        elif over_limit:
            flush()
 
    flush()
    return subtitles
 
 
def transcribe_audio(audio_path: str, audio_language: str):
    """
    Function to filter the speech in the audio file (via faster-whisper's built-in
    Silero VAD) and turn it into subtitle-sized text segments.
 
    Arguments:
    audio_path: path to the target audio
 
    Returns:
    list[dict]: list of subtitle-sized segments with the keys 'start', 'end', 'text'
                (text in French, ready for translation)
    """
    segments, info = whisper.transcribe(
        audio_path,
        beam_size=5,
        language=audio_language,
        word_timestamps=True,              # nécessaire pour re-découper en sous-titres
        vad_filter=True,                   # utilise Silero VAD en interne pour ignorer les silences
        vad_parameters=dict(
            min_silence_duration_ms=800,   # évite de couper une phrase en plein milieu
            min_speech_duration_ms=500,    # segments trop courts = moins de contexte pour Whisper
            speech_pad_ms=300,             # marge avant/après chaque segment : évite de tronquer les mots
            max_speech_duration_s=15,      # resplit automatiquement les longs passages de parole
        ),
        condition_on_previous_text=False,  # évite qu'une erreur de décodage se propage segment après segment
        no_speech_threshold=0.6,           # plus strict sur la détection de non-parole résiduelle
        compression_ratio_threshold=2.4,   # filtre les répétitions/hallucinations typiques
    )
 
    # les timestamps de faster-whisper sont déjà remappés sur l'audio d'origine
    words = []
    for seg in segments:
        if seg.words:
            for w in seg.words:
                words.append({
                    "word": w.word,
                    "start": w.start,
                    "end": w.end,
                })
 
    if not words:
        return []
 
    return _split_words_into_subtitles(words)


def transcribe_audio_with_silvero(audio_path: str, audio_language: str): 
    """
    Function to only filter the speech in the audio file using silvero, then turning the audio into text

    Arguments:
    audio_path: path to the target audio

    Returns:
    list[dict]: list of segments with the keys 'start', 'end', 'text'
                (text in French, ready for translation)

    """
    wav = vad.read_audio(audio_path, sampling_rate=16000)
    
    speech_timestamps = vad.get_speech_timestamps(
        wav,
        vad_model,
        sampling_rate=16000,
        min_silence_duration_ms=800,   # évite de couper une phrase en plein milieu
        min_speech_duration_ms=500,    # segments trop courts = moins de contexte pour Whisper
        speech_pad_ms=300,             # marge avant/après chaque segment : évite de tronquer les mots
        return_seconds=True
    )



    results = []
    
    for i, ts in enumerate(speech_timestamps):
        start_sample = int(ts['start'] * 16000)
        end_sample = int(ts['end'] * 16000)
        segment_audio = wav[start_sample:end_sample]
        
        os.makedirs("segments", exist_ok=True)
        
        segment_path = os.path.join("segments", f"segment_{i}.wav")
        sf.write(segment_path, segment_audio.numpy(), 16000)

        # transcription 
        segments, info = whisper.transcribe(
            segment_path,
            beam_size=5,
            language=audio_language,
            word_timestamps=True,              # nécessaire pour re-découper en sous-titres
            condition_on_previous_text=False,  # segments indépendants : pas de contexte partagé, donc pas de risque de dérive
            no_speech_threshold=0.6,           # plus strict sur la détection de non-parole résiduelle
            compression_ratio_threshold=2.4,   # filtre les répétitions/hallucinations typiques
        )


        text = " ".join(seg.text.strip() for seg in segments)
        results.append({
            "start": ts["start"],
            "end": ts["end"],
            "text": text
        })

    delete_folder(folder_path="segments")

    return results

def delete_folder(folder_path: str):
    """
    Deletes a folder and all its contents.

    Arguments:
    folder_path: path to the folder to be deleted
    """
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)