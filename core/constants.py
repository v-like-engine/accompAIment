# Constant tables and names used in the program below:

# The table of note names:
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
# Constant names for chord types:
MINOR = 'm'
MAJOR = ''
DIMINISHED = 'DIM'
SUS2 = 'sus2'
SUS4 = 'sus4'
REST = 'rest'
# Scale steps for Major and minor keys:
MAJOR_SCALE_STEPS = [2, 2, 1, 2, 2, 2, 1]
MINOR_SCALE_STEPS = [2, 1, 2, 2, 1, 2, 2]
# Triad types according to the scale steps:
MAJOR_KEY_SCALES = [MAJOR, MINOR, MINOR, MAJOR, MAJOR, MINOR, DIMINISHED]
MINOR_KEY_SCALES = [MINOR, DIMINISHED, MAJOR, MINOR, MINOR, MAJOR, MAJOR]
# Chord note offsets:
CHORD_NOTE_OFFSETS = {MAJOR: [0, 4, 7], MINOR: [0, 3, 7], SUS2: [0, 2, 7], SUS4: [0, 5, 7], DIMINISHED: [0, 3, 6]}
# Allowed positions for sus2 and sus4 chords (can be calculated from scale steps):
MAJOR_SUS2_ALLOWED = [MAJOR_SCALE_STEPS[i] != 1 for i in range(7)]
MINOR_SUS2_ALLOWED = [MINOR_SCALE_STEPS[i] != 1 for i in range(7)]
MAJOR_SUS4_ALLOWED = [i not in [4 - 1, 7 - 1] for i in range(7)]
MINOR_SUS4_ALLOWED = [i not in [2 - 1, 6 - 1] for i in range(7)]
