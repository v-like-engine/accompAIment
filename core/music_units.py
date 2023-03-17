from core.constants import *
import music21 as mus
import random


class AtomicPiece:
    """
    Abstract parent class for Notes and Rests
    """
    def __init__(self, piece):
        """
        Constructor of the AtomicPiece
        :param piece: music21 Note or Rest object with duration
        """
        self.duration = piece.duration.quarterLength


class Note(AtomicPiece):
    """
    The class of the note which contains pitch (e.g. C#), octave number, it's duration and starting time.
    Needed for quick calculations of simultaneous playing of two notes,
    because the starting_time and duration are easily accessibly without calculation.
    However, instance of music21 class is accessible by note.note_itself
    """

    def __init__(self, note: mus.note.Note, octave_offset=0):
        """
        Constructor of the Note class, takes the music21 Note class instance and the octave_offset (for inverses, etc.)
        :param note: music21 Note class instance
        :param octave_offset: the number to add to the base octave of the note during processing; by default set to 0
        """
        super().__init__(note)
        self.note_itself = note
        self.pitch = note.name
        self.octave = note.octave
        self.octave_offset = octave_offset
        if note.measureNumber:
            self.starting_time = (note.measureNumber - 1) * 4.0 + note.offset
        else:
            self.starting_time = note.offset

    def get_note21(self) -> mus.note.Note:
        """
        Getter of music21 object
        :return: Note music21 object
        """
        return self.note_itself

    def get_volume21(self) -> mus.volume.Volume:
        """
        Getter for music21 volume object
        :return: Volume from music21
        """
        return self.note_itself.volume

    def get_octave(self) -> int:
        """
        Getter for the octave of the note (calculated with the offset)
        :return: octave of the note
        """
        if self.octave:
            return self.octave + self.octave_offset
        elif self.note_itself.octave:
            return self.note_itself.octave + self.octave_offset
        else:
            self.set_octave()
            return self.octave + self.octave_offset

    def set_octave(self, octave=3):
        """
        Setter for the note octave
        :param octave: new octave
        :return: None
        """
        self.octave = octave


class Rest(AtomicPiece):
    """
    The class of the Rest piece of the music
    """
    def __init__(self, rest: mus.note.Rest):
        """
        Constructor of the rest. The music21 Rest class instance must be provided
        :param rest: the music21 Rest class instance
        """
        super().__init__(rest)
        self.note_itself = rest
        if rest.measureNumber:
            self.starting_time = (rest.measureNumber - 1) * 4.0 + rest.offset
        else:
            self.starting_time = rest.offset


class Key:
    """
    Class of the Key that stores the key's name, tonic, scale, gamma (cycling_pitches) and allows to get
    all the consonant chords
    """
    def __init__(self, key_name: str):
        """
        Constructor for the key, takes the key name
        :param key_name: string containing the name of the key (in tiny notation, e.g. C#m or F)
        """
        self.scale = MINOR if MINOR in key_name else MAJOR
        self.name = key_name
        self.tonic = key_name.rstrip(self.scale)
        self.cyclic_pitches = []
        self.find_cyclic_key_pitches()

    def find_cyclic_key_pitches(self):
        """
        Method to find the row of the key table (or the part of the circle of fifths)
        """
        for i in range(7):
            pitch = NOTE_NAMES[(NOTE_NAMES.index(self.tonic) +
                                (sum(MINOR_SCALE_STEPS[:i]) if (self.scale == MINOR) else
                                 (sum(MAJOR_SCALE_STEPS[:i])))) % 12]
            self.cyclic_pitches.append(pitch)

    def get_chords(self, generate_rests: bool = False):
        """
        Method to get all the consonant chords for the current key. Chords can be used for the Accompaniment generation
        :param generate_rests: are rest (silent) chords allowed or not
        :return: list of consonant chords
        """
        consonant_chords = []
        for i in range(7):
            triad_name = self.cyclic_pitches[i] + (MINOR_KEY_SCALES[i] if (self.scale == MINOR) else
                                                   MAJOR_KEY_SCALES[i])
            consonant_chords.append(Chord(triad_name))
        for i in range(7):
            triad_type = (MINOR_KEY_SCALES[i] if (self.scale == MINOR) else MAJOR_KEY_SCALES[i])
            sus2_allowed = (MINOR_SUS2_ALLOWED[i] if (self.scale == MINOR) else MAJOR_SUS2_ALLOWED[i])
            sus4_allowed = (MINOR_SUS4_ALLOWED[i] if (self.scale == MINOR) else MAJOR_SUS4_ALLOWED[i])
            if triad_type != DIMINISHED:
                consonant_chords.append(Chord(self.cyclic_pitches[i] + triad_type, 1))
                consonant_chords.append(Chord(self.cyclic_pitches[i] + triad_type, 2))
                if sus2_allowed:
                    consonant_chords.append(Chord(self.cyclic_pitches[i] + SUS2))
                if sus4_allowed:
                    consonant_chords.append(Chord(self.cyclic_pitches[i] + SUS4))
            if generate_rests:
                consonant_chords.append(Chord(REST))
        return consonant_chords


class Chord:
    """
    Class of the Chord, supports both Three-note chords and rest (silent) chords
    """
    def __init__(self, chord_name: str, inverse_number=0):
        """
        Constructor of the Chord. Chord name must be provided. Possible types of Chords are:
        m, DIM, sus2, sus4, (Major is empty string after the tonic)
        :param chord_name: name of the chord, which must contain tonic name and chord type
        :param inverse_number: 0, 1 or 2 for the inverse of triad Chords
        """
        self.inverse = inverse_number
        if chord_name != REST:
            self.chord_type = SUS2 if (SUS2 in chord_name) else (SUS4 if
                                                                 (SUS4 in chord_name) else
                                                                 DIMINISHED if (DIMINISHED in chord_name)
                                                                 else MINOR if (MINOR in chord_name) else MAJOR)
            self.tonic = chord_name.rstrip(self.chord_type)
            self.name = chord_name
            self.note_names = []
            self.notes = []
            self.chord_itself = None
            self.calculate_notes()
        else:
            self.chord_type = REST
            self.tonic = None
            self.name = REST
            self.notes = [Rest(mus.note.Rest())]
            self.note_names = [REST]
            self.chord_itself = self.notes[0].note_itself
        # TODO: chord_itself from three notes

    def __str__(self):
        """
        :return: string representation of the Chord: it's name and notes
        """
        return self.tonic + self.chord_type + \
               (('inv' + str(self.inverse)) if self.inverse else '') + ' chord: ' + \
               ' '.join(list(map(lambda x: x.pitch, self.notes)))

    def calculate_notes(self):
        """
        Method to calculate all the notes of the Chord (even the rest), given the chord tonic and type.
        The table of offsets must be present in the file as CHORD_NOTE_OFFSETS.
        The notes keyboard must also be present as NOTE_NAMES
        :return: None, notes are stored into Chord.notes
        """
        duration = mus.duration.Duration(4.0)
        if self.chord_type == REST:
            for i in range(3):
                new_rest21 = mus.note.Rest(duration=duration)
                new_rest = Rest(new_rest21)
                self.notes.append(new_rest)
                self.note_names.append(REST)
        else:
            for offset in CHORD_NOTE_OFFSETS[self.chord_type]:
                name = (NOTE_NAMES[(NOTE_NAMES.index(self.tonic) + offset) % 12])
                self.note_names.append(name)
                new_note21 = mus.note.Note(name, duration=duration)
                new_note = Note(new_note21, (1 if ((NOTE_NAMES.index(self.tonic) + offset) > 12) else 0) +
                                (1 if (self.inverse == 1 and len(self.note_names) == 1) or
                                      (self.inverse == 2 and len(self.note_names) <= 2) else 0))
                self.notes.append(new_note)
        self.chord_itself = mus.chord.Chord([self.notes[0].note_itself, self.notes[1].note_itself,
                                             self.notes[2].note_itself])
        # TODO 8: Dominantsept chord, Leading tone (Cmaj7 C E G B and Dominantsept is C E G B- (flat))
        # TODO 9: Polychords (Cmaj + Gmaj = Cmaj9 = C E G + G B D = C E G B D)

    def get_chord21(self):
        """
        :return: music21 representation of the chord or rest
        """
        return self.chord_itself


class Accompaniment:
    """
    Accompaniment is Chromosome for the evolutionary algorithm,
    which is the sequence of chords for the accompaniment of the initial melody
    """
    def __init__(self, chords: list[Chord]):
        """
        Constructor of the accompaniment
        :param chords: list of Chords
        """
        self.chords = chords
        self.genes_count = len(chords)

    def __str__(self):
        res = ""
        res += '\n'.join((str(self.chords[i]) for i in range(self.genes_count)))
        res += '\n-----------------------------------'
        return res


class Melody:
    """
    Class of the Melody. Has methods to determine the key, parse all notes, find average volume and octaves
    """
    def __init__(self, stream: mus.stream.Stream, generate_rests: bool = False):
        """
        Constructor of the Melody
        :param stream: the converted and parsed melody's stream from music21 converter
        :param generate_rests: boolean to allow or prohibit the rest (silent) chord generation for the key
        """
        self.stream = stream
        self.size_in_bars = int(stream.duration.quarterLength)
        self.notes = []
        self.key = None
        self.parse_notes()
        self.determine_key()
        self.chords = self.key.get_chords(generate_rests)
        self.lowest_octave, self.average_octave, self.highest_octave = self.get_octaves()

    def parse_notes(self):
        """
        Parse notes (and rests) of the melody and store them into Melody.notes
        :return: None
        """
        notes = []
        for part in self.stream:
            if type(part) == mus.stream.Part:
                for bar in part:
                    if type(bar) == mus.stream.Measure:
                        for note in bar:
                            if type(note) == mus.note.Note:
                                if note.pitch.accidental is not None and (note.pitch.accidental.name == 'flat'):
                                    note.pitch = mus.pitch.Pitch(NOTE_NAMES[NOTE_NAMES.index(note.pitch.step) - 1])
                                notes.append(Note(note))
                            elif type(note) == mus.note.Rest:
                                notes.append(Rest(note))
        self.notes = notes

    def determine_key(self):
        """
        Method for the key determining of the whole melody. Determining is performed by manual calculation method.
        However, automatic analysis (by music21 library) can be performed instead, just de-comment commented lines
        :return: None, key is stored into Melody.key
        """
        # auto_determined = (self.stream.analyze('key'))
        set_of_notes = set()
        count_of_notes = dict()
        i = 0
        while type(self.notes[i]) == Rest:
            i += 1
        first_note = self.notes[i].pitch
        i = -1
        while type(self.notes[i]) == Rest:
            i -= 1
        last_note = self.notes[i].pitch
        for note in self.notes:
            if type(note) != Rest:
                set_of_notes.add(note.pitch)
                count_of_notes[note.pitch] = count_of_notes.get(note.pitch, 0) + 1
        mostly_used_note = (list(count_of_notes.keys())[list(count_of_notes.values()).index(
            max(list(count_of_notes.values())))])
        possible_keys = []
        key_probabilities = []
        for note in set_of_notes:
            missing_chords = 0
            for i in range(7):
                if NOTE_NAMES[(NOTE_NAMES.index(note) + sum(MAJOR_SCALE_STEPS[:i])) % 12] not in set_of_notes:
                    missing_chords += 1
            if (len(set_of_notes) < 7 and missing_chords <= (7 - len(set_of_notes))) or missing_chords == 0:
                possible_keys.append(note)
                key_probabilities.append(1)
                possible_keys.append(NOTE_NAMES[(NOTE_NAMES.index(note) + sum(MAJOR_SCALE_STEPS[:5])) % 12] + MINOR)
                key_probabilities.append(1)
        for i in range(len(possible_keys)):
            key = possible_keys[i]
            tonic = key.rstrip(MINOR)
            steps = MINOR_SCALE_STEPS if tonic != key else MAJOR_SCALE_STEPS
            mediant = NOTE_NAMES[(NOTE_NAMES.index(tonic) + sum(steps[:2])) % 12]
            dominant = NOTE_NAMES[(NOTE_NAMES.index(tonic) + sum(steps[:4])) % 12]
            subdominant = NOTE_NAMES[(NOTE_NAMES.index(tonic) + sum(steps[:3])) % 12]
            if last_note == tonic:
                key_probabilities[i] *= 3
            elif last_note == dominant:
                key_probabilities[i] *= 2.5
            elif last_note == mediant:
                key_probabilities[i] *= 2.25
            elif last_note == subdominant:
                key_probabilities[i] *= 1.5
            if first_note == tonic:
                key_probabilities[i] *= 2
            elif first_note == dominant:
                key_probabilities[i] *= 1.75
            elif first_note == mediant:
                key_probabilities[i] *= 1.75
            elif first_note == subdominant:
                key_probabilities[i] *= 1.25
            if mostly_used_note == tonic:
                key_probabilities[i] *= 2.5
            elif mostly_used_note == dominant:
                key_probabilities[i] *= 2
            elif mostly_used_note == mediant:
                key_probabilities[i] *= 1.75
            elif mostly_used_note == subdominant:
                key_probabilities[i] *= 1.5
        # self.key = Key(auto_determined.tonic.name + (MINOR if auto_determined.mode == 'minor' else MAJOR))
        self.key = Key(possible_keys[key_probabilities.index(max(key_probabilities))])

    def get_average_volume(self):
        """
        Method to get the average note's volume of the melody's notes
        :return: average volume
        """
        sum_volumes = 0
        notes_count = len(self.notes)
        for note in self.notes:
            if type(note) != Rest:
                sum_volumes += int(note.get_volume21().velocity)
        return sum_volumes // notes_count

    def get_octaves(self):
        """
        Method to calculate the lowest, average and highest note's octave in the melody
        :return: lowest, average, highest note's octave
        """
        lowest = 9
        highest = 0
        sum_of_octaves = 0
        notes_count = len(self.notes)
        for note in self.notes:
            if type(note) != Rest:
                oct = int(note.get_octave())
                if oct < lowest:
                    lowest = oct
                if oct > highest:
                    highest = oct
                sum_of_octaves += oct
        return lowest, sum_of_octaves // notes_count, highest
