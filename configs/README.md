# Config Files

The purpose of the config file is to specify the necessary sweep information in a way that is easily human readable, and human editable.  These files use a YAML format where the main top-level fields are: 

- **'vst-name'**: 

  The name of the VST, as used internally by REAPER (the name used in the FX select menu)

- **'sweeps'**: 

  A list of sweeps.  Each sweep is a set of parameter names, min and max values, and the step size to increment between them.

- **'defaults'**: 

  A list of parameter names and corresponding values.  These are the values that the VST will be initialized with before sweeping.
  
  Complete example files are given in the subfolders of this directory.
  
## Generating Config Files
  
Creating these files entirely by hand would be quite tedious, so the tone-render/extract_params.py script can be used to automate most of the process.  Simply run the script as follows:
  
```
          $ python extract_params.py --vst_name "Fortin Nameless Suite"
                                   --format yaml
                                   --output_file "nameless_default.yaml"
```

The resulting output file will look like:

```
vst: Fortin Nameless Suite (Neural DSP)
sweeps:
defaults:
  - name: Input Gain
    value: 0.80
  - name: Output Gain
    value: 0.68
  - name: ----
    value: 1.00
  - name: ----
    value: 1.00
  - name: Channel
    value: 1.00
  - name: Pedal Section Bypass
    value: 1.00
  - name: Booster On
    value: 1.00
  - name: Booster Amount
...
```

As you can see, the default values for the VST's FXParams have been automatically filled in.  You can also have these defaults set to a specific setting of the VST by opening it first in REAPER, adjusting the parameters to the desired setting, and then running the script without the --vst_name parameter.

The only remaining task now is to specify some parameter sweeps.  We can add to the 'sweeps' field the following text:

```
sweeps:
  - comment: "Tied EQ Gain sweep"
    params:
    - name: ['Gain 1', 'Gain 2']
      min: 0.1
      max: 1.0
      step: 0.2
    - name: ['Treble', 'Mid', 'Bass']
      min: 0.1
      max: 1.0
      step: 0.1
```

This specifies one sweep (specifying multiple in a single config file is supported) which sweeps the `Gain 1' and `Gain 2' parameters together, from .1 to 1.0 by increments of 0.2, and sweeps the EQ parameters (also tied together) from .1 to 1.0 by increments of 0.1.  There are 5 settings of the former, and 10 settings of the latter, so this sweep would consist of 50 different parameter settings.
