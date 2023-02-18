import reapy.reascript_api as RPR
import subprocess


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
        # msg("Generating new DI with following command via sox:\n" + cmd)
        print("Generating new DI with following command via sox:\n" + cmd)
    process = subprocess.run(cmd.split(" "),
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
    # Bring the new extended DI clip onto the original track
    # RPR.SetOnlyTrackSelected(track.id)
    project.cursor_position = 0
    RPR.InsertMedia(str(outfile), 0)