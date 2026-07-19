import srt
from datetime import timedelta

def dict_to_srt(segments: list[dict], output_path: str = "srt/output.srt"):
    """
    Converts a list of segments {start, end, text} into an SRT file.

    Arguments:
    segments: a list of dictionaries with the keys 'start', 'end', 'text' (in seconds)
    output_path: path to the .srt file to be generated
    """
    subs = []

    for i, seg in enumerate(segments):
        subs.append(srt.Subtitle(
            index=i + 1,
            start=timedelta(seconds=seg['start']),
            end=timedelta(seconds=seg['end']),
            content=seg['text']
        ))

    srt_content = srt.compose(subs)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)