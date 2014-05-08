EXPO SCHEDULER
==========================
Howard Grimberg

EECS 649 - Intro. to Artificial Intelligence

Final Project (4)

5/6/2014

Description
----------------

The purpose of the project was to implement a planner/scheduler using a genetic algorithm. Genetic algorithms basically attempt to look at multiple heuristics and try to improve them using various random and non-random means until the ideal (or as close as possible to ideal) solution is found. The goal was to automatic scheduling for competitions at the annual Engineering EXPO and produce a good schedule. The constraints include limited time (5 hours), limited number of conncurrent things per each time slot, variable time slots (5 minutes each before each rotation). Each team can only be in one place at a time, so the algorithm must ensure that the same team is not in the same time slot twice. The evolutionary algorithm produces generations of solutions. Each generation attempts to improve on the characteristics of its parents, although this is not always the case. Because the algorithm relies on probabilistic methods, the execution time has a huge variance between different runs. If a good solution is chosen randomly, the algorithm is very fast. If a poor solution si chosen randomly, the algorithm will be slow. Usually, it is somewhere in between (taking about 5-7 seconds for 271 team-event pairs). 



To Run
------------------------------
***Ensure that you have python3 installed. python2 should work but is untested, so use at your own risk.***
  1. Grant executable permissions to attempt2.py by typing 'chmod +x attempt2.py' (without quotes) into your terminal.
  2. To run, type './attempt2.py -b team_event_more.csv'. This will run the program and print the schedule to the console.
    *Note, this may take some time (up to 90 seconds), please be patient. Usually it is much faster*
  3. As an alternative, you may also run 'python3 attempt2.py -b team_event_more.csv'. Replace python3 with python2 for python 2.
  4. The default start time is 09:00 with an end time of 14:00 (2:00 PM), with 5 minute intervals and 5 actions per time slot.
  5. Run ./attempt2.py --help for all parameters.
  6. Additional test files are provided
  
***Tested on EECS Cycle Servers***


License
---------
Licensed under the MIT license. See LICENSE.md
