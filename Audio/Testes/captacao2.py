#Biblioteca necessárias para o funcionamento do resto do código
import pyaudio
import wave
import keyboard
import time

#Configuranções da gravação do ficheiro de áudio
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
OUTPUT_FILENAME = "teste.wav"

#Incia o PyAudio
audio = pyaudio.PyAudio()

#Abre os formatos e taxas para gravação
stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

#Lista para guardar os blocos de áudio
frames = []

#Mensagem para o usuário
print("Press SPACE to start recording")
keyboard.wait('space')
print("Recording... Press SPACE to stop.")
time.sleep(0.5)

#Loop de captura do áudio
while True:
    try:
        data = stream.read(CHUNK)
        frames.append(data)
    except KeyboardInterrupt:
        break
    if keyboard.is_pressed('space'):
        print("Stopping recording after a brief delay...")
        time.sleep(0.5)
        break

#Termina os formatos e taxas da gravação
stream.stop_stream()
stream.close()
audio.terminate()

#Guarda o áudio em .wav
waveFile = wave.open(OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()