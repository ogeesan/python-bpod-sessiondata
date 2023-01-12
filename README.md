A Python package for reading and using `SessionData`, the output .mat files from the MATLAB Bpod installation.

To install, download this package and use `pip install -e .`

# Usage

```python
from pybpoddata import SessionDataClass
SessionData = SessionDataClass(path/to/SessionData.mat)
```

`SessionData` is then an object

Alternatively, you could:

```python
from pybpoddata import load_sessiondata_dict
SessionData = load_sessiondata_dict(path/to/SessionData.mat)
```

The first example is recommended because plotting functions and other bits and pieces were built to work with `BpodDataClass` rather than a dictionary.

# `SessionDataClass`

`pybpoddata.dataclass.SessionDataClass` is built for working with Bpod data as exported from Bpod’s MATLAB installation.

`load_sessiondata_dict()` will load in the .mat file as a Python dictionary, with some reformatting applied.

- Extraneous Trial cell array is removed: `SessionData.RawEvents.Trial{trial}.States` becomes `SessionData['RawEvents'][trial]['States']`
- The time arrays in `States` and `Events` are reformatted to ensure compatibility during indexing.
- `SettingsFile` and `RawData` don’t get any reformatting because I never use them, but they almost certain do require reformatting if you’re going to use them. Happy to take an issue/pull request for them.

`BpodDataClass` can take a path to a file or a dictionary as an input.

The benefit of working with this `SessionDataClass` is that you can extend the functionality using [class inheritance](https://docs.python.org/3/tutorial/classes.html#inheritance) to fit the specifics of your Bpod protocol.

```python
from pybpoddata import dataclass as bpoddataclass
class SessionDataClass(BpodDataClass.SessionDataClass):
    def __init__(self, fpath):
    	super().__init__(fpath)
    
    def get_trial(self, trial):
        return TrialClass(self, trial)
    
class TrialClass(bpoddataclass.AbstractTrialClass):
    def __init__(self, SessionData, trial):
        super().__init__(SessionData, trial)
    
    def outcome(self):
        return my_outcome
```
