from math import floor
from Player import Player
import globfile
from Genome import Genome
from Species import Species


class Population:
    def __init__(self, size):
        globfile.next_connection_number = 0
        
        self.players: list[Player] = []
        self.best_player = None  # the best player ever
        self.best_score = 0  # best score of the best player ever
        self.global_best_score = 0
        
        self.innovationHistory = []
        
        self.generation = 1
        self.species: list[Species] = []
                
        self.n_inputs = 4
        self.n_outputs = 1
        self.layers = 2
        for _ in range(size):
            new_player = Player(agent=Genome(self.n_inputs, self.n_outputs, layers=self.layers))
            self.players.append(new_player)
            new_player.agent.mutate(self.innovationHistory)
            new_player.agent.generate_network()

    def update(self):
        for player in self.players:
            if player.isAlive:
                player.look_around()
                player.update()
                player.check_crash()

            if player.score > self.global_best_score:
                self.global_best_score = player.score
        
    def done(self):
        self.global_best_score = 0
        for player in self.players:
            player.check_crash()
            if player.isAlive:
                return False
        return True

    def create_species(self):
        species = []
        for player in self.players:
            found_species = False
            for specie in species:
                if specie.is_in_species(player):
                    specie.add_player(player)
                    found_species = True
                    break
            if not found_species:
                species.append(Species(player))
        return species
    
    def speciate(self):
        for specie in self.species:
            specie.players = []
        for player in self.players:
            found_species = False
            for specie in self.species:
                if specie.is_in_species(player.agent):
                    specie.add_player(player)
                    found_species = True
                    break
            if not found_species:
                self.species.append(Species(player))
                
    def calculate_fitness_level(self):
        for player in self.players:
            player.fitness_level()
            
    def sort_species(self):
        for specie in self.species:
            specie.sort_species()
        self.species.sort(key=lambda s: s.best_score, reverse=True)
        
    def total_average_fitness(self, species):
        total = 0
        for s in species:
            total += s.average_fitness
        return total / len(species)
    
    def birth_new_generation(self):  # natural selection
        self.calculate_fitness_level()
        prev_best = sorted(self.players, key=lambda p: p.fitness, reverse=True)[0] #TODO: probably doesnt get the best player
        print("Best player's fitness:", prev_best.fitness)
        print("Best player's DNA:\n", prev_best.agent)

        self.speciate()
        self.calculate_fitness_level()
        self.sort_species()
            
        # kill the birds that haven't learned how to fly
        # kill the species that are so bad they don't deserve the chance to reproduce
        self.bye_bye_idiots(threshold=15)  # kill the species that haven't improved in threshold=15 generations
        
        print(f"Generation: {self.generation}, mutations: {len(self.innovationHistory)}, species: {len(self.species)} =======================")
        
        sum_of_species_average = sum([s.average_fitness for s in self.species])
        baby_birds = []
        for specie in self.species:
            baby_birds.append(specie.best_player.__copy__())
            # the number of babies this species is allowed (-1 because the best player is already added)
            num_babies = floor(specie.average_fitness / sum_of_species_average * len(self.players)) - 1
            
            for _ in range(num_babies):
                baby_birds.append(specie.hatch_egg(self.innovationHistory))
        
        # if we don't have enough babies we need to fix that
        # first we need to keep the best
        if len(baby_birds) < len(self.players):
            baby_birds.append(prev_best.__copy__())

        while len(baby_birds) < len(self.players):
            baby_birds.append(self.species[0].hatch_egg(self.innovationHistory))  # only take from the best species b/c elitism

        # aliasing errors suck so lets be extra careful
        self.players.clear()
        for bird in baby_birds:
            self.players.append(bird.__copy__())
        self.generation += 1
        
        # unscramble the baby birds brains
        for baby_bird in self.players:
            baby_bird.agent.generate_network()
            
    def bye_bye_idiots(self, threshold=15):
        species_to_kill = []
        for specie in self.species:
            specie.cull()
            specie.share_fitness()
            if len(specie.players) == 0:
                species_to_kill.append(specie)
            specie.set_average_fitness()
            
        for specie in species_to_kill:
            self.species.remove(specie)
            
        for specie in self.species[2:]:
            if specie.staleness >= threshold:
                self.species.remove(specie)
                
        sum_of_species_average = sum([specie.average_fitness for specie in self.species])
        
        for specie in self.species[1:]:
            if specie.average_fitness / sum_of_species_average * len(self.players) < 1:
                self.species.remove(specie)

    def draw(self, screen):
        for player in self.players:
            player.draw(screen)
