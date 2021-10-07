'''
pip install pyAudio may not work
Instead download and install a wheel from here:
https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

or use: 

pip install pipwin
pipwin install pyaudio

pipwin is like pip, but it installs precompiled Windows binaries provided by Christoph Gohlke.
'''

# to display in separate Tk window
import matplotlib
matplotlib.use('TkAgg')

import pyaudio
import os
import struct
import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import fft
import time
from tkinter import TclError

# ------------ Audio Setup ---------------
# constants
CHUNK = 1024 * 2             # samples per frame
FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)
CHANNELS = 1                 # single channel for microphone
RATE = 44100                 # samples per second
# Signal range is -32k to 32k
# limiting amplitude to +/- 4k
AMPLITUDE_LIMIT = 4096

# pyaudio class instance
p = pyaudio.PyAudio()

# stream object to get data from microphone
stream = p.open(
	format=FORMAT,
	channels=CHANNELS,
	rate=RATE,
	input=True,
	output=True,
	frames_per_buffer=CHUNK
)

# ------------ Plot Setup ---------------
# create matplotlib figure and axes
# Use interactive mode
plt.ion()
fig, (ax1, ax2) = plt.subplots(2, figsize=(15, 7))
# variable for plotting
x = np.arange(0, 2 * CHUNK, 2)       # samples (waveform)
xf = np.linspace(0, RATE, CHUNK)     # frequencies (spectrum)

# create a line object with random data
line, = ax1.plot(x, np.random.rand(CHUNK), '-', lw=2)

# create semilogx line for spectrum, to plot the waveform as log not lin
line_fft, = ax2.semilogx(xf, np.random.rand(CHUNK), '-', lw=2)

# format waveform axes
ax1.set_title('AUDIO WAVEFORM')
ax1.set_xlabel('samples')
ax1.set_ylabel('volume')
ax1.set_ylim(-AMPLITUDE_LIMIT, AMPLITUDE_LIMIT)
ax1.set_xlim(0, 2 * CHUNK)
plt.setp(ax1, xticks=[0, CHUNK, 2 * CHUNK], yticks=[-AMPLITUDE_LIMIT, 0, AMPLITUDE_LIMIT])

# format spectrum axes
ax2.set_xlim(20, RATE / 2)
print('stream started')

if __name__ == '__main__':
	# for measuring frame rate
	frame_count = 0
	start_time = time.time()

	while True:
		
		# binary data
		data = stream.read(CHUNK)  
		# Open in numpy as a buffer
		data_np = np.frombuffer(data, dtype='h')

		# Update the line graph
		line.set_ydata(data_np)
		
		# compute FFT and update line
		yf = fft(data_np)
		# The fft will return complex numbers, so np.abs will return their magnitude

		line_fft.set_ydata(np.abs(yf[0:CHUNK])  / (512 * CHUNK))
		
		# update figure canvas
		try:
			fig.canvas.draw()
			fig.canvas.flush_events()
			frame_count += 1
			
		except TclError:
			
			# calculate average frame rate
			frame_rate = frame_count / (time.time() - start_time)
			
			print('stream stopped')
			print('average frame rate = {:.0f} FPS'.format(frame_rate))
			break