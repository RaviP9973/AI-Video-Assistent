# AI Video Assistant

An AI-powered video and meeting assistant that converts YouTube videos or local audio/video files into searchable meeting intelligence. It transcribes the input, generates an executive summary, extracts action items, decisions, and open questions, and provides a conversational RAG interface for asking questions about the transcript.

## Features

- Download audio from YouTube URLs with `yt-dlp`.
- Accept local audio and video files.
- Convert media to mono, 16 kHz WAV audio for speech recognition.
- Split long recordings into manageable audio chunks.
- Transcribe English audio locally with OpenAI Whisper.
- Transcribe and translate Hinglish audio to English through the Sarvam AI API.
- Generate a short meeting title, summary, and structured insights with one Mistral analysis request.
- Extract:
  - Action items, owners, and deadlines
  - Key decisions
  - Unresolved questions and follow-up topics
- Build a local ChromaDB vector store from the transcript.
- Use Hugging Face `all-MiniLM-L6-v2` embeddings for semantic retrieval.
- Answer transcript-grounded questions through a LangChain LCEL RAG chain.
- Use a Streamlit interface with pipeline progress, results, and chat history.
- Provide a command-line interface through `main.py`.

The initial title, summary, action items, key decisions, and open questions are generated in one LLM request to reduce API usage. Each question asked in the RAG chat still requires one additional LLM request.

## Architecture

```text
YouTube URL or local media file
              |
              v
     Audio download/conversion
              |
              v
       WAV normalization/chunking
              |
              v
      Whisper or Sarvam transcription
              |
              v
           Full transcript
       /          |          \
      v           v           v
   Summary     Extraction    Vector store
      |           |              |
      +-----------+--------------+
                  v
        LangChain RAG chat assistant
```

### Main components

| Component | File | Responsibility |
| --- | --- | --- |
| Streamlit application | `app.py` | Web interface, pipeline execution, progress states, results, and chat |
| CLI pipeline | `main.py` | Terminal workflow and interactive transcript chat |
| Media processing | `utils/audio_processor.py` | YouTube download, media conversion, WAV normalization, and chunking |
| Transcription | `core/transcriber.py` | Whisper transcription and Sarvam Hinglish transcription/translation |
| Summarization | `core/summarizer.py` | Transcript splitting, title generation, and map-reduce summarization |
| Information extraction | `core/extractor.py` | Action item, decision, and open-question extraction |
| RAG orchestration | `core/rag_engine.py` | Retriever, prompt, Mistral model, and LCEL chain |
| Vector storage | `core/vector_store.py` | Embeddings, ChromaDB persistence, and similarity retrieval |

## Technology Stack

- **Language:** Python 3.10+
- **LLM orchestration:** LangChain, LangChain Expression Language (LCEL)
- **LLM:** Mistral AI (`mistral-small-latest`)
- **Speech recognition:** OpenAI Whisper
- **Speech translation:** Sarvam AI API
- **Embeddings:** Hugging Face Sentence Transformers, `all-MiniLM-L6-v2`
- **Vector database:** ChromaDB
- **UI:** Streamlit
- **Media processing:** FFmpeg, `ffmpeg-python`, PyDub
- **Video download:** `yt-dlp`
- **Configuration:** `python-dotenv`
- **HTTP integration:** `requests`

## Requirements

- Python 3.10 or newer
- FFmpeg installed and available on your system `PATH`
- A Mistral AI API key
- A Sarvam API key only when using Hinglish mode
- Sufficient disk space for the Whisper model, downloaded media, audio chunks, and embedding model
- Internet access for YouTube downloads, Mistral requests, model downloads, and Sarvam requests

Whisper runs locally, so CPU inference can take some time. The default Whisper model is `small`; a smaller model can be selected for faster execution on modest hardware.

## Installation

### 1. Clone or open the project

```bash
git clone <your-repository-url>
cd AI-Video-Assistant--main
```

### 2. Create and activate a virtual environment

#### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the installed dependency resolver does not install it transitively, install the text splitter package explicitly:

```bash
pip install langchain-text-splitters
```

### 4. Install FFmpeg

FFmpeg is an external system dependency and is not installed by `pip`.

#### Windows

Install FFmpeg using a package manager such as `winget`, or download a build and add its `bin` directory to `PATH`:

```powershell
winget install Gyan.FFmpeg.Shared
ffmpeg -version
```

#### macOS

```bash
brew install ffmpeg
ffmpeg -version
```

#### Ubuntu/Debian

```bash
sudo apt update
sudo apt install ffmpeg
ffmpeg -version
```

## Environment Configuration

Create a `.env` file in the project root. Do not commit this file or expose the keys publicly.

```env
MISTRAL_API_KEY=your_mistral_api_key
SARVAM_API_KEY=your_sarvam_api_key

# Optional Whisper configuration
WHISPER_MODEL=small

# Optional Sarvam configuration
SARVAM_STT_MODEL=saaras:v2.5

# Optional YouTube authentication (browser name: chrome, edge, or firefox)
YT_COOKIES_FROM_BROWSER=chrome

# Alternative to browser extraction: exported Netscape-format cookies
# YT_COOKIE_FILE=C:\path\to\youtube-cookies.txt
```

### Required keys by mode

| Variable | Required for | Description |
| --- | --- | --- |
| `MISTRAL_API_KEY` | All complete runs | Title generation, summarization, extraction, and RAG answers |
| `SARVAM_API_KEY` | `hinglish` mode | Speech-to-text translation through Sarvam AI |
| `WHISPER_MODEL` | Optional | Local Whisper model name; defaults to `small` |
| `SARVAM_STT_MODEL` | Optional | Sarvam model name; defaults to `saaras:v2.5` |
| `YT_COOKIES_FROM_BROWSER` | Optional | Browser from which yt-dlp reads YouTube cookies when YouTube requires sign-in |
| `YT_COOKIE_FILE` | Optional | Path to an exported Netscape-format YouTube cookie file; takes precedence over browser extraction |

## Running the Application

### Streamlit web application

From the project root, with the virtual environment activated:

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit, usually:

```text
http://localhost:8501
```

In the sidebar:

1. Enter a YouTube URL or local media path.
2. Select `english` or `hinglish`.
3. Select **Analyse**.
4. Review the title, summary, transcript, action items, decisions, and questions.
5. Ask questions in the meeting chat section.

### Command-line application

```bash
python main.py
```

The CLI asks for:

- A YouTube URL or local file path
- A language: `english` or `hinglish`

After processing, it prints the analysis and opens an interactive RAG chat. Type `exit`, `quit`, or `q` to stop chatting.

## Supported Inputs

### YouTube URL

```text
https://www.youtube.com/watch?v=VIDEO_ID
```

The application downloads the best available audio and converts it to WAV using FFmpeg.

### Local file

The input can be a local audio or video path supported by FFmpeg/PyDub, for example:

```text
C:\Users\YourName\Videos\meeting.mp4
```

or:

```text
/home/user/videos/meeting.mp4
```

The media is converted to mono 16 kHz WAV and split into ten-minute chunks before transcription.

## RAG Workflow

The retrieval-augmented generation workflow is implemented as follows:

1. The transcript is split into 500-character chunks with 50-character overlap.
2. Each chunk is stored as a LangChain `Document` with a chunk index.
3. `all-MiniLM-L6-v2` creates an embedding for every chunk.
4. ChromaDB persists the embeddings locally in `vector_db/`.
5. Similarity search retrieves the four most relevant chunks for a question.
6. Retrieved transcript context is inserted into a prompt for Mistral.
7. The assistant is instructed to answer only from the transcript context.

The application creates the vector store during analysis. The generated `vector_db/` directory is local application data and should generally not be committed to source control.

## Project Structure

```text
AI-Video-Assistant--main/
|
|-- app.py                         # Streamlit web application
|-- main.py                        # CLI pipeline and chat
|-- test.py                        # Manual pipeline example
|-- requirements.txt               # Python dependencies
|-- .env                           # Local secrets; do not commit
|-- core/
|   |-- extractor.py               # Action items, decisions, questions
|   |-- rag_engine.py              # LangChain RAG pipeline
|   |-- summarizer.py              # Title and summary generation
|   |-- transcriber.py             # Whisper and Sarvam transcription
|   `-- vector_store.py            # ChromaDB and embeddings
|-- utils/
|   `-- audio_processor.py         # Downloading and audio preparation
|-- downloades/                    # Downloaded/generated media files
`-- vector_db/                     # Generated ChromaDB persistence directory
```

## Troubleshooting

### `ffmpeg` is not recognized

Install FFmpeg and make sure its `bin` directory is on `PATH`. Verify with:

```bash
ffmpeg -version
```

### Mistral authentication errors

Check that `MISTRAL_API_KEY` exists in the root `.env` file and that the application is started from the project root.

### Hinglish transcription fails

Set `SARVAM_API_KEY` in `.env`. Sarvam requests are only used when the selected language is `hinglish`.

### Whisper is slow or uses too much memory

Choose a smaller model in `.env`:

```env
WHISPER_MODEL=base
```

Available model choices depend on the Whisper installation and local hardware. Smaller models are faster but may be less accurate.

### First run takes a long time

The first run may download the Whisper model and the Hugging Face embedding model. Later runs can reuse locally cached model files.

### YouTube download fails

Confirm that the URL is accessible and update `yt-dlp`:

```powershell
pip install --upgrade yt-dlp
```

If yt-dlp reports `Sign in to confirm you’re not a bot`, add the browser where you are signed in to YouTube to `.env`:

```env
YT_COOKIES_FROM_BROWSER=chrome
```

Supported values include `chrome`, `edge`, and `firefox`. Close the browser before starting the app if cookie extraction fails. Browser cookies are read locally and are not stored in the project. Do not commit exported cookie files or API credentials.

If Chrome cookie extraction still fails, export your YouTube cookies in Netscape `cookies.txt` format using a trusted cookie-export tool, save the file outside the repository, and set:

```env
YT_COOKIE_FILE=C:\path\to\youtube-cookies.txt
```

When `YT_COOKIE_FILE` is set, it takes precedence over `YT_COOKIES_FROM_BROWSER`. Treat this file like a password and never commit or share it.

## Limitations and Notes

- Transcription and summarization can be expensive or slow for long recordings.
- English transcription is local through Whisper; LLM analysis still requires the Mistral API.
- Hinglish mode sends audio pieces to the Sarvam API.
- The current interface accepts a path or URL as text rather than using a file upload widget.
- The repository includes PDF-related dependencies, but PDF export is not currently wired into the application.
- `test.py` is a manual execution script rather than an automated test suite.
- Generated audio, model files, secrets, and vector-store data should remain outside version control.

## Security and Privacy

- Keep `.env` out of Git and never paste API keys into source files.
- English audio is processed locally by Whisper, but transcript prompts are sent to Mistral for title generation, summaries, extraction, and RAG answers.
- Hinglish audio is sent to Sarvam AI in short WAV segments for transcription and translation.
- Review the privacy policies and terms of the external services before processing sensitive recordings.

## Future Improvements

- Add Streamlit file upload support.
- Add PDF and text export buttons.
- Add automated unit and integration tests.
- Add speaker diarization and timestamps.
- Add configurable chunk sizes and retrieval parameters.
- Add persistent multi-meeting collections and meeting selection.
- Add Docker packaging and deployment documentation.
- Add structured JSON output for extracted action items and decisions.

## License

No license file is currently included. Add a license before distributing the project publicly.