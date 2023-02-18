"""
A data generation for single settings

The intent of this module is to iterate through
multiple media files (.wav, .midi, .xml) and run
them through a single setting of a VST.  Initialize
the VST to the desired settings, then run the script.


Example:
    An example command to render data, given an existing config file::

        $ python render_single.py 
            --input_dir media_files/
            --output_dir "/output"
            --reaper_dir "/Documents/REAPER Media/"
"""

import sys
import xml
import os
import argparse
import tqdm
from pathlib import Path

import reapy
import reapy.reascript_api as RPR
import subprocess


def main(media_dir, output_dir, reaper_dir)
    # Start Reaper project
    project = reapy.Project()
    track = project.tracks[0]

    for media_file in tqdm(media_folder.glob('*.xml')):
        # Clear the track
        project.cursor_position = 0
        try:
            track.items[-1].delete()
        except:
            pass

        # Put media on track
        RPR.InsertMedia(str(media_file), 0) 

        # Render the audio
        RPR.Main_OnCommand(42230, 0)

        # Identify the most recent .wav in Reaper output dir
        reaper_output_files = reaper_dir.glob('*.wav')
        rendered_file = max(reaper_output_files, key=lambda p: p.stat().st_ctime)

        # Move file to output and rename
        output_filename = Path(media_file).stem
        print(output_filename)
        # cmd = f"mv {rendered_file} {output_folder}{output_filename}.wav"
        # print(cmd)
        process = subprocess.run(["mv",
            rendered_file,
            f"{output_folder}{output_filename}.wav"
            ],
            stdout=subprocess.PIPE,
            universal_newlines=True)






if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options for VST rendering.')
    parser.add_argument('--input_dir', type=Path, required=True,
                        help="the (root) directory holding media to serve as DI or triggers (MIDI)")
    parser.add_argument('--output_dir', type=Path, required=True,
                        help="the (root) directory where data will be written")
    parser.add_argument('--reaper_dir', type=Path, required=True,
                        help="the directory Reaper writes files to")
    args = parser.parse_args()

    main(args.input_dir, args.output_dir, args.reaper_dir)

