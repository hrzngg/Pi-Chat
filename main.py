# Core
import io
import wave
import struct
import pygame
from datetime import datetime

# Third-party
import pvporcupine as picovoice
import pyaudio
import speech_recognition as speech
from piper import PiperVoice as piperVoice

# Local modules
import constants 
from keywords import keywords, actions


# Logice
    # Wakeword detection
picoVoice = picovoice.create(access_key=constants.PICOVOICE_API_KEY, keywords=[constants.WAKEWORD])
    # Speech recognizer
recognition = speech.Recognizer()
audioInnit = pyaudio.PyAudio()

stream = audioInnit.open(
    rate=picoVoice.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=picoVoice.frame_length,
    input_device_index=constants.MIC_INDEX  # Make sure this matches your ReSpeaker mic index
)

    # Is bubble active
isSpeaking = False 
pygame.mixer.init()
    # loading voice models 
voice = piperVoice.load("/home/xpi5/workspace/en_US-amy-medium.onnx")
beep = pygame.mixer.Sound(constants.WAKEWORDSOUND)

# functions
def speak(speechText):
    for chunk in voice.synthesize(speechText):
        speechStream = audioInnit.open(format=pyaudio.get_format_from_width(chunk.sample_width),
                                     channels=chunk.sample_channels,
                                     rate=chunk.sample_rate,
                                     output=True)
        speechStream.write(chunk.audio_int16_bytes)
        speechStream.stop_stream()
        speechStream.close()

try:
    while True:
        try:
            pcm = stream.read(picoVoice.frame_length, exception_on_overflow=False)
        except OSError:
            continue  
        pcm = struct.unpack_from("h" * picoVoice.frame_length, pcm)

        isSpeaking = False
        if picoVoice.process(pcm) >= 0:
            beep.play()

            frames = []
            for _ in range(0, int(picoVoice.sample_rate / picoVoice.frame_length * constants.SPEECH_DURATION)):
                data = stream.read(picoVoice.frame_length)
                frames.append(data)

            wav_buffer = io.BytesIO()
            wf = wave.open(wav_buffer, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(picoVoice.sample_rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            wav_buffer.seek(0)

            with speech.AudioFile(wav_buffer) as source:
                audio = recognition.record(source)
            try:
                sentence = recognition.recognize_google(audio).lower()
                foundKeyword = False

                for i, word in enumerate(keywords):
                    if word in sentence:
                        response = actions[i]
                        speak(response)
                        
                        foundKeyword = True
                        isSpeaking = True
                        break
                if not foundKeyword:
                    isSpeaking = True
                    print("no found keyword")

            except speech.UnknownValueError:
                speak("Sorry, I was unable to understand what you said")
                isSpeaking = False
                continue
            except speech.RequestError:
                print("Speech recognition service unavailable.")
                isSpeaking = False
                continue
            

except KeyboardInterrupt:
    speak("Shutting down")

finally:
    if stream.is_active():
        stream.stop_stream()
    stream.close()
    picoVoice.delete()
    audioInnit.terminate()
