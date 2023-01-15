import datetime

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from . import analysis, io, plot


class BaseSessionDataClass:
    def __init__(self, filepath_or_dict):
        """
        Python version of SessionDataClass

        :param filepath_or_dict: path to a file or a dictionary to turn into the object
        :type filepath_or_dict: str or Path or dict
        """
        # Handle filepath or dictionary input
        if isinstance(filepath_or_dict, dict):
            filepath = None
            sessiondatadict = filepath_or_dict
        else:
            filepath = filepath_or_dict
            sessiondatadict = io.load_sessiondata_dict(filepath, simplify_rawevents=True)
        
        is_legacy = io.determine_version(sessiondatadict) == 'legacy'
        
        self.meta = {'filename': filepath,
                     'start_time': None,
                     'allstates': [],  # all states that the session will enter
                     'allevents': [],  # all events that the session will encounter
                     'is_legacy': is_legacy
                     }  

        # Set each dictionary item as an attribute of the object
        # This doesn't seem like best practice: Might change this to use @property while storing the raw data in ._sessiondata?
        for key, item in sessiondatadict.items():
            setattr(self, key, item)

        # Sometimes the session errors before completing the first trial
        if not list(sessiondatadict.keys()).__contains__('nTrials'):
            self.nTrials = 0
            return

        # Complete meta information
        allstates, allevents = analysis.find_all_states_events(sessiondatadict['RawEvents'])
        self.meta['allstates'] = allstates
        self.meta['allevents'] = allevents
    
    def get_trial(self, trial):
        return AbstractTrialClass(self, trial)

    def __iter__(self):
        """Use SessionData in a for loop to return Trial objects"""
        for trial in range(self.nTrials):
            yield self.get_trial(trial)


class SessionDataClass(BaseSessionDataClass):
    """
    Class for dealing with SessionData in Python.

    Loads SessionDataClass MATLAB structure "fields" in as class attributes.
    """

    # Specify the default attributes and their data types
    default_attributes = ['Info', 'nTrials', 'RawEvents', 'RawData', 'TrialStartTimestamp', 'TrialEndTimestamp',
                          'SettingsFile']
    Info: dict
    nTrials: int
    RawEvents: list  # Note that this removes the ['Trial'] index requirement
    RawData: dict
    TrialStartTimestamp: np.ndarray
    TrialEndTimestamp: np.ndarray
    SettingsFile: dict
    
    meta: dict  # This is created on initialisation of an object

    def __init__(self, filepath_or_dict):
        super().__init__(filepath_or_dict)
        if self.meta['is_legacy']:
            raise AssertionError("Cannot create SessionDataClass from legacy Bpod data, use LegacySessionDataClass instead")
        
        start_str = self.Info['SessionDate'] + ' ' + self.Info['SessionStartTime_UTC']
        self.meta['start_time'] = datetime.datetime.strptime(start_str, '%d-%b-%Y %H:%M:%S')

    def trial_times(self, timetype='start'):
        if timetype == 'start':
            starttime = self.meta['start_time']
            return [starttime + datetime.timedelta(seconds=x) for x in self.TrialStartTimestamp]
        elif timetype == 'duration':
            return self.TrialEndTimestamp - self.TrialStartTimestamp
        else:
            raise AssertionError(f"timetype '{timetype}' is not 'start' or 'duration'")
    
    def summary(self):
        """Print a text summary for a fast understanding"""
        print(f"Filename: {self.meta['filename']}\n"
              f"{self.nTrials} trials completed in {self.TrialEndTimestamp[-1] / 60:.1f} minutes on {self.meta['start_time']}\n"
              f"All states: {self.meta['allstates']}\n"
              f"All events: {self.meta['allevents']}\n")

    def summary_plot(self, fig=None):
        fig = plt.gcf() if fig is None else fig

        gridspec = plt.GridSpec(5, 1, figure=fig)

        papaax = plt.subplot(gridspec[0])
        plot.plot_statedurations_across_trials(self, papaax)

        ax = plt.subplot(gridspec[1], sharex=papaax)
        plot.plot_eventnumbers_across_trials(self, ax)

        ax = plt.subplot(gridspec[2], sharex=papaax)
        
        plot.plot_trialtimes(self, ax)

        statedata = analysis.calculate_trial_times_table(self)
        eventdata = analysis.calculate_event_occurrences_table(self)

        ax = plt.subplot(gridspec[3])
        medians = analysis.calculate_medians_table(statedata, 'State', 'Duration')
        sns.scatterplot(data=medians, x='Duration', y='State', color='r', label='Median')
        sns.stripplot(data=statedata, x='Duration', y='State', orient='h',
                      zorder=-1, color='b', alpha=0.3)
        ax.grid()
        sns.despine()

        ax = plt.subplot(gridspec[4])
        medians = analysis.calculate_medians_table(eventdata, 'Event', 'Occurrences')
        sns.scatterplot(data=medians, x='Occurrences', y='Event', color='r', label='Median')
        sns.stripplot(data=eventdata, x='Occurrences', y='Event', orient='h',
                      zorder=-1, color='b', alpha=0.3)
        ax.grid()
        sns.despine()
        

class AbstractTrialClass:
    def __init__(self, sessiondata, trial):
        self.SessionData = sessiondata
        self.trial = trial

    def outcome(self):
        """Return a string describing what the outcome of the trial was.

        :return: String name of outcome type
        :rtype: str
        """
        # IF you're going to use this then you have to class TrialClass(AbstracTrialClass):
        # Then you'd use self.RawEvents to access the states and work out what happened
        raise NotImplementedError("User must create own TrialClass that defines what an outcome is")

    def RawEvents(self):
        return self.SessionData.RawEvents[self.trial]

    def start_time(self, relative_to='trial'):
        trial_start_timestamp = self.SessionData.TrialStartTimestamp[self.trial]
        if relative_to == 'trial':
            return trial_start_timestamp
        elif relative_to == 'clock':
            return self.SessionData.meta['start_time'] + datetime.timedelta(seconds=trial_start_timestamp)
        else:
            raise AssertionError(f"relative_to '{relative_to}' is not 'trial' or 'clock'")

    def plot(self):
        plot.plottrial(self.RawEvents())


class LegacySessionDataClass(BaseSessionDataClass):
    """
    Class for dealing with SessionData generated by pre Gen2 Bpod installations.
    As you can see I haven't written anything for this at all.
    """
    def __init__(self, fpath_or_dict):
        super().__init__(fpath_or_dict)
        
        # I'm not sure if the start time data is recoverable from the vanilla
        # legacy bpod, but it could be extracted from the file name...

    def summary(self):
        """Print a text summary for a fast understanding"""
        print(f"Filename: {self.meta['filename']}\n"
              f"{self.nTrials} trials completed in {self.TrialStartTimestamp[-1] / 60:.1f} minutes on {self.meta['start_time']}\n"
              f"All states: {self.meta['allstates']}\n"
              f"All events: {self.meta['allevents']}\n")
    
    def summary_plot(self, fig=None):
        fig = plt.gcf() if fig is None else fig

        gridspec = plt.GridSpec(4, 1, figure=fig)

        papaax = plt.subplot(gridspec[0])
        plot.plot_statedurations_across_trials(self, papaax)

        ax = plt.subplot(gridspec[1], sharex=papaax)
        plot.plot_eventnumbers_across_trials(self, ax)


        statedata = analysis.calculate_trial_times_table(self)
        eventdata = analysis.calculate_event_occurrences_table(self)

        ax = plt.subplot(gridspec[2])
        medians = analysis.calculate_medians_table(statedata, 'State', 'Duration')
        sns.scatterplot(data=medians, x='Duration', y='State', color='r', label='Median')
        sns.stripplot(data=statedata, x='Duration', y='State', orient='h',
                      zorder=-1, color='b', alpha=0.3)
        ax.grid()
        sns.despine()

        ax = plt.subplot(gridspec[3])
        medians = analysis.calculate_medians_table(eventdata, 'Event', 'Occurrences')
        sns.scatterplot(data=medians, x='Occurrences', y='Event', color='r', label='Median')
        sns.stripplot(data=eventdata, x='Occurrences', y='Event', orient='h',
                      zorder=-1, color='b', alpha=0.3)
        ax.grid()
        sns.despine()