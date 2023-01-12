A Python package for reading and using `SessionData`, the output .mat files from the MATLAB Bpod installation.

To install, download this package and use `pip install -e .`

# Usage

You can either load in the .mat file as a `SessionDataClass` object (which provides extra functionality) or a as a dictionary.

```python
filepath = 'path/to/SessionData.mat'

# Create an object
from pybpoddata import SessionDataClass
SessionData = SessionDataClass(filepath)

# Create a dictionary
from pybpoddata import load_sessiondata_dict
SessionData = load_sessiondata_dict(path/to/SessionData.mat)
```

I recommend using `SessionDataClass` Because plotting functions and other bits and pieces were built to work with `BpodDataClass` rather than a dictionary, and extending the functionality is banger.

## What loading does

`scipy.io.loadmat` can load .mat files in but the final output needs to be tweaked. The *default* values in SessionData are modified — any extra will require your own formatting.

1. Extraneous Trial cell array is removed: `SessionData.RawEvents.Trial{trial}.States` becomes `SessionData['RawEvents'][trial]['States']`
2. The time arrays in `States` and `Events` are reformatted to ensure compatibility during indexing (this is the most important one)
3. `SettingsFile` and `RawData` don’t get any reformatting because I never use them, but they almost certain do require reformatting if you are going to use them. Happy to take an issues/pull requests for them.

# Using `SessionDataClass`

`pybpoddata.dataclass.SessionDataClass` is built for working with Bpod data as exported from Bpod’s MATLAB installation.

`BpodDataClass` can take a path to a file or a dictionary (`io.load_sessiondata_dict` is recommended) as an input.

The benefit of working with this `SessionDataClass` is that you can extend the functionality using [class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance) to fit the specifics of your Bpod protocol.

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
        return my_outcome_function(self)
```
