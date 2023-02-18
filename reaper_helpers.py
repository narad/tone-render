from typing import Dict, List
from pathlib import Path

import reapy
import reapy.reascript_api as RPR
from reapy.core.track import Track
from reapy.core.project import Project


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
