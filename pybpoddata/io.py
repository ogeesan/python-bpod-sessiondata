import datetime

import numpy as np
from scipy.io import loadmat

def load_sessiondata_dict(fpath):
    """
    Loads a mat file into a dictionary that's been reformatted for ease of use.

    SessionData['RawEvents'] does not contain the unnecessary ['Trial'] anymore.
    Note that SettingsFile and RawData is undeveloped

    The slowest part of this is loading the .mat file, the conversions don't take much time at all.

    :param fpath: path to a SessionData .mat file
    :return:
    :rtype: dict
    """

    # If loading without simplify_cells it results in annoying numpy data types
    sessiondata = loadmat(fpath, simplify_cells=True)['SessionData']

    sessiondata['TrialStartTimestamp'] = np.array(sessiondata['TrialStartTimestamp'])
    sessiondata['TrialEndTimestamp'] = np.array(sessiondata['TrialEndTimestamp'])

    # If it's one trial then the TrialData dict isn't within a list
    if sessiondata['nTrials'] == 1:
        sessiondata['RawEvents']['Trial'] = [sessiondata['RawEvents']['Trial']]

    # Convert values in State/Events into arrays
    reformatted_RawEvents = []
    for trial in range(sessiondata['nTrials']):
        reformatted_RawEvents.append(reformat_trialdata(sessiondata['RawEvents']['Trial'][trial]))
    sessiondata['RawEvents'] = reformatted_RawEvents

    return sessiondata

def reformat_trialdata(trialdata_):
    """Converts scipy's auto-formatted States and Events arrays into arrays of consistent dimensions
    
    State arrays are shape (n_entries, 2) and Event arrays are shape (1,)

    :param trialdata_: The MATLAB equivalent of RawEvents.Trial{trial} from scipy's loadmat
    :type trialdata_: dict
    :return: dict with keys States and Events
    :rtype: dict
    """
    trialdata = dict()
    trialdata['States'] = dict()
    for statename, timelist in trialdata_['States'].items():
        timearray = np.array(timelist)
        if timearray.ndim == 1:  # Ensure all time arrays are shape (n_entires x 2)
            timearray = timearray.reshape(1, 2)
        trialdata['States'][statename] = timearray
    trialdata['Events'] = dict()
    for eventname, timelist in trialdata_['Events'].items():
        timearray = np.array(timelist)
        if timearray.ndim == 0:
            timearray = timearray.reshape(1, )
        trialdata['Events'][eventname] = timearray
    return trialdata


def datenum_to_datetime(datenum):
    """Convert MATLAB datenum to datetime object
    :param datenum: Date in MATLAB's datenum format
    :type datenum: int
    :return: Converted datetime
    :rtype: datetime.datetime
    """

    """Convert Matlab datenum into Python datetime.

    :param datenum: Date in datenum format
    :return: Datetime object corresponding to datenum.
    """


    days = datenum % 1
    return datetime.datetime.fromordinal(int(datenum)) \
           + datetime.timedelta(days=days) \
           - datetime.timedelta(days=366)