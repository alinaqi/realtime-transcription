import argparse
from deepgram import DeepgramClient, DeepgramClientOptions, LiveTranscriptionEvents, LiveOptions
import httpx
import threading
import os
from openai import OpenAI
from pathlib import Path
import subprocess
from queue import Queue
from groq import Groq


# The API key you created in step 1
DEEPGRAM_API_KEY = '<your deepgram api key>'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '<your openai api key>')

# URL for the real-time streaming audio you would like to transcribe
URL = 'http://stream.live.vc.bbcmedia.co.uk/bbc_world_service'


# Queue for managing audio playback
audio_queue = Queue()
# Lock for managing audio playback to prevent overlapping
playback_lock = threading.Lock()

client = Groq(
    api_key="<your groq api key>",
)

def play_audio_with_ffplay(file_path):
    try:
        # Use subprocess to call ffplay and play the audio in a blocking way
        subprocess.run(['ffplay', '-nodisp', '-autoexit', str(file_path)], check=True,stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f'Finished playing audio: {file_path}')
    except Exception as e:
        print(f'Failed to play audio with FFmpeg: {e}')

def audio_player():
    while True:
        # Get the next audio file from the queue
        file_path = audio_queue.get()
        if file_path is None:
            break  # Stop the thread if None is received
        with playback_lock:
            play_audio_with_ffplay(file_path)
        audio_queue.task_done()


def generate_speech(text, openai_client, api="OPENAI", language="German"):
    try:
        if api == "OPENAI":
            # Generate translated text using OpenAI API
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use the appropriate model name
                messages=[
                    {"role": "system", "content": f"Translate the text to {language}. Return no additional data."},
                    {"role": "user", "content": text}
                ]
            )

            response = response.choices[0].message.content

        elif api == "GROQ":
            # Generate translated text using Groq API
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": f"Translate the text to {language}. Return no additional data.",
                    },
                    {
                        "role": "user",
                        "content": text,
                    }

                ],
                model="gemma2-9b-it",
            )
            response = response.choices[0].message.content
            
        # Generate spoken audio from text using OpenAI TTS API
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="nova",  # Choose from available voices: alloy, echo, fable, onyx, nova, shimmer
            input=response
        )

        # Define the output file path
        output_file_path = Path(__file__).parent / "output_speech.mp3"
        
        # Stream the output audio to a file
        response.stream_to_file(output_file_path)
        
        audio_queue.put(output_file_path)

    except Exception as e:
        print(f'Failed to generate speech: {e}')


def main(language):
    try:
        print('Starting...')
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)
        openai_client = OpenAI(api_key=OPENAI_API_KEY)

        print('Connected to Deepgram')
        # Start the audio player thread
        print('Starting audio player...')
        threading.Thread(target=audio_player, daemon=True).start()

        dg_connection = deepgram.listen.live.v('1')

        

        # Listen for any transcripts received from Deepgram and write them to the console
        def on_message(self, result, **kwargs):
            try:
                # Access the 'channel' and 'alternatives' keys safely
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) == 0:
                    return
                print(f'Transcript: {sentence}')
                # Convert to speech and playback
                generate_speech(sentence, openai_client, "OPENAI", language)
            except Exception as e:
                print(f'Error in on_message: {e}')


        # Create a WebSocket connection to Deepgram with event handlers
        options = LiveOptions(
            smart_format=True, model="nova-2", language="en-GB"
        )
        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.start(options)

        lock_exit = threading.Lock()
        exit_flag = False


        # Listen for the connection to open and send streaming audio from the URL to Deepgram
        def myThread():
            nonlocal exit_flag
            with httpx.stream('GET', URL) as r:
                for data in r.iter_bytes():
                    lock_exit.acquire()
                    if exit_flag:
                        break
                    lock_exit.release()
                    dg_connection.send(data)

        myHttp = threading.Thread(target=myThread)
        myHttp.start()

        input('Press Enter to stop transcription...\n')
        lock_exit.acquire()
        exit_flag = True
        lock_exit.release()

        myHttp.join()

        # Indicate that we've finished by sending the close stream message
        dg_connection.finish()
        print('Finished')

         # Stop the audio player thread
        audio_queue.put(None)

    except Exception as e:
        print(f'Could not open socket: {e}')
        return

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Real-time transcription and translation playback.')
    parser.add_argument('--language', type=str, default='German', help='The language to translate the text into.')
    args = parser.parse_args()

    # Pass the language argument to the main function
    main(args.language)