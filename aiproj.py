#!/usr/bin/env python3

from argparse import ArgumentParser
from queue import PriorityQueue
from datetime import datetime
import csv




TIME_FORMAT = '%H:%M'

#| Class that encapsulates information regarding a specifc competition event.






class Event:
    def __init__(self, name, max_concurrent):
        self.name = name
        self.max_concurrent = max_concurrent

    def __unicode__(self):
        return self.name


#| Class that encapsulates information regarding a specific team

class Team:
    def __init__(self, name, division):
        self.name = name
        self.division = division
        self.events = {}



    def add_event(self,evt):
        self.events[evt.name] = evt

    def __unicode__(self):
        return self.name





class Expo:
    def __init__(self, start_time,end_time, time_quant):
        self.teams = {}
        self.divisions = []
        self.events = {}
        self.start_time = start_time
        self.end_time = end_time
        self.time_quant = time_quant

    def add_team(self,team):
        self.teams[team.name] = team

    def add_event(self, event):
        self.events[event.name] = event

    def add_event_to_team(self, event_name, team_name):
        evt = self.events[event_name]
        team = self.teams[team_name]

    def get_division_teams(self, div):
        return filter(lambda x: x.division == div, list(self.teams.values()))







def load_events(expo, fname):
    pass

def load_teams(expo, fname):
    pass

def load_event_team_bindings(expo, fname):
    pass


#| Function that will return a EXPO class that contains team and events.
def loader(fname):
    fopen = open(fname,'r')
    csvread = csv.reader(fopen)
    teams = []

    events = {}

    for row in csvread:
        team_name = str(row[0])
        team_ev = []
        for col in row[1:]:
            v = col.strip()
            if (v):
                team_ev.append(v)
                if v in events:
                    events[v] += 1
                else:
                    events[v] = 1
        team = Team(team_name,team_ev)
        teams.append(team)

    return Expo(teams, events, '0900','1400')




def dispatch(expo):
    sort_by_num_events = sorted(expo.teams, key=lambda x:  x.event_count, reverse=True)
    pq = PriorityQueue(1000)

    for i in expo.teams:
        pq.put(i)

    TIME_QUANTUM_MIN = 5
    NUM_OF_HOURS = 5
    SLOT_IN_HOUR =( 60 // TIME_QUANTUM_MIN)-1
    EVENT_CAP = 3

    #| Initialize Schedule
    sched  = [[0 for x in range(SLOT_IN_HOUR)] for x in range(5)]
    for h in range(0,NUM_OF_HOURS):
        for s in range(0,SLOT_IN_HOUR):
            event_dir ={}
            for e in expo.events.keys():
                event_dir[e] = []

            sched[h][s] = event_dir

    while not pq.empty():
        team = pq.get()
        evt = team.events.pop()

        hr = 0
        d = False
        while hr < 5:
            slt = 0
            b = False
            while slt < SLOT_IN_HOUR:
                a = sched[hr][slt][evt]
                if (len(a) < 3):
                    a.append(team.name)
                    sched[hr][slt][evt] = a
                    if(len(team.events) > 0):
                        pq.put(team)
                    b = True
                    break
                else:
                    slt += 1
            hr += 1
            if(b):
                break

        if(hr == 4):
            team.events.append(evt)
            pq.put(team)

    return sched








def genetic(expo):



    def fitness(time_slot


    pass











#| Main function for ease of reading

def Main():
    parser = ArgumentParser(description="Arguments for Scheduler")
    parser.add_argument('-b', '--bindings',metavar='BindingsFile', required=True, help='The CSV file containing team<->event bindings')
    parser.add_argument('-t', '--teams',metavar='TeamsFile', required=True, help='The CSV file containing teams and the divison they belong to')
    parser.add_argument('-e', '--events',metavar='EventsFile', required=True, help='The CSV file containing events and max per timeslot, per divison')

    start_time_str = '09:00'
    end_time_str = '14:00'



    args = parser.parse_args()





if __name__ == '__main__':
    Main()

