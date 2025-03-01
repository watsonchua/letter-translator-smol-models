from services.groq_client import groq_client

def transcribe_audio(audio_file, audio_filename):
    transcription = groq_client.audio.transcriptions.create(
        file=(audio_filename, audio_file),
        model="whisper-large-v3-turbo",
        response_format="verbose_json",
        )
    print(transcription)
    return transcription


if __name__ == "__main__":
    # filename = "/mnt/c/Users/watso/Documents/Sound Recordings/Recording (3).m4a"
    filename = "/mnt/c/Users/watso/Downloads/voice_01-03-2025_13-28-10.ogg"
    with open(filename, "rb") as audio_file:
        transcribe_audio(audio_file, filename)