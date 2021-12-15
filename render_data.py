import reapy
import reapy.reascript_api as RPR

import sys
import yaml

import pathlib
import glob

from sweeps import Sweeper, Param
from utils import seconds_to_str, byte_to_str

# For generating extended DI outside of Python
import subprocess

# For segmenting processed wavs
from pydub import AudioSegment
from pydub.utils import make_chunks



message_mode = ['stdout', 'console', 'both'][0]
real_time_mult = 11.5
path_to_reaper_output = "/Users/narad/Documents/REAPER Media/"
output_dir = "/Users/narad/Desktop/reaper_out/"

def msg(m):
    if message_mode == 'stdout' or message_mode == 'both':
        print(str(m))
    elif message_mode == 'console' or message_mode == 'both':
        RPR.ShowConsoleMsg(str(m) + "\n")


def get_fx_envelopes(track, param_names, fx_number=0, threshold=-1):
    msg("Collecting parameters...")
    name2env = dict()
    for i, p in enumerate(track.fxs[0].params):
        if threshold > 0 and i >= threshold:
            break
        else:
            # Any parameter that receives a GetFXEnvelope call
            # will have an envelope created in the track, so best
            # to restrict it to the relevant set
            if p.name in param_names:
                name2env[p.name] = RPR.GetFXEnvelope(track.id, fx_number, i, True)
    return name2env


# def insertpt(time, settings_d, name2env):
#   for key, val in settings_d.items():
#     RPR.InsertEnvelopePoint(name2env[key], 
#                             time, 
#                             val, 
#                             1, 0, False, True)


def generate_data(di_filename, yaml_filename):
    # Read yaml settings for VST sweep
    with open(yaml_filename) as file:
        sweep_info = yaml.load(file)
    param_names = [p['name'] for p in sweep_info['params']]

    # Start Reaper project
    project = reapy.Project()
    for track in project.tracks:
        track.delete()
    project.cursor_position = 0


    # Load DI on to track
    di_filename = str(pathlib.Path(di_filename).resolve())
    RPR.InsertMedia(di_filename, 0)
    track = project.tracks[0]
    clip_len = project.cursor_position

    # Load VST
    track.add_fx(sweep_info['vst'])

    # Read VST params
    fx_number = 0
    name2env = get_fx_envelopes(track, param_names, fx_number)

    # Set default VST param values from yaml
    plist = track.fxs[0].params
    for pdict in sweep_info['defaults']:
        pname = pdict["name"]
        try:
            plist[pname] = pdict["value"]
        except:
            print("Warning, error setting default value for: ", pname)

    # Compute sweeps
    params = []
    for p_dict in sweep_info['params']:
        params.append(Param(p_dict['name'], p_dict['min'], p_dict['max']))
    sweeper = Sweeper(params)
    sweeps = sweeper.full_sweep()

    # Print stats on sweep beforehand
    sweeps = list(sweeps)
    time_in_secs = len(sweeps) * clip_len
    time_in_minutes = time_in_secs / 60.0
    mb_per_minute = 8 * 1048576
    size_in_mb = byte_to_str(time_in_minutes * mb_per_minute)
    print(f"Beginning sweep of {len(sweeps)} settings, recording {clip_len}s of each.")
    print(f"This will create roughly {seconds_to_str(time_in_secs)} ({size_in_mb}) of audio.")

    # # Loop DI to match the number of envelope changes
    # # The method below does this more efficiently
    # # using a call out to sox
    infile = di_filename
    outfile = output_dir + "full_di.wav"
    # times = 3 # len(sweeps)
    # cmd = f'sox {infile} {outfile} repeat {times}'
    # print("cmd: ", cmd)
    # process = subprocess.run(cmd.split(" "), 
    #                          stdout=subprocess.PIPE, 
    #                          universal_newlines=True)
    # The following can also be used, but can be an overwhelming
    # amount of calls for the Reaper API 
    RPR.SetOnlyTrackSelected(track.id)
    with reapy.inside_reaper():
        for _ in range(len(sweeps)-1):
            RPR.InsertMedia(di_filename, 0)

    # Bring the new extended DI clip onto the original track
    # RPR.SetOnlyTrackSelected(track.id)
    # RPR.InsertMedia(outfile, 0)

    # Specify sweeps over parameters as changes in FX param envelopes
    t = 0
    for setting in sweeps:
        for param_name, param_val in setting.items():
            fx_env = name2env[param_name]
            RPR.InsertEnvelopePoint(fx_env, t, param_val, 1, 0, False, True)
        t += clip_len

    # Render file
    RPR.Main_OnCommand(42230, 0)

    # Postprocess the rendered file
    list_of_paths = pathlib.Path(path_to_reaper_output).glob('*')   
    rendered_file = max(list_of_paths, key=lambda p: p.stat().st_ctime)
    # Split into chunks
    audio = AudioSegment.from_file(rendered_file , "wav") 
    chunk_length_ms = clip_len * 1000 # pydub calculates in millisec
    chunks = make_chunks(audio, chunk_length_ms) #Make chunks of one sec
    # Write to file
    for i, chunk in enumerate(chunks):
        chunk.export(f"reaper_out/{i:08d}.wav", format="wav")


    # write out settings in index file
    with open(pathlib.Path(output_dir) / pathlib.Path("settings.yaml"), "w") as settings_file:
        for i, setting in enumerate(sweeps):
            settings_file.write(f"- filename: {i:08d}.wav\n")
            settings_file.write(f"  settings:\n")
            for param_name, param_val in setting.items():
                settings_file.write(f"  - {param_name}: {param_val}\n")



if __name__ == '__main__':
    di_filename = sys.argv[1]
    yaml_filename = sys.argv[2]
    generate_data(di_filename, yaml_filename)





# RPR.Main_OnCommand(41824, 0) <- keeps the render dialogue open

