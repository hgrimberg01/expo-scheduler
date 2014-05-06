#!/usr/bin/env python3
from random import randint,choice
from copy import copy as ShallowCopy
from copy import deepcopy as DeepCopy
import math

import csv
with open("team_event_elem_school.csv",'r') as f:
        r = csv.reader(f)
        test_bindings = [(row[0].strip(), row[1].strip()) for row in r ]

#test_bindings = [('Team A', 'Event A'), ('Team B', 'Event A'), ('Team C', 'Event A'),
#            ('Team A', 'Event B'), ('Team B', 'Event B'), ('Team C', 'Event B'),
#            ('Team B', 'Event C'), ('Team C', 'Event C')]

# Number of Time Slots (Hours * 60 ) / Minutes Per Time Slot
TIME_SLOTS = (5 * 60 // 5)

# Number of teams that can be scheduled to a slot
NUMBER_PER_SLOT = 5

class Slot:
    def __init__(self, time, team, event):
        self.time = time
        self.team = team
        self.event = event

    def time_overlap(self, slt):
        if(slt.time == self.time and self.event == slt.event):
            return True
        else:
            return False




# Assume for now we only schedule one event at a time
class Chromosome:
    def __init__(self,bindings, parent=None, parent_two = None):
        self.times = [ []  for x in range(TIME_SLOTS)]

        # Schedule is a dictionary that maps team names to events
        # and the respective time slots
        # The entire binding is the key -> time slot

        self.schedule = {}
        self.parent = parent
        self.parent_two = parent_two
        self.bindings = bindings
        self.crossover_points = None
        self.mutation_size = None
        self.crossover_prob = None
        self.mutation_prob = None
        self.open_slots = []

        if(self.parent == None):
            self.build_chromosome()

    def get_fitness(self):
        fitness = 0
        team_conflict = False
        not_all_teams_scheduled = False


        for i,k in enumerate(self.times):
            if not len(k) > NUMBER_PER_SLOT:
                fitness += len(k)

        for team_tuple, slot in self.schedule.items():
            for team_tuple2, slot2 in self.schedule.items():
                if team_tuple[0] == team_tuple2[0] and slot == slot2:
                    team_conflict = True
                else:
                    fitness += 1



        return fitness


    def build_chromosome(self):
        if(self.parent == None):
            # No parent, so randomly build a schedule,
            for binding in self.bindings:
                rand_pos = randint(1, TIME_SLOTS) - 1
                selection = binding
                self.schedule[selection] = rand_pos
                self.times[rand_pos].append(selection)
        else:
            pass


    def rebuild_times_from_sched(self):
        self.times = [ []  for x in range(TIME_SLOTS)]
        for team, slot in self.schedule.items():
            self.times[slot].append(team)

    def crossover(self, size=1, strategy='RAND'):

        if(strategy == 'UNION'):
            new_sched = {}
            for team, time in self.parent.schedule.items():
                for team2, time2 in self.parent_two.schedule.items():
                    if(team == team2 and time2 == time):
                        new_sched[team] = time
                        self.times[time].append(team)
                    else:
                        new_sched[team] = time
                        self.times[time].append(team)
                        new_sched[team2] = time2
                        self.times[time2].append(team2)
            self.schedule = new_sched
            self.rebuild_times_from_sched()
        elif(strategy == 'RAND'):
            new_sched = DeepCopy(self.parent.schedule)

            #Choose N(size) of from second parent to put into first parent

            for i in range(size):
                rand_key_one = choice(list(new_sched.keys()))
                rand_key_two = choice(list(self.parent_two.schedule.keys()))

                val_one = new_sched[rand_key_one]
                val_two = self.parent_two.schedule[rand_key_two]

                new_sched[rand_key_two] = val_one
                new_sched[rand_key_one] = val_two

            self.schedule = new_sched
            self.rebuild_times_from_sched()






    def mutate(self, size=1, strategy='INTELLIGENT'):

        new_sched = self.schedule
        if(strategy == 'RAND'):
            for i in range(size):
                rand_key_one = choice(list(new_sched.keys()))

                rd = randint(1,TIME_SLOTS) - 1
                old_val = self.schedule[rand_key_one]

                self.times[old_val].remove(rand_key_one)
                self.schedule[rand_key_one] = rd
                self.times[rd].append(rand_key_one)
        elif(strategy == 'INTELLIGENT'):
            for i,r in enumerate(self.times):
                if(len(r) > NUMBER_PER_SLOT):
                    reloc = r[NUMBER_PER_SLOT:]
                    r = r[:NUMBER_PER_SLOT]
                    for mv in reloc:

                        self.schedule[mv] = self.find_open_slot()

                        self.rebuild_times_from_sched()



    def find_open_slot(self):
        for i,r in enumerate(self.times):
            if len(r) < NUMBER_PER_SLOT:
                return i



    def print_times(self):
        pass

    def print_sched(self):
        for team, slot in self.schedule.items():
            print ("%s  %s" % team, slot)
        return


class ScheduleGenerator:

    def __init__(self,bindings):
        self.bindings = bindings


    def gen_sched(self):
        generations = 0
        best_fitness = -1
        running_gens = 0
        parents = []
        init = Chromosome(self.bindings)
        init2 = Chromosome(self.bindings)
        if1 = init.get_fitness()
        if2 = init2.get_fitness()
        gens = 1
        if(if1 > if2):
            best_fitness = if1
            parents.insert(0, init)
            parents.append(init2)
        elif (if2 >= if1):
            best_fitness = if2
            parents.insert(0, init2)
            parents.append(init)

        ideal_fitness = (len(self.bindings) ** 2)
        while (best_fitness < ideal_fitness):
            rand_parent_one = parents[randint(1,len(parents))-1]
            rand_parent_two = parents[randint(1,len(parents))-1]
            new_chromosome = Chromosome(init.bindings, rand_parent_one,rand_parent_two)
            mt = math.ceil((len(self.bindings) - best_fitness) / 2)
            if(mt <= 0):
                mt = 1
            #print(str(mt))
            new_chromosome.crossover(mt)
            strategy = 'RAND'
            if(best_fitness >= round( ideal_fitness * 0.85) ):
                strategy = 'INTELLIGENT'
            gens += 1
            new_chromosome.mutate(mt,strategy)
            fitness = new_chromosome.get_fitness()
           # print('Best: '+str(best_fitness))
           # print('--------')
           # new_chromosome.print_sched()
            if(fitness >= best_fitness):
                best_fitness = fitness
                parents.insert(0,new_chromosome)

            #print(parents)

       # parents[0].print_sched()
        sched = parents[0].schedule
        from collections import OrderedDict
        fsched = OrderedDict(sorted(sched.items(), key=lambda t: t[0]))
        counts = {}
        for k,v in fsched.items():
            if v not in counts:
                counts[v] = 1
            else:
                counts[v] += 1
            a = '%s  %s' % (k,v)
            print(a)

        print (counts)
        print(parents[0].get_fitness())

        print('Generation :' + str(gens))








gen = ScheduleGenerator(test_bindings)
gen.gen_sched()















