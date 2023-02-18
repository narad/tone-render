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
from tqdm import tqdm
from pathlib import Path

import reapy
import reapy.reascript_api as RPR
import subprocess


def main(media_dir, output_dir, reaper_dir, max_len):
    # Start Reaper project
    project = reapy.Project()
    track = project.tracks[0]

    for media_file in tqdm(list(media_dir.glob('*.xml'))):
        # Clear the track
        project.cursor_position = 0
        try:
            track.items[-1].delete()
        except:
            pass

        # Put media on track
        RPR.InsertMedia(str(media_file.resolve()), 0) 

        # Render the audio
        RPR.Main_OnCommand(42230, 0)

        # Identify the most recent .wav in Reaper output dir
        reaper_output_files = reaper_dir.glob('*.wav')
        rendered_file = max(reaper_output_files, key=lambda p: p.stat().st_ctime)

        # Move file to output and rename
        output_file = output_dir / f"{media_file.stem}.wav"
        process = subprocess.run(["mv",
            rendered_file,
            output_file,
            ],
            stdout=subprocess.PIPE,
            universal_newlines=True)
        if max_len > 0:
            process = subprocess.run(["sox",
                output_file,
                "/tmp/trimmed.wav",
                "trim",
                "0",
                str(max_len)
                ],
                stdout=subprocess.PIPE,
                universal_newlines=True)
            process = subprocess.run(["mv",
                "/tmp/trimmed.wav",
                output_file
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
    parser.add_argument('--max_len', type=float, default=-1,
                        help="the max length for rendered files")
    args = parser.parse_args()

    # Make output dir if not existing
    args.output_dir.mkdir(parents=True, exist_ok=True)


    main(args.input_dir, args.output_dir, args.reaper_dir, args.max_len)

