import os

start_note = "C#1"
for scale in ['chromatic', 'pentatonic-minor', 'hijaroshi']:
	for duration in ['quarter', 'half']:
		cmd = f"python3 scripts/scales.py --duration {duration} --scale {scale} --start_note C#1 --output_file data/{scale}_{duration}_from_{start_note}_continuous.xml"
		os.system(cmd)
		cmd = f"python3 scripts/scales.py --duration {duration} --scale {scale} --start_note C#1 --one_per_measure True --output_file data/{scale}_{duration}_from_{start_note}_with_breaks.xml"
		os.system(cmd)