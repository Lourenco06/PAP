#Biblioteca necessárias para o funcionamento do resto do código
import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft
from scipy.io import wavfile

#Carregar o arquivo onde es´ta o áudio
fs, y = wavfile.read('teste.wav')

#Converter para áudio mono, somando o canal esquerdo(0) e o direito(1)
if len(y.shape) == 2:
    y = y[:,0] + y[:,1]

#Criação do vetor do tempo
t = np.linspace(0, len(y) / fs,num=len(y))

#"Plotar" o som do dominio do tempo
plt.figure()
plt.plot(t, y)
plt.title('Som do Dominio do Tempo')
plt.xlabel('Tempo(s)')
plt.ylabel('Amplitude')
plt.show()

transf = fft(y)
transf = transf[:len(transf)//2]

n = len(y)

freq = np.arange(0,n) * fs / n
freq = freq[:len/(freq)//2]

plt.figure()
plt.plot(freq, np.abs(transf))
plt.axis([0, 1500, 0, 2000])
plt.title('Dominio de Frequência')
plt.xlabel
plt.ylabel
plt.show()