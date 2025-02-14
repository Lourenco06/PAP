# Programador....: Lourenço Moreira (c) 2025
# Observações....: Guitar Tuner in Python

import os
import numpy as np
import scipy.fft
import sounddevice as sd
import time

# Configurações do Afinador
TUNINGS = {
    "1": [82.41, 110.00, 146.83, 196.00, 246.94, 329.63],  # E Standard
    "2": [77.78, 103.83, 138.59, 185.00, 233.08, 311.13],  # Eb Standard
    "3": [73.42, 110.00, 146.83, 196.00, 246.94, 329.63],  # Drop D
    "4": [69.30, 103.83, 138.59, 185.00, 233.08, 311.13]   # Drop C#
}
TOLERANCE = 0.5
ALL_NOTES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

# Configurações do processamento de áudio
SAMPLE_FREQ = 48000  
WINDOW_SIZE = 48000
WINDOW_STEP = 12000  
NUM_HPS = 5  
POWER_THRESH = 5e-7  
CONCERT_PITCH = 440  

HANN_WINDOW = np.hanning(WINDOW_SIZE)
DELTA_FREQ = SAMPLE_FREQ / WINDOW_SIZE  

# Função para exibir o menu de afinação
def exibir_menu():
    print("Bem-vindo ao SharpTuner. Aqui estão as Afinações Disponíveis:")
    print("-------------------------")  
    print("1. E Standard")
    print("2. Eb Standard")
    print("3. Drop D")
    print("4. Drop C#")
    print("5. Voltar")
    print("-------------------------")

# Perguntar ao utilizador qual afinação deseja usar
while True:
    exibir_menu()
    escolha = input("Escolha uma opção: ")

    if escolha in TUNINGS:
        TARGET_FREQUENCIES = TUNINGS[escolha]
        break
    if escolha == "5":
        print("A sair do afinador...")
        exit()
    else:
        print("Opção inválida, tente novamente.")

# Função para identificar a nota mais próxima
def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch / CONCERT_PITCH) * 12))
    closest_note = ALL_NOTES[i % 12] + str(4 + (i + 9) // 12)
    closest_pitch = CONCERT_PITCH * 2**(i / 12)
    return closest_note, closest_pitch

# Aplicar o método HPS
def apply_hps(magnitude_spec):
    hps_spec = magnitude_spec.copy()
    for h in range(2, NUM_HPS + 1):
        decimated = magnitude_spec[::h]  
        hps_spec[:len(decimated)] *= decimated ** 0.8
    return hps_spec

# Callback para processar o áudio em tempo real
current_string = 0
done = False

def callback(indata, frames, time, status):
    global current_string, done, TARGET_FREQUENCIES
    static_text = f"Toca a {current_string + 1}ª corda ({TARGET_FREQUENCIES[current_string]} Hz)."

    if any(indata):
        if not hasattr(callback, "window_samples"):
            callback.window_samples = np.zeros(WINDOW_SIZE)

        callback.window_samples = np.concatenate((callback.window_samples, indata[:, 0]))
        callback.window_samples = callback.window_samples[len(indata[:, 0]):]

        signal_power = (np.linalg.norm(callback.window_samples, ord=2, axis=0)**2) / len(callback.window_samples)
        if signal_power < POWER_THRESH:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(static_text)
            print("Nota mais próxima: ...")
            return

        hann_samples = callback.window_samples * HANN_WINDOW
        magnitude_spec = abs(scipy.fft.fft(hann_samples)[:len(hann_samples)//2])

        for i in range(int(20 / DELTA_FREQ)):  
            magnitude_spec[i] = 0 
            
        magnitude_spec = apply_hps(magnitude_spec)

        max_ind = np.argmax(magnitude_spec)
        max_freq = max_ind * (SAMPLE_FREQ / WINDOW_SIZE)
        closest_note, closest_pitch = find_closest_note(max_freq)

        os.system('cls' if os.name == 'nt' else 'clear')
        print(static_text)
        print(f"Nota mais próxima: {closest_note} ({max_freq:.2f} Hz).")

        if abs(max_freq - TARGET_FREQUENCIES[current_string]) <= TOLERANCE:
            input("Corda afinada! Pressione Enter para avançar.")
            current_string += 1
            if current_string >= len(TARGET_FREQUENCIES):
                print("Parabéns! Todas as cordas estão afinadas!")
                done = True

# Boot do Afinador
try:
    print("A iniciar o afinador...")
    with sd.InputStream(channels=1, callback=callback, blocksize=WINDOW_STEP, samplerate=SAMPLE_FREQ):
        while not done:
            time.sleep(0.1)
except Exception as exc:
    print(str(exc))