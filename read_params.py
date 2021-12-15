import reapy
import reapy.reascript_api as RPR

import sys

def get_params(vst_name, format="tsv"):
	# Start Reaper project
	project = reapy.Project()
	# for track in project.tracks:
	#     track.delete()
	project.cursor_position = 0
	track = project.tracks[0]

	# Load VST
	track.add_fx(vst_name)

	# Enumerate parameters
	for i, p in enumerate(track.fxs[0].params):
		if format == "tsv":
			print(f"{i}\t{p.name}\t{p}")
		elif format == "yaml":
			print(f"  - name: {p.name}")
			print(f"    value: {p:.2f}")


if __name__ == '__main__':
	vst_name = sys.argv[1]
	if len(sys.argv) > 2:
		get_params(vst_name, format=sys.argv[2])
	else:
		get_params(vst_name)
