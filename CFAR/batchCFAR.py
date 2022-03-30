from scipy.io import wavfile
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import re

def performCfar(input_signal, numTrainingCells, numGuardCells, falseAlarmRate):
    # Perform Greatest-Of CFAR
    # numTrainingCells:
    #   the number of training cells on each side of the cell under test
    # numGuardCells:
    #   the number of guard cells on each side of the cell under test
    
    # Initialize variables
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

def createDataset(datapath, filenames):
    # Create a dictionary dataset

    # Initialize the dict
    dataSet = {'name':[], 'signal':[], 'powSignal':[], 
    'timeAxis':[], 'sampleRate':[], 'numSigs': 0}

    for i,file in enumerate(filenames): 
        # Read wav file & initial processing
        sample_rate, sig_audio = wavfile.read(datapath + file)
        pow_audio_signal = sig_audio / np.power(2, 15)
        time_axis = 1000 * np.arange(0, len(pow_audio_signal), 1) / float(sample_rate)
        pow_audio_signal = np.abs(pow_audio_signal)

        # Populate the dict
        dataSet['name'].append(file)
        dataSet['signal'].append(sig_audio)
        dataSet['powSignal'].append(pow_audio_signal)
        dataSet['timeAxis'].append(time_axis)
        dataSet['sampleRate'].append(sample_rate)
        dataSet['numSigs'] += 1
    return dataSet

def plotSignal(dataSet, sigFormat='powSignal', cols=2):
    # Plot audio signal
    # sigFormat = signal or powSignal
    rows = int(np.ceil(dataSet['numSigs']/cols))
    fig, axes = plt.subplots(rows, cols, figsize=(10,8), constrained_layout=True)
    for i in range(dataSet['numSigs']):
        r = i // cols
        c = i % cols
        ax = axes[r][c]
        ax.plot(dataset['timeAxis'][i], dataSet[sigFormat][i], label='Signal')
        ax.set_title(dataSet['name'][i])
        ax.legend(loc="upper left")
    plt.show(block=False)

def calculateCFAR(audioDict, falseAlarmRate=0.1, trainingCells=5000, guardCells=50):
    dictName = 'cfar' + str(int(falseAlarmRate*100))
    audioDict[dictName] = []
    for i in range(audioDict['numSigs']):
        cfarThreshold,_ = performCfar(audioDict['powSignal'][i], trainingCells, guardCells, falseAlarmRate)
        audioDict[dictName].append(cfarThreshold)
    return audioDict

def plotCFAR(dataSet, cfarsToPlot='all', cols=2):
    # Plot audio signal & CFAR threshold
    # cfarsToPlot = all or the dict key for the corresponding cfar (ie: cfar20)
    if cfarsToPlot == "all":
        r = re.compile(".*cfar")
        cfarList = list(filter(r.match, list(dataset.keys())))
    else:
        cfarList = cfarsToPlot

    # list of colors to use for the cfar plots
    colorList = ['r','g','c','m','orange','y','k','lime','hotpink']

    rows = int(np.ceil(dataset['numSigs']/cols))
    fig, axes = plt.subplots(rows, cols, figsize=(10,8), constrained_layout=True)
    for i in range(dataset['numSigs']):
        r = i // cols
        c = i % cols
        ax = axes[r][c]
        ax.plot(dataset['timeAxis'][i], dataset['powSignal'][i], label='Signal')
        plt.xlabel('Time (ms)')
        for j,cfars in enumerate(cfarList):
            ax.plot(dataset['timeAxis'][i], dataset[cfars][i], colorList[j], label=cfars.capitalize())
        ax.set_title(dataset['name'][i])
        ax.legend(loc="upper left")
    plt.show(block=False)

# Load data
datapath = "./data/"
f = open(datapath + "fileNames.txt")
filenames = f.read().splitlines()
f.close()

# Create dataset and plot signal
dataset = createDataset(datapath,filenames)
plotSignal(dataset)

# Calculate and plot CFAR
dataset = calculateCFAR(dataset, 0.2)
dataset = calculateCFAR(dataset, 0.05)
plotCFAR(dataset)

#pause to see plots
input()
