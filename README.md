

# Real-Time Transcription and Translation

This project provides a real-time transcription and translation system using audio streams from the BBC World Service. The application transcribes the audio stream and translates the transcription into a specified language using either the OpenAI API or the Groq API. The translated text is then converted into spoken audio and played back to the user.

## Features

- **Real-Time Transcription**: Uses Deepgram API to transcribe live audio streams from the BBC.
- **Translation**: Supports translation to various languages using OpenAI or Groq APIs.
- **Text-to-Speech**: Converts translated text to speech using OpenAI TTS (Text-to-Speech) API.
- **Audio Playback**: Plays back the generated audio using `ffplay`.

## Requirements

- Python 3.8 or higher
- `ffplay` (part of FFmpeg)
- Deepgram API key
- OpenAI API key
- Groq API key
- Python libraries:
  - `argparse`
  - `deepgram`
  - `httpx`
  - `openai`
  - `groq`

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/alinaqi/realtime-transcription.git
   cd realtime-transcription
   ```

2. **Install Required Libraries**:
   Install the required Python libraries using pip:
   ```bash
   pip install deepgram-sdk httpx openai groq
   ```

3. **Install FFmpeg**:
   Ensure `ffplay` (part of FFmpeg) is installed on your system. For installation instructions:

   - **Ubuntu/Debian**:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **macOS** (via Homebrew):
     ```bash
     brew install ffmpeg
     ```
   - **Windows**: Download and install FFmpeg from the [official website](https://ffmpeg.org/download.html).

4. **Configure API Keys**:
   - Set your Deepgram API key in the script:
     ```python
     DEEPGRAM_API_KEY = '<your deepgram api key>'
     ```
   - Set your OpenAI API key in the script or as an environment variable:
     ```python
     OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<your openai api key>')
     ```
   - Set your Groq API key in the script:
     ```python
     client = Groq(api_key="<your grqo key>")
     ```

## Usage

To run the script, use the following command:

```bash
python deepgram_test.py --language <LANGUAGE>
```

Replace `<LANGUAGE>` with the language you want to translate the text into (e.g., `German`, `French`, `Spanish`, etc.).

### Example

To translate the transcription to German:

```bash
python deepgram_test.py --language German
```

## How It Works

1. **Audio Stream**: The script starts by connecting to the BBC World Service's live audio stream.
2. **Real-Time Transcription**: It uses the Deepgram API to transcribe the audio in real time.
3. **Translation**: The transcribed text is translated into the specified language using the OpenAI or Groq API.
4. **Text-to-Speech**: The translated text is converted to speech using the OpenAI TTS API.
5. **Playback**: The generated audio is played back to the user using `ffplay`.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This is just a proof of concept so no license. 

## Acknowledgements

- [Deepgram](https://deepgram.com) for their real-time transcription API.
- [OpenAI](https://openai.com) for their GPT and TTS services.
- [Groq](https://groq.com) for their machine learning API services.
- [BBC World Service](http://stream.live.vc.bbcmedia.co.uk/bbc_world_service) for providing the live audio stream.

