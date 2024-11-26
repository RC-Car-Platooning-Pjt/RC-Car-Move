import sys
import os
from gtts import gTTS
import pygame
from google.cloud import speech
import pyaudio
import queue
from Global_Var import G
import asyncio
# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms chunks

class MicrophoneStream(object):
    global RATE
    global CHUNK
    def __init__(self, rate , chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break
            yield b''.join(data)
            
class Voice:
    async def run(self, client):
        while True:
            if (not G.pairflag) and G.voiceflag:
                self.play_audio("스피커로 페어링 하시겠습니까?")
                command = self.listen_for_command()
                if command and "페어" in command:
                    self.play_audio(" 페어링을 시작합니다.")
                    # Bluetooth 페어링 로직을 추가할 수 있습니다.
                    client.publish("RCCAR/2/sound", 1)
                    G.voiceflag = False
                else:
                    self.play_audio("명령을 인식하지 못했습니다. 다시 시도해주세요.")
            await asyncio.sleep(1)

    def play_audio(self,text):
        """텍스트를 음성으로 변환하고 재생"""
        tts = gTTS(text=text, lang='ko')  # 한국어로 변환
        tts.save("output.mp3")  # 오디오 파일로 저장

        # pygame을 사용해 오디오 재생
        pygame.mixer.init()
        pygame.mixer.music.load("output.mp3")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            continue
        pygame.mixer.quit()
        os.remove("output.mp3")

    def listen_for_command(self):
        """음성 명령 인식"""
        language_code = 'ko-KR'
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding='LINEAR16',
            sample_rate_hertz=RATE,
            max_alternatives=1,
            language_code=language_code
        )
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)
            responses = client.streaming_recognize(streaming_config, requests)

            for response in responses:
                if not response.results:
                    continue

                result = response.results[0]
                if not result.alternatives:
                    continue

                transcript = result.alternatives[0].transcript.strip()
                print(f"Recognized: {transcript}")
                return transcript
            
Vd = Voice()
