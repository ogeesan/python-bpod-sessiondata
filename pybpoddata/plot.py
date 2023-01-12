"""
Functions for plotting.

"""

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from .analysis import calculate_deadtime


def plot_statedurations_across_trials(sessiondata, ax=None):
    """Plot a heatmap showing states and their durations

    :param sessiondata: session data object
    :type sessiondata: pybpoddata.BpodDataClass.SessionDataClass
    :param ax:
    :type ax: plt.Axes
    :return:
    :rtype: numpy.typing.ndarray
    """
    all_states = sessiondata.meta['allstates']
    statearray = np.empty((sessiondata.nTrials, len(all_states)))
    statearray[:] = np.nan

    for trial, RawEvent in enumerate(sessiondata.RawEvents):
        statedict = RawEvent['States']
        for stateindex, statename in enumerate(all_states):
            if statename not in statedict.keys():
                continue
            if np.isnan(statedict[statename][0, 0]):
                statearray[trial, stateindex] = 0
            else:
                duration = np.diff(statedict[statename], axis=1)
                statearray[trial, stateindex] = np.sum(np.abs(duration))

    for stateindex in range(len(all_states)):
        maxval = statearray[:, stateindex].max()
        if maxval == 0:
            continue
        statearray[:, stateindex] = statearray[:, stateindex] / maxval
        # statearray[:, stateindex] = zscore(statearray[:, stateindex], nan_policy='omit')  # returns nans if all values same

    ax = plt.gca() if ax is None else ax
    ax.imshow(statearray.T, aspect='auto', interpolation='none', cmap='viridis')
    ax.set_yticks(range(len(all_states)))
    ax.set_yticklabels(all_states, rotation=0)
    return statearray


def plot_eventnumbers_across_trials(sessiondata, ax=None):
    """Plot a heatmap showing how many times all events occurred for each trial

    :param sessiondata: session data object
    :type sessiondata: pybpoddata.BpodDataClass.SessionDataClass
    :param ax:
    :type ax: plt.Axes
    :return:
    :rtype: numpy.typing.ndarray
    """
    all_events = sessiondata.meta['allevents']
    eventarray = np.empty((sessiondata.nTrials, len(all_events)))
    eventarray[:] = np.nan
    for trial, RawEvent in enumerate(sessiondata.RawEvents):
        eventdict = RawEvent['Events']
        for eventindex, eventname in enumerate(all_events):
            if eventname not in eventdict.keys():
                continue
            else:
                eventarray[trial, eventindex] = len(eventdict[eventname])

    for eventindex in range(len(all_events)):
        maxval = np.nanmax(eventarray[:, eventindex])
        if maxval == 0:
            continue
        eventarray[:, eventindex] = eventarray[:, eventindex] / maxval
        # eventarray[:, eventindex] = zscore(eventarray[:, eventindex], nan_policy='omit')

    ax = plt.gca() if ax is None else ax
    ax.imshow(eventarray.T, aspect='auto', interpolation='none', cmap='viridis')
    ax.set_yticks(range(len(all_events)))
    ax.set_yticklabels(all_events, rotation=0)
    return eventarray


def plot_trialtimes(sessiondata, ax=None):
    """Plot trial durations in blue and dead times in red

    :param sessiondata:
    :type sessiondata: pybpoddata.BpodDataClass.SessionDataClass
    :param ax:
    :type ax: plt.Axes
    :return:
    :rtype:
    """
    trialdurations = sessiondata.TrialEndTimestamp - sessiondata.TrialStartTimestamp
    deadtimes = calculate_deadtime(sessiondata.TrialStartTimestamp, sessiondata.TrialEndTimestamp)[1:]

    ax = plt.gca() if ax is None else ax
    c = 'blue'
    ax.plot(trialdurations, c=c, marker='.', linewidth=1, alpha=0.5)
    ax.set_ylabel('Trial Duration (s)', c=c)
    ax2 = plt.twinx(ax)
    c = 'red'
    ax2.plot(deadtimes, c=c, marker='.', linewidth=1, alpha=0.5)
    ax2.set_ylabel('Dead Time (s)', color=c)


def plottrial(trialdata_):
    """Plots all events in a single trial, mainly for troubleshooting a trial.

    :param trialdata_: RawEvents['Trial'][trialnumber]
    :type trialdata_: dict
    :return: Handle of plt handle
    :rtype: matplotlib.pyplot.ax
    """
    gridspec = plt.GridSpec(5, 1)
    ax = plt.subplot(gridspec[:4])
    plot_states(trialdata_['States'])
    plt.setp(ax.get_xticklabels(), visible=False)
    ax.set_xlabel('')
    plt.subplot(gridspec[4], sharex=ax)
    plot_events(trialdata_['Events'])


def plot_states(statedict, ax=None):
    """Plot movement through all states that were entered into.

    :param statedict: RawEvents[trial]['States']
    :type statedict: dict
    :param iax:
    :type ax: plt.Axes
    :return:
    :rtype:
    """
    entered_states = [statename for statename, times in statedict.items() if not np.isnan(times[0, 0])]

    # Step 1: Construct a table with each state entered
    statetable = []
    for statename in entered_states:
        for start, end in statedict[statename]:
            statetable.append({'State': statename,
                               'StartTime': start,
                               'EndTime': end})
    statetable = pd.DataFrame(statetable)
    # Step 2: Sort by state's start time (table is currently sorted by states)
    statetable = statetable.sort_values(by='StartTime').reset_index(drop=True)
    statetable['Index'] = None
    for index, statename in enumerate(entered_states[::-1]):
        statetable.loc[statetable.State == statename, 'Index'] = index

    # Step 3: Convert state table with row per state entry into row per time
    #   I tried making the long table from the start and then sorting Time, but that doesn't work
    #   because if a starttime and endtime of different states are the same (0 Timer states) then
    #   then two state starts can be consecutive if the sort happens to allocate it that way
    newstatetable = []
    for index, row in statetable.iterrows():
        # Two rows per state, the first for state entry time and the second for state exit time
        newstatetable.append({'State': row.State,
                              'Time': row.StartTime,
                              'Index': row.Index,
                              'Start': True})
        newstatetable.append({'State': row.State,
                              'Time': row.EndTime,
                              'Index': row.Index,
                              'Start': False})
    statetable = pd.DataFrame(newstatetable)

    ax = plt.gca() if ax is None else ax
    ax.plot(statetable.Time, statetable.Index, c='k', linewidth=1)
    ax.scatter(statetable.Time[statetable.Start], statetable.Index[statetable.Start],
               marker='.', c='k', label='State Starts')
    ax.set_yticks(range(len(entered_states)))
    ax.set_yticklabels(entered_states[::-1])
    ax.grid()
    ax.set_xlabel('Time')
    ax.set_ylabel('State')
    # ax.legend()
    sns.despine(ax=ax)
    return statetable


def plot_events(eventdict, ax=None):
    """Plot scatter of event timings

    :param eventdict: RawEvents[trial]['Events']
    :type eventdict: dict
    :param ax:
    :type ax: plt.Axes
    :return:
    :rtype:
    """
    used_events = [eventname for eventname in eventdict.keys()]
    eventtable = []
    for eventname in used_events:
        for time in eventdict[eventname]:
            eventtable.append({'Event': eventname,
                               'Time': time})
    eventtable = pd.DataFrame(eventtable)
    eventtable['Index'] = None
    for index, eventname in enumerate(used_events[::-1]):
        eventtable.loc[eventtable.Event == eventname, 'Index'] = index

    ax = plt.gca() if ax is None else ax
    ax.scatter(eventtable.Time, eventtable.Index, marker='|')
    ax.set_yticks(range(len(used_events)))
    ax.grid()
    ax.set_yticklabels(used_events[::-1])
    ax.set_ylabel('Event')
    ax.set_xlabel('Time')
    sns.despine(ax=ax)