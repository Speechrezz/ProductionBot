'''
A bunch of helper function to help declutter music_bot.py
'''
from matplotlib import pyplot as plt
from matplotlib import ticker
import numpy as np
import time
import pyloudnorm as pyln

def generate_waveform(song, data_stream, color="blue", debug = False):
    y = np.array(song.get_array_of_samples())
    if song.channels >= 2:
        y = y.reshape((-1, song.channels)) / 32767 # max value of a 16-bit unsigned integer
    
    # Generate graph
    amp = np.zeros(y.shape[0])
    for i in range(y.shape[1]):
        amp += y[:, i]
    amp = amp / y.shape[1]

    plt.figure(figsize=(8,3), facecolor=(0.21176471, 0.22352941, 0.24313725))
    plt.rcParams['xtick.color'] = "white"
    plt.rcParams['ytick.color'] = "white"
    plt.plot(np.linspace(0, y.shape[0] / song.frame_rate, y.shape[0]), amp, color = color)
    ax = plt.gca()
    ax.get_yaxis().set_visible(debug)
    ax.set_facecolor((0.21176471, 0.22352941, 0.24313725))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    formatter = ticker.FuncFormatter(lambda s, x: time.strftime('%M:%S', time.gmtime(s)))
    ax.xaxis.set_major_formatter(formatter)

    # Save content into the data stream
    plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 100)
    plt.close()
    data_stream.seek(0)
    return y

def get_loudness_str(samplerate, y, debug = False):
    max_loudness = np.max(y)
    try:
        # measure the loudness first 
        meter = pyln.Meter(samplerate) # create BS.1770 meter
        loudness = meter.integrated_loudness(y)
    except ValueError: # is thrown if file is too short
        if debug:
            return max_loudness
        return ""
    if debug:
        return f"{loudness:.2f} LUFS, {max_loudness:.2f} max amplitude"
    return f"**Integrated Loudness:** {loudness:.2f} LUFS"