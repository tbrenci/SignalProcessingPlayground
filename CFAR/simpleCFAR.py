from scipy.io import wavfile
import matplotlib.pyplot as plt
import numpy as np
import time

def performCfar(input_signal, numTrainingCells, numGuardCells, falseAlarmRate):
    # Perform Greatest-Of CFAR
    # numTrainingCells:
    #   the number of training cells on EACH side of the cell under test
    # numGuardCells:
    #   the number of guard cells on EACH side of the cell under test
    
    cfarThreshold = []
    peaks = []
    thresholdFactor = numTrainingCells*(falseAlarmRate**(-1/numTrainingCells) - 1)

    for cut in range(len(input_signal)):

        # Sum the leading training cells, only if the full number of training cells exists before the CUT
        if cut < numTrainingCells + numGuardCells:
            leadingTrainingCells = np.array(-1)
        else:
            leadingStartIdx = cut - numTrainingCells - numGuardCells 
            leadingTrainingCells = input_signal[leadingStartIdx : leadingStartIdx + numTrainingCells - 1]    
        # Sum the trailing training cells, only if the full number of training cells exists after the CUT
        if cut > len(input_signal) - numTrainingCells + numGuardCells:
            trailingTrainingCells = np.array(-1)
        else:
            trailingStartIdx = cut + numGuardCells + 1
            trailingTrainingCells = input_signal[trailingStartIdx : trailingStartIdx + numTrainingCells - 1]

        # Find the greatest of the leading training cells or the trailling training cells
        # Calculate the average of the largest of the leading/trailling training cells, and store
        greatestOf = max(leadingTrainingCells.sum(),trailingTrainingCells.sum())
        threshold = greatestOf/numTrainingCells * thresholdFactor
        cfarThreshold.append(threshold)

        # If the CUT exceeds the threshold, record the index
        if input_signal[cut] > threshold:
            peaks.append(cut)

    cfarThreshold = np.asarray(cfarThreshold)
    peaks = np.asarray(peaks).astype(int)
    return cfarThreshold, peaks

# Load Data    
datapath = "./data/cat_sound_1.wav"
sample_rate, sig_audio = wavfile.read(datapath)

# Process Signal
pow_audio_signal = sig_audio / np.power(2, 15)
time_axis = 1000 * np.arange(0, len(pow_audio_signal), 1) / float(sample_rate)
pow_audio_signal = np.abs(pow_audio_signal)

# Perform CFAR with various probabilities of false alarm
cfarThreshold,peaks = performCfar(pow_audio_signal, 5000, 50, 0.2) # 20% probability of false alarm
cfarThreshold2,peaks2 = performCfar(pow_audio_signal, 5000, 50, .05) # 5% probability of false alarm

# Plot CFAR results
plt.figure()
plt.plot(time_axis, pow_audio_signal, 'b', label="Signal")
plt.plot(time_axis, cfarThreshold, 'r', label="Cfar20%")
plt.plot(time_axis, cfarThreshold2, 'g', label="Cfar5%")
plt.xlabel('Time (ms)')
plt.legend(loc="upper right")
plt.show()
