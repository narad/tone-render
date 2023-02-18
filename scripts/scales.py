from musical_scales import scale, Note
import argparse
from pathlib import Path

import xml.etree.ElementTree as ET
from xml.dom import minidom
import re 


header = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE score-partwise PUBLIC
    "-//Recordare//DTD MusicXML 4.0 Partwise//EN"
    "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
  <work>
    <work-title>XXX</work-title>
  </work>
  <part-list>
    <score-part id="P1">
      <part-name>Music</part-name>
    </score-part>
  </part-list>
  <part id="P1">
'''

footer = '''
  </part>
</score-partwise>
'''

letters = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def parse_note(note):
	note_str = str(note)
	if '#' in note_str:
		return note_str[:2], int(note_str[2:3])
	else:
		return note_str[:1], int(note_str[1:2])

def lte(n1, n2):
	l1, o1 = parse_note(n1)
	l2, o2 = parse_note(n2)
	if o1 < o2:
		return True
	if o1 > o2:
		return False
	if l1 == l2:
		return True
	return letters.index(l1) < letters.index(l2)


def note_to_str(note):
	letter, octave, duration = note
	s = ""
	s += (f"""<note>
        <pitch>
          <step>{letter}</step>
          <octave>{octave}</octave>""")
	if "#" in letter:
		s += " <alter>+1</alter>"
	s += f"""
        </pitch>
        <duration>{duration}</duration>
        <type>{dur2name[duration]}</type>
      </note>"""
	return s


def rest_to_str(rest_dur):
	return f"""<note><rest measure="yes"/><duration>{rest_dur}</duration><type>{dur2name[rest_dur]}</type></note>""".replace("\n", "")


def fill_measure(notes, divisions_per_measure, mcount=0, add_rests=False):
	dpm = divisions_per_measure
	s = ""
	s += (f"""<measure number="{mcount}"><attributes><divisions>32</divisions></attributes>""")
	for note in notes:
		s += note_to_str(note)
		_,_,duration = note
		dpm -= duration
	if add_rests:
		while dpm > 0:
			rest = biggest_rest(dpm)
			s += rest_to_str(rest)
			dpm -= rest

	s += "</measure>\n"
	return s


def biggest_rest(space):
	for k in dur2name.keys():
		if k <= space:
			return k


beats_per_measure = 128

name2dur = {
	"whole": 128,
	"half": 64,
	"quarter": 32,
	"eigth": 16,
	"sixteenth": 8,
}

dur2name = {
	128: "whole",
	64: "half",
	32: "quarter",
	16: "eigth",
	8: "sixteenth",
}

def write_xml(notes, output_file):
	global header
	global footer

	notes_per_measure = beats_per_measure / name2dur[args.duration]
	lheader = header.replace("XXX", f"{args.scale} {args.duration} note")

	x = lheader
	if args.one_per_measure:
		for i, note in enumerate(notes):
			x += fill_measure([note], beats_per_measure, mcount=i+1, add_rests=args.add_rests)
	else:
		# group by appropriate number of notes per measure
		w = int(notes_per_measure)
	#	print(w)
		notes = [notes[i:i+w] for i in range(0, len(notes), w)]
		for i, notes_in_measure in enumerate(notes):
	#		print(notes_in_measure)
			x += fill_measure(notes_in_measure, beats_per_measure, mcount=i+1, add_rests=args.add_rests)
	x += footer

	# make it pretty
	tree = ET.fromstring(x.replace("\n", ""))
	xmlstr = minidom.parseString(ET.tostring(tree)).toprettyxml(indent="   ")

	xmlstr = re.sub(" +\n", "", xmlstr)

	# write to file
	with open(output_file, "w") as f:
		f.write(xmlstr)


# Notes:
# Default start/stop notes roughly correspond to 7-string guitar range
# C#1 is the lowest for a 9-string like in the Hellraiser Sample Pack
# List of scales available here: 
# https://github.com/hmillerbakewell/musical-scales

# Parse commandline args
parser = argparse.ArgumentParser()
parser.add_argument('--start_note', type=str, default="B1", help='The lowest note in the scale')
parser.add_argument('--end_note', type=str, default="E6", help='The highest note in the scale (or threshold)')
parser.add_argument('--scale', type=str, default="chromatic", help='The type of scale.  Use hyphens for spaces.')
parser.add_argument('--duration', type=str, default="quarter", help="The duration of the note")
parser.add_argument('--one_per_measure', type=str, help="Play one note and fill the rest of the measure with rest")
parser.add_argument('--add_rests', type=bool, default=False, help="Whether to explicitly add rests or not (good for viewing scores)")
parser.add_argument('--notes_per_file', type=str, choices=['single', 'multiple'], help="Whether to write each note to a separate file.")
parser.add_argument('--output_file', type=str, default="out.xml", help="Output music XML file")
parser.add_argument('--output_dir', type=Path, default="./", help="Output folder for multiple music XML files")
parser.add_argument('--direction', type=str, choices=['ascending', 'descending'], default='ascending', help="Direction of the scale")
args = parser.parse_args()


start_letter, start_octave = parse_note(args.start_note)
end_letter, end_octave = parse_note(args.end_note)

# Create the sequence of notes in the scale
notes = scale(Note(start_letter) - (12 * (3-start_octave)), args.scale.replace("-", " "), octaves = (end_octave-start_octave))
# Chop off notes beyond the boundary points
notes = [n for n in notes if lte(str(n), args.end_note)]
# Convert to the letter/octave/duration tuple format used from here on
notes = [parse_note(note) + (name2dur[args.duration],) for note in notes]
# Flip the direction if it should be descending
if args.direction == "descending":
	notes.reverse()

# Make output dir if not existing
args.output_dir.mkdir(parents=True, exist_ok=True)

# Process
if args.notes_per_file == 'single':
	for note in notes:
		print(note)
		letter, octave, dur_int = note
		dur = dur2name[dur_int]
		write_xml([note],
			        output_file=args.output_dir / f"{letter}{str(octave)}_{dur}.xml")

else:
	write_xml(notes, args.output_file)













#

#with open("New_Database.xml", "w") as f:
#    f.write(xmlstr)

    #f.write(ET.indent(tree, space=' ', level=0))




# mcount = 1
# for i, note in enumerate(notes):
# 	letter, octave = parse_note(note)
# 	if i % notes_per_measure == 0 or args.one_per_measure:
# 		if i != 0:
# 			print(f"""    </measure>\n""")
# 			mcount += 1
# 		print(f"""    <measure number="{mcount}">
# 						<attributes>
#     						<divisions>32</divisions>
#     					</attributes>""")
# 	note = str(note)
# 	if "#" in letter:
# 		accidental_tag = " <alter>+1</alter>"
# 	else:
# 		accidental_tag = ""
# 	print(f"""<note>
#         <pitch>
#           <step>{letter}</step>
#           <octave>{octave}</octave>{accidental_tag}
#         </pitch>
#         <duration>{name2dur[args.duration]}</duration>
#         <type>{args.duration}</type>
#       </note>""")

# 	if args.one_per_measure:
# 		print(f"""			
# 			<note>
# 	   	 		<rest measure="yes"/>
# 	    		<duration>{beats_per_measure - name2dur[args.duration]}</duration>
# 	  		</note>""")


# for _ in range(int(len(notes) % notes_per_measure)):
# 	print(f"""
# 		<note>
#    	 		<rest measure="yes"/>
#     		<duration>{args.duration}</duration>
#   		</note>""")

# print(footer)


