# Bibliotecas
import copy # Copias de Objetos e Listas
import os # Comandos do Sistema Operativo
import numpy as np # Cálculos Matemáticos e Manipulação de Arrays
import scipy.fft # Transformada de Fourier
import sounddevice as sd # Processamento de Áudio em Tempo Real
import time # Funções de Tempo

# Configurações para o Afinador
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
POWER_THRESH = 1e-6  
CONCERT_PITCH = 440  
WHITE_NOISE_THRESH = 0.2  

HANN_WINDOW = np.hanning(WINDOW_SIZE)

# Cálculos consoante as Variáveis impostas em cima
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ  
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ  
DELTA_FREQ = SAMPLE_FREQ / WINDOW_SIZE  
OCTAVE_BANDS = [50, 100, 200, 400, 800, 1600, 3200, 6400, 12800, 25600]

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
        print("Saindo do afinador...")
        exit()
    else:
        print("Opção inválida, tente novamente.")

# Função para identificar a nota mais próxima
def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch / CONCERT_PITCH) * 12))
    closest_note = ALL_NOTES[i % 12] + str(4 + (i + 9) // 12)
    closest_pitch = CONCERT_PITCH * 2**(i / 12)
    return closest_note, closest_pitch

# Callback para processar o áudio em tempo real
current_string = 0
done = False

def callback(indata, frames, time, status):
    global current_string, done, TARGET_FREQUENCIES  

    static_text = f"Toca a {current_string + 1}ª corda ({TARGET_FREQUENCIES[current_string]} Hz)."

    if status:
        if "overflow" in str(status):
            return  
        print(status)

    if any(indata):
        if not hasattr(callback, "window_samples"):
            callback.window_samples = [0 for _ in range(WINDOW_SIZE)]
        if not hasattr(callback, "last_displayed_note"):
            callback.last_displayed_note = None

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

        for i in range(int(62 / DELTA_FREQ)):
            magnitude_spec[i] = 0

        max_ind = np.argmax(magnitude_spec)
        max_freq = max_ind * (SAMPLE_FREQ / WINDOW_SIZE)

        closest_note, closest_pitch = find_closest_note(max_freq)

        os.system('cls' if os.name == 'nt' else 'clear')
        print(static_text)
        print(f"Nota mais próxima: {closest_note} ({max_freq} Hz).")

        if abs(max_freq - TARGET_FREQUENCIES[current_string]) <= TOLERANCE:
            escolha = input("Corda afinada! (Enter para avançar, 'b' para voltar): ").strip().lower()
            if escolha == "b":
                current_string = max(0, current_string - 1)
            else:
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