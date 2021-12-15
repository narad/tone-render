# Tone Render

<img alt="Tone Render Logo" src="https://github.com/narad/tone-render/blob/main/images/tone_render.jpeg?raw=true" width="700" />

ToneRender is a package that works together with the [Reaper](https://www.reaper.fm/) DAW to programmatically sweep through parameter settings of VST instruments, rendering the output to .wav files.  This allows users to efficiently generate a large and diverse set of sound samples of the instrument's tones.  Reaper can render the files much faster than real-time, so sampling from VSTs can be much more practical than sampling real devices.  The resulting collections of tones can be used for the academic study of timbre or to support machine learning of music audio.

Specifically ToneRender deals with guitar-type sounds where a waveform is fed into the VST, and an output waveform is recorded (i.e., it is not designed to rip samples out of sample-based VSTs or soundbanks).  To this end, there are a variety of DIs (Direct Inputs) included in the repo to use for this purpose.  More details are provided in 

https://github.com/narad/amp-space

# Instructions

So you have a VST you're interested in sampling.  The following 

Things you need to create/specify:
- A config file describing the FXParams, their values, and their indices used from within Reaper.  

`python3 render_data.py <DI-wav-file> <VST-config-YAML-file>`

## Requirements

The main dependency for this work is [Reapy](https://github.com/RomeoDespres/reapy), a Python library for interfacing with Reaper.  Unlike the Lua or EEL variants of ReaScript, Reapy can be run completely outside of a running Reaper instance,[^1].  Working from within Python also gives us access to better libraries for a wider range of markdown languages for config files, basic audio processing (like splitting), and calls to shell commands, all of which are made use of here.

The disadvantage of Reapy and running it from outside of a Reaper instance is that there are some limitations on the frequency of API calls.  This can come into play when duplicating the DI audio to create track long enough for thousands of FXParam changes.  Sometimes it may be necessary to use external calls to [Sox](http://sox.sourceforge.net/), but by default this package is not required.
