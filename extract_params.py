"""
A support script for reading/exporting VST parameter information


Example:
    Extracting VST params to a yaml file::

        $ python extract_params.py --vst_name "Fortin Nameless Suite"
                                   --format yaml
                                   --output_file "nameless_default.yaml"
"""

import sys
import argparse
import reapy


def extract_params(args: argparse.Namespace) -> None:
    """
    Outputs the logging message to stdout or to the REAPER console
    Args:
        args (namespace): The argument namespace

    Returns:
        None
    """

    # Start Reaper project
    project = reapy.Project()
    track = project.tracks[0]

    # Load VST
    if track.n_fxs > 0 and (args.vst_name is None or args.vst_name in track.fxs[-1].name):
        sys.stderr.write("VST already loaded.  Using existing VST.\n")
        sys.stderr.flush()
    else:
        track.add_fx(args.vst_name)

    # Setup output stream
    output = open(args.output_file, "w", encoding='UTF-8') if args.output_file else sys.stdout

    # Maybe print the YAML header info for ToneRender config files
    if args.format == "yaml" and args.yaml_header:
        # Extract the VST name in proper format
        vst_name = args.vst_name if args.vst_name else track.fxs[0].name
        if vst_name.startswith('VST: '):
            vst_name = vst_name[5:]
        output.write(f"vst: {vst_name}\n")
        output.write("sweeps:\n")
        output.write("defaults:\n")

    # Write out all the VST parameters to stream
    for i, param in enumerate(track.fxs[-1].params):
        if args.params and param.name not in args.params or (args.suppress_midi and "MIDI" in param.name):
            pass
        else:
            if args.format == "tsv":
                output.write(f"{i}\t{param.name}\t{param}\n")
            elif args.format == "yaml":
                clean_name = f"\"{param.name}\"" if ':' in param.name else param.name
                output.write(f"  - name: {clean_name}\n")
                output.write(f"    value: {param:.2f}\n")

    # Close stream
    output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options for extracting VST parameters.')
    parser.add_argument('--vst_name', type=str, required=False,
                        help='name of a VST instrument to analyze')
    parser.add_argument('--output_file', type=str, required=False,
                        help='path to an output yaml file')
    parser.add_argument('--format', type=str, choices=['tsv', 'yaml'], default='tsv',
                        help='which format to print the FX parameter information')
    parser.add_argument('--yaml_header', type=bool, default=True,
                        help='if writing yaml, include header for ToneRender config file')
    parser.add_argument('--params', type=str, required=False,
                        help='optionally print only a subset of params, given as comma \
                              delimited string')
    parser.add_argument('--suppress_midi', type=bool, default=True,
                        help='ignore parameters related to MIDI CC')
    args = parser.parse_args()
    print(type(args))
    extract_params(args)
