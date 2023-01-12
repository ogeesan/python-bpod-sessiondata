A Python package for reading and using `SessionData`, the output .mat files from the MATLAB Bpod installation.

To install, download this package and use `pip install -e .`

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

## What loading does

`scipy.io.loadmat` can load .mat files in but the final output needs to be tweaked. The *default* values in SessionData are modified — any extra will require your own formatting.

1. Extraneous Trial cell array is removed: `SessionData.RawEvents.Trial{trial}.States` becomes `SessionData['RawEvents'][trial]['States']`
2. The time arrays in `States` and `Events` are reformatted to ensure compatibility during indexing (this is the most important one)
3. `SettingsFile` and `RawData` don’t get any reformatting because I never use them, but they almost certain do require reformatting if you are going to use them. Happy to take an issues/pull requests for them.

# Using `SessionDataClass`

`pybpoddata.dataclass.SessionDataClass` is built for working with Bpod data as exported from Bpod’s MATLAB installation.

`SessionDataClass` can take a path to a file or a dictionary (`io.load_sessiondata_dict` is recommended) as an input.

`SessionDataClass` can be iterated over:

```python
outcomes = [Trial.outcome() for Trial in SessionData]
```

In order to make full use of this, you must extend the functionality using [class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance) to fit the specifics of your Bpod protocol.

```python
# In your own project environment
from pybpoddata import classes
class SessionDataClass(classes.SessionDataClass):
    def __init__(self, fpath):
    	super().__init__(fpath)  # Run the parent's init
        
        # Apply formatting that's unique to your protocol
        self.MyUniqueProperty = format_myuniqueproperty(self.MyUniqueProperty)
    
    # You can "overwrite" the parent's methods
    def get_trial(self, trial):
        return TrialClass(self, trial)
    
class TrialClass(classes.AbstractTrialClass):
    def __init__(self, SessionData, trial):
        super().__init__(SessionData, trial)
    
    def outcome(self):
        RawEvents = self.RawEvents
        outcome_string = my_outcome_function(RawEvents)  # This function depends on your protocol
        return outcome_string
```

In this way I think it makes a lot of sense to use `TrialClass` objects to do the work involved with the behaviour (e.g. how many times a mice did X before Y) rather than access the `SessionData` object directly.
