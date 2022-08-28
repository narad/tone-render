"""
The main data generation script

This module utilizes Reapy to create a project in the
REAPER DAW, load an FX item (typically a VST instrument)
and loop audio through many possible settings of its
parameters.  Basic info on the FX item, provided in a
yaml config file, is required.

Example:
    An example command to render data, given an existing config file::

        $ python render_data.py --di_file dis/prog-metal/prog-metal-1.wav
                                --conf_file "config/NDSP Nameless Amp/nameless.yaml"
                                --output_dir "/output"
                                --reaper_dir "/Documents/REAPER Media/"
                                --copy_method sox
"""

import sys
import argparse

from pathlib import Path
import shutil

# For generating extended DI outside of Python
import subprocess

from typing import Dict, List

# For segmenting processed wavs
from pydub import AudioSegment
from pydub.utils import make_chunks

import reapy
import reapy.reascript_api as RPR
from reapy.core.project import Project
from reapy.core.track import Track


from sweeps import Sweeper, SweepConfig
from utils import seconds_to_str, byte_to_str


# How do you want your messages logged?
#MSG_MODE = ['stdout', 'console', 'both'][0]


def msg(message: str) -> None:
    """
    Outputs the logging message to stdout or to the REAPER console
    Args:
        message (str): The logging message

    Returns:
        None
    """
    if MSG_MODE in ('stdout', 'both'):
        print(message)
    if MSG_MODE in ('console', 'both'):
        RPR.ShowConsoleMsg(message + "\n")


def get_fx_envelopes(track: Track, param_names: List[str], fx_number: int=0, threshold: int=-1) -> Dict[str,str]:
    """
    Returns the FX envelopes for the param_names provided.
    Args:
        track (reapy.core.track.Track): The Track on which the FX is added
        param_names (List[str]): The names of the FXParams to change
        fx_number (int): The idx of the fx (should be 0 unless multiple FX)
        threshold (int): Maximum number of envelopes to collect

    Returns:
        dict[str,str]: a mapping of envelope names to their corresponding envelope ID str
    """
    name2env = dict()
    # print("param names from conf:")
    # for pname in param_names:
    #     print(pname)
    # print()
    # print("param names from VST:")
    # for i, p in enumerate(track.fxs[0].params):
    #     print(p.name)
    # print()


    for i, p in enumerate(track.fxs[0].params):
        print(p.name)
        if threshold > 0 and i >= threshold:
            print("breaking on threshold")
            break
        else:
            # Any parameter that receives a GetFXEnvelope call
            # will have an envelope created in the track, so best
            # to restrict it to the relevant set
            if p.name in param_names:
                name2env[p.name] = RPR.GetFXEnvelope(track.id, fx_number, i, True)
    return name2env


def copy_DI_sox(project, infile, outfile, times, verbose=False) -> None:
    """
    Lengthens the DI to cover the duration of desired samples using SoX
    Args:
            project (reapy.core.project.Project): The Track on which the FX is added
            track (reapy.core.track.Track): The Track on which the FX is added
            infile (Path): The original DI file
            outfile (Path): The output DI file
            times (int): Number of times to repeat the DI

    Returns:
        None
    """
    # Create a long DI file, looping the original
    cmd = f'sox {infile} {outfile} repeat {times}'
    if verbose:
        msg("Generating new DI with following command via sox:\n" + cmd)
    process = subprocess.run(cmd.split(" "),
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
    # Bring the new extended DI clip onto the original track
    # RPR.SetOnlyTrackSelected(track.id)
    project.cursor_position = 0
    RPR.InsertMedia(str(outfile), 0)


def copy_DI_reapy(project, di_file, times, margin) -> None:
    """
    Lengthens the DI to cover the duration of desired samples using repeated calls
    to the REAPER API via Reapy.

    Args:
            project (reapy.core.project.Project): The Track on which the FX is added
            track (reapy.core.track.Track): The Track on which the FX is added
            di_file (Path): The original DI file
            times (int): Number of times to repeat the DI

    Returns:
        None
    """
    # Get the absolute path filename
    filename = str(di_file.resolve())
    project.cursor_position = 0

    # Gives this track focus, making it the receiver of InsertMedia calls
#    RPR.SetOnlyTrackSelected(track.id)
    # inside_reaper() context helps with the API limitations for repetitive calls
    with reapy.inside_reaper():
        for _ in range(times):
            project.cursor_position += margin
            RPR.InsertMedia(filename, 0)


def split_audio(wav_file, clip_len, output_dir, idx_offset=0, verbose: bool=False) -> None:
    """
    Splits the rendered audio .wav file into many, one for each setting

    Args:
            wav_file (Path): The output .wav file generated by REAPER
            clip_len (float): The length in seconds of each clip
            output_dir (Path): The output directory to write split files

    Returns:
        None
    """
    # Split into chunks
    if verbose:
        msg(f"Splitting {wav_file}...")
    audio = AudioSegment.from_file(wav_file , "wav")
    chunk_length_ms = clip_len * 1000 # pydub calculates in millisec
    chunks = make_chunks(audio, chunk_length_ms)
    # If the output dir does not exist, make it
    output_dir.mkdir(parents=True, exist_ok=True)
    # Write to file
    for i, chunk in enumerate(chunks):
        chunk.export(output_dir / f"{i+idx_offset:08d}.wav", format="wav")


def delete_tmp_files(files: List[Path], verbose: bool=False) -> None:
    """
    Deletes the given files

    Args:
            files (List[Path]): A list of files to delete

    Returns:
        None
    """
    for file in files:
        if file.is_file():
            if args.verbose:
                msg(f"Deleting rendered file: {file}")
            file.unlink()



def get_clip_len(file: Path, project: Project):
    project.cursor_position = 0
    # Load DI on to track
    RPR.InsertMedia(str(file.resolve()), 0)
    track = project.tracks[0]
    clip_len = project.cursor_position
    track.items[-1].delete()
    project.cursor_position = 0
    return clip_len


def warmup(file: Path, project: Project):
    project.cursor_position = 0
    # Load DI on to track
    RPR.InsertMedia(str(file.resolve()), 0)
    track = project.tracks[0]
    RPR.Main_OnCommand(42230, 0)
    track.items[-1].delete()
    project.cursor_position = 0



def generate_data(args):
    """
    The main data generation function

    Args:
            args (argparse): The configuration options specifying how to generate data

    Returns:
        None
    """
    # Read yaml settings for VST sweep
    print(args.conf_file)
    print()
    config = SweepConfig(args.conf_file)

    # Start Reaper project
    project = reapy.Project()

    clip_len = get_clip_len(args.di_file, project)
    print(clip_len)

    # Compute sweeps
    sweeper = Sweeper(config, max_samples=args.max_samples)
    file_offset = 0
    for sweep_name, sweep in sweeper.sweeps:
        sweep = list(sweep)


        # if args.max_samples > -1 and args.max_samples < len(sweep):
        #     if args.verbose:
        #         msg(f"Reducing the number of sweeps in {sweep_name},\n  {len(sweep)} -> {args.max_samples}")
        #         sweep = sample(sweep, args.max_samples)

        # # Print stats on sweep beforehand
        if args.verbose:
            time_in_seconds = len(sweep) * clip_len
            size_in_mb = byte_to_str(time_in_seconds * args.mb_per_second)
            msg(f"Performing sweep {sweep_name}")
            msg(f"Beginning sweep of {len(sweep)} settings, recording {clip_len}s of each.")
            msg(f"This will create roughly {seconds_to_str(time_in_seconds)} ({size_in_mb}) of audio.")
        render_data(sweep, clip_len, project, config.vst_name, config.default_values(), args)
        split_data(args, clip_len, len(sweep), file_offset)
        file_offset += len(sweep)

    # write out settings in index file
    sweeper.write(args.output_dir / "settings.yaml", args.di_file)

    # possibly copy the DI to the output directory
    if args.copy_di:
        shutil.copy(args.di_file, args.output_dir / args.di_file.name)





def render_data(sweep, clip_len, project, vst_name, default_values, args):
#    print(list(sweep))
    # Delete all old tracks (and therefore the VST and envelopes)
    for track in project.tracks:
        track.delete()
    project.cursor_position = 0

#    warmup(args.di_file, project)
    num_settings = len(sweep)

    # Loop DI to match the number of settings changes
    if args.copy_method == "sox":
        # copy via calls out to sox
        copy_DI_sox(project,
                    infile=args.di_file,
                    outfile=args.output_dir / args.sox_di_name,
                    times=num_settings,
                    margin=args.margin)
    else:
        # copy via Reapy
        copy_DI_reapy(project,
                      args.di_file, 
                      times=num_settings,
                      margin=args.margin)


#    clip_len = int(project.cursor_position / num_settings)


    # Now that there is a track of audio, reference it
    track = project.tracks[0]

    # Load VST
    fx = track.add_fx(vst_name) #config.vst_name)
#    fx.make_online()
    fx.open_ui()


    # Read VST params
    fx_number = 0
    if args.verbose:
        msg("Collecting parameters...")
    tunable_parameters = sweep[0].keys()
    name2env = get_fx_envelopes(track, 
                                tunable_parameters, #[p.name for p in config.tunable_parameters()], 
                                fx_number)
    print("Found params")
    for pname in name2env.keys():
        print(pname)
    print()

    # Set default VST param values from yaml
    plist = track.fxs[fx_number].params

    for pname, pvalue in default_values.items(): #config.default_values().items():
        try:
            plist[pname] = pvalue
        except:
            if args.verbose:
                msg("Warning, error setting default value for: ", pname)


    # Specify sweeps over parameters as changes in FX param envelopes
    if args.verbose:
        msg("Setting envelopes...")
    time = 0
    for setting in sweep:
        for param_name, param_val in setting.items():
            try:
                RPR.InsertEnvelopePoint(name2env[param_name], time, param_val, 1, 0, False, True)
            except KeyError:
                msg(f"Parameter {param_name} from the config file not found in VST.")
                msg("List of VST keys found:")
                for k in name2env.keys():
                    msg(f"  {k}")
        time += clip_len
        time += args.margin


    # Warmup / required to fix audio glitch at the start of
    # recording in some environments
    if args.warmup_time > 0:
        import time
        project.cursor_position = 0
        project.play()
        time.sleep(args.warmup_time)
        project.pause()
        project.cursor_position = 0


    # # Render file
    if args.verbose:
        msg("Rendering...")
    RPR.Main_OnCommand(42230, 0)


def split_data(args, clip_len, num_settings, idx_offset):
    # Postprocess the rendered file
    if args.verbose:
        msg("Processing rendered file...")

    # Identify the most recent .wav in Reaper output dir
    reaper_output_files = args.reaper_dir.glob('*.wav')
    rendered_file = max(reaper_output_files, key=lambda p: p.stat().st_ctime)

    # Split into chunks into the provided new output dir
    split_audio(rendered_file, clip_len + args.margin, args.output_dir, idx_offset)

    # Clean up
    if args.delete_tmp_files:
        if args.verbose:
            msg("Deleting tmp files...")
        delete_tmp_files([rendered_file,                            # Output of REAPER
                          args.output_dir / args.sox_di_name,       # Output of SoX
                          args.output_dir / f"{num_settings+idx_offset:08d}.wav" # Excess audio from splitting
                          ],
                          verbose=args.verbose)

    if args.verbose:
        msg("Done.\n")




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options for VST rendering.')
    parser.add_argument('--di_file', type=str, required=True,
                        help='path to a DI wav file, as str.  can provide multiple files separated by comma')
    parser.add_argument('--conf_file', type=Path, required=True,
                        help='path to a VST FXParam config file')
    parser.add_argument('--output_dir', type=Path, required=True,
                        help="the (root) directory where data will be written")
    parser.add_argument('--reaper_dir', type=Path, required=True,
                        help="the directory Reaper writes files to")
    parser.add_argument('--copy_method', type=str, choices=['sox', 'reapy'],
                        help="the method used to copy the DI for each sweep")
    parser.add_argument('--margin', type=float, default=0.1,
                        help="amount of blank audio between DIs in seconds")
    parser.add_argument('--delete_tmp_files', type=bool, default=False,
                        help="delete the intermediary files made during rendering")
    parser.add_argument('--mb_per_second', type=int, default=139810,
                        help="constant used for estimating diskspace requirement")
    parser.add_argument('--sox_di_name', type=str, default="full_di.wav",
                        help="name of the generated long DI file if using SoX copy_method")
    parser.add_argument('--copy_di', type=bool, default=True, 
                        help="copy the DI file to the output_dir for future reference")
    parser.add_argument('--warmup_time', type=int, default=15,
                        help="amount of seconds to play the track prior to recording to prevent audio glitches")
    parser.add_argument('--verbose', type=bool, default=False,
                        help="whether to print logging information")
    parser.add_argument('--max_samples', type=int, default=-1,
                        help="max number of samples.  If less than total specified sweeps, sample uniformly.")
    parser.add_argument('--logging', type=str, choices=['stdout', 'console', 'both'], default='stdout',
                        help="destination of logging messages (default is 'stdout', but can also print to REAPER 'console'.")
    args = parser.parse_args()

    # Set the logging mode
    global MSG_MODE
    MSG_MODE = args.logging


    # Collect possibly multiple DI files
    di_files = [Path(f) for f in args.di_file.split(',')]

    # Collect possibly multiple conf files
    if args.conf_file.is_dir():
        conf_files = list([f for f in args.conf_file.iterdir() if f.suffix == '.yaml'])
    else:
        conf_files = [args.conf_file]


    # Loop through all given DI and conf files
    root_output_dir = args.output_dir
    for di_file in di_files:
        for conf_file in conf_files:

            # Check args for safety
            if not di_file.is_file():
                sys.exit(f"DI file <{di_file}> not found.")
            if not conf_file.is_file():
                sys.exit(f"Config file <{conf_file}> not found.")

            # Set rendering args for this specific run
            args.__dict__['di_file'] = di_file
            args.__dict__['conf_file'] = conf_file
            args.__dict__['output_dir'] = root_output_dir / conf_file.stem / di_file.stem
            print(args.__dict__['output_dir'])
            if args.verbose:
                print(args)
            generate_data(args)
























    #     # otherwise render for just the one provided config file
    #     elif args.conf_file.is_file():
    #         generate_data(args)
    #     else:
    # #        print(f"Invalid config file: {args.conf_file}")
    #         sys.exit(f"Config file <{args.conf_file}> not found.")




#    fx.open_floating_window()



    # # Load DI on to track
    # RPR.InsertMedia(str(args.di_file.resolve()), 0)
    # track = project.tracks[0]
    # clip_len = project.cursor_position

    # print(track.items)
    # track.items[0].delete()
    # print(track.items)
    # Item.active_take
