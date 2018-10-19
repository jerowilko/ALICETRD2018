"""python3 tbsum.py [FILE...]

Produce a histogram of interesting events summed over time bins.

Extract interesting events from raw data files, sum the data arrays, sum
over the time bins, and save a histogram in a file called tbsum.png.

Parameters
----------
FILE : list of arbitrary length of paths to raw data files, relative to
this file's directory.  If this parameter is absent, process all files in `defaults.DEFAULT_DATA_FOLDER`.
"""
import defaults
import o32reader as rdr
import adcarray as adc
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import glob
import sys

array_shape = (12, 144, 30)
def sum_events(path):
    """Extract interesting events from a file, and sum the data arrays.
    
    Parameters
    ----------
    path : str
        Path to a raw data file

    Returns
    -------
    data_sum : array of shape (12, 144, 30)
        The sum of all interesting events, without summing over time
    """
    reader = rdr.o32reader(path)
    analyser = adc.adcarray()

    def is_interesting(data):
        return np.max(data) > defaults.DEFAULT_BASELINE

    maxevno = None
    minevno = None
    absmax = None
    absmin = None
    data_sum = np.zeros(array_shape)
    for evno, raw_data in enumerate(reader):
        if evno % defaults.PRINT_EVNO_EVERY == 0:
            print("Proccessing events %d–%d"
                    % (evno, evno + defaults.PRINT_EVNO_EVERY))

        if evno == 0:
            # Skip the first event as it may be a configuration event
            # depending on run configurations.
            continue 

        analyser.analyse_event(raw_data)
        data = analyser.data[:12] # The last four rows are zeros.
        data[defaults.DATA_EXCLUDE_MASK] = 0.0

        maxval = np.max(data)
        minval = np.min(data)

        if absmax is None or maxval > absmax:
            absmax = maxval
            maxevno = evno

        if absmin is None or minval < absmin:
            absmin = minval
            minevno = evno

        if is_interesting(data):
            data_sum += data
    return data_sum

if __name__ == '__main__':
    fig =  plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    tbsum = np.zeros(array_shape[:-1])
    x = np.arange(tbsum.shape[0])
    y = np.arange(tbsum.shape[1])
    xx, yy = np.meshgrid(x, y, indexing='ij')
    if len(sys.argv) <= 1:
        files = glob.glob(defaults.DEFAULT_DATA_FOLDER + '/*')
    else:
        files = sys.argv[1:]
    for f in files:
        tbsum += np.sum(sum_events(f), 2)
    ax.bar3d(xx.ravel(), yy.ravel(), 0, 1, 1, tbsum.ravel())
    fig.savefig('tbsum')