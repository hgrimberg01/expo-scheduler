#!/usr/bin/env python3
from argparse import ArgumentParser
from random import randint, choice
from copy import deepcopy as DeepCopy
from datetime import datetime, timedelta
import math
import csv


# Some testing leftovers
#test_bindings = [('Team A', 'Event A'), ('Team B', 'Event A'), ('Team C', 'Event A'),
#            ('Team A', 'Event B'), ('Team B', 'Event B'), ('Team C', 'Event B'),
#            ('Team B', 'Event C'), ('Team C', 'Event C')]


""" Temporal Chromosome Class """

class Chromosome:
    def __init__(self,bindings, parent=None, parent_two = None, time_slots=60, max_nums=5):

        # Make an empty matrix(list-of-lists)

        self.times = [ []  for x in range(time_slots)]

        # Schedule is a dictionary that maps team names to events
        # and the respective time slots
        # The entire binding is the key -> time slot

        self.schedule = {}
        self.parent = parent
        self.parent_two = parent_two
        self.bindings = bindings
        self.time_slots = time_slots
        self.max_nums = max_nums
        # If there is no parent, we can safely assume we are the first in a
        # generation. Thus, proceed to randomly build an initial schedule.
        if(self.parent == None):
            self.build_chromosome()

    # Here is where the magic happens.
    # The fitness function determines the relative "goodness"
    # of a given state. Here, the varying heuristics are distilled into a
    # single number

    def get_fitness(self):
        # Initial Fitness Value
        fitness = 0

        # Flag that indicates scheduling conflicts
        team_conflict = False

        # Scan  each column in the time matrix(time slot)
        for i,k in enumerate(self.times):
            # If the amount of teams in the slot is permissible,
            # increment the fitness value by the number of teams in the slot.
            if not len(k) > self.max_nums:
                fitness += len(k)

        # Iterate through the schedule dictionary (team_tuple is the key, slot
        # is the integer value of the corresponding timeslot )
        for team_tuple, slot in self.schedule.items():

            # Now compare each key,value pair against every other pair.
            # TODO: Here is the first major slowdown of the algorithm as this
            #       operation is O(n^2)
            for team_tuple2, slot2 in self.schedule.items():

                # Set the conflict flag if the same team is scheduled twice in
                # the same time slot AND its not the same event.
                if team_tuple[0] == team_tuple2[0] and slot == slot2 and not team_tuple[1] == team_tuple2[1]:
                    team_conflict = True
                    break

                else:

                    # Otherwise, we know a team is scheduled without a
                    # conflict. Increment the fitness
                    fitness += 1


        return fitness

    # Builds the initial chromosome assuming there is no pre conditions
    # Does it completely randomly
    def build_chromosome(self):
        if(self.parent == None):
            # No parent, so randomly build a schedule,
            # Choose a team,event pair
            for binding in self.bindings:

                # Pick a random timeslot
                rand_pos = randint(1, self.time_slots) - 1
                selection = binding

                # Update the schedule and time matrix accordingly
                self.schedule[selection] = rand_pos
                self.times[rand_pos].append(selection)
        else:
            pass

    # Utility method that will rebuild the times matrix
    # from the current schedule. Useful for debugging and taking
    # a shotgun appoach to solve the problem
    def rebuild_times_from_sched(self):
        self.times = [ []  for x in range(self.time_slots)]
        for team, slot in self.schedule.items():
            self.times[slot].append(team)


    # Crossover function that randomly combines the schedule dictionaries
    # of two parents into a new one for the child.
    # It has two strategies implemented, but only Random(RAND) is tested.
    # RAND randomly mixes the schedules N (size) times. This can be improved
    # by randomly mixing more than one at a time.

    def crossover(self, size=1, strategy='RAND'):

        # Simple set union strategy for crossing over. Takes the union of the
        # two schedules. UNTESTED
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

        # Random strategy. Gives the first parent preference
        elif(strategy == 'RAND'):

            # Need a deep copy of the parents schedule to avoid modifying the
            # parent.
            new_sched = DeepCopy(self.parent.schedule)

            #Choose N(size) of from second parent to put into first parent

            for i in range(size):
                rand_key_one = choice(list(new_sched.keys()))
                rand_key_two = choice(list(self.parent_two.schedule.keys()))

                val_one = new_sched[rand_key_one]
                val_two = self.parent_two.schedule[rand_key_two]

                new_sched[rand_key_two] = val_one
                new_sched[rand_key_one] = val_two

            # Sets the schedule and rebuild the times matrix.
            self.schedule = new_sched
            self.rebuild_times_from_sched()





    # Mutate has two stragies for moving indivudal schedule elements around,
    # Random and Intelligent.
    def mutate(self, size=1, strategy='INTELLIGENT'):

        new_sched = self.schedule

        # Random is used to get close to solution, but gets much worse
        # as the solution space gets smaller with a large dataset (ie, when the
        # solution is 90% complete).
        # Permutes the schedule N (size) times by swapping values between
        # distinct keys.

        if(strategy == 'RAND'):
            for i in range(size):
                rand_key_one = choice(list(new_sched.keys()))

                rd = randint(1,self.time_slots) - 1
                old_val = self.schedule[rand_key_one]

                self.times[old_val].remove(rand_key_one)
                self.schedule[rand_key_one] = rd
                self.times[rd].append(rand_key_one)

        # The intelligent strategy will find an overloaded slot, reduce its
        # contents to the maximum allowed, and then find a new location for the
        # leftovers. This is slower to get close to the solution but is
        # neccesary to find a good solution.

        elif(strategy == 'INTELLIGENT'):
            # Iterate through all time slots

            for i,r in enumerate(self.times):
                # If we have too many elements in a slot
                if(len(r) > self.max_nums):
                    # Grab everything past the maximum size (array slicing
                    # syntax)
                    reloc = r[self.max_nums:]

                    # Reduce the contents of the slot to the maximum allowable
                    # items,
                    self.times[i] = r[:self.max_nums]

                    # Relocate what we removed from the overloaded slot
                    for mv in reloc:
                        open_slot = self.find_open_slot(mv)
                        self.schedule[mv] = open_slot
                        self.times[open_slot].append(mv)


    # Find me an open slot that also does not contain the tuple itself.
    def find_open_slot(self,mv):
        for i,r in enumerate(self.times):

            # Check if there is space in this timeslot and the entire tuple
            # (team, event pair) is not already on this slot.
            if len(r) < self.max_nums and mv not in r:

                # Since we know this a candidate slot, see if this team is
                # already in the slot.
                team_name_matches = filter(lambda x:  x[0] == mv[0], r)

                if not list(team_name_matches):
                    return i


""" Main schedule generating class """

class ScheduleGenerator:

    def __init__(self,bindings, time_slots=60, max_nums=5):
        self.time_slots = time_slots
        self.max_nums = max_nums
        self.bindings = bindings


    def gen_sched(self):
        generations = 0
        best_fitness = -1
        running_gens = 0
        parents = []
        self.parents = parents
        # Generate two random chromosomes
        init = Chromosome(self.bindings, time_slots=self.time_slots, max_nums=self.max_nums)
        init2 = Chromosome(self.bindings, time_slots=self.time_slots, max_nums=self.max_nums)

        # Get their fitness
        if1 = init.get_fitness()
        if2 = init2.get_fitness()

        # Assume they are part of gen. 1
        gens = 1

        # Set the Chromosome with the best fitness as the head of the list
        if(if1 > if2):
            best_fitness = if1
            parents.insert(0, init)
            parents.append(init2)
        elif (if2 >= if1):
            best_fitness = if2
            parents.insert(0, init2)
            parents.append(init)

        runs = 0

        # Calculate Ideal Fitness
        ideal_fitness = (len(self.bindings) ** 2) + len(self.bindings)

        # Keep spinning until we meet our ideal fitness
        while (best_fitness < ideal_fitness ):
            #rand_parent_one = parents[randint(1,len(parents))-1]

            # One parent is always the current best candidate
            rand_parent_one = parents[0]

            # The other parent is chosen at random
            rand_parent_two = parents[randint(1,len(parents))-1]
            new_chromosome = Chromosome(init.bindings,rand_parent_one,rand_parent_two, time_slots=self.time_slots, max_nums=self.max_nums)

            # Reduce the amount of mutation and crossing over as we approach
            # our goal.
            mt = math.floor((len(self.bindings) - best_fitness) / 2)
            if(mt <= 0):
                mt = 1
            new_chromosome.crossover(mt)

            # Default mutation strategy is Random
            strategy = 'RAND'

            # When we get very close to the answer, Random is no longer useful.
            # Switch over to a far slow, but more intelligent mutation
            # algorithm

            if(best_fitness >= round( ideal_fitness * 0.87)  ):
                strategy = 'INTELLIGENT'
                gens += 1
            #print(gens)
            #print('Fitness:'+str(best_fitness))

            # Mutate
            new_chromosome.mutate(mt, strategy)
            # Get the fitness
            fitness = new_chromosome.get_fitness()
            # If the new chromosome is better than any other, update the best
            # fitness and insert it into the head of the list.
            if(fitness >= best_fitness):
                best_fitness = fitness
                parents.insert(0,new_chromosome)


    def get_best(self):
        return self.parents[0].schedule









# prints the schedule sorted by team name. Also Prints the number of
# tuples in each time slot and some other stuff.

def print_schedule(ideal_sched,timed,start_time):

    sched = ideal_sched
    from collections import OrderedDict
    fsched = OrderedDict(sorted(sched.items(), key=lambda t: t[0]))
    counts = {}
    fmat = '%35s %20s %10s'
    header = fmat  % ('Team','Event','Time')
    print(header)
    print('----------------------------------------------------------------------------------------')
    for k,v in fsched.items():
        if v not in counts:
            counts[v] = 1
        else:
            counts[v] += 1
            td = timedelta(minutes=v*timed)
            final_time = start_time + td
            a = '%35s|%20s|%10s' % (k[0],k[1],final_time.strftime('%I:%M %p'))
            print(a)

    print('----------------------------------------------------------------------------------------')
    print('COUNTS:')
    print (counts)




# Main  function. Prase input and such.

def main():

    parser = ArgumentParser(description="Arguments for Scheduler")
    parser.add_argument('-b', '--bindings', metavar='BindingsFile', required=True, help='The CSV file containing team<->\
                        event bindings')

    parser.add_argument('-st', '--starttime', metavar='StartTime', default='09:00', help='The start time in\
                        24 Hour Format (14:01 -> 02:01 PM)')

    parser.add_argument('-et', '--endtime', metavar='EndTime', default='14:00', help='The end time in 24 Hour\
                        Format (14:01 -> 02:01 PM)')

    parser.add_argument('-el', '--eventlength', metavar='EventTime',  default=5, help='The length of a given\
                        time slot (aka event) in minutes.')

    parser.add_argument('-n', '--number', metavar='Number',  default=5, help='The number of teams that can\
                        fit in a single time slot.')

    args = vars(parser.parse_args())
    test_bindings = []
    with open(args['bindings'].strip(),'r') as f:
            r = csv.reader(f)
            test_bindings = [(row[0].strip(), row[1].strip()) for row in r ]

    start_time = args['starttime']
    end_time = args['endtime']

    start_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')

    time_d = end_time - start_time
    # Number of Time Slots Total Minutes / Minutes Per Time Slot
    time_slots = int(math.floor(( (time_d.seconds/60) / int(args['eventlength']))))

    # Number of teams that can be scheduled to a slot
    number_per_slot = int(args['number'])
    if len(test_bindings) > time_slots * number_per_slot:
        raise Exception('Not enough time for all teams to be scheduled')

    gen = ScheduleGenerator(test_bindings, time_slots, number_per_slot)
    gen.gen_sched()

    print_schedule(gen.get_best(), int(args['eventlength']), start_time)


# Isolate the main function
if __name__ == '__main__':
    main()








