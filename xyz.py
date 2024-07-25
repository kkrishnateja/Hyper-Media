import os
import subprocess
import librosa
import re
import soundfile as sf
from yt_dlp import YoutubeDL
import whisper


def convert_audio_to_text(VIDEO_URL):
    OUTPUT_DIR = 'content'  # Output directory for audio files

    # Create the output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Download audio using yt-dlp
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(OUTPUT_DIR, 'ytaudio.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([VIDEO_URL])

    # Convert to WAV using ffmpeg
    input_mp3_file = os.path.join(OUTPUT_DIR, 'ytaudio.mp3')
    output_wav_file = os.path.join(OUTPUT_DIR, 'ytaudio.wav')
    ffmpeg_cmd = ['ffmpeg', '-i', input_mp3_file, '-y', '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', output_wav_file]
    subprocess.run(ffmpeg_cmd, check=True)

    # Check if the output file exists
    if os.path.exists(output_wav_file):
        print(f"Successfully converted {input_mp3_file} to {output_wav_file}")
    else:
        print(f"Failed to convert {input_mp3_file} to {output_wav_file}")
        exit(1)

    # Load Whisper model
    model = whisper.load_model("base")

    # Transcribe audio
    result = model.transcribe(output_wav_file)
    full_transcript = result["text"]

    # Create a regular expression to match words in the transcript
    word_regex = r"\b\w+\b"

    # Find all the words in the transcript
    words = re.findall(word_regex, full_transcript)

    # Calculate the total duration of the audio
    total_duration = librosa.get_duration(filename=output_wav_file)

    # Calculate the average duration of each word
    average_word_duration = total_duration / len(words)

    # Create a dictionary to store the clickable words and their corresponding timestamps
    clickable_words = {}
    current_time = 0
    wordsT = {}
    i = 0
    for word in words:
        # Create a clickable link for the word
        wordsT[i] = word
        clickable_words[i] = f"{VIDEO_URL}&t={int(current_time)}s"
        i += 1
        current_time += average_word_duration

    # Print the clickable words as HTML links
    html_output = ""
    for i, link in clickable_words.items():
        html_output += f"<a href='{link}' target='_blank'>{wordsT[i]}</a> "

    return html_output


# a = convert_audio_to_text("https://youtube.com/watch?v=E59rFxl3XM4")
# print(a)
