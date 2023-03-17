from core.generator import *


def start():
    """
    Main function for running the program and setting parameters. Provides interface for working with user.
    Here user specifies input files' names, style number and the rest chord generation permission
    :return:
    """
    print('Welcome to the MIDI Accompaniment generator!\n',
          'The program was made by Vladislav Urzhumov, student of Innopolis University. November, 2022.')
    print(' The program will generate one output file for each input file specified.')
    print('It\'s interface is simple, however, I\'ve tried to make it as user friendly as possible!\n')
    print('In the following input field you will be able to provide filenames with extensions (only .mid) of input',
          'files (separated by space) to process them in the program.\n',
          'If you just press enter without specifying any names,',
          'base input files will be used.\n',
          'Base input files (according to the task) are: input1.mid, input2.mid, input3.mid')
    files = (input('Please, specify filenames or just press enter for sample generation: ').split() or
             ['data/samples/input1.mid', 'data/samples/input2.mid', 'data/samples/input3.mid'])
    print('\nGreat! Now, please, specify the style of the music you want to receive in the output files.',
          '\nStyles differ in instruments used, sometimes octaves for the accompaniment  and even additional parts.',
          '\nThe list of currently available styles:\n',
          '0 (Stock, just press enter) - Classical piano\n',
          '1 - Acoustic Guitar\n',
          '2 - Orchestra with Violin and Violoncello\n',
          '3 - Japanese style (Koto and Flute)\n',
          '4 - Xylophone\n',
          '5 - Choir and Church Bell\n')
    style = (int(input('Please, specify the number of style or press enter: ') or 0))
    while style < 0 or style > 5:
        style = (int(input('Please, specify correct number (0 to 5) or press enter: ') or 0))
    print('\nPerfect! Last thing before we start. Should the program use Rests',
          '("silence" chords) as the part of Accompaniment?')
    rests = any(input('Type something if yes, or just press enter for no: '))
    print('Thank you! Now we start! It will take some time...\n')
    for input_file in files:
        try:
            stream = mus.converter.parse(input_file)
            print('Your file', input_file, 'was converted succesfully')
            melody = Melody(stream, rests)
            print('The key of the melody was determined as', melody.key.name)
            generator = GeneratorOfAccompaniment(melody)
            filename = None
            try:
                filename = ('data/results/output-' + input_file.lstrip('data/samples/input').rstrip('.mid') + '-'
                            + melody.key.name + '.mid')
                generator.generate_midi_accompaniment(filename, style)
                print('The Accompaniment was successfully generated!')
            except FileNotFoundError:
                print('Error! Output file', filename, 'can not be created in the specified directory')
        except FileNotFoundError:
            print('Error! File', input_file, 'was not found in the current directory or has an incorrect name.')
