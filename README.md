# Tone Render

<img alt="Tone Render Logo" src="https://github.com/narad/tone-render/blob/main/images/tone_render.jpeg?raw=true" width="700" />

ToneRender is a package that works together with the [Reaper](https://www.reaper.fm/) DAW to programmatically sweep through parameter settings of VST instruments, rendering the output to .wav files.  This allows users to efficiently generate a large and diverse set of sound samples of the instrument's tones.  Reaper can render the files much faster than real-time, so sampling from VSTs can be much more practical than sampling real devices.  The resulting collections of tones can be used for the academic study of timbre or to support machine learning of music audio.

Specifically ToneRender deals with guitar-type sounds where a waveform is fed into the VST, and an output waveform is recorded (i.e., it is not designed to rip samples out of sample-based VSTs or soundbanks).  To this end, there are a variety of DIs (Direct Inputs) included in the repo to use for this purpose.  More details are provided in 

https://github.com/narad/amp-space

# Instructions

So you have a VST you're interested in sampling.  To do this using the ToneRender package, you need to create/specify the following things:

- A config file describing the FXParams, their values, and their indices used from within Reaper.
- A source waveform (a DI, or direct input, if using an amplifier or FX VST)
- A sweep file specifying what parameter configurations to test

With these in place, generating audio samples is as simple as running the main script:

`python3 render_data.py <DI-wav-file> <VST-config-YAML-file>`

How to create these is outlined below:

### 1. Creating a config file containing VST information

### 2. Providing a source waveform

Currently ToneRender only supports condition sample generation, i.e., some audio file is transformed by the VST instrument, resulting in an output audio sample.  You can create your own source recording, or use one of the provided waveforms.  The /dis folder contains sample guitar DIs for a variety of music genres.

### 3. Specifying a Parameter Sweep

# Other uses

Other code which may be useful was developed to create synthetic DI files, is the rendery_single.py script.  In essence, this script works in the opposite way from the render_data.py script: it takes in multiple media files (could be DIs, but also MIDI or musicXML), and processes them through a single VST setting in REAPER.  This makes it ideal for creating data from MIDI-triggered sample library VSTs, was used to general single note DI files available in the synthetic DIs folder.

### 1. Create a set of media files.  The scales scripts can be used to do just that:

`python scripts/scales.py --scale chromatic --one_per_measure True --notes_per_file single --duration half --output_dir media_files/`

This will generate a set musicXML files, where each file represents a single note from B1 to E6 on the chromatic scale.

### 2. Setup a VST

In this case the goal is to create guitar DI samples for every note in the chromatic scale.  This requires an appropriate VST.  In this case I set the track FX to load the Ample Metal Hellrazer plugin, and turned off all effects, so each musicXML event will trigger the playing of a recorded DI sample from a real guitar.

### 3. Render the data

`python render_single.py --input_dir media_files/ --output_dir note_wavs/ --reaper_dir ~/Documents/REAPER\ Media/`

This will generate a corresponding set of audio files, where each file is named identically (but with a .wav extension), and can be used as DI for reamping.  This makes it simple and straightforward to create a dataset of from sounds that can be triggered from MIDI events, such as drum or keyboard samples.

## Requirements

The main dependency for this work is [Reapy](https://github.com/RomeoDespres/reapy), a Python library for interfacing with Reaper.  Unlike the Lua or EEL variants of ReaScript, Reapy can be run completely outside of a running Reaper instance,[^1].  Working from within Python also gives us access to better libraries for a wider range of markdown languages for config files, basic audio processing (like splitting), and calls to shell commands, all of which are made use of here.

The disadvantage of Reapy and running it from outside of a Reaper instance is that there are some limitations on the frequency of API calls.  This can come into play when duplicating the DI audio to create track long enough for thousands of FXParam changes.  Sometimes it may be necessary to use external calls to [Sox](http://sox.sourceforge.net/), but by default this package is not required.
