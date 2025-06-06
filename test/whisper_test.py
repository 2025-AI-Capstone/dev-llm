import time
import whisper
import argparse
"""
OpenAI Whisper ASR Test Script

This script tests the performance of the OpenAI Whisper model by measuring:
1. Model loading time
2. Audio transcription time

Usage:
    python whisper_test.py --model <model_size> --audio <audio_file>

Arguments:
    --model: Select the Whisper model size (tiny, base, small, medium, large). Default is 'small'.
    --audio: Path to the audio file to transcribe.

Example:
    python whisper_test.py --model small --audio sample.wav

Requirements:
    - Install Whisper: pip install git+https://github.com/openai/whisper.git
    - Install FFmpeg: sudo apt install ffmpeg (Linux) / brew install ffmpeg (MacOS)

Output:
    - Displays the time taken for model loading and transcription.
    - Prints the transcribed text.
"""

def transcribe_audio(model_size, audio_path):
    print(f"Loading Whisper model: {model_size}...")
    start_time = time.time()
    model = whisper.load_model(model_size)
    load_time = time.time() - start_time
    print(f"Model loaded in {load_time:.2f} seconds.")
    
    print("Transcribing audio...")
    start_time = time.time()
    result = model.transcribe(audio_path)
    transcribe_time = time.time() - start_time
    
    print(f"Transcription completed in {transcribe_time:.2f} seconds.")
    print("\nTranscribed Text:\n")
    print(result["text"])
    
    return load_time, transcribe_time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test OpenAI Whisper ASR performance.")
    parser.add_argument("--model", type=str, default="small", choices=["tiny", "base", "small", "medium", "large"], help="Choose Whisper model size.")
    parser.add_argument("--audio", type=str, required=True, help="Path to the audio file.")
    args = parser.parse_args()
    
    transcribe_audio(args.model, args.audio)