import numpy as np
import pandas as pd


def find_all_states_events(raweventlist):
    """Finds all of the states and events that this session enters into

    :param raweventlist: List of dicts, with 'States' and 'Events' keys.
    :type raweventlist: list
    :return: allstates, allevents
    :rtype: list, list
    """

    allstates = []
    allevents = []
    for trialdata in raweventlist:

        statenames = trialdata['States'].keys()
        [allstates.append(state) for state in statenames if state not in allstates]

        eventnames = trialdata['Events'].keys()
        [allevents.append(event) for event in eventnames if event not in allevents]

    return allstates, allevents


def calculate_deadtime(starttimes, endtimes):
    """Calculate time between each trial.
    Dead time has a high contribution from GUI updating and SessionData saving (if there's a lot of data)

    :param starttimes: TrialStartTimestamp
    :type starttimes: numpy.typing.ndarray
    :param endtimes: TrialEndTimestamp
    :type endtimes: numpy.typing.ndarray
    :return: dead times
    :rtype: numpy.typing.ndarray
    """
    deadtimes = np.append(np.nan, endtimes) - np.append(starttimes, np.nan)
    return np.abs(deadtimes)


def calculate_trial_times_table(sessiondata):
    """Find duration spent in states during each trial

    :param sessiondata:
    :type sessiondata: SessionDataClass
    :return: Table of all trials and time spent inside each for each trial
    :rtype: pd.DataFrame
    """
    statedata = {'Trial': [],
                 'State': [],
                 'Duration': []}
    for trial, RawEvent in enumerate(sessiondata.RawEvents):
        statedict = RawEvent['States']
        for statename in statedict.keys():
            duration = np.diff(statedict[statename], axis=1).sum()  # total time spent in the state
            statedata['Trial'].append(trial)
            statedata['State'].append(statename)
            statedata['Duration'].append(duration)
    statedata = pd.DataFrame(statedata)
    return statedata


def calculate_event_occurrences_table(sessiondata):
    """Find the number of times each event occurs in each trial

    :param sessiondata:
    :type sessiondata: SessionDataClass
    :return: Long table of events and the number of Occurrences
    :rtype: pd.DataFrame
    """
    all_events = sessiondata.meta['allevents']
    eventdata = {'Trial': [],
                 'Event': [],
                 'Occurrences': []}
    for trial, RawEvent in enumerate(sessiondata.RawEvents):
        eventdict = RawEvent['Events']
        # Note that we are sorting through all possible events, not only the ones existing in this trial
        for eventname in all_events:
            if eventname not in eventdict.keys():
                occurrences = 0
            else:
                occurrences = len(eventdict[eventname])
            eventdata['Trial'].append(trial)
            eventdata['Event'].append(eventname)
            eventdata['Occurrences'].append(occurrences)
    return pd.DataFrame(eventdata)


def calculate_medians_table(data, uniquecol, valuecol):
    """Calculate medians for values in a long arranged table

    :param data: Table extracted from calculate_trial_times_table or calculate_event_occurrences_table
    :type data: pd.DataFrame
    :param uniquecol: Column to find unique values of states/events in
    :type uniquecol: str
    :param valuecol: Column to apply .median() to
    :type valuecol: str
    :return:
    :rtype: pd.DataFrame
    """
    unique_types = list(data.loc[:, uniquecol].unique())
    medians = []
    for uniquename in unique_types:
        medians.append({uniquecol: uniquename,
                        valuecol: data.loc[(data.loc[:, uniquecol] == uniquename), valuecol].median()})
    medians = pd.DataFrame(medians)
    return medians


def getlicks(eventdata, portnumber, align=True):
    """Returns aligned lick data"""
    inevent = f"Port{portnumber}In"
    outevent = f"Port{portnumber}Out"
    return get_licks(eventdata, inevent, outevent, align=align)


def get_licks(Events, portinevent, portoutevent, align=True):
    """
    Find lick start and stop events
    :param Events: events entered into during a trial
    :type Events: dict
    :param portinevent: name of lick start event
    :type portinevent: str
    :param portoutevent: name of lick end event
    :type portoutevent: str
    :param align: add nans if out before in or last event is in
    :type align: bool
    :return: portins, portouts
    :rtype: numpy.typing.ndarray, numpy.typing.ndarray
    """
    if portinevent in Events.keys():
        portins = Events[portinevent]
    else:
        portins = np.full((1,), np.nan)

    if portoutevent in Events.keys():
        portouts = Events[portoutevent]
    else:
        portouts = np.full((1,), np.nan)

    if align:
        if portins[0] > portouts[0]:
            portins = np.insert(portins, 0, np.nan)
        if portouts[-1] < portins[-1]:
            portouts = np.insert(portouts, len(portouts), np.nan)

    return portins, portouts

def find_used_port_numbers(allevents):
    """
    Find the numbers of all port events in a list of events

    :param allevents: List of all events e.g. SessionDataClass.meta['allevents']
    :type allevents: list
    :return: List of each port i that had any Port[i] event
    :rtype: list
    """
    used_portevents = [event for event in allevents if event[:4] == 'Port']
    port_numbers = [int(event[4]) for event in used_portevents]
    unique_ports = []
    for port_number in port_numbers:
        if port_number not in unique_ports:
            unique_ports.append(port_number)
    return unique_ports
