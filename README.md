# amp-space-synth-gen
Code for programmatically generating timbre samples from VSTs

# Instructions

So you have a VST you're interested in sampling.  The following 

Things you need to create/specify:
- A config file describing the FXParams, their values, and their indices used from within Reaper.  

`python3 render_data.py <DI-wav-file> <VST-config-YAML-file>`

## Requirements

The main dependency for this work is [Reapy](https://github.com/RomeoDespres/reapy), a Python library for interfacing with Reaper.  Unlike the Lua or EEL variants of ReaScript, Reapy can be run completely outside of a running Reaper instance,[^1].  Working from within Python also gives us access to better libraries for a wider range of markdown languages for config files, basic audio processing (like splitting), and calls to shell commands, all of which are made use of here.

The disadvantage of Reapy and running it from outside of a Reaper instance is that there are some limitations on the frequency of API calls.  This can come into play when duplicating the DI audio to create track long enough for thousands of FXParam changes.  Sometimes it may be necessary to use external calls to [Sox](http://sox.sourceforge.net/), but by default this package is not required.
