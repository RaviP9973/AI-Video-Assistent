import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)

def download_youtube_audio(url:str) ->str:
    output_path = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    ydl_opts = {
        "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
        "outtmpl": output_path,
        "noplaylist": True,
        "continuedl": False,
        "overwrites": True,
        "retries": 3,
        "fragment_retries": 3,
        "socket_timeout": 30,
        "quiet": False,
        "no_warnings": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
    }

    browser = os.getenv("YT_COOKIES_FROM_BROWSER", "").strip()
    cookie_file = os.getenv("YT_COOKIE_FILE", "").strip()
    if cookie_file:
        ydl_opts["cookiefile"] = cookie_file
    elif browser:
        browser_parts = tuple(part.strip() or None for part in browser.split(":", 3))
        ydl_opts["cookiesfrombrowser"] = browser_parts

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as error:
            message = str(error)
            if "Sign in to confirm you’re not a bot" in message or "Sign in to confirm you're not a bot" in message:
                raise RuntimeError(
                    "YouTube rejected this request as a bot. Set "
                    "YT_COOKIES_FROM_BROWSER=chrome (or edge/firefox), or set "
                    "YT_COOKIE_FILE to an exported Netscape cookies.txt file in .env. "
                    "Then restart the app and make sure you are signed in to YouTube."
                ) from error
            if "Could not copy" in message and "cookie database" in message:
                raise RuntimeError(
                    f"yt-dlp could not read the {browser or 'browser'} cookie database. "
                    "Close all windows of that browser and restart the app. "
                    "If this continues, export YouTube cookies to a Netscape "
                    "cookies.txt file and set YT_COOKIE_FILE in .env."
                ) from error
            raise
        source_path = ydl.prepare_filename(info)

    return os.path.splitext(source_path)[0] + ".wav"



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path



def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

        chunks.append(chunk_path)
    
    return chunks

def process_input(source: str) -> list:
    source = source.strip()
    if len(source) >= 2 and source[0] == source[-1] and source[0] in {'"', "'"}:
        source = source[1:-1].strip()

    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        if not os.path.isfile(source):
            raise FileNotFoundError(f"Input file was not found: {source}")
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks


