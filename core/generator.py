from core.evolutionary_algorithm import *


class GeneratorOfAccompaniment:
    """
    Class for all generation handling. Instance of this class is an instrument to use for converting into
    the MIDI file with all the needed settings
    """

    def __init__(self, melody: Melody, number_of_generations_ea=100, population_size_ea=1000,
                 new_members_percentage_ea=30):
        """
        Constructor with all the needed parameters for evolutionary algorithm described above
        :param melody: Melody of the original input track
        :param number_of_generations_ea: how many iterations to perform (the amount of new generations to make)
        :param population_size_ea: the size of one generation (in members)
        :param new_members_percentage_ea: how many percents of new members (with respect to the initial population size)
                to generate using crossover and mutations for each generation
        """
        self.melody = melody
        self.chords = melody.chords
        self.key = melody.key
        self.ea = EvolutionaryAlgorithm(number_of_generations_ea, population_size_ea, new_members_percentage_ea,
                                        melody, self.key)

    def get_best_accompaniment(self):
        """
        :return: the best accompaniment found by the evolutionary algorithm
        """
        return self.ea.evolve()

    def generate_midi_accompaniment(self, output_file_name: str, style: int):
        """
        Method that creates the MIDI output file with the best generated accompaniment and initial melody.
        Uses settings provided to it
        :param output_file_name:
        :param style:
        :param rests_generation:
        :return:
        """
        accompaniment = self.get_best_accompaniment()
        chords_part = mus.stream.Part()
        chords_instruments = [mus.instrument.ElectricPiano(),
                              mus.instrument.AcousticGuitar(),
                              mus.instrument.Violoncello(),
                              mus.instrument.Flute(),
                              mus.instrument.Xylophone(),
                              mus.instrument.Choir()]
        chords_octave = [(self.melody.lowest_octave - 1),
                         (self.melody.lowest_octave - 1),
                         (self.melody.lowest_octave - 1),
                         (self.melody.average_octave - 1),
                         (self.melody.lowest_octave - 1),
                         (self.melody.highest_octave + 0)]
        chords_volume = [self.melody.get_average_volume(),
                         min(127, self.melody.get_average_volume() + 4),
                         max(16, self.melody.get_average_volume() - 10),
                         min(127, self.melody.get_average_volume() + 20),
                         max(16, self.melody.get_average_volume() - 8),
                         max(16, self.melody.get_average_volume() - 8)]
        chords_part.insert(chords_instruments[style])
        for chord in accompaniment.chords:
            chord21 = chord.get_chord21()
            if type(chord21) != mus.note.Rest:
                for i in range(len(chord21.notes)):
                    if type(chord.notes[i]) != Rest:
                        chord21.notes[i].octave = chords_octave[style] + chord.notes[i].octave_offset
                        chord21.notes[i].volume = chords_volume[style]
                        chord21.duration.quarterLength = 1.0
                chords_part.append(mus.chord.Chord(chord21))
            else:
                chords_part.append(mus.note.Rest(duration=mus.duration.Duration(1.0)))
        music_part = mus.stream.Part()
        music_instruments = [mus.instrument.ElectricPiano(),
                             mus.instrument.AcousticGuitar(),
                             mus.instrument.Violin(),
                             mus.instrument.Koto(),
                             mus.instrument.Xylophone(),
                             mus.instrument.ChurchBells()]
        music_part.insert(music_instruments[style])
        for note in self.melody.notes:
            if type(note) != Rest:
                music_part.append(note.note_itself)
            else:
                music_part.append(note.note_itself)
        output = mus.stream.Stream()
        output.append(music_part)
        output.append(chords_part)
        midi_file = mus.midi.translate.streamToMidiFile(output)
        midi_file.open(output_file_name, 'wb')
        midi_file.write()
        midi_file.close()
