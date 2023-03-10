from setuptools import setup

setup(
    name='pybpoddata',
    version='1.1.1',
    author='George Stuyt',
    packages=['pybpoddata'],
    description="Interact with SessionData .mat files from a MATLAB Bpod installation as a dict or an object",
    install_requires=['numpy',
                      'matplotlib',
                      'scipy',
                      'seaborn',
                      'pandas']
)