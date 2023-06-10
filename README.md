A Python package for reading and using `SessionData`, the output .mat files from the MATLAB Bpod installation. A framework for interacting with data in an object-oriented method is provided, which could leverage the functions in `pybpoddata.analysis` to build a system specific to your task. 

To install, make a local copy of this repository and `pip install path/to/repo/folder`.

# Usage

You can either load in the .mat file as a `SessionDataClass` object (which provides extra functionality) or as a dictionary.

```python
filepath = 'path/to/SessionData.mat'

# Create an object
from pybpoddata import SessionDataClass
SessionData = SessionDataClass(filepath)

# Create a dictionary
from pybpoddata import load_sessiondata_dict
SessionData = load_sessiondata_dict(filepath)
```

I recommend using `SessionDataClass` for two reasons: because `pybpoddata.analysis` was built to work with `SessionDataClass` and because extending functionality with classes is perfect for this type of data. But it’s simpler (in some cases) to interact with the dictionary.

`SessionDataClass` can be iterated over:

```python
outcomes = [Trial.outcome() for Trial in SessionData]
```

However, to make full use of this functionality you would have to write code that handles the specifics for your task, detailed later.

## What loading does

`scipy.io.loadmat` can load .mat files but the final output needs to be tweaked for consistent formatting. The *default* values in SessionData are modified — any extra will require your own formatting.

1. Extraneous Trial cell array is removed: `SessionData.RawEvents.Trial{trial}.States` becomes `SessionData['RawEvents'][trial]['States']`
2. The time arrays in `States` and `Events` are reformatted to ensure compatibility during indexing (State times are shape n x 2)
3. `SettingsFile` and `RawData` don’t get any reformatting because I never use them, but they almost certain do require reformatting if you are going to use them. Happy to take issues/pull requests for them.

## Time profile

Using the `snakeviz` plugin in an iPython console I’ve looked at loading times into `SessionDataClass`. Using a 4.25 MB .mat file, the total time is 0.170 seconds. The breakdown of of that time:

| Function                           | Time (s) | Percent of total time |
| ---------------------------------- | -------- | --------------------- |
| `scipy.io.loadmat`                 | 0.157    | 92.3%                 |
| `pybpoddata.io.reformat_trialdata` | 0.0093   | 5.5%                  |
| everything else                    | 0.0037   | 2.2%                  |

In other words, not a lot of additional time is required to reformatt the data.

# Adapting `SessionDataClass` to your own task
In order to make full use of the objected-oriented approach to Bpod data, you have to extend the functionality of `SessionDataClass` using [class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance) to fit the specifics of your Bpod protocol. For example, you might be interested in a trial's pre-stimulus time but how that is calculated depends on your task structure and what exactly you're after.

To do this, you should define your own `BpodData` module (.py file) and then within that define your own bpod-related classes.

```python
# In your own project
from pybpoddata import classes

class SessionDataClass(classes.SessionDataClass):
    def __init__(self, fpath):
    	super().__init__(fpath)  # Run the parent's init
        
        # Apply formatting that's unique to your protocol
        self.MyUniqueProperty = format_myuniqueproperty(self.MyUniqueProperty)
    
    # Make get_trial return your own TrialClass
    def get_trial(self, trial):
        return TrialClass(self, trial)
    
    # Perhaps you have your own functions for visualising the session
    def plot_behaviour(self, ax=None):
        create_my_custom_plot(self.RawEvents, ax=ax)
    
class TrialClass(classes.AbstractTrialClass):
    def __init__(self, SessionData, trial):
        super().__init__(SessionData, trial)
    
    def outcome(self):
        RawEvents = self.RawEvents
        outcome_string = my_outcome_function(RawEvents)  # This function depends on your protocol
        return outcome_string
```

I think it makes a lot of sense to use `TrialClass` objects to do the work involved with the behaviour (e.g. how many times a mice did X before Y) rather than access the `SessionData` object directly.
