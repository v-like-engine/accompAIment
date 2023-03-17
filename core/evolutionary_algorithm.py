from core.music_units import *
from core.list_generation import *
from core.constants import *


class EvolutionaryAlgorithm:
    def __init__(self, number_of_generations: int, population_size: int, new_members_percentage: int,
                 melody: Melody, key: Key):
        """
        Constructor of the Evolutionary Algorithm class
        :param number_of_generations: how many iterations to perform
        :param population_size: the amount of members in generation
        :param new_members_percentage: how many (in percents) new members should be generated
        :param melody: the initial melody (needed for fitness calculation)
        :param key: the key of the melody for the fast access
        """
        self.n_iterations = number_of_generations
        self.population_size = population_size
        self.melody = melody
        self.number_of_genes_in_chromosome = melody.size_in_bars
        self.key = key
        self.chords = melody.chords
        self.new_members_percentage = new_members_percentage
        self.current_generation = []
        self.current_fitness = []
        self.current_fitness_sum = 0

    def generate_zeroth_generation(self):
        """
        Method to generate the initial generation (purely random members) for evolutionary algorithm
        :return: None
        """
        for g in range(self.population_size):
            chords_sequence = []
            for i in range(self.melody.size_in_bars):
                chords_sequence.append(random.choice(self.chords))
            self.current_generation.append(Accompaniment(chords_sequence))
        self.current_fitness = self.generate_fitness_list(self.current_generation)
        self.current_fitness_sum = sum(self.current_fitness)

    def generate_fitness_list(self, population):
        """
        Method for generating the list of fitness values for the provided population members (in the same order)
        :param population: population whose members need their fitness value to be calculated
        :return: list of fitness values for the members of population
        """
        fitnesses = []
        for chromosome in population:
            fitnesses.append(self.calculate_fitness(chromosome))
        return fitnesses

    def calculate_fitness(self, chromosome: Accompaniment, debug=False):
        """
        Method for caluclating fitness for one chromosome (Accompaniment)
        :param chromosome: Accompaniment to calculate fitness of
        :param debug: should the method print the calculated fitness or not
        :return: fitness of the chromosome
        """
        CONSONANCE_COEFFICIENT = 1
        REPETITION_COEFFICIENT = 25
        PROGRESSION_COEFFICIENT = 5
        fitness = (CONSONANCE_COEFFICIENT * self.consonance_fitness(chromosome) +
                   REPETITION_COEFFICIENT * self.chord_repetition_fitness(chromosome) +
                   PROGRESSION_COEFFICIENT * self.chord_progression_fitness(chromosome))
        if debug:
            print('Consonance:', CONSONANCE_COEFFICIENT * self.consonance_fitness(chromosome))
            print('Rep:', REPETITION_COEFFICIENT * self.chord_repetition_fitness(chromosome))
            print('Progression:', PROGRESSION_COEFFICIENT * self.chord_progression_fitness(chromosome))
        return fitness

    def consonance_fitness(self, chromosome: Accompaniment):
        """
        Fitness calculation for the consonant notes
        :param chromosome:
        :return:
        """
        fitness = 0
        # consonance_interval_table = [0, 7, 5, 4, 3, 9, 8, 2, 10, 11, 1, 6]
        # in consonance table: first three intervals are the most consonant, then next four are considered as
        # mild consonance, next two are mildly dissonant, last three result in sharp dissonance
        consonance = [0, 7, 5]
        mild_consonance = [4, 3, 9, 8]
        mild_dissonance = [2, 10]
        dissonance = [11, 1, 6]
        for i in range(len(chromosome.chords)):
            chord = chromosome.chords[i]
            for note in self.melody.notes:
                if type(note) != Rest:
                    if note.starting_time > ((i + 1) * 1.0):
                        break
                    elif (i * 1.0) < note.starting_time < ((i + 1) * 1.0):
                        duration = (min([note.starting_time + note.duration, (i + 1) * 1.0]) - note.starting_time)
                    elif i * 1.0 < (note.starting_time + note.duration):
                        duration = note.starting_time + note.duration - i * 1.0
                    else:
                        duration = 0
                    if duration:
                        for chord_note in chord.note_names:
                            if chord_note != REST:
                                interval = abs((NOTE_NAMES.index(note.pitch) - NOTE_NAMES.index(chord_note)) % 12)
                                # if interval points on the fact that two notes
                                # (from the melody and from the chosen chord)
                                # are mildly consonant, fitness grows by the note duration
                                # (during the chord is played) * 1
                                # sharp consonance is considered five times as good as mild consonance
                                # tonic gives the most fitness bonus
                                # mild dissonance is not the worst thing to happen,
                                # so the fitness grows by 0.4 * duration
                                # dissonance gives 0
                                if interval in consonance:
                                    fitness += 5 * duration * (3 - consonance.index(interval))
                                elif interval in mild_consonance:
                                    fitness += 1 * duration
                                elif interval in mild_dissonance:
                                    fitness += 0.1 * duration
                            else:
                                fitness -= 10 * duration
                else:
                    # Rest chord is better when the rest is present in the melody
                    if note.starting_time > ((i + 1) * 1.0):
                        break
                    elif (i * 1.0) < note.starting_time < ((i + 1) * 1.0):
                        duration = (min([note.starting_time + note.duration, (i + 1) * 1.0]) - note.starting_time)
                    elif i * 1.0 < (note.starting_time + note.duration):
                        duration = note.starting_time + note.duration - i * 1.0
                    else:
                        duration = 0
                    if duration:
                        if chord.chord_type == REST:
                            fitness += 1 * duration
        return max(1, fitness)

    def chord_repetition_fitness(self, chromosome: Accompaniment):
        """
        Fitness calculation for the doubled chords (one chord repetition, if chord is not silent)
        :param chromosome: one accompaniment we calculate the fitness for
        :return: fitness bonus for chord repetition
        """
        fitness = 0
        for i in range(chromosome.genes_count):
            # When the chord is repeated twice, the fitness grows by 2.
            # However, if it is repeated more than two times in a row, the fitness does not grow.
            # For the exactly four repetitions progression, see progression fitness calculation
            repetition_bonus = 0
            if i > 0 and chromosome.chords[i - 1].note_names == chromosome.chords[i].note_names and \
                    chromosome.chords[i].note_names[0] != REST:
                repetition_bonus += 1
            if i < chromosome.genes_count - 1 and \
                    chromosome.chords[i].note_names == chromosome.chords[i + 1].note_names and \
                    chromosome.chords[i].note_names[0] != REST:
                if repetition_bonus > 0:
                    repetition_bonus -= 1
                else:
                    repetition_bonus += 1
            fitness += repetition_bonus
        return fitness

    def chord_progression_fitness(self, chromosome: Accompaniment):
        """
        Fitness calculation for chord progressions
        Some popular chord progressions are in main_progressions list
        If the progression was found in the accompaniment, the significant fitness bonus is added
        :param chromosome: one accompaniment we calculate the fitness for
        :return: fitness bonus for chord progressions
        """
        fitness = 0
        main_progressions = [[0, 0, 0, 0], [0, 3, 4, 4], [0, 0, 3, 4], [0, 3, 0, 4], [0, 3, 4, 3], [0, 3, 4, 0],
                             [0, 5, 1, 4], [3, 3, 0, 0], [4, 4, 0, 0], [5, 3, 0, 4], [0, 5, 3, 4]]
        # TODO 9: understand major and minor progressions, make chord_progression_fitness method smarter
        # TODO 10: sort main progressions to determine stronger ones and change fitness bonus to 100 + 10 * pr.index(pr)
        for i in range(chromosome.genes_count - 3):
            triads = list(map(lambda x: x.name, self.chords[:7]))
            intervals = []
            for a in range(4):
                if chromosome.chords[i + a].name in triads:
                    intervals.append((triads.index(self.key.name) - triads.index(chromosome.chords[i + a].name)) % 7)
            if intervals in main_progressions:
                fitness += 100
        return fitness

    def mutate(self, child: Accompaniment):
        """
        Method for mutating the child Chromosome (Accompaniment)
        Mutating is crucial to enlarge the number of different genes in the population,
        because randomly mutated genes (Chords in our case) may not be contained in parent's Chromosomes
        :param child: child Chromosome (Accompaniment, sequence of chords)
        :return: mutated child (however, the initial child Accompaniment is changed in the same way, so we have
        two ways of accessing the child for the convenience)
        """
        for i in range(len(child.chords)):
            if random.randint(0, 99) <= 12:
                # mutate with the probability 0.13
                child.chords[i] = random.choice(self.chords)
        return child

    def crossover(self, parent1: Accompaniment, parent2: Accompaniment):
        """
        Method for performing the uniform crossover between two parent Chromosomes (Accompaniments), returns their child
        Uniform crossover means that each gene (Chord) has the equal probability to be father's or mother's
        :param parent1: father Accompaniment
        :param parent2: mother Accompaniment
        :return: new child Accompaniment
        """
        child_genes = []  # list of Chords
        for i in range(self.number_of_genes_in_chromosome):
            child_genes.append(random.choice([parent1.chords[i], parent2.chords[i]]))
        return Accompaniment(child_genes)

    def create_new_generation(self):
        """
        Method for one iteration (generation renewal) performing
        It creates new_members_percentage * population_size new members and sorts the list by fitness value
        The most fit (population_size) members are chosen for the new generation
        """
        new_members = []
        number_of_crossovers = self.new_members_percentage * self.population_size // 100
        fathers, mothers = determine_parents_lists(self.current_generation, self.current_fitness,
                                                   self.current_fitness_sum, number_of_crossovers)
        for i in range(number_of_crossovers):
            new_accompaniment = self.mutate(self.crossover(fathers[i], mothers[i]))
            new_members.append(new_accompaniment)
        # constructing list of pairs: [member, fitness] and sorting it in ascending order
        children_fitness = self.generate_fitness_list(new_members)
        overall_fitness = self.current_fitness + children_fitness
        overall_generation = self.current_generation + new_members
        overall_extended_generation_with_fitness = []
        for i in range(self.population_size + number_of_crossovers):
            overall_extended_generation_with_fitness.append([overall_generation[i], overall_fitness[i]])
        overall_extended_generation_with_fitness.sort(key=lambda x: x[1])
        self.current_generation = list(map(lambda x: x[0],
                                           overall_extended_generation_with_fitness[number_of_crossovers:]))
        self.current_fitness = self.generate_fitness_list(self.current_generation)
        self.current_fitness_sum = sum(self.current_fitness)

    def evolve(self) -> Accompaniment:
        """
        Method to start evolution: generate zeroth generation and perform n_iterations iterations
        :return: best (by fitness) accompaniment generated
        """
        self.generate_zeroth_generation()
        for i in range(self.n_iterations):
            self.create_new_generation()
        return self.current_generation[-1]
